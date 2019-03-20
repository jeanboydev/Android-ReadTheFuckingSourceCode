# Android - PowerManagerService 灭屏

## 一、Power 按键灭屏

当 Power 键灭屏时，会在 PhoneWindowManager 中处理按键事件后，调用到 PMS 的 `gotoSleep()` 进行灭屏处理，下面直接看看 PhoneWindowManger 中对 Power 键灭屏的处理以及和 PMS 的交互。

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

@Override
public int interceptKeyBeforeQueueing(KeyEvent event, int policyFlags) {
    //...
    final boolean interactive = (policyFlags & FLAG_INTERACTIVE) != 0;
    final boolean down = event.getAction() == KeyEvent.ACTION_DOWN;
    final boolean canceled = event.isCanceled();
    final int keyCode = event.getKeyCode();
    //...
    // Handle special keys.
    switch (keyCode) {
        //...
        case KeyEvent.KEYCODE_POWER: {
            // Any activity on the power button stops the accessibility shortcut
            cancelPendingAccessibilityShortcutAction();
            result &= ~ACTION_PASS_TO_USER;
            isWakeKey = false; // wake-up will be handled separately
            if (down) {//处理按下事件
                interceptPowerKeyDown(event, interactive);
            } else {//处理抬起事件
                interceptPowerKeyUp(event, interactive, canceled);
            }
            break;
        }
        //...
    }
    //...
    return result;
}
```

### 1.1 interceptPowerKeyUp()

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

private void interceptPowerKeyUp(KeyEvent event, boolean interactive, boolean canceled) {
    final boolean handled = canceled || mPowerKeyHandled;
    mScreenshotChordPowerKeyTriggered = false;
    cancelPendingScreenshotChordAction();
    cancelPendingPowerKeyAction();

    if (!handled) {
        //...
        // No other actions.  Handle it immediately.
        powerPress(eventTime, interactive, mPowerKeyPressCounter);
    }

    // Done.  Reset our state.
    finishPowerKeyPress();
}
```

在处理 Power 键抬起事件时，开始了灭屏流程。

### 1.2 powerPress()

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

private void powerPress(long eventTime, boolean interactive, int count) {
    if (mScreenOnEarly && !mScreenOnFully) {
        Slog.i(TAG, "Suppressed redundant power key press while "
               + "already in the process of turning the screen on.");
        return;
    }

   if (count == 2) {//处理同时按两个按键的情况
        powerMultiPressAction(eventTime, interactive, mDoublePressOnPowerBehavior);
    } else if (count == 3) {//处理同时按三个个按键的情况
        powerMultiPressAction(eventTime, interactive, mTriplePressOnPowerBehavior);
    } else if (interactive && !mBeganFromNonInteractive) {
        switch (mShortPressOnPowerBehavior) {
            case SHORT_PRESS_POWER_NOTHING:
                break;
            case SHORT_PRESS_POWER_GO_TO_SLEEP://灭屏
                mPowerManager.goToSleep(eventTime,
                                        PowerManager.GO_TO_SLEEP_REASON_POWER_BUTTON, 0);
                break;
            case SHORT_PRESS_POWER_REALLY_GO_TO_SLEEP://灭屏，直接跳过 Doze 状态
                mPowerManager.goToSleep(eventTime,
                                        PowerManager.GO_TO_SLEEP_REASON_POWER_BUTTON,
                                        PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE);
                break;
            case SHORT_PRESS_POWER_REALLY_GO_TO_SLEEP_AND_GO_HOME://灭屏，回到 Home
                mPowerManager.goToSleep(eventTime,
                                        PowerManager.GO_TO_SLEEP_REASON_POWER_BUTTON,
                                        PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE);
                launchHomeFromHotKey();
                break;
                //...
        }
    }
}
```

在这里调用了 PowerManager 的 `goToSleep()` 方法来灭屏。

### 1.3 goToSleep()

```java
//frameworks/base/core/java/android/os/PowerManager.java

public void goToSleep(long time, int reason, int flags) {
    try {
        mService.goToSleep(time, reason, flags);
    } catch (RemoteException e) { }
}
```

可以看到，在 PowerManger 中开始向下调用到了 PoweManagerService 中的 `goToSleep()` 中。

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@Override // Binder call
public void goToSleep(long eventTime, int reason, int flags) {
    if (eventTime > SystemClock.uptimeMillis()) {
        throw new IllegalArgumentException("event time must not be in the future");
    }
    //检查权限
    mContext.enforceCallingOrSelfPermission(
        android.Manifest.permission.DEVICE_POWER, null);

    final int uid = Binder.getCallingUid();
    final long ident = Binder.clearCallingIdentity();
    try {
        //调用 gotToSleepInternal
        goToSleepInternal(eventTime, reason, flags, uid);
    } finally {
        Binder.restoreCallingIdentity(ident);
    }
}
```

这个方法的参数和 PowerManager,PhoneWindowManage r中的同名方法对应，需要注意的是第二个参数和第三个参数；
第二个参数：表示灭屏原因，在 PowerManager 中定义了一些常量值来表示；
第三个参数：是一个标识，用来表示是否直接进入灭屏，一般的灭屏流程，都会先进入 Doze 状态，然后才会进入 Sleep 状态，如果将 flag 设置为 1，则将会直接进入 Sleep 状态，这部分会在下文中逐渐分析到。

### 1.4 goToSleepInternal()

在 goToSleep() 方法中，检查权限之后，开始调用了 goToSleepInternal() 方法，该方法如下：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void goToSleepInternal(long eventTime, int reason, int flags, int uid) {
    synchronized (mLock) {
        //详见【1.5】
        if (goToSleepNoUpdateLocked(eventTime, reason, flags, uid)) {
            updatePowerStateLocked();//详见【1.6】
        }
    }
}
```

这个方法逻辑很简单，首先是调用了 `goToSleepNoUpdateLocked()` 方法，并根据该方法返回值来决定是否调用 `updatePowerStateLocked()` 方法。

### 1.5 goToSleepNoUpdateLocked()

一般来说，goToSleepNoUpdateLocked() 都会返回 true，现在看看该方法：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@SuppressWarnings("deprecation")
private boolean goToSleepNoUpdateLocked(long eventTime, int reason, int flags, int uid) {
    if (eventTime < mLastWakeTime
        || mWakefulness == WAKEFULNESS_ASLEEP
        || mWakefulness == WAKEFULNESS_DOZING
        || !mBootCompleted || !mSystemReady) {
        return false;
    }

    try {
        switch (reason) {
            case PowerManager.GO_TO_SLEEP_REASON_DEVICE_ADMIN:
                Slog.i(TAG, "Going to sleep due to device administration policy "
                       + "(uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_TIMEOUT:
                Slog.i(TAG, "Going to sleep due to screen timeout (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_LID_SWITCH:
                Slog.i(TAG, "Going to sleep due to lid switch (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_POWER_BUTTON:
                Slog.i(TAG, "Going to sleep due to power button (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_SLEEP_BUTTON:
                Slog.i(TAG, "Going to sleep due to sleep button (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_HDMI:
                Slog.i(TAG, "Going to sleep due to HDMI standby (uid " + uid +")...");
                break;
            default:
                Slog.i(TAG, "Going to sleep by application request (uid " + uid +")...");
                reason = PowerManager.GO_TO_SLEEP_REASON_APPLICATION;
                break;
        }

        //标记最后一次灭屏时间
        mLastSleepTime = eventTime;
        //用于判定是否进入屏保
        mSandmanSummoned = true;
        //设置 wakefulness 值为 WAKEFULNESS_DOZING，
        //因此先进 Doze 状态，详见【1.5.1】
        setWakefulnessLocked(WAKEFULNESS_DOZING, reason);

        // Report the number of wake locks that will be cleared by going to sleep.
        //灭屏时，将清楚以下三种使得屏幕保持亮屏的 wakelock 锁，numWakeLocksCleared 统计下个数
        int numWakeLocksCleared = 0;
        final int numWakeLocks = mWakeLocks.size();
        for (int i = 0; i < numWakeLocks; i++) {
            final WakeLock wakeLock = mWakeLocks.get(i);
            switch (wakeLock.mFlags & PowerManager.WAKE_LOCK_LEVEL_MASK) {
                case PowerManager.FULL_WAKE_LOCK:
                case PowerManager.SCREEN_BRIGHT_WAKE_LOCK:
                case PowerManager.SCREEN_DIM_WAKE_LOCK:
                    numWakeLocksCleared += 1;
                    break;
            }
        }

        // Skip dozing if requested.
        //如果带有 PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE 的 flag，
        //则直接进入 Sleep 状态，不再进入 Doze 状态
        if ((flags & PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE) != 0) {
            //该方法才会真正地进入睡眠，详见【1.5.2】
            reallyGoToSleepNoUpdateLocked(eventTime, uid);
        }
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
    return true;
}
```

在这个方法中：

首先，是判断调用该方法的原因并打印  log，该  log  在日常分析问题时非常有用；
然后，通过 `setWakefulnessLocked()` 将当前  wakefulness  设置为 Doze 状态；
最后，通过 flag 判断，如果 flag 为 1，则调用 `reallyGoToSleepNoUpdateLocked()` 方法直接进入 Sleep 状态。

因此，系统其他模块在调用 PM.goToSleep() 灭屏时，在除指定 flag 为 `PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE` 的情况外，都会首先进入 Doze，再由 Doze 进入 Sleep。

#### 1.5.1 setWakefulnessLocked()

`setWakefulnessLocked()` 方法用来设置 wakefulness 值，同时将会调用 Notifier中wakefulness 相关的逻辑，这部分在之前的流程分析中也分析过，这里再来看下：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void setWakefulnessLocked(int wakefulness, int reason) {
    if (mWakefulness != wakefulness) {
        //设置 mWakefulness
        mWakefulness = wakefulness;
        mWakefulnessChanging = true;
        mDirty |= DIRTY_WAKEFULNESS;
        //调用 Notifier 中的方法，做 wakefulness 改变开始时的工作
        mNotifier.onWakefulnessChangeStarted(wakefulness, reason);
    }
}
```

我们跟着执行流程来进行分析，Notifier 是 PMS 模块中用于进行“通知”的一个组件类。比如：发送亮灭屏广播就是它来负责，具体详细的分析请【】查看。这里针对于灭屏场景，再来看下其中的逻辑：

##### 1.5.1.1 onWakefulnessChangeStarted()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public void onWakefulnessChangeStarted(final int wakefulness, int reason) {
    //由于 wakefulness 为 Doze，故 interactive 为 false
    final boolean interactive = PowerManagerInternal.isInteractive(wakefulness);
    //...
    // Handle any early interactive state changes.
    // Finish pending incomplete ones from a previous cycle.
    if (mInteractive != interactive) {
        // Finish up late behaviors if needed.
        if (mInteractiveChanging) {
            handleLateInteractiveChange();
        }

        // Start input as soon as we start waking up or going to sleep.
        mInputManagerInternal.setInteractive(interactive);
        mInputMethodManagerInternal.setInteractive(interactive);

        // Notify battery stats.
        try {
            mBatteryStats.noteInteractive(interactive);
        } catch (RemoteException ex) { }

        // Handle early behaviors.
        mInteractive = interactive;
        mInteractiveChangeReason = reason;
        mInteractiveChanging = true;
        handleEarlyInteractiveChange();
    }
}
```

在这个方法中，首先根据 wakefulness 值判断了系统当前的交互状态，如果是处于 Awake 状态和 Dream 状态，则表示可交互；如果处于 Doze 和 Asleep 状态，则表示不可交互；由于在 setWakefulnessLocked() 中已经设置了 wakefulness 为 DOZE 状态，因此此时处于不可交互状态，接下来开始执行 handleEarlyInteractiveChange() 方法：

##### 1.5.1.2 handleEarlyInteractiveChange()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void handleEarlyInteractiveChange() {
    synchronized (mLock) {
        if (mInteractive) {//此时为 false
            // Waking up...
            mHandler.post(new Runnable() {
                @Override
                public void run() {
                    // Note a SCREEN tron event is logged in PowerManagerService.
                    mPolicy.startedWakingUp();
                }
            });

            // Send interactive broadcast.
            mPendingInteractiveState = INTERACTIVE_STATE_AWAKE;
            mPendingWakeUpBroadcast = true;
            updatePendingBroadcastLocked();
        } else {
            // Going to sleep...
            // Tell the policy that we started going to sleep.
            final int why = translateOffReason(mInteractiveChangeReason);
            mHandler.post(new Runnable() {
                @Override
                public void run() {//通过 PhoneWindowManager 设置锁屏
                    mPolicy.startedGoingToSleep(why);
                }
            });
        }
    }
}
```

在这个方法中，将调用 mPolicy.startedGoingToSleep(why) 进行锁屏流程。

### 1.6 updatePowerStateLocked()

回到 PMS 中，在处理完 `setWakefulnessLocked()` 方法后，由于没有 `PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE`，所以不会立即执行 `reallyGoToSleepNoUpdateLocked()` 方法，此时 `goToSleepNoUpdateLocked()` 方法完毕并返回 true。

之后开始执行 `updatePowerStateLocked()` 方法了，这个方法对于熟悉 PMS 模块的人来说再熟悉不过了，它是整个 PMS 的核心，详细的分析请点击这里，在这里我们只看其灭屏时的一些处理。

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updatePowerStateLocked() {
    //...
    try {
        //...

        // Phase 2: Update display power state.
        //更新屏幕状态
        boolean displayBecameReady = updateDisplayPowerStateLocked(dirtyPhase2);

        // Phase 3: Update dream state (depends on display ready signal).
        //更新屏保信息
        updateDreamLocked(dirtyPhase2, displayBecameReady);

        // Phase 4: Send notifications, if needed.
        // 收尾
        finishWakefulnessChangeIfNeededLocked();

        // Phase 5: Update suspend blocker.
        // Because we might release the last suspend blocker here, we need to make sure
        // we finished everything else first!
        //释放锁
        updateSuspendBlockerLocked();
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
}
```

- `updateDisplayPowerStateLocked()` 将会向 DisplayPowerController 请求新的屏幕状态，完成屏幕的更新；
- updateDreamLocked() 方法用来更新屏保信息，除此之外还有一个任务——调用 reallyGoToSleep() 方法进入休眠，即由 DOZE 状态进入 Sleep 状态。
- `finishWakefulnessChangeIfNeededLocked()` 方法用来做最后的收尾工作，当然，在这里会调用到 Notifier 中进行收尾。
- `updateSuspendBlockerLocked()` 方法将用来更新 SuspendBlocker 锁，会根据当前的 WakeLock 类型以及屏幕状态来决定是否需要申请 SuspendBlocker 锁。

在 `updateDreamLocked()` 中更新屏保状态时，如果此时处于Doze状态且屏保没有进行，则将调用 `reallyGoToSleepNoUpdateLocked()` 方法，将 wakefulness 值设置为了 Sleep，部分代码如下：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void handleSandman() { // runs on handler thread
    //...
    synchronized (mLock) {
        //...
        //决定是否继续 Dream
        if (wakefulness == WAKEFULNESS_DREAMING) {
            //...
        } else if (wakefulness == WAKEFULNESS_DOZING) {
            if (isDreaming) {
                return; // continue dozing
            }

            //进入 asleep 状态
            reallyGoToSleepNoUpdateLocked(SystemClock.uptimeMillis(), Process.SYSTEM_UID);
            updatePowerStateLocked();
        }
    }
    //...
}
```

#### 1.6.1 reallyGoToSleepNoUpdateLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

// Done dozing, drop everything and go to sleep.
private boolean reallyGoToSleepNoUpdateLocked(long eventTime, int uid) {
    if (eventTime < mLastWakeTime || mWakefulness == WAKEFULNESS_ASLEEP
        || !mBootCompleted || !mSystemReady) {
        return false;
    }

    try {
        //设置为 ASLEEP 状态
        setWakefulnessLocked(WAKEFULNESS_ASLEEP, PowerManager.GO_TO_SLEEP_REASON_TIMEOUT);
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
    return true;
}
```

到这里 Power 按键灭屏过程已经分析完了，我们来看下整体流程。

![Power 按键灭屏流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pms_gosleep/01.png)

## 二、超时灭屏

经过上面的分析，我们知道了 Power 键灭屏由 PhoneWindowManager 发起了 `goToSleep`，现在来看看超时灭屏是如何实现的。

时灭屏主要有两个影响因素：休眠时间和用户活动。休眠时间在 Settings 中进行设置，用户活动是指当手机处于亮屏状态，都会调用 `userActivityNoUpdateLocked()` 方法去更新用户活动时间。接下来我们就从 `userActivityNoUpdateLocked()` 方法开始分析其超时灭屏的流程。

### 2.1 userActivityNoUpdateLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean userActivityNoUpdateLocked(long eventTime, int event, int flags, int uid) {
    if (eventTime < mLastSleepTime || eventTime < mLastWakeTime
        || !mBootCompleted || !mSystemReady) {
        return false;
    }

    try {
        if (eventTime > mLastInteractivePowerHintTime) {
            powerHintInternal(PowerHint.INTERACTION, 0);
            mLastInteractivePowerHintTime = eventTime;
        }

        mNotifier.onUserActivity(event, uid);

        if (mUserInactiveOverrideFromWindowManager) {
            mUserInactiveOverrideFromWindowManager = false;
            mOverriddenTimeout = -1;
        }

        //如果 wakefulness 为 Asleep 或 Doze，不再计算超时时间，直接返回
        if (mWakefulness == WAKEFULNESS_ASLEEP
            || mWakefulness == WAKEFULNESS_DOZING
            || (flags & PowerManager.USER_ACTIVITY_FLAG_INDIRECT) != 0) {
            return false;
        }

        //如果带有该 flag，则会小亮一会儿再灭屏
        if ((flags & PowerManager.USER_ACTIVITY_FLAG_NO_CHANGE_LIGHTS) != 0) {
            if (eventTime > mLastUserActivityTimeNoChangeLights
                && eventTime > mLastUserActivityTime) {
                mLastUserActivityTimeNoChangeLights = eventTime;
                mDirty |= DIRTY_USER_ACTIVITY;
                if (event == PowerManager.USER_ACTIVITY_EVENT_BUTTON) {
                    mDirty |= DIRTY_QUIESCENT;
                }

                return true;
            }
        } else {
            if (eventTime > mLastUserActivityTime) {
                //将当前时间赋值给 mLastUserActivityTime
                mLastUserActivityTime = eventTime;
                mDirty |= DIRTY_USER_ACTIVITY;
                if (event == PowerManager.USER_ACTIVITY_EVENT_BUTTON) {
                    mDirty |= DIRTY_QUIESCENT;
                }
                return true;
            }
        }
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
    return false;
}
```

在这个方法中，如果传入的参数 flag 为 `PowerManager.USER_ACTIVITY_FLAG_NO_CHANGE_LIGHTS`，则将事件时间赋值给 mLastUserActivityTimeNoChangeLights，否则将事件时间赋值给 mLastUserActivityTime。这个 flag 标志用于延长亮屏或 Dim 的时长一小会儿。

当这个方法执行之后，就得到了 mLastUserActivityTime 或者 mLastUserActivityTimeNoChangeLights 的值，然后经过一些调用后，又会进入 `updatePowerStateLocked()` 方法中。在这个方法中，与超时灭屏直接相关的就是 for 循环部分：

### 2.2 updatePowerStateLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updatePowerStateLocked() {
    //...
    try {
        //...
        for (;;) {
            int dirtyPhase1 = mDirty;
            dirtyPhase2 |= dirtyPhase1;
            mDirty = 0;

            updateWakeLockSummaryLocked(dirtyPhase1);
            updateUserActivitySummaryLocked(now, dirtyPhase1);//详见【2.2.1】
            if (!updateWakefulnessLocked(dirtyPhase1)) {//详见【2.3】
                break;
            }
        }
        //...
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
}
```

其中 `updateWakeLockSummaryLocked()` 用来统计WakeLock，这里就不分析该方法了，详细的分析请【】。

#### 2.2.1 updateUserActivitySummaryLocked()

现在从 `updateUserActivitySummaryLocked()` 方法开始分析，该方法如下：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateUserActivitySummaryLocked(long now, int dirty) {
    // Update the status of the user activity timeout timer.
    if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY
                  | DIRTY_WAKEFULNESS | DIRTY_SETTINGS)) != 0) {
        mHandler.removeMessages(MSG_USER_ACTIVITY_TIMEOUT);

        long nextTimeout = 0;
        if (mWakefulness == WAKEFULNESS_AWAKE
            || mWakefulness == WAKEFULNESS_DREAMING
            || mWakefulness == WAKEFULNESS_DOZING) {
            //获取睡眠时长，为 Settings.Secure.SLEEP_TIMEOUT 的值和最小休眠时间的最大值，
            //Settings.Secure.SLEEP_TIMEOUT 一般为 -1，表示禁用，因此该值默认为 -1
            final int sleepTimeout = getSleepTimeoutLocked();
            //获取休眠时长，在 Settings 中设置的值
            final int screenOffTimeout = getScreenOffTimeoutLocked(sleepTimeout);
            //获取 Dim 时长，由休眠时长剩 Dim 百分比得到
            final int screenDimDuration = getScreenDimDurationLocked(screenOffTimeout);
            //用户活动是否由 Window 覆盖
            final boolean userInactiveOverride = mUserInactiveOverrideFromWindowManager;

            //该值用来统计用户活动状态，每次进入该方法，置为 0
            mUserActivitySummary = 0;
            //上次用户活动时间 >= 上次唤醒时间
            if (mLastUserActivityTime >= mLastWakeTime) {
                //下次超时时间为上次用户活动时间 + 休眠时间 - Dim 时间
                //到达这个时间后，将进入 Dim 状态
                nextTimeout = mLastUserActivityTime
                    + screenOffTimeout - screenDimDuration;
                //如果当前时间 < nextTimeout，则此时处于亮屏状态，
                //标记 mUserActivitySummary 为 USER_ACTIVITY_SCREEN_BRIGHT
                if (now < nextTimeout) {
                    mUserActivitySummary = USER_ACTIVITY_SCREEN_BRIGHT;
                } else {
                    //如果当前时间 > nextTimeout，此时有两种情况，要么进入 Dim 要么进入 Sleep
                    //将上次用户活动时间 + 灭屏时间赋值给 nextTimeout，
                    //如果该值大于当前时间，则说明此时应该处于 Dim 状态
                    //因此将标记 mUserActivitySummary 为 USER_ACTIVITY_SCREEN_DIM
                    nextTimeout = mLastUserActivityTime + screenOffTimeout;
                    if (now < nextTimeout) {
                        mUserActivitySummary = USER_ACTIVITY_SCREEN_DIM;
                    }
                }
            }
            //判断和 USER_ACTIVITY_FLAG_NO_CHANGE_LIGHTS 标记相关，如果带有此标记，才会进入该 if
            if (mUserActivitySummary == 0
                && mLastUserActivityTimeNoChangeLights >= mLastWakeTime) {
                //下次超时时间 = 上次用户活动时间 + 灭屏时间
                nextTimeout = mLastUserActivityTimeNoChangeLights + screenOffTimeout;
                //根据当前时间和 nextTimeout 设置 mUserActivitySummary
                if (now < nextTimeout) {
                    if (mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_BRIGHT
                        || mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_VR) {
                        mUserActivitySummary = USER_ACTIVITY_SCREEN_BRIGHT;
                    } else if (mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_DIM) {
                        mUserActivitySummary = USER_ACTIVITY_SCREEN_DIM;
                    }
                }
            }

            //不满足以上条件时，此时 mUserActivitySummary 为 0，
            //这种情况应该为当 mUserActivitySummary 经历了 USER_ACTIVITY_SCREEN_BRIGHT
            //和 USER_ACTIVITY_SCREEN_DIM 之后才会执行到这里
            if (mUserActivitySummary == 0) {
                if (sleepTimeout >= 0) {
                    //获取上次用户活动时间的最后一次时间
                    final long anyUserActivity = Math.max(mLastUserActivityTime,
                                                          mLastUserActivityTimeNoChangeLights);
                    if (anyUserActivity >= mLastWakeTime) {
                        nextTimeout = anyUserActivity + sleepTimeout;
                        //将 mUserActivitySummary 值置为 USER_ACTIVITY_SCREEN_DREAM，表示屏保
                        if (now < nextTimeout) {
                            mUserActivitySummary = USER_ACTIVITY_SCREEN_DREAM;
                        }
                    }
                } else {
                    //将 mUserActivitySummary 值置为 USER_ACTIVITY_SCREEN_DREAM，表示屏保
                    mUserActivitySummary = USER_ACTIVITY_SCREEN_DREAM;
                    nextTimeout = -1;
                }
            }

            if (mUserActivitySummary != USER_ACTIVITY_SCREEN_DREAM && userInactiveOverride) {
                if ((mUserActivitySummary &
                     (USER_ACTIVITY_SCREEN_BRIGHT | USER_ACTIVITY_SCREEN_DIM)) != 0) {
                    // Device is being kept awake by recent user activity
                    if (nextTimeout >= now && mOverriddenTimeout == -1) {
                        // Save when the next timeout would have occurred
                        mOverriddenTimeout = nextTimeout;
                    }
                }
                mUserActivitySummary = USER_ACTIVITY_SCREEN_DREAM;
                nextTimeout = -1;
            }

            if (mUserActivitySummary != 0 && nextTimeout >= 0) {
                //发送一个异步 Handler 定时消息
                Message msg = mHandler.obtainMessage(MSG_USER_ACTIVITY_TIMEOUT);
                msg.setAsynchronous(true);
                mHandler.sendMessageAtTime(msg, nextTimeout);
            }
        } else {//当 wakefulness = Sleep 的时候，直接将 mUserActivitySummary 置为 0
            mUserActivitySummary = 0;
        }
    }
}
```

#### 2.2.2 MSG_USER_ACTIVITY_TIMEOUT

Handler 的调用处理逻辑如下：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@Override
public void handleMessage(Message msg) {
    switch (msg.what) {
        case MSG_USER_ACTIVITY_TIMEOUT:
            handleUserActivityTimeout();
            break;
    }
}

private void handleUserActivityTimeout() { // runs on handler thread
    synchronized (mLock) {
        mDirty |= DIRTY_USER_ACTIVITY;
        updatePowerStateLocked();
    }
}
```

当执行到这个方法后，现在就统计得到了 `mWakeLockSummary` 和 `mUserActivitySummary` 的值，现在我们看下一个方法  `updateWakefulnessLocked()`。

### 2.3 updateWakefulnessLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean updateWakefulnessLocked(int dirty) {
    boolean changed = false;
    if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY | DIRTY_BOOT_COMPLETED
                  | DIRTY_WAKEFULNESS | DIRTY_STAY_ON | DIRTY_PROXIMITY_POSITIVE
                  | DIRTY_DOCK_STATE)) != 0) {
        //isItBedTimeYetLocked() 判断是否需要"睡觉"了，详见【2.3.1】
        if (mWakefulness == WAKEFULNESS_AWAKE && isItBedTimeYetLocked()) {
            final long time = SystemClock.uptimeMillis();
            if (shouldNapAtBedTimeLocked()) {//进入屏保，详见【2.3.2】
                changed = napNoUpdateLocked(time, Process.SYSTEM_UID);
            } else {//开始休眠，详见【2.3.3】
                changed = goToSleepNoUpdateLocked(time,
						PowerManager.GO_TO_SLEEP_REASON_TIMEOUT, 0, Process.SYSTEM_UID);
            }
        }
    }
    return changed;
}
```

这个方法中可以看到，首先根据 `isItBedTimeYetLocked()` 和 mWakefulness 来决定是否执行，然后根据`shouldNapAtBedTimeLocked()` 决定进入屏保还是休眠。

该方法如果返回值为 true，则说明此时屏幕状态发生改变（在 `goToSleepNoUpdateLocked()` 和 `napNoUpdateLocked()` 中会分别设置 mWakefulness 为 DREAM 和 ASLEEP），因此将不会跳出 for 循环，再次进行一次循环。这就是为何会设置一个死循环的目的，同时也说明只有超时灭屏才会循环两次，其他情况下都会只执行一次 for 循环就退出。

#### 2.3.1 isItBedTimeYetLocked()

回到该方法中，我们继续看看 isItBedTimeYetLocked()：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean isItBedTimeYetLocked() {
    return mBootCompleted && !isBeingKeptAwakeLocked();
}

private boolean isBeingKeptAwakeLocked() {
    return mStayOn//是否需要保持常亮
        || mProximityPositive//PSensor 是否靠近
        || (mWakeLockSummary & WAKE_LOCK_STAY_AWAKE) != 0//当前是否有 Wakelock 类型为屏幕相关的锁
        || (mUserActivitySummary & (USER_ACTIVITY_SCREEN_BRIGHT
				| USER_ACTIVITY_SCREEN_DIM)) != 0//当前用户活动状态是否为 Dream 或者 0
        || mScreenBrightnessBoostInProgress;//是否处于亮度增强过程中
}
```

以上代码可以看出，如果有任意一个条件为 true，那么就不能进入休眠或者屏保状态，因此只有全部为 false 时，才会返回 false，从而说明需要“睡觉”了，接着会进入 if 条件中。

#### 2.3.2 shouldNapAtBedTimeLocked()

如果 `shouldNapAtBedTimeLocked()` 返回 true，则开始屏保，否则直接休眠。

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean shouldNapAtBedTimeLocked() {
    return mDreamsActivateOnSleepSetting
        || (mDreamsActivateOnDockSetting
            && mDockState != Intent.EXTRA_DOCK_STATE_UNDOCKED);
}
```

#### 2.3.3 goToSleepNoUpdateLocked()

当开始休眠时，直接调用了 `goToSleepNoUpdateLocked()` 方法中了，于是开始走休眠流程，之后的逻辑和 Power 键灭屏一样了。

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@SuppressWarnings("deprecation")
private boolean goToSleepNoUpdateLocked(long eventTime, int reason, int flags, int uid) {
    if (DEBUG_SPEW) {
        Slog.d(TAG, "goToSleepNoUpdateLocked: eventTime=" + eventTime
               + ", reason=" + reason + ", flags=" + flags + ", uid=" + uid);
    }

    if (eventTime < mLastWakeTime
        || mWakefulness == WAKEFULNESS_ASLEEP
        || mWakefulness == WAKEFULNESS_DOZING
        || !mBootCompleted || !mSystemReady) {
        return false;
    }

    Trace.traceBegin(Trace.TRACE_TAG_POWER, "goToSleep");
    try {
        switch (reason) {
            case PowerManager.GO_TO_SLEEP_REASON_DEVICE_ADMIN:
                Slog.i(TAG, "Going to sleep due to device administration policy "
                       + "(uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_TIMEOUT:
                Slog.i(TAG, "Going to sleep due to screen timeout (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_LID_SWITCH:
                Slog.i(TAG, "Going to sleep due to lid switch (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_POWER_BUTTON:
                Slog.i(TAG, "Going to sleep due to power button (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_SLEEP_BUTTON:
                Slog.i(TAG, "Going to sleep due to sleep button (uid " + uid +")...");
                break;
            case PowerManager.GO_TO_SLEEP_REASON_HDMI:
                Slog.i(TAG, "Going to sleep due to HDMI standby (uid " + uid +")...");
                break;
            default:
                Slog.i(TAG, "Going to sleep by application request (uid " + uid +")...");
                reason = PowerManager.GO_TO_SLEEP_REASON_APPLICATION;
                break;
        }

        mLastSleepTime = eventTime;
        mSandmanSummoned = true;
        setWakefulnessLocked(WAKEFULNESS_DOZING, reason);

        // Report the number of wake locks that will be cleared by going to sleep.
        int numWakeLocksCleared = 0;
        final int numWakeLocks = mWakeLocks.size();
        for (int i = 0; i < numWakeLocks; i++) {
            final WakeLock wakeLock = mWakeLocks.get(i);
            switch (wakeLock.mFlags & PowerManager.WAKE_LOCK_LEVEL_MASK) {
                case PowerManager.FULL_WAKE_LOCK:
                case PowerManager.SCREEN_BRIGHT_WAKE_LOCK:
                case PowerManager.SCREEN_DIM_WAKE_LOCK:
                    numWakeLocksCleared += 1;
                    break;
            }
        }
        EventLog.writeEvent(EventLogTags.POWER_SLEEP_REQUESTED, numWakeLocksCleared);

        // Skip dozing if requested.
        if ((flags & PowerManager.GO_TO_SLEEP_FLAG_NO_DOZE) != 0) {
            reallyGoToSleepNoUpdateLocked(eventTime, uid);
        }
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
    return true;
}
```

整个超时灭屏的流程分析就到这里了，从以上流程中可以看到，mWakeLockSummary 和 mUserActivitySummary 的作用相当重要。到这里超时灭屏过程已经分析完了，我们来看下整体流程。

![Power 按键灭屏流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pms_gosleep/02.png)

## 参考资料

- [Android电源管理系列之 PowerManagerService](http://www.robinheztto.com/2017/06/14/android-power-pms-1/)
- [PowerManagerService 分析](https://blog.csdn.net/FightFightFight/article/details/79532191)

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！