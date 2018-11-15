# Android - PowerManagerService - WakeLock

## WakeLock


WakeLock 是 Android 系统中一种锁的机制，只要有进程持有这个锁，系统就无法进入休眠状态。应用程序要申请 WakeLock 时，需要在清单文件中配置 `android.Manifest.permission.WAKE_LOCK` 权限。

根据作用时间，WakeLock 可以分为永久锁和超时锁，永久锁表示只要获取了 WakeLock 锁，必须显式的进行释放，否则系统会一直持有该锁；后者表示在到达给定时间后，自动释放 WakeLock 锁，其实现原理为方法内部维护了一个 Handler。

根据释放原则，WakeLock 可以分为计数锁和非计数锁，默认为计数锁，如果一个 WakeLock 对象为计数锁，则一次申请必须对应一次释放；如果为非计数锁，则不管申请多少次，一次就可以释放该 WakeLock。以下代码为 WakeLock 申请释放示例，要申请 WakeLock，必须有 PowerManager 实例，如下：

```Java
 PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
 //获取 WakeLock 对象
 PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "My Tag");
 wl.acquire();
 Wl.acquire(int timeout);//超时锁
 wl.release();//释放锁
```

在整个 WakeLock 机制中，对应不同的范围，有三种表现形式：

- PowerManger.WakeLock：PowerManagerService 和其他应用、服务交互的接口；
- PowerManagerService.WakeLock：PowerManager.WakeLock 在 PMS 中的表现形式；
- SuspendBlocker：PowerManagerService.WakeLock 在向底层节点操作时的表现形式。

下面开始对 WakeLock 的详细分析。

应用中获取 WakeLock 对象，获取的是位于 PowerManager 中的内部类 —— WakeLock 的实例，在 PowerManager 中看看相关方法：

```Java
public WakeLock newWakeLock(int levelAndFlags, String tag) {
    validateWakeLockParameters(levelAndFlags, tag);
    return new WakeLock(levelAndFlags, tag, mContext.getOpPackageName());
}
```

在 PowerManager 的 newWakeLock() 方法中，首先进行了参数的校验，然后调用 WakeLock 构造方法获取实例，构造方法如下：

```Java
WakeLock(int flags, String tag, String packageName) {
    //表示 wakelock 类型或等级
    mFlags = flags;
    //一个 tag，一般为当前类名
    mTag = tag;
    //获取 wakelock 的包名
    mPackageName = packageName;
    //一个 Binder 标记
    mToken = new Binder();
    mTraceName = "WakeLock (" + mTag + ")";
}
```

- WakeLock 等级

WakeLock 共有以下几种等级：

```Java
//如果持有该类型的 wakelock 锁，则按 Power 键灭屏后，
//即使允许屏幕、按键灯灭，也不会释放该锁，CPU 不会进入休眠状态
public static final int PARTIAL_WAKE_LOCK;

//Deprecated，如果持有该类型的 wakelock 锁，
//则使屏幕保持亮/ Dim 的状态，键盘灯允许灭，按 Power 键灭屏后，会立即释放
public static final int SCREEN_DIM_WAKE_LOCK;

//Deprecated，如果持有该类型的 wakelock 锁，
//则使屏幕保持亮的状态，键盘灯允许灭，按 Power 键灭屏后，会立即释放
public static final int SCREEN_BRIGHT_WAKE_LOCK;

//Deprecated，如果持有该类型的 wakelock 锁，
//则使屏幕、键盘灯都保持亮，按 Power 键灭屏后，会立即释放
public static final int FULL_WAKE_LOCK;

//如果持有该锁，则当 PSensor 检测到有物体靠近时关闭屏幕，
//远离时又亮屏，该类型锁不会阻止系统进入睡眠状态，比如
//当到达休眠时间后会进入睡眠状态，但是如果当前屏幕由该 wakelock 关闭，则不会进入睡眠状态。
public static final int PROXIMITY_SCREEN_OFF_WAKE_LOCK;

//如果持有该锁，则会使屏幕处于 DOZE 状态，同时允许 CPU 挂起，
//该锁用于 DreamManager 实现 Doze 模式，如 SystemUI 的 DozeService
public static final int DOZE_WAKE_LOCK;

//如果持有该锁,则会时设备保持唤醒状态，以进行绘制屏幕，
//该锁常用于 WindowManager 中，允许应用在系统处于 Doze 状态下时进行绘制
public static final int DRAW_WAKE_LOCK;
```

除了等级之外，还有几个标记：

```Java
//该值为 0x0000FFFF，用于根据 flag 判断 Wakelock 的级别，如：
//if((wakeLock.mFlags & PowerManager.WAKE_LOCK_LEVEL_MASK) == PowerManager.PARTIAL_WAKE_LOCK){}
public static final int WAKE_LOCK_LEVEL_MASK;

//用于在申请锁时唤醒设备，一般情况下，申请 wakelock 锁时不会唤醒设备，
//它只会导致屏幕保持打开状态，如果带有这个 flag，则会在申请 wakelock 时就点亮屏幕，
//如：常见通知来时屏幕亮，该 flag 不能和 PowerManager.PARTIAL_WAKE_LOCE 一起使用。
public static final int ACQUIRE_CAUSES_WAKEUP;

//在释放锁时，如果 wakelock 带有该标志，则会小亮一会再灭屏，
//该 flag 不能和 PowerManager.PARTIAL_WAKE_LOCE 一起使用。
public static final int ON_AFTER_RELEASE;

//和其他标记不同，该标记是作为 release() 方法的参数，
//且仅仅用于释放 PowerManager.PROXIMITY_SCREEN_OFF_WAKE_LOCK 类型的锁，
//如果带有该参数，则会延迟释放锁，直到传感器不再感到对象接近
public static final int RELEASE_FLAG_WAIT_FOR_NO_PROXIMITY;
```

## 申请 WakeLock

当获取到 WakeLock 实例后，就可以申请 WakeLock 了。前面说过了，根据作用时间，WakeLock 锁可以分为永久锁和超时锁，根据释放原则，WakeLock 可以分为计数锁和非计数锁。申请方式如下：

```Java
PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "My Tag");
wl.acquire();//申请一个永久锁
Wl.acquire(int timeout);//申请一个超时锁
```

- acquire()

```Java
public void acquire() {
    synchronized (mToken) {
        acquireLocked();
    }
}

public void acquire(long timeout) {
    synchronized (mToken) {
        acquireLocked();
        //申请锁之后，内部会维护一个 Handler 去完成自动释放锁
        mHandler.postDelayed(mReleaser, timeout);
    }
}
```

可以看到这两种方式申请方式完全一样，只不过如果是申请一个超时锁，则会通过 Handler 延时发送一个消息，到达时间后去自动释放锁。

到这一步，对于申请 wakelock 的应用或系统服务来说就完成了，具体的申请在 PowerManager 中进行，继续看看：

- acquireLocked()

```Java
private void acquireLocked() {
    //应用每次申请 wakelock，内部计数和外部计数加 1
    mInternalCount++;
    mExternalCount++;
    //如果是非计数锁或者内部计数值为1,即第一次申请该锁，才会真正去申请
    if (!mRefCounted || mInternalCount == 1) {
        mHandler.removeCallbacks(mReleaser);
        Trace.asyncTraceBegin(Trace.TRACE_TAG_POWER, mTraceName, 0);
        try {
            //向 PowerManagerService 申请锁
            mService.acquireWakeLock(mToken, mFlags, mTag, mPackageName, mWorkSource,
                    mHistoryTag);
        } catch (RemoteException e) {
            throw e.rethrowFromSystemServer();
        }
        //表示此时持有该锁
        mHeld = true;
    }
}
```

是否是计数锁可以通过 setReferenceCount() 来设置，默认为计数锁：

```Java
public void setReferenceCounted(boolean value) {
    synchronized (mToken) {
        mRefCounted = value;
    }
}
```

从 acquire() 方法可以看出，对于计数锁来说，只会在第一次申请时向 PowerManagerService 去申请锁，当该 wakelock 实例第二次、第三次去申请时，如果没有进行过释放，则只会对计数引用加 1，不会向 PowerManagerService 去申请。如果是非计数锁，则每次申请，都会调到 PowerManagerService 中去。

- acquireWakeLock()

PowerManagerService 中的 acquireWakeLock() 方法如下：

```Java
@Override // Binder call
public void acquireWakeLock(IBinder lock, int flags, String tag, 
                     String packageName,WorkSource ws, String historyTag) {
    //...
    //检查 wakelock 级别
    PowerManager.validateWakeLockParameters(flags, tag);
    //检查 WAKE_LOCK 权限
    mContext.enforceCallingOrSelfPermission(android.Manifest.permission.WAKE_LO   
                        CK, null);
    //如果是 DOZE_WAKE_LOCK 级别 wakelock，还要检查 DEVICE_POWER 权限
    if ((flags & PowerManager.DOZE_WAKE_LOCK) != 0) {
        mContext.enforceCallingOrSelfPermission(
                android.Manifest.permission.DEVICE_POWER, null);
    } else {
        ws = null
    }
    //...
    //重置当前线程上传入的IPC标志
    final long ident = Binder.clearCallingIdentity();
    try {
        acquireWakeLockInternal(lock, flags, tag, packageName, ws, historyTag,
                  uid, pid);
    } finally {
        Binder.restoreCallingIdentity(ident);
    }
}
```

- acquireWakeLockInternal()

```Java
private void acquireWakeLockInternal(IBinder lock, int flags, String tag, String packageName,
        WorkSource ws, String historyTag, int uid, int pid) {
    synchronized (mLock) {
        //PMS 中的 WakeLock 类
        WakeLock wakeLock;
        //查找是否已存在该 PM.WakeLock 实例
        int index = findWakeLockIndexLocked(lock);
        boolean notifyAcquire;
        //是否存在 wakelock
        if (index >= 0) {
            wakeLock = mWakeLocks.get(index);
            if (!wakeLock.hasSameProperties(flags, tag, ws, uid, pid)) {
            	//更新 wakelock
                notifyWakeLockChangingLocked(wakeLock, flags, tag, packageName,
                        uid, pid, ws, historyTag);
                wakeLock.updateProperties(flags, tag, packageName, 
                                ws, historyTag, uid, pid);
            }
            notifyAcquire = false;
        } else {
              //从SpareArray<UidState> 中查找是否存在该 uid
              UidState state = mUidState.get(uid);
              if (state == null) {
                  state = new UidState(uid);
                  //设置该 Uid 的进程状态
                  state.mProcState = ActivityManager.PROCESS_STATE_NONEXISTENT;
                  mUidState.put(uid, state);
              }
            //将该 uid 申请的 WakeLock 计数加 1
            //创建新的 PMS.WakeLock 实例
            wakeLock = new WakeLock(lock, flags, tag, packageName, ws, 
                              historyTag, uid, pid);
            try {
                lock.linkToDeath(wakeLock, 0);
            } catch (RemoteException ex) {
                throw new IllegalArgumentException("Wake lock is already dead.");
            }
            //添加到 wakelock 集合中
            mWakeLocks.add(wakeLock);
            //用于设置 PowerManger.PARTIAL_WAKE_LOCK 能否可用
            //1.缓存的不活动进程不能持有 wakelock 锁               
            //2.如果处于 idle 模式，则会忽略掉所有未处于白名单中的应用申请的锁
            setWakeLockDisabledStateLocked(wakeLock);
            //表示有新的wakelock申请了
            notifyAcquire = true;
        }
        //判断是否直接点亮屏幕，如果带有点亮屏幕标志值，并且 wakelock 类型为
        //FULL_WAKE_LOCK，SCREEN_BRIGHT_WAKE_LOCK，SCREEN_DIM_WAKE_LOCK，则进行下 
        //步处理
        applyWakeLockFlagsOnAcquireLocked(wakeLock, uid);
        //更新标志位
        mDirty |= DIRTY_WAKE_LOCKS;
        updatePowerStateLocked();//分析详见上一章【PackageManagerService 启动】
        if (notifyAcquire) {
           //当申请了锁后，在该方法中进行长时锁的判断，通知 BatteryStatsService      
           // 进行统计持锁时间等
            notifyWakeLockAcquiredLocked(wakeLock);
        }
    }
}
```

首先通过传入的第一个参数 IBinder 进行查找 WakeLock 是否已经存在，若存在，则不再进行实例化，在原有的 WakeLock 上更新其属性值；若不存在，则创建一个 WakeLock 对象，同时将该 WakeLock 保存到 List 中。此时已经获取到了 WakeLock 对象，这里需要注意的是，此处的 WakeLock 对象和 PowerManager 中获取的不是同一个 WakeLock 哦！

获取到 WakeLock 实例后，还通过 setWakeLockDisabledStateLocked(wakeLock) 进行了判断该 WakeLock 是否可用，主要有两种情况：

- 缓存的不活动进程不能持有WakeLock锁；
- 如果处于idle模式，则会忽略掉所有未处于白名单中的应用申请的锁。

根据情况会设置 WakeLock 实例的 disable 属性值表示该 WakeLock 是否不可用。下一步进行判断是否直接点亮屏幕。

```Java
private void applyWakeLockFlagsOnAcquireLocked(WakeLock wakeLock, int uid) {
    if ((wakeLock.mFlags & PowerManager.ACQUIRE_CAUSES_WAKEUP) != 0
            && isScreenLock(wakeLock)) {
        //...
        wakeUpNoUpdateLocked(SystemClock.uptimeMillis(), wakeLock.mTag, opUid,
                opPackageName, opUid);
    }
}

private boolean wakeUpNoUpdateLocked(long eventTime, String reason, int reasonUid,
        String opPackageName, int opUid) {
    //如果 eventTime < 上次休眠时间、设备当前处于唤醒状态、没有启动完成、没有准备
    //完成，则不需要更新，返回 false
    if (eventTime < mLastSleepTime || mWakefulness == WAKEFULNESS_AWAKE
            || !mBootCompleted || !mSystemReady) {
        return false;
    }
    try {
        //...
        //更新最后一次唤醒时间值
        mLastWakeTime = eventTime;
        //设置wakefulness
        setWakefulnessLocked(WAKEFULNESS_AWAKE, 0);
        //通知BatteryStatsService/AppService屏幕状态发生改变
        mNotifier.onWakeUp(reason, reasonUid, opPackageName, opUid);
        //更新用户活动事件时间值
        userActivityNoUpdateLocked(
                eventTime, PowerManager.USER_ACTIVITY_EVENT_OTHER, 0, reasonUid);
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_POWER);
    }
    return true;
}
```

wakeUpNoUpdateLocked() 方法是唤醒设备的主要方法。在这个方法中，首先更新了 mLastWakeTime 这个值，表示上次唤醒设备的时间，在系统超时休眠时用到这个值进行判断。现在，只需要知道每次亮屏，都走的是这个方法，关于具体是如何唤醒屏幕的，在第 5 节中进行分析。

## 未完成

- notifyWakeLockAcquiredLocked()

如果有新的 WakeLock 实例创建，则 notifyAcquire 值为 true，通过以下这个方法通知 Notifier，Notifier 中则会根据该锁申请的时间开始计时，并以此来判断是否是一个长时间持有的锁。

```Java
private void notifyWakeLockAcquiredLocked(WakeLock wakeLock) {
    if (mSystemReady && !wakeLock.mDisabled) {
        wakeLock.mNotifiedAcquired = true;
        wakeLock.mStartTimeStamp = SystemClock.elapsedRealtime();
        //Called when a wake lock is acquired.
        mNotifier.onWakeLockAcquired(wakeLock.mFlags, 
                        wakeLock.mTag, wakeLock.mPackageName,
                wakeLock.mOwnerUid, wakeLock.mOwnerPid, wakeLock.mWorkSource,
                wakeLock.mHistoryTag);
        //...
        //重新开始检查持锁时间
        restartNofifyLongTimerLocked(wakeLock);
    }
}
```


- updateSuspendBlockerLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateSuspendBlockerLocked() {
    //是否需要保持 CPU 活动状态的 SuspendBlocker 锁，具体表现为持有 Partical WakeLock
    final boolean needWakeLockSuspendBlocker = ((mWakeLockSummary & WAKE_LOCK_CPU) != 0);
    //是否需要保持 CPU 活动状态的 SuspendBlocker 锁，具体表现保持屏幕亮度
    final boolean needDisplaySuspendBlocker = needDisplaySuspendBlockerLocked();
    //是否自动挂起，如果不需要屏幕保持唤醒，则说明可以自动挂起 CPU
    final boolean autoSuspend = !needDisplaySuspendBlocker;
    //是否处于交互模式，屏幕处于 Bright 或者 Dim 状态时为 true
    final boolean interactive = mDisplayPowerRequest.isBrightOrDim();

    //mDecoupleHalAutoSuspendModeFromDisplayConfig:自动挂起模式和显示状态解偶
    if (!autoSuspend && mDecoupleHalAutoSuspendModeFromDisplayConfig) {
        //禁止 CPU 自动挂起模式
        setHalAutoSuspendModeLocked(false);
    }

    //如果存在 PARTIAL_WAKE_LOCK 类型的 WakeLock，申请 mWakeLockSuspendBlocker 锁
    //从上面我们知道有 WAKE_LOCK_CPU 标志的话就获取一个 suspendblocker，这才是真正阻止 CPU 待机的东西
    if (needWakeLockSuspendBlocker && !mHoldingWakeLockSuspendBlocker) {
        mWakeLockSuspendBlocker.acquire();
        mHoldingWakeLockSuspendBlocker = true;
    }
    //只有屏幕亮的时候才需要 display suspendblocker，当屏幕熄灭或者 doze 的时候这里不会获取 suspendblocker
    if (needDisplaySuspendBlocker && !mHoldingDisplaySuspendBlocker) {
        mDisplaySuspendBlocker.acquire();
        mHoldingDisplaySuspendBlocker = true;
    }

    // Inform the power HAL about interactive mode.
    // Although we could set interactive strictly based on the wakefulness
    // as reported by isInteractive(), it is actually more desirable to track
    // the display policy state instead so that the interactive state observed
    // by the HAL more accurately tracks transitions between AWAKE and DOZING.
    // Refer to getDesiredScreenPolicyLocked() for details.
    //这只设备为可交互模式
    if (mDecoupleHalInteractiveModeFromDisplayConfig) {
        // When becoming non-interactive, we want to defer sending this signal
        // until the display is actually ready so that all transitions have
        // completed.  This is probably a good sign that things have gotten
        // too tangled over here...
        if (interactive || mDisplayReady) {
            setHalInteractiveModeLocked(interactive);
        }
    }

    //如果不再持有 PARTIAL_WAKELOCK 类型的 WakeLock 锁，释放 mWakeLockSuspendBlocker 锁
    if (!needWakeLockSuspendBlocker && mHoldingWakeLockSuspendBlocker) {
        mWakeLockSuspendBlocker.release();
        mHoldingWakeLockSuspendBlocker = false;
    }
    //如果不再需要屏幕保持亮屏，释放 mDisplaySuspendBlocker 锁
    if (!needDisplaySuspendBlocker && mHoldingDisplaySuspendBlocker) {
        mDisplaySuspendBlocker.release();
        mHoldingDisplaySuspendBlocker = false;
    }

    //启动自动挂起模式
    if (autoSuspend && mDecoupleHalAutoSuspendModeFromDisplayConfig) {
        setHalAutoSuspendModeLocked(true);
    }
}
```

在 updateSuspendBlockerLocked() 方法中，会根据当前系统是否持有 PARTIAL_WAKELOCK 类型的锁，来决定是否要申请或释放 mWakeLockSuspendBlocker 锁，然后会根据当前系统是否要屏幕亮屏来决定是否要申请或释放 mDisplaySuspendBlocker锁。

在PMS的构造方法中创建了两个 SuspendBlocker 对象：mWakeLockSuspendBlocker 和 mDisplaySuspendBlocker，前者表示获取一个 PARTIAL_WAKELOCK 类型的 WakeLock 使 CPU 保持活动状态，后者表示当屏幕亮屏、用户活动时使 CPU 保持活动状态。因此实际上，上层 PowerManager 申请和释放锁，最终在PMS中都交给了 SuspendBlocker 去申请和释放锁。也可以说 SuspendBlocker 类的两个对象是 WakeLock 锁反映到底层的对象。只要持有二者任意锁，都会使得CPU处于活动状态。

- needDisplaySuspendBlockerLocked()

```Java
private boolean needDisplaySuspendBlockerLocked() {
    //mDisplayReady 表示显示器是否准备完毕
    if (!mDisplayReady) {
        return true;
    }
    //请求 Display 策略状态为 Bright 或 DIM，这个 if 语句用来判断当 PSensor 灭屏时是否需要 Display 锁
    if (mDisplayPowerRequest.isBrightOrDim()) {
        // If we asked for the screen to be on but it is off due to the proximity
        // sensor then we may suspend but only if the configuration allows it.
        // On some hardware it may not be safe to suspend because the proximity
        // sensor may not be correctly configured as a wake-up source.
        //如果没有 PROXIMITY_SCREEN_OFF_WAKE_LOCK 类型的 WakeLock 锁 || PSensor 正在处于远离状态
        //或在 PSensor 灭屏后不允许进入 Suspend 状态，满足之一，则申请 misplaySuspendBlocker 锁
        if (!mDisplayPowerRequest.useProximitySensor || !mProximityPositive
                || !mSuspendWhenScreenOffDueToProximityConfig) {
            return true;
        }
    }
    if (mScreenBrightnessBoostInProgress) {
        return true;
    }
    // Let the system suspend if the screen is off or dozing.
    return false;
}
```

SuspendBlocker 是一个接口，并且只有 acquire() 和 release() 两个方法，PMS.SuspendBlockerImpl 实现了该接口，因此，最终申请流程执行到了 PMS.SuspendBlockerImpl的acquire() 中。

在 PMS.SuspendBlockerImpl.acquire() 中进行申请时，首先将成员变量计数加 1，然后调用到JNI层去进行申请。

```C++
//frameworks\base\services\core\jni\com_android_server_power_PowerManagerService.cpp

@Override
public void acquire() {
    synchronized (this) {
        //引用计数
        mReferenceCount += 1;  
        if (mReferenceCount == 1) {
            nativeAcquireSuspendBlocker(mName);
        }
    }
}
```

这里使用了引用计数法，如果 mReferenceCount > 1，则不会进行锁的申请，而是仅仅将 mReferenceCount + 1，只有当没有申请的锁时，才会其正真执行申请锁操作，之后不管申请几次，都是 mReferenceCount 加 1。

在 JNI 层中可以明确的看到有一个申请锁的 acquire_wake_lock() 方法，代码如下：

```C++
///hardware/libhardware_legacy/power/power.c

static void nativeAcquireSuspendBlocker(JNIEnv *env, jclass /* clazz */, jstring nameStr) {
    ScopedUtfChars name(env, nameStr);
    acquire_wake_lock(PARTIAL_WAKE_LOCK, name.c_str());
}

int acquire_wake_lock(int lock, const char* id) {
    initialize_fds();
    ALOGI("acquire_wake_lock lock=%d id='%s'\n", lock, id);
    if (g_error) return g_error;
    int fd;
    size_t len;
    ssize_t ret;
    if (lock != PARTIAL_WAKE_LOCK) {
        return -EINVAL;
    }
    fd = g_fds[ACQUIRE_PARTIAL_WAKE_LOCK];
    ret = write(fd, id, strlen(id));
    if (ret < 0) {
        return -errno;
    }
    return ret;
}
```

在这里，向 `/sys/power/wake_lock` 文件写入了 id，这个 id 就是我们上层中实例化 SuspendBlocker 时传入的 String 类型的 name，这里在这个节点写入文件以后，就说明获得了 wakelock。到这里，整个 WakeLock 的申请流程就结束了。





## 释放 WakeLock

如果是通过 `acquire(long timeout)` 方法申请的超时锁，则会在到达时间后自动去释放，如果是通过 acquire() 方法申请的永久锁，则必须进行显式的释放，否则由于系统一直持有 wakelock 锁，将导致无法进入休眠状态，从而导致耗电过快等功耗问题。

在前面分析申请锁时已经说了，如果是超时锁，通过 Handler.post(Runnable) 的方式进行释放，该 Runnable 定义如下：

```Java
private final Runnable mReleaser = new Runnable() {
    public void run() {
        release(RELEASE_FLAG_TIMEOUT);
    }
};
```

RELEASE_FLAG_TIMEOUT 是一个用于 release() 方法的 flag，表示释放的为超时锁。如果是永久锁，则必须通过调用 release() 方法进行释放了，该方法如下：

```Java
public void release() {
    release(0);
}
```

因此，不管是哪种锁的释放，其实都是在 release(int) 中进行的，只不过参数不同，该方法如下：

```Java
public void release(int flags) {
    synchronized (mToken) {
        //内部计数 -1
        mInternalCount--;
        //如果释放超时锁，外部计数 -1
        if ((flags & RELEASE_FLAG_TIMEOUT) == 0) {
            mExternalCount--;
        }
        //如果释放非计数锁或内部计数为 0,并且该锁还在持有,则通过 PowerManagerService 去释放
        if (!mRefCounted || mInternalCount == 0) {
            mHandler.removeCallbacks(mReleaser);
            if (mHeld) {
                Trace.asyncTraceEnd(Trace.TRACE_TAG_POWER, mTraceName, 0);
                try {
                    mService.releaseWakeLock(mToken, flags);
                } catch (RemoteException e) {
                    throw e.rethrowFromSystemServer();
                }
                //表示不持有该锁
                mHeld = false;
            }
        }
        //如果时计数锁，并且外部计数小于 0,则抛出异常
        if (mRefCounted && mExternalCount < 0) {
            throw new RuntimeException("WakeLock under-locked " + mTag);
        }
    }
}
```

对于计数锁的释放，每次都会对内部计数值减一，只有当你内部计数值减为 0 时，才会去调用 PowerManagerService 去真正的释放锁；如果释放非计数锁，则每次都会调用 PowerManagerService 进行释放。

```Java
@Override // Binder call
public void releaseWakeLock(IBinder lock, int flags) {
    if (lock == null) {
        throw new IllegalArgumentException("lock must not be null");
    }
    //检查权限
    mContext.enforceCallingOrSelfPermission(android.Manifest.permission.
         WAKE_LOCK, null);
    //重置当前线程的 IPC 标志
    final long ident = Binder.clearCallingIdentity();
    try {
        //去释放锁
        releaseWakeLockInternal(lock, flags);
    } finally {
        //设置新的 IPC 标志
        Binder.restoreCallingIdentity(ident);
    }
}
```

在这个方法中，进行了权限检查后，就交给下一个方法去处理了，具体代码如下：

```Java
private void releaseWakeLockInternal(IBinder lock, int flags) {
    synchronized (mLock) {
        //查找 WakeLock 是否存在
        int index = findWakeLockIndexLocked(lock);
        if (index < 0) {
            return;
        }
        WakeLock wakeLock = mWakeLocks.get(index);
            //该 flag 用来推迟释放 PowerManager.PROXIMITY_SCREEN_OFF_WAKE_LOCK 类型的锁，
            //它会在传感器感觉不在靠近的时候才释放该锁
            if ((flags & PowerManager.RELEASE_FLAG_WAIT_FOR_NO_PROXIMITY) != 0) {
                //表示在点亮屏幕前需要等待 PSensor 返回负值
                mRequestWaitForNegativeProximity = true;
            }
        if ((flags & PowerManager.RELEASE_FLAG_WAIT_FOR_NO_PROXIMITY) != 0) {
            mRequestWaitForNegativeProximity = true;
        }
        //取消 Binder 的死亡代理
        wakeLock.mLock.unlinkToDeath(wakeLock, 0);
        //释放锁
        removeWakeLockLocked(wakeLock, index);
    }
}
```

在 releaseWakeLockInternal() 中处理时，首先查找 WakeLock 是否存在，若不存在，直接返回；然后检查是否带有影响释放行为的标志值，上面已经提到过，目前只有一个值，之后取消了 Binder 的死亡代理，最后调用了 removeWakeLockLocked() 方法：

```Java
private void removeWakeLockLocked(WakeLock wakeLock, int index) {
    //从 List中 移除
    mWakeLocks.remove(index);
    //得到该 wakelock 中的 UidState 属性
    UidState state = wakeLock.mUidState;
    state.mNumWakeLocks--;
    if (state.mNumWakeLocks <= 0 &&
            state.mProcState == ActivityManager.PROCESS_STATE_NONEXISTENT) {
        //从 SpareArray<UidState> 中移除该 wakelock 的 UidState
        //注意,下面的 mUidState 是 SpareArray<UidState>，而上面的 mUidState 是 wakeLock.mUidState
        mUidState.remove(state.mUid);
    }
    //使用 Notifier 通知其他应用
    notifyWakeLockReleasedLocked(wakeLock);
    //对带有 ON_AFTER_RELEASE 标志的 wakelock 进行处理
    applyWakeLockFlagsOnReleaseLocked(wakeLock);
    mDirty |= DIRTY_WAKE_LOCKS;
    //更新电源状态信息
    updatePowerStateLocked();
}
```

在 removeWakeLockLocked() 中，对带有 ON_AFTER_RELEASE 标志的 wakelock 进行处理，前面分析过了，该标志和用户体验相关，当有该标志时，释放锁后会亮一段时间后灭屏，这里来看看 applyWakeLockFlagsOnReleaseLocked(wakeLock) 方法：

- applyWakeLockFlagsOnReleaseLocked()

```Java
/**
 *如果当前释放的 wakelock 带有 PowerManager.ON_AFTER_RELEASE 标志，则会屏幕在灭屏时小亮一会儿才会熄灭
 */
private void applyWakeLockFlagsOnReleaseLocked(WakeLock wakeLock) {
    if ((wakeLock.mFlags & PowerManager.ON_AFTER_RELEASE) != 0
            && isScreenLock(wakeLock)) {
        //更新用户活动时间，并带有 PowerManager.USER_ACTIVITY_FLAG_NO_CHANGE_LIGHTS 标志，用于延缓灭屏时间
        userActivityNoUpdateLocked(SystemClock.uptimeMillis(),
                PowerManager.USER_ACTIVITY_EVENT_OTHER,
                PowerManager.USER_ACTIVITY_FLAG_NO_CHANGE_LIGHTS,
                wakeLock.mOwnerUid);
    }
}
```

最后，又将调用updatePowerStateLocked()，其中和 WakeLock 申请和释放相关的都 updateSuspendBlockerLocked() 中，释放相关代码如下：


```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateSuspendBlockerLocked() {
    //...
    //如果不再持有 PARTIAL_WAKELOCK 类型的 WakeLock 锁，释放 mWakeLockSuspendBlocker 锁
    if (!needWakeLockSuspendBlocker && mHoldingWakeLockSuspendBlocker) {
        mWakeLockSuspendBlocker.release();
        mHoldingWakeLockSuspendBlocker = false;
    }
    //如果不再需要屏幕保持亮屏，释放 mDisplaySuspendBlocker 锁
    if (!needDisplaySuspendBlocker && mHoldingDisplaySuspendBlocker) {
        mDisplaySuspendBlocker.release();
        mHoldingDisplaySuspendBlocker = false;
    }
    //...
}
```

如果满足条件，则释放 SuspendBlocker 锁。申请 SuspendBlocker 流程已经分析过了，接下来我们分析释放 SuspendBlocker 流程。在 SuspendBlocker 中释放锁如下：

```Java
@Override
public void release() {
    synchronized (this) {
    	//计数-1
        mReferenceCount -= 1;
        if (mReferenceCount == 0) {
        	//调用 JNI 层进行释放
            nativeReleaseSuspendBlocker(mName);
        } else if (mReferenceCount < 0) {
            mReferenceCount = 0;
        }
    }
}
```

在释放锁时，如果有多个锁，实际上是对锁计数的属性减1，直到剩余一个时才会调用 JNI 层执行释放操作。具体代码如下：

```C++
//frameworks\base\services\core\jni\com_android_server_power_PowerManagerService.cpp

static void nativeReleaseSuspendBlocker(JNIEnv *env, jclass /* clazz */, jstring nameStr) {
    ScopedUtfChars name(env, nameStr);
    release_wake_lock(name.c_str());
}
```

在JNI层方法中，调用了HAL层的方法，通过文件描述符向 `/sys/power/wake_unlock` 中写值完成释放：

```C++
int release_wake_lock(const char* id) {
    initialize_fds();
    //    ALOGI("release_wake_lock id='%s'\n", id);
    if (g_error) return g_error;
    ssize_t len = write(g_fds[RELEASE_WAKE_LOCK], id, strlen(id));
    if (len < 0) {
        return -errno;
    }
    return len;
}
```

到这里为止，WakeLock 的释放流程也就分析完毕了。

## PowerManagerService.Broadcasts 锁

这个类型的 SuspendBlocker 并没有在 PMS 中进行实例化，它以构造方法的形式传入了 Notifier 中，Notifier 类相当于是 PMS 的”中介“，PMS 中和其他服务的部分交互通过 Notifier 进行，还有比如亮屏广播、灭屏广播等，都是由 PMS 交给 Notifier 来发送，这点在下篇文章中进行分析。因此，如果 CPU 在广播发送过程中进入休眠，则广播无法发送完成，因此，需要一个锁来保证 Notifier 中广播的成功发送，这就是 PowerManagerService.Broadcasts 锁的作用，当广播发送完毕后，该锁立即就释放了。

## 参考资料

- [资料标题](http://www.baidu.com)


