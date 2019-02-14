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

在这个方法中，对Power键的按下和抬起做了处理，按下时，调用 `interceptPowerKeyDown()` 。

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
	//详见下面分析
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
        //调用内部方法，详见下面分析
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
            updatePowerStateLocked();//详见下面分析
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
        //处理 wakefulness 改变前的操作，详见下面分析
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

到这里 Power 按键亮屏过程已经分析完了，我们来看下整体流程。

![Power 按键亮屏流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pms_wakeup/01.png)

## 二、USB 插入亮屏

当插拔 USB 时，会发送 `BATTERY_CHANGED` 广播，PowerManagerService 中对该广播进行监听，如果收到广播后，配置了插播 USB 时亮屏，则会进行亮屏操作。

在 BatteryService 中，如果电池状态发生改变，则会发送一个 `ACTION_BATTERY_CHANGED` 广播：

```java
//frameworks/base/services/core/java/com/android/server/BatteryService.java

private void sendIntentLocked() {
    //  Pack up the values and broadcast them to everyone
    final Intent intent = new Intent(Intent.ACTION_BATTERY_CHANGED);
    intent.addFlags(Intent.FLAG_RECEIVER_REGISTERED_ONLY
                    | Intent.FLAG_RECEIVER_REPLACE_PENDING);
    //...
    mHandler.post(new Runnable() {
        @Override
        public void run() {
            ActivityManager.broadcastStickyIntent(intent, UserHandle.USER_ALL);
        }
    });
}
```

在 PowerManagerService 中，注册了广播接受者，会接收该广播：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public void systemReady(IAppOpsService appOps) {
    //...
    // Register for broadcasts from other components of the system.
    IntentFilter filter = new IntentFilter();
    filter.addAction(Intent.ACTION_BATTERY_CHANGED);
    filter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);
    mContext.registerReceiver(new BatteryReceiver(), filter, null, mHandler);
    //...
}
```

因此当 BatteryService 中检测到底层电池状态发生变化后，会发送该广播，PowerManagerService 中的 BatteryReceiver 用于接受该广播并进行处理，如下：

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private final class BatteryReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        synchronized (mLock) {
            handleBatteryStateChangedLocked();
        }
    }
}
```

### 1.1 handleBatteryStateChangedLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void handleBatteryStateChangedLocked() {
    mDirty |= DIRTY_BATTERY_STATE;
    updatePowerStateLocked();
}
```

在这里对 mDirty 进行了置位，之后开始调用 updatePowerStateLocked() 方法。

### 1.2 updatePowerStateLocked()

在之前已经分析过该方法了，具体分析详见【PowerManagerService - 启动流程】中【2.4】章节，其中调用的 `updateIsPoweredLocked()` 方法是插播 USB 亮屏的入口方法，所有和电池相关的都是在这里处理。

到这里 USB 插入亮屏过程已经分析完了，我们来看下整体流程。

![USB 插入亮屏流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pms_wakeup/02.png)

## 三、PowerManager

PowerManager 可以说是 PowerManagerService 向 Application 层提供信息的一个接口。PowerManager 用来控制设备电源状态。在上面分析了 PowerManagerService 是一个系统服务，由 SystemServer 启动并运行，并没有提供上层调用的接口。因此，PowerManager 作为 PowerManagerService 的一个代理类，向上层应用层提供开放接口，供 Application 层调用，实现对电源的管理，其实现原理和上文谈到的 Binider 注册有关。 PowerManager 作为系统级别服务，在获取其实例时，通过以下方式进行获取：

```java
PowerManager pm = (PowerManager) mContext.getSystemService(Context.POWER_SERVICE);
```

通过 `Context.POWER_SERVICE` 获取了 PowerManager 实例，而这个字段在 PowerManagerService 进行 Binder 注册的时候使用了。因此，实际上 PowerManager 对象中包含了一个 PowerManagerService.BindService 对象，当应用层调用 PowerManager 开放接口后，PowerManager 再通过 PowerManagerService.BindService 向下调用到了 PowerManagerService 中。这点可以在 PowerManager 的构造方法中看出：

```java
public PowerManager(Context context, IPowerManager service, Handler handler) {
    mContext = context;
    mService = service;
    mHandler = handler;
}
```

在 PowerManager 中，提供了许多 public 方法，当应用层调用这些方法时，PowerManager 将向下调用 PowerManagerService。

## 四、Notifier

Notifier 类好比 PMS 和其他系统服务交互的”中介“，Notifier 和 PMS 在结构上可以说是组合关系，PMS 中需要和其他组件交互的大部分都由 Notifier 处理，如亮灭屏通知其他服务等，亮灭屏广播也是在该类中发出。这里介绍其中的部分方法，有些可能已经在上面内容的分析中涉及到了。

### 4.1 onWakefulnessChangeStarted()

该方法用于亮屏或者灭屏时逻辑的处理，和 onWakefulnessChangeFinished() 方法对应，分别负责操作开始和结束的逻辑处理，当 wakefulness 改变时进行回调，因此当亮屏、灭屏、进入 Doze 模式时都会调用这个方法，看看这个方法：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

public void onWakefulnessChangeStarted(final int wakefulness, int reason) {
    //是否可以和用户进行交互
    //既 wakefulness == WAKEFULNESS_AWAKE || WAKEFULNESS_DREAM
    final boolean interactive = PowerManagerInternal.isInteractive(wakefulness);
    mHandler.post(new Runnable() {
        @Override
        public void run() {
            mActivityManagerInternal.onWakefulnessChanged(wakefulness);
        }
    });

    //如果为 false，表示交互状态发生改变，即从亮屏到灭屏或者从灭屏到亮屏
    if (mInteractive != interactive) {
        //交互状态发生了改变
        if (mInteractiveChanging) {
            handleLateInteractiveChange();//处理交互改变后的任务
        }

        //与 InputManagerService 交互
        mInputManagerInternal.setInteractive(interactive);
        mInputMethodManagerInternal.setInteractive(interactive);

        //和 BatteryStatsService 交互
        try {
            mBatteryStats.noteInteractive(interactive);
        } catch (RemoteException ex) { }

        //处理交互完成前的操作
        mInteractive = interactive;
        mInteractiveChangeReason = reason;
        mInteractiveChanging = true;
        handleEarlyInteractiveChange();
    }
}
```

首先判断系统是否可以进行交互，如果处于 Dream 或者 Awake 状态，表示可以进行交互，interactive 为 true；在这个方法中有两个关键方法 `handleLateInteractiveChange()` 和 `handleEarlyInteractiveChange()` 分别表示处理交互状态改变后的操作和改变前的操作。如果是亮屏场景，则在执行到该方法时，在 setWakeFulnessLocked() 方法中将 wakefulness 设置为了 WAKEFULNESS_AWAKE，所以 interactive 为 true，mInteractive 是 false。因此，会先执行 handleEarlyInteractiveChange()。

#### 4.1.1 handleEarlyInteractiveChange()

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private void handleEarlyInteractiveChange() {
    synchronized (mLock) {
        if (mInteractive) {//是亮屏或者灭屏
            //亮屏...
            mHandler.post(new Runnable() {
                @Override
                public void run() {
                    // Note a SCREEN tron event is logged in PowerManagerService.
                    mPolicy.startedWakingUp();
                }
            });

            // 发送完成后的广播
            mPendingInteractiveState = INTERACTIVE_STATE_AWAKE;
            mPendingWakeUpBroadcast = true;
            updatePendingBroadcastLocked();
        } else {
            //灭屏...
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

### 4.2 onWakefulnessChangeFinished()

该方法负责 wakefulness 状态改变完成后的工作与【4.1】中方法相对应。这个方法较简单，当 PMS 中调用它后，它会调用 handleLaterInteractiveChanged() 方法,如下：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

public void onWakefulnessChangeFinished() {
    if (mInteractiveChanging) {
        mInteractiveChanging = false;
        handleLateInteractiveChange();
    }
}
```

#### 4.2.1 handleLateInteractiveChange()

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private void handleLateInteractiveChange() {
    synchronized (mLock) {
        if (mInteractive) {//是亮屏或者灭屏
            //亮屏...
            mHandler.post(new Runnable() {
                @Override
                public void run() {
                    mPolicy.finishedWakingUp();
                }
            });
        } else {
            //灭屏...
            if (mUserActivityPending) {
                mUserActivityPending = false;
                mHandler.removeMessages(MSG_USER_ACTIVITY);
            }

            // Tell the policy we finished going to sleep.
            final int why = translateOffReason(mInteractiveChangeReason);
            mHandler.post(new Runnable() {
                @Override
                public void run() {
                    LogMaker log = new LogMaker(MetricsEvent.SCREEN);
                    log.setType(MetricsEvent.TYPE_CLOSE);
                    log.setSubtype(why);
                    MetricsLogger.action(log);
                    EventLogTags.writePowerScreenState(0, why, 0, 0, 0);
                    mPolicy.finishedGoingToSleep(why);
                }
            });

            // 发送完成后的广播
            mPendingInteractiveState = INTERACTIVE_STATE_ASLEEP;
            mPendingGoToSleepBroadcast = true;
            updatePendingBroadcastLocked();
        }
    }
}
```

在这个方法中，如果是亮屏，则调用 PhoneWindowManager 的 finishedWakingUp() 表示亮屏处理成功。如果是灭屏，则调用 PhoneWindowManager 的 `finishedGoingToSleep()`。

### 4.3 updatePendingBroadcaseLocked()

这个方法用于交互状态改变时发送广播，最常见的就是由亮屏-灭屏之间的改变了，都会发送这个广播。亮屏时，在 `handlerEarlyInteractiveChang()` 方法中调用该方法发送广播；灭屏时，在 `handlerLateInteractiveChang()` 中调用方法发送广播。接下来会分两种情况进行分析。

当系统由不可交互变成可交互时，如由灭屏 - 亮屏，首先做了如下处理：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private void updatePendingBroadcastLocked() {
    /**
     * 广播没有进行中 && 要发送的广播状态 != UNKNOW
     * && (发送亮屏广播||发送灭屏广播||发送广播状态！=当前广播交互状态）
     * mBroadcastedInteractiveState 值实际上是上次发送广播交互状态的值
     */
    if (!mBroadcastInProgress
        && mPendingInteractiveState != INTERACTIVE_STATE_UNKNOWN
        && (mPendingWakeUpBroadcast || mPendingGoToSleepBroadcast
            || mPendingInteractiveState != mBroadcastedInteractiveState)) {
        mBroadcastInProgress = true;
        //申请一个 Suspend 锁，以防广播发送未完成系统休眠而失败
        mSuspendBlocker.acquire();
        Message msg = mHandler.obtainMessage(MSG_BROADCAST);
        msg.setAsynchronous(true);
        mHandler.sendMessage(msg);
    }
}
```

在这个方法中，使用到的几个属性值意义如下：

```java
//要广播的交互状态
private int mPendingInteractiveState;
//是否广播亮屏
private boolean mPendingWakeUpBroadcast;
//是否广播灭屏
private boolean mPendingGoToSleepBroadcast;
//当前要广播的交互状态
private int mBroadcastedInteractiveState;
//是否广播正在进行中
private boolean mBroadcastInProgress;
```

在这个方法中，首先申请了一个 suspend 锁，这个锁是通过在 PowerManagerService 中创建 Notifier 对象时创建传入的 name 为PowerManagerService.Broadcast 在广播发送完成后又进行了释放，这样作的目的是避免在发送广播过程中系统休眠而导致广播未发送完成。

#### 4.3.1 sendNextBroadcaset()

之后通过 Handler 中调用 sendNextBroadcaset() 方法发送广播，看看这个方法：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private final class NotifierHandler extends Handler {
    @Override
    public void handleMessage(Message msg) {
        switch (msg.what) {
                //...
            case MSG_BROADCAST:
                sendNextBroadcast();
                break;
                //...
        }
    }
}

private void sendNextBroadcast() {
    final int powerState;
    synchronized (mLock) {
        //当前广播的交互状态 = 0（成员变量默认0）
        if (mBroadcastedInteractiveState == INTERACTIVE_STATE_UNKNOWN) {
            // Broadcasted power state is unknown.  Send wake up.
            mPendingWakeUpBroadcast = false;
            mBroadcastedInteractiveState = INTERACTIVE_STATE_AWAKE;
        } else if (mBroadcastedInteractiveState == INTERACTIVE_STATE_AWAKE) {
            //当前广播的交互状态为亮屏
            //广播亮屏||广播灭屏||最终要广播的交互状态为灭屏
            if (mPendingWakeUpBroadcast || mPendingGoToSleepBroadcast
                || mPendingInteractiveState == INTERACTIVE_STATE_ASLEEP) {
                mPendingGoToSleepBroadcast = false;
                mBroadcastedInteractiveState = INTERACTIVE_STATE_ASLEEP;
            } else {
                finishPendingBroadcastLocked();
                return;
            }
        } else { //当前广播的交互状态为灭屏
            if (mPendingWakeUpBroadcast || mPendingGoToSleepBroadcast
                || mPendingInteractiveState == INTERACTIVE_STATE_AWAKE) {
                mPendingWakeUpBroadcast = false;
                mBroadcastedInteractiveState = INTERACTIVE_STATE_AWAKE;
            } else {
                finishPendingBroadcastLocked();
                return;
            }
        }

        mBroadcastStartTime = SystemClock.uptimeMillis();
        powerState = mBroadcastedInteractiveState;
    }

    EventLog.writeEvent(EventLogTags.POWER_SCREEN_BROADCAST_SEND, 1);

    if (powerState == INTERACTIVE_STATE_AWAKE) {
        sendWakeUpBroadcast();//发送亮屏广播
    } else {
        sendGoToSleepBroadcast();//发送灭屏广播
    }
}
```

#### 4.3.2 sendWakeUpBroadcast()

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private void sendWakeUpBroadcast() {
    if (mActivityManagerInternal.isSystemReady()) {
        //广播发送完成后最后被 mWakeUpBroadcastDone 接受
        mContext.sendOrderedBroadcastAsUser(mScreenOnIntent, 
               UserHandle.ALL, null, mWakeUpBroadcastDone, mHandler,
                0, null, null);
    } else {
        sendNextBroadcast();
    }
}
```

mWakeUpBroadcastDone 会在最后接受触发 onReceive() 方法，继续看看 mWakeUpBroadcastDone 这个广播接受器：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private final BroadcastReceiver mWakeUpBroadcastDone = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {
        EventLog.writeEvent(EventLogTags.POWER_SCREEN_BROADCAST_DONE, 1,
                            SystemClock.uptimeMillis() - mBroadcastStartTime, 1);
        sendNextBroadcast();
    }
};
```

在这里又调用了 sendNextBroadcast() 方法，并根据条件判断，走 `else if`  语句直接调用了 `finishPendingBroadcastLocked()` 方法，该方法如下：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private void finishPendingBroadcastLocked() {
    //表示此时没有正在进行的广播
    mBroadcastInProgress = false;
    //释放 suspend 锁
    mSuspendBlocker.release();
}
```

在这个方法中，将 mBroadcastInProgress 值设置为 false，表示当前没有正在进行中的广播，并释 sendGoToSleepBroadcast 放了避免系统 CPU 休眠的 Suspend 锁，亮屏广播就发送完毕了。

#### 4.3.3 sendGoToSleepBroadcast()

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private void sendGoToSleepBroadcast() {
    if (mActivityManagerInternal.isSystemReady()) {
        //广播发送后最后一个广播接受器 mGoToSleepBroadcastDone
        mContext.sendOrderedBroadcastAsUser(mScreenOffIntent, 
               UserHandle.ALL, null,
                mGoToSleepBroadcastDone, mHandler, 0, null, null);
    } else {
        sendNextBroadcast();
    }
}
```

灭屏广播发出后，mGoToSleepBroadcastDone 会在最后接受到，这里进行收尾处理：

```java
//frameworks/base/services/core/java/com/android/server/power/Notifier.java

private final BroadcastReceiver mGoToSleepBroadcastDone = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {
        sendNextBroadcast();
    }
};
```

这里又调用了 sendNextBroadcast() 方法，走 else 语句，调用了`finishPendingBroadcastLocked()`，在这个方法中重置了 mBroadcastInPorgress 和释放了 Suspend。

## 参考资料

- [Android电源管理系列之 PowerManagerService](http://www.robinheztto.com/2017/06/14/android-power-pms-1/)
- [PowerManagerService 分析](https://blog.csdn.net/FightFightFight/article/details/79532191)


## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！