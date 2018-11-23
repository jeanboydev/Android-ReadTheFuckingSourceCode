# Android - PowerManagerService 亮屏

## 一、Power 按键亮屏

这里直接从 PhoneWindowManager 开始分析，按 Power 键后，会触发 PhoneWindowManager 的 interceptKeyBeforeQueueing() 方法：

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

@Override
public int interceptKeyBeforeQueueing(KeyEvent event, int policyFlags) {
    //...
    // Handle special keys.
    switch (keyCode) {
        //...
        case KeyEvent.KEYCODE_POWER: {
            // Any activity on the power button stops the accessibility shortcut
            cancelPendingAccessibilityShortcutAction();
            result &= ~ACTION_PASS_TO_USER;
            isWakeKey = false; // wake-up will be handled separately
            if (down) {
                interceptPowerKeyDown(event, interactive);
            } else {
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

在这个方法中，对Power键的按下和抬起做了处理，按下时，调用`interceptPowerKeyDown()` 。

### 1.1 interceptPowerKeyDown()

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

private void interceptPowerKeyDown(KeyEvent event, boolean interactive) {
    // Hold a wake lock until the power key is released.
    if (!mPowerKeyWakeLock.isHeld()) {
        //申请一个唤醒锁，使 CPU 保持唤醒
        mPowerKeyWakeLock.acquire();
    }
    //...
    if (!mPowerKeyHandled) {
        if (interactive) {
            //...
        } else {
            //进行亮屏处理
            wakeUpFromPowerKey(event.getDownTime());
            //...
        }
    }
}
```

在这个方法中，首先是申请了一个唤醒锁，然后会对一些特定功能进行处理，如截屏、结束通话，等等，然后如果此时处于非交互状态 `interactive = false`，进行亮屏操作。

### 1.2 mPowerKeyWakeLock.acquire()

`mPowerKeyWakeLock.acquire();` 申请锁的流程已经在上一篇【PowerManagerService - WakeLock 机制】中【3.1】章节分析过了。这里继续看 `wakeUpFromPowerKey()` 方法。

### 1.3 wakeUpFromPowerKey()

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

private void wakeUpFromPowerKey(long eventTime) {
    //第三个参数为亮屏原因，因此如果是 power 键亮屏，则 log 中会出现 android.policy:POWER
    wakeUp(eventTime, mAllowTheaterModeWakeFromPowerKey, "android.policy:POWER");
}

private boolean wakeUp(long wakeTime, boolean wakeInTheaterMode, String reason) {
    final boolean theaterModeEnabled = isTheaterModeEnabled();
    if (!wakeInTheaterMode && theaterModeEnabled) {
        return false;
    }

    if (theaterModeEnabled) {
        Settings.Global.putInt(mContext.getContentResolver(),
                               Settings.Global.THEATER_MODE_ON, 0);
    }

    mPowerManager.wakeUp(wakeTime, reason);
    return true;
}
```

在这个方法中，首先判断是否允许在剧院模式下点亮屏幕，之后通过 PowerManager 在 PowerManagerService 进行屏幕的唤醒，先来看看 PowerManager 的 `wakeup（）` 方法。

### 1.4 PowerManager.wakeup()

```java
//frameworks/base/core/java/android/os/PowerManager.java

public void wakeUp(long time, String reason) {
    try {
        mService.wakeUp(time, reason, mContext.getOpPackageName());
    } catch (RemoteException e) {
        throw e.rethrowFromSystemServer();
    }
}
```

接着会进入到 PowerManagerService 中的 `wakeUp()` 方法。

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@Override // Binder call
public void wakeUp(long eventTime, String reason, String opPackageName) {
    if (eventTime > SystemClock.uptimeMillis()) {
        throw new IllegalArgumentException("event time must not be in the future");
    }
    //权限检查
    mContext.enforceCallingOrSelfPermission(
        android.Manifest.permission.DEVICE_POWER, null);
    //清除 IPC 标志
    final int uid = Binder.getCallingUid();
    final long ident = Binder.clearCallingIdentity();
    try {
        //调用内部方法
        wakeUpInternal(eventTime, reason, uid, opPackageName, uid);
    } finally {
        //重置 IPC 标志
        Binder.restoreCallingIdentity(ident);
    }
}
```

在 PowerManagerService 中暴露给 Binder 客户端的方法中，进行了权限的检查，然后调用 `wakeUpInternal()` 方法。

### 1.5 wakeUpInternal()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void wakeUpInternal(long eventTime, String reason, int uid, String opPackageName,
                            int opUid) {
    synchronized (mLock) {
        if (wakeUpNoUpdateLocked(eventTime, reason, uid, opPackageName, opUid)) {
            updatePowerStateLocked();
        }
    }
}
```

这里又调用了 `wakeUpNoUpdateLocked()` 方法，如果这个方法返回 true，则会执行 `updatePowerStateLocked()` 方法，如果返回 false，则整个过程结束。这个方法在我们分析 wakelock 申请时提到过，如果申请的 wakelock 锁带有唤醒屏幕的标志，也只执行这个方法，因此，这个方法是唤醒屏幕的主要方法之一，来看看这个方法。

### 1.6 wakeUpNoUpdateLocked()


```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean wakeUpNoUpdateLocked(long eventTime, String reason, int reasonUid,
                                     String opPackageName, int opUid) {
    if (eventTime < mLastSleepTime || mWakefulness == WAKEFULNESS_AWAKE
        || !mBootCompleted || !mSystemReady) {
        return false;
    }
    try {
        //根据当前 wakefulness 状态打印 log，这些 log 很有用
        switch (mWakefulness) {
            case WAKEFULNESS_ASLEEP:
                Slog.i(TAG, "Waking up from sleep (uid " + reasonUid +")...");
                break;
            case WAKEFULNESS_DREAMING:
                Slog.i(TAG, "Waking up from dream (uid " + reasonUid +")...");
                break;
            case WAKEFULNESS_DOZING:
                Slog.i(TAG, "Waking up from dozing (uid " + reasonUid +")...");
                break;
        }
        //设置最后一次亮屏时间，即该次的时间
        mLastWakeTime = eventTime;
        //设置 wakefulness 为 WAKEFULNESS_AWAKE，详见【1.6.1】
        setWakefulnessLocked(WAKEFULNESS_AWAKE, 0);

        //Notifier 中通知 BatteryStatsService 统计亮屏，详见【1.6.2】
        mNotifier.onWakeUp(reason, reasonUid, opPackageName, opUid);
        //更新用户活动时间
        userActivityNoUpdateLocked(
            eventTime, PowerManager.USER_ACTIVITY_EVENT_OTHER, 0, reasonUid);
    } finally { }
    return true;
}
```

在这个方法中，Log 中的 reason 需要注意一下：

- Power 键亮屏，则 reason 是 PWM 中传入的 `android.policy:POWER`；
- 来电亮屏为 `android.server.am:TURN_ON`;
- USB 插拔时为 `android.server.power:POWER`

所以不管是哪种亮屏方式，最终都会在这里汇合的。之后通过 `setWakefulnessLocked()`  方法设置 wakefulness，再通过Notifier 进行处理和通知其他系统服务 wakefulness 的改变，最后更新用户活动的时间，重置下次超时灭屏时间。

#### 1.6.1 setWakefulnessLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void setWakefulnessLocked(int wakefulness, int reason) {
    if (mWakefulness != wakefulness) {
        //改变 Wakefulness
        mWakefulness = wakefulness;
        mWakefulnessChanging = true;
        //置位操作
        mDirty |= DIRTY_WAKEFULNESS;
        //处理 wakefulness 改变前的操作
        mNotifier.onWakefulnessChangeStarted(wakefulness, reason);
    }
}
```

首先，改变当前 mWakefulness 值，将 mWakefulnessChanging 标记为 true，将 mWakefulness 值标志为 DIRTY_WAKEFULNESS，然后通过 Notifier 进行改变 wakefulness 之前的一些处理，Notifier 负责 PMS 和其他系统服务的交互。而 Notifier 中的 `onWakefulnessChangeStarted()` 方法，就是亮屏的主要方法之一，如：发送亮屏或者灭屏的广播等。

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

public void onWakefulnessChangeStarted(final int wakefulness, int reason) {
    final boolean interactive = PowerManagerInternal.isInteractive(wakefulness);
    
    // Tell the activity manager about changes in wakefulness, not just interactivity.
    // It needs more granularity than other components.
    mHandler.post(new Runnable() {
        @Override
        public void run() {
            mActivityManagerInternal.onWakefulnessChanged(wakefulness);
        }
    });

    // Handle any early interactive state changes.
    // Finish pending incomplete ones from a previous cycle.
    //亮屏操作 mInteractive=false != interactive=true
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
        handleEarlyInteractiveChange();//详见下面分析
    }
}
```

##### 1.6.1.1 handleEarlyInteractiveChange()

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

 private void handleEarlyInteractiveChange() {
     synchronized (mLock) {
         if (mInteractive) {
             // Waking up...
             mHandler.post(new Runnable() {
                 @Override
                 public void run() {
                     // Note a SCREEN tron event is logged in PowerManagerService.
                     //回调 PhoneWindowManager
                     mPolicy.startedWakingUp();
                 }
             });

             // Send interactive broadcast.
             mPendingInteractiveState = INTERACTIVE_STATE_AWAKE;
             mPendingWakeUpBroadcast = true;
             //发送亮/灭屏广播
             updatePendingBroadcastLocked();
         } else {
             // Going to sleep...
             // Tell the policy that we started going to sleep.
             final int why = translateOffReason(mInteractiveChangeReason);
             mHandler.post(new Runnable() {
                 @Override
                 public void run() {
                     mPolicy.startedGoingToSleep(why);
                 }
             });
         }
     }
 }
```

首先，会回调 PhoneWindowManager 中的 `startedWakingUp()`，然后发送亮屏广播。

##### 1.6.1.2 startedWakingUp()

```java
//frameworks/base/services/core/java/com/android/server/policy/PhoneWindowManager.java

@Override
public void startedWakingUp() {
    EventLog.writeEvent(70000, 1);
    if (DEBUG_WAKEUP) Slog.i(TAG, "Started waking up...");

    // Since goToSleep performs these functions synchronously, we must
    // do the same here.  We cannot post this work to a handler because
    // that might cause it to become reordered with respect to what
    // may happen in a future call to goToSleep.
    synchronized (mLock) {
        mAwake = true;

        updateWakeGestureListenerLp();
        updateOrientationListenerLp();
        updateLockScreenTimeout();
    }

    if (mKeyguardDelegate != null) {
        mKeyguardDelegate.onStartedWakingUp();
    }
}
```

#### 1.6.2 mNotifier.onWakeUp()

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

public void onWakeUp(String reason, int reasonUid, String opPackageName, int opUid) {
    try {
        //开始统计亮屏时间
        mBatteryStats.noteWakeUp(reason, reasonUid);
        if (opPackageName != null) {
            mAppOps.noteOperation(AppOpsManager.OP_TURN_SCREEN_ON, opUid, opPackageName);
        }
    } catch (RemoteException ex) { }
}
```

接下来，执行 `userActivityNoUpdateLocked()` 方法，这个方法任务只有一个——负责更新系统和用户最后交互时间，计算的时间在 `updateUserActivitySummary()` 方法中会用于判断何时灭屏。

#### 1.6.3 userActivityNoUpdateLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean userActivityNoUpdateLocked(long eventTime, int event, int flags, int uid) {
    if (eventTime < mLastSleepTime || eventTime < mLastWakeTime
        || !mBootCompleted || !mSystemReady) {
        return false;
    }

    Trace.traceBegin(Trace.TRACE_TAG_POWER, "userActivity");
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

        if (mWakefulness == WAKEFULNESS_ASLEEP
            || mWakefulness == WAKEFULNESS_DOZING
            || (flags & PowerManager.USER_ACTIVITY_FLAG_INDIRECT) != 0) {
            return false;
        }
        
        /**
         * USER_ACTIVITY_FLAG_NO_CHANGE_LIGHTS 标识
         * 只有带有 PowerManager.ON_AFTER_RELEASE 类型的锁在释放时才会有该 flag，
         * 在亮屏流程中没有该标识，因此不满足该条件，
         * 如果满足条件，改变 mLastUserActivityTimeNoChangeLights 的值，否则进入 else 语句，
         * 改变 mLastUserActivityTime 的值
         */
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

在这个方法中来看下 PowerManager.USER_ACTIVITY_FLAG_NO_CHANGE_LIGHT 这个值，这个值和释放 WakeLock 有关系，在分析 WakeLock 释放流程时分析到，如果带有 PowerManager.ON_AFTER_RELEASE 标记，则在释放该 WakeLock 时会先亮一小会之后才会灭屏，这里正是为何会亮一小会才会灭屏的关键。

### 1.7 updatePowerStateLocked()

这些方法执行完后,执行 `updatePowerStateLocked()` 方法更新所有信息，这个方法作为 PowerManagerService 的核心方法，在【PowerManagerService 启动流程】中【2.4】章节已经分析过了。



```java

```



## 二、USB 插入亮屏


## 参考资料

- [资料标题](http://www.baidu.com)


