# Android - 大标题

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

```


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

## 参考资料

- [资料标题](http://www.baidu.com)


