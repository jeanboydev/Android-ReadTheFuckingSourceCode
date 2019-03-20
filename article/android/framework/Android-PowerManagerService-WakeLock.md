# Android - PowerManagerService WakeLock

## 一、WakeLock 介绍


WakeLock 是 Android 系统中一种锁的机制，只要有进程持有这个锁，系统就无法进入休眠状态。应用程序要申请 WakeLock 时，需要在清单文件中配置 `android.Manifest.permission.WAKE_LOCK` 权限。

根据作用时间，WakeLock 可以分为永久锁和超时锁，永久锁表示只要获取了 WakeLock 锁，必须显式的进行释放，否则系统会一直持有该锁；后者表示在到达给定时间后，自动释放 WakeLock 锁，其实现原理为方法内部维护了一个 Handler。

根据释放原则，WakeLock 可以分为计数锁和非计数锁，默认为计数锁，如果一个 WakeLock 对象为计数锁，则一次申请必须对应一次释放；如果为非计数锁，则不管申请多少次，一次就可以释放该 WakeLock。以下代码为 WakeLock 申请释放示例，要申请 WakeLock，必须有 PowerManager 实例，如下：

```Java
PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
//获取 WakeLock 对象
PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "My Tag");
wl.acquire();//申请锁
Wl.acquire(int timeout);//申请超时锁
wl.release();//释放锁
```

在整个 WakeLock 机制中，对应不同的范围，有三种表现形式：

- PowerManger.WakeLock：PowerManagerService 和其他应用、服务交互的接口；
- PowerManagerService.WakeLock：PowerManager.WakeLock 在 PMS 中的表现形式；
- SuspendBlocker：PowerManagerService.WakeLock 在向底层节点操作时的表现形式。

下面开始对 WakeLock 的详细分析。

## 二、WakeLock 的等级

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

## 三、申请 WakeLock

当获取到 WakeLock 实例后，就可以申请 WakeLock 了。前面说过了，根据作用时间，WakeLock 锁可以分为永久锁和超时锁，根据释放原则，WakeLock 可以分为计数锁和非计数锁。申请方式如下：

```Java
PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
//详见
PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "My Tag");
wl.acquire();//申请一个永久锁
Wl.acquire(int timeout);//申请一个超时锁
```

### 3.1 newWakeLock()

应用中获取 WakeLock 对象，获取的是位于 PowerManager 中的内部类 —— WakeLock 的实例，在 PowerManager 中看看相关方法：

```Java
//frameworks/base/core/java/android/os/PowerManager.java

public WakeLock newWakeLock(int levelAndFlags, String tag) {
    validateWakeLockParameters(levelAndFlags, tag);
    return new WakeLock(levelAndFlags, tag, mContext.getOpPackageName());
}
```

在 PowerManager 的 newWakeLock() 方法中，首先进行了参数的校验，然后调用 WakeLock 构造方法获取实例，构造方法如下：

```Java
//frameworks/base/core/java/android/os/PowerManager.java

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

### 3.2 acquire()

```Java
//frameworks/base/core/java/android/os/PowerManager.java

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

### 3.3 acquireLocked()

```Java
//frameworks/base/core/java/android/os/PowerManager.java

private void acquireLocked() {
    //应用每次申请 wakelock，内部计数和外部计数加 1
    mInternalCount++;
    mExternalCount++;
    //如果是非计数锁或者内部计数值为 1，即第一次申请该锁，才会真正去申请
    if (!mRefCounted || mInternalCount == 1) {
        mHandler.removeCallbacks(mReleaser);
        Trace.asyncTraceBegin(Trace.TRACE_TAG_POWER, mTraceName, 0);
        try {
            //向 PowerManagerService 申请锁，详见【3.4】
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
//frameworks/base/core/java/android/os/PowerManager.java

public void setReferenceCounted(boolean value) {
    synchronized (mToken) {
        mRefCounted = value;
    }
}
```

从 acquire() 方法可以看出，对于计数锁来说，只会在第一次申请时向 PowerManagerService 去申请锁，当该 wakelock 实例第二次、第三次去申请时，如果没有进行过释放，则只会对计数引用加 1，不会向 PowerManagerService 去申请。如果是非计数锁，则每次申请，都会调到 PowerManagerService 中去。

### 3.4 acquireWakeLock()

PowerManagerService 中的 acquireWakeLock() 方法如下：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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
        //详见【3.5】
        acquireWakeLockInternal(lock, flags, tag, packageName, ws, historyTag,
                  uid, pid);
    } finally {
        Binder.restoreCallingIdentity(ident);
    }
}
```

### 3.5 acquireWakeLockInternal()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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
              //从 SpareArray<UidState> 中查找是否存在该 uid
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
        applyWakeLockFlagsOnAcquireLocked(wakeLock, uid);//更新电源状态，详见【3.6】
        //更新标志位
        mDirty |= DIRTY_WAKE_LOCKS;
        updatePowerStateLocked();//更新电源状态，详见【3.7】
        if (notifyAcquire) {
           //当申请了锁后，在该方法中进行长时锁的判断，通知 BatteryStatsService      
           // 进行统计持锁时间等，详见【3.8】
            notifyWakeLockAcquiredLocked(wakeLock);
        }
    }
}
```

首先通过传入的第一个参数 IBinder 进行查找 WakeLock 是否已经存在，若存在，则不再进行实例化，在原有的 WakeLock 上更新其属性值；若不存在，则创建一个 WakeLock 对象，同时将该 WakeLock 保存到 List 中。此时已经获取到了 WakeLock 对象，这里需要注意的是，此处的 WakeLock 对象和 PowerManager 中获取的不是同一个 WakeLock 哦！

获取到 WakeLock 实例后，还通过 setWakeLockDisabledStateLocked(wakeLock) 进行了判断该 WakeLock 是否可用，主要有两种情况：

- 缓存的不活动进程不能持有 WakeLock 锁；
- 如果处于 idle 模式，则会忽略掉所有未处于白名单中的应用申请的锁。

根据情况会设置 WakeLock 实例的 disable 属性值表示该 WakeLock 是否不可用。下一步进行判断是否直接点亮屏幕。

### 3.6 applyWakeLockFlagsOnAcquireLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void applyWakeLockFlagsOnAcquireLocked(WakeLock wakeLock, int uid) {
    if ((wakeLock.mFlags & PowerManager.ACQUIRE_CAUSES_WAKEUP) != 0
            && isScreenLock(wakeLock)) {
        //...
        //详见上一章【PackageManagerService 启动 - 2.4.1.1.1】
        wakeUpNoUpdateLocked(SystemClock.uptimeMillis(), wakeLock.mTag, opUid,
                opPackageName, opUid);
    }
}
```

wakeUpNoUpdateLocked() 方法是唤醒设备的主要方法。在这个方法中，首先更新了 mLastWakeTime 这个值，表示上次唤醒设备的时间，在系统超时休眠时用到这个值进行判断。现在，只需要知道每次亮屏，都走的是这个方法，详细分析请看上一章中的内容。

### 3.7 updatePowerStateLocked()

该流程分析详见上一章【PackageManagerService 启动 - updatePowerStateLocked() 分析】

### 3.8 notifyWakeLockAcquiredLocked()

如果有新的 WakeLock 实例创建，则 notifyAcquire 值为 true，通过以下这个方法通知 Notifier，Notifier 中则会根据该锁申请的时间开始计时，并以此来判断是否是一个长时间持有的锁。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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

### 3.9 restartNofifyLongTimerLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void restartNofifyLongTimerLocked(WakeLock wakeLock) {
    wakeLock.mAcquireTime = SystemClock.uptimeMillis();
    if ((wakeLock.mFlags & PowerManager.WAKE_LOCK_LEVEL_MASK)
        == PowerManager.PARTIAL_WAKE_LOCK && mNotifyLongScheduled == 0) {
        enqueueNotifyLongMsgLocked(wakeLock.mAcquireTime + MIN_LONG_WAKE_CHECK_INTERVAL);
    }
}
```

### 3.10 enqueueNotifyLongMsgLocked()

```java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void enqueueNotifyLongMsgLocked(long time) {
     mNotifyLongScheduled = time;
     Message msg = mHandler.obtainMessage(MSG_CHECK_FOR_LONG_WAKELOCKS);
     msg.setAsynchronous(true);
     mHandler.sendMessageAtTime(msg, time);
 }
```

到这里 WakeLock 的申请已经分析完了，我们来看下整体流程。

![WakeLock 申请流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pms_wakelock/01.png)

## 四、释放 WakeLock

如果是通过 `acquire(long timeout)` 方法申请的超时锁，则会在到达时间后自动去释放，如果是通过 acquire() 方法申请的永久锁，则必须进行显式的释放，否则由于系统一直持有 wakelock 锁，将导致无法进入休眠状态，从而导致耗电过快等功耗问题。

在前面分析申请锁时已经说了，如果是超时锁，通过 Handler.post(Runnable) 的方式进行释放，该 Runnable 定义如下：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private final Runnable mReleaser = new Runnable() {
    public void run() {
        release();
    }
};
```

### 4.1 release()

RELEASE_FLAG_TIMEOUT 是一个用于 release() 方法的 flag，表示释放的为超时锁。如果是永久锁，则必须通过调用 release() 方法进行释放了，该方法如下：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public void release() {
    release(0);
}
```

因此，不管是哪种锁的释放，其实都是在 release(int) 中进行的，只不过参数不同，该方法如下：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public void release(int flags) {
    synchronized (mToken) {
        //内部计数 -1
        mInternalCount--;
        //如果释放超时锁，外部计数 -1
        if ((flags & RELEASE_FLAG_TIMEOUT) == 0) {
            mExternalCount--;
        }
        //如果释放非计数锁或内部计数为 0，并且该锁还在持有，则通过 PowerManagerService 去释放
        if (!mRefCounted || mInternalCount == 0) {
            mHandler.removeCallbacks(mReleaser);
            if (mHeld) {
                Trace.asyncTraceEnd(Trace.TRACE_TAG_POWER, mTraceName, 0);
                try {
                    mService.releaseWakeLock(mToken, flags);//详见下面分析
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

### 4.2 releaseWakeLock()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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
        //释放锁，详见下面分析
        removeWakeLockLocked(wakeLock, index);
    }
}
```

在 releaseWakeLockInternal() 中处理时，首先查找 WakeLock 是否存在，若不存在，直接返回；然后检查是否带有影响释放行为的标志值，上面已经提到过，目前只有一个值，之后取消了 Binder 的死亡代理，最后调用了 removeWakeLockLocked() 方法。

### 4.3 removeWakeLockLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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
    //更新电源状态信息，详见
    updatePowerStateLocked();
}
```

在 removeWakeLockLocked() 中，对带有 ON_AFTER_RELEASE 标志的 wakelock 进行处理，前面分析过了，该标志和用户体验相关，当有该标志时，释放锁后会亮一段时间后灭屏，这里来看看 applyWakeLockFlagsOnReleaseLocked(wakeLock) 方法：

### 4.4 applyWakeLockFlagsOnReleaseLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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

最后，又将调用 updatePowerStateLocked()。

### 4.5 updatePowerStateLocked()

该流程分析详见上一章【PackageManagerService 启动 - updatePowerStateLocked() 分析】，updatePowerStateLocked() 中的第5阶段会调用 updateSuspendBlockerLocked()，其中和 WakeLock 申请和释放相关的都 updateSuspendBlockerLocked() 中。

### 4.6 updateSuspendBlockerLocked()


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
//frameworks\base\services\core\jni\com_android_server_power_PowerManagerService.cpp

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

在释放锁时，如果有多个锁，实际上是对锁计数的属性减1，直到剩余一个时才会调用 JNI 层执行释放操作。

### 4.7 nativeReleaseSuspendBlocker()

```C++
//hardware/libhardware_legacy/power/power.c

static void nativeReleaseSuspendBlocker(JNIEnv *env, jclass /* clazz */, jstring nameStr) {
    ScopedUtfChars name(env, nameStr);
    release_wake_lock(name.c_str());
}
```

在 JNI 层方法中，调用了 HAL 层的方法，通过文件描述符向 `/sys/power/wake_unlock` 中写值完成释放：

```C++
//hardware/libhardware_legacy/power/power.c

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

到这里为止，WakeLock 的释放流程也就分析完毕了，我们来看下整体流程。

![WakeLock 申请流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pms_wakelock/02.png)

## 五、Broadcasts

这个类型的 SuspendBlocker 并没有在 PowerManagerService 中进行实例化，它以构造方法的形式传入了 Notifier 中，Notifier 类相当于是 PowerManagerService 的”中介“，PowerManagerService 中和其他服务的部分交互通过 Notifier 进行，还有比如亮屏广播、灭屏广播等，都是由 PowerManagerService 交给 Notifier 来发送，这点在下篇文章中进行分析。因此，如果 CPU 在广播发送过程中进入休眠，则广播无法发送完成，因此，需要一个锁来保证 Notifier 中广播的成功发送，这就是 PowerManagerService.Broadcasts 锁的作用，当广播发送完毕后，该锁立即就释放了。

## 参考资料

- [Android电源管理系列之 PowerManagerService](http://www.robinheztto.com/2017/06/14/android-power-pms-1/)
- [PowerManagerService 分析](https://blog.csdn.net/FightFightFight/article/details/79532191)

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！