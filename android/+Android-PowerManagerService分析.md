# Android - PowerManagerService

## PowerManagerService 启动

- SystemServer.startBootstrapServices()

跟其他系统服务一样，PowerManagerService 也是继承于 SystemService 并通过 SystemServer 来启动。

```Java
//frameworks/base/services/core/java/com/android/server/SystemServer.java

private void startBootstrapServices() {
        //...
        mPowerManagerService = mSystemServiceManager.startService(PowerManagerService.class);
        //...
        mPackageManagerService.systemReady();
        //...
        //系统启动的各个阶段会调用 startBootPhase() 方法
        mSystemServiceManager.startBootPhase(xxx);
}
```

SystemServiceManager 的 startService() 方法就是使用 class 进行反射来创建 PowerManagerService 的实例。

```Java
//frameworks/base/services/core/java/com/android/server/SystemServiceManager.java

public <T extends SystemService> T startService(Class<T> serviceClass) {
        try {
            //...
            final T service;
            try {
                //通过反射创建 PowerManagerService
                Constructor<T> constructor = serviceClass.getConstructor(Context.class);
                service = constructor.newInstance(mContext);
            } catch (InstantiationException ex) {
               //...
            }

            startService(service);
            return service;
        } finally {}
    }
    
public void startService(@NonNull final SystemService service) {
        // 将服务添加到服务列表里
        mServices.add(service);
        
        try {
            // 启动服务，最终回调到 onStart 方法
            service.onStart();
        } catch (RuntimeException ex) {}
    }
```

## PowerManagerService 构造方法

首先来看下 PowerManagerService 的构造方法。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public PowerManagerService(Context context) {
        super(context);
        mContext = context;//context 为 SystemContext
        //创建处理消息的线程
        mHandlerThread = new ServiceThread(TAG,
                Process.THREAD_PRIORITY_DISPLAY, false /*allowIo*/);
        mHandlerThread.start();
        mHandler = new PowerManagerHandler(mHandlerThread.getLooper());
        mConstants = new Constants(mHandler);

        synchronized (mLock) {
            //创建两个 suspendBlocker 对象
            mWakeLockSuspendBlocker = createSuspendBlockerLocked("PowerManagerService.WakeLocks");
            mDisplaySuspendBlocker = createSuspendBlockerLocked("PowerManagerService.Display");
            //防止 CPU 进入睡眠状态
            mDisplaySuspendBlocker.acquire();
            mHoldingDisplaySuspendBlocker = true;
            mHalAutoSuspendModeEnabled = false;
            mHalInteractiveModeEnabled = true;
            //设置 mWakefulness 为唤醒状态
            mWakefulness = WAKEFULNESS_AWAKE;

            sQuiescent = SystemProperties.get(SYSTEM_PROPERTY_QUIESCENT, "0").equals("1");
            //初始化电源相关设置，通过 jni 调用 native 方法
            nativeInit();
            nativeSetAutoSuspend(false);
            nativeSetInteractive(true);
        }
    }
```
PowerManagerService 构造函数中首先创建了处理消息的进程及对应的 handler 对象以进行消息处理，然后创建SuspendBlocker 对象，用于 WakeLocks 与 Display，并设置 mWakefulness 的初始状态为 WAKEFULNESS_AWAKE，最后进入到 native 层初始化。下面先看一下关于 mWakefulness 的定义。

```Java
//frameworks/base/core/java/android/os/PowerManagerInternal.java

/**
 * 设备处于休眠状态，只能被 wakeUp() 唤醒．
 */
public static final int WAKEFULNESS_ASLEEP = 0;

/**
 * 设备处于正常工作(fully awake)状态．
 */
public static final int WAKEFULNESS_AWAKE = 1;

/**
 * 设备处于播放屏保状态．
 */
public static final int WAKEFULNESS_DREAMING = 2;

/**
 * 设备处于 doze 状态，只有低耗电的屏保可以运行，其他应用被挂起．
 */
public static final int WAKEFULNESS_DOZING = 3;
```

继续回到 PowerManagerService 构造函数的 native 初始化中，接着来看 nativeInit() 的实现。

```C++
//frameworks/base/services/core/jni/com_android_server_power_PowerManagerService.cpp

static const JNINativeMethod gPowerManagerServiceMethods[] = {
    /* name, signature, funcPtr */
    { "nativeInit", "()V",
            (void*) nativeInit },
    { "nativeAcquireSuspendBlocker", "(Ljava/lang/String;)V",
            (void*) nativeAcquireSuspendBlocker },
    { "nativeReleaseSuspendBlocker", "(Ljava/lang/String;)V",
            (void*) nativeReleaseSuspendBlocker },
    { "nativeSetInteractive", "(Z)V",
            (void*) nativeSetInteractive },
    { "nativeSetAutoSuspend", "(Z)V",
            (void*) nativeSetAutoSuspend },
    { "nativeSendPowerHint", "(II)V",
            (void*) nativeSendPowerHint },
    { "nativeSetFeature", "(II)V",
            (void*) nativeSetFeature },
};
```

从方法定义中可以看到 nativeInit 就是调用 nativeInit()。

```C++
//frameworks/base/services/core/jni/com_android_server_power_PowerManagerService.cpp

static void nativeInit(JNIEnv* env, jobject obj) {
    // 创建一个全局对象，引用 PowerManagerService
    gPowerManagerServiceObj = env->NewGlobalRef(obj);
    // 利用 hw_get_module 加载 power 模块
    status_t err = hw_get_module(POWER_HARDWARE_MODULE_ID,
            (hw_module_t const**)&gPowerModule);
    if (!err) {
        gPowerModule->init(gPowerModule);
    } else {
        ALOGE("Couldn't load %s module (%s)", POWER_HARDWARE_MODULE_ID, strerror(-err));
    }
}
```

nativeInit 的主要任务时装载 power 模块，该模块由厂商实现，以高通为例，如下。

```C++
//device/qcom/common/power/power.c

static struct hw_module_methods_t power_module_methods = {
    .open = NULL,
};

struct power_module HAL_MODULE_INFO_SYM = {
    .common = {
        .tag = HARDWARE_MODULE_TAG,
        .module_api_version = POWER_MODULE_API_VERSION_0_2,
        .hal_api_version = HARDWARE_HAL_API_VERSION,
        .id = POWER_HARDWARE_MODULE_ID,
        .name = "QCOM Power HAL",
        .author = "Qualcomm",
        .methods = &power_module_methods,
    },

    .init = power_init,
    .powerHint = power_hint,
    .setInteractive = set_interactive,
};
```

power_module 中实现了 init，powerHint，setInteractive，nativeInit 最终调用到 HAL power 模块的 power_init 具体实现中。接着看 native 初始化 nativeSetAutoSuspend 的实现。

```C++
//frameworks/base/services/core/jni/com_android_server_power_PowerManagerService.cpp

static void nativeSetAutoSuspend(JNIEnv* /* env */, jclass /* clazz */, jboolean enable) {
    if (enable) {
        ALOGD_IF_SLOW(100, "Excessive delay in autosuspend_enable() while turning screen off");
        autosuspend_enable();
    } else {
        ALOGD_IF_SLOW(100, "Excessive delay in autosuspend_disable() while turning screen on");
        autosuspend_disable();
    }
}

//system/core/libsuspend/autosuspend.c

int autosuspend_disable(void)
{
    int ret;

    ret = autosuspend_init();
    if (ret) {
        return ret;
    }

    ALOGV("autosuspend_disable\n");

    if (!autosuspend_enabled) {
        return 0;
    }

    ret = autosuspend_ops->disable();
    if (ret) {
        return ret;
    }

    autosuspend_enabled = false;
    return 0;
}
```

nativeSetAutoSuspend 最终调用到 libsuspend 的 autosuspend_disable 禁止系统休眠。继续看 native 初始化 nativeSetInteractive，nativeSetFeature 的实现。

```C++
//frameworks/base/services/core/jni/com_android_server_power_PowerManagerService.cpp

static void nativeSetInteractive(JNIEnv* /* env */, jclass /* clazz */, jboolean enable) {
    if (gPowerModule) {
        if (enable) {
            ALOGD_IF_SLOW(20, "Excessive delay in setInteractive(true) while turning screen on");
            gPowerModule->setInteractive(gPowerModule, true);
        } else {
            ALOGD_IF_SLOW(20, "Excessive delay in setInteractive(false) while turning screen off");
            gPowerModule->setInteractive(gPowerModule, false);
        }
    }
}

static void nativeSetFeature(JNIEnv *env, jclass clazz, jint featureId, jint data) {
    int data_param = data;

    if (gPowerModule && gPowerModule->setFeature) {
        gPowerModule->setFeature(gPowerModule, (feature_t)featureId, data_param);
    }
}
```

同 nativeInit 一样，最终都是调用到 HAL power 模块的具体实现中。以上是构造函数的分析流程，下面继续看 PowerManagerService 在系统启动过程中回调 onStart()，systemReady() 的实现。

- onStart()

在 SystemServer 中 startService 中调用到 PowerManagerService 构造函数做完初始化操作之后便会调用PowerManagerService 的 onStart() 函数：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@Override
public void onStart() {
    //BinderService 继承 IPowerManager.Stub，其实就是 PowerManager 的服务端
    //这里其实就是把 BinderService 对象注册到 ServiceManager 中
    publishBinderService(Context.POWER_SERVICE, new BinderService());
    publishLocalService(PowerManagerInternal.class, new LocalService());
    //加入 Watchdog 监控
    Watchdog.getInstance().addMonitor(this);
    Watchdog.getInstance().addThread(mHandler);
}
```

onStart() 完成的工作就是将 POWER_SERVICE 作为 Binder 的服务端，注册到 SystemService 中去；将PowerManagerInternal 注册到本地服务中，将自己加到 watchdog 的监控队列中去；将之前在构造函数中创建的 mHandler 对象加入到 watchdog 的中，用于监视 mHandler 的 looper 是否空闲。

## systemReady()

SystemServer 创建完 PowerManagerService 后，继续调用 systemReady() 方法，再做一些初始化的工作。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public void systemReady(IAppOpsService appOps) {
        synchronized (mLock) {
            mSystemReady = true;
            mAppOps = appOps;
            //5.0 后的新方法，localService 可以直接取
            mDreamManager = getLocalService(DreamManagerInternal.class);
            mDisplayManagerInternal = getLocalService(DisplayManagerInternal.class);
            mPolicy = getLocalService(WindowManagerPolicy.class);
            mBatteryManagerInternal = getLocalService(BatteryManagerInternal.class);
            //获取最小、最大、默认的屏幕点亮超时时间
            PowerManager pm = (PowerManager) mContext.getSystemService(Context.POWER_SERVICE);
            mScreenBrightnessSettingMinimum = pm.getMinimumScreenBrightnessSetting();
            mScreenBrightnessSettingMaximum = pm.getMaximumScreenBrightnessSetting();
            mScreenBrightnessSettingDefault = pm.getDefaultScreenBrightnessSetting();
            mScreenBrightnessForVrSettingDefault = pm.getDefaultScreenBrightnessForVrSetting();
            //传感器相关，传感器检查到外部事件可以通过发送消息到 mHandler 的消息队列中处理
            SensorManager sensorManager = new SystemSensorManager(mContext, mHandler.getLooper());
            
            // The notifier runs on the system server's main looper so as not to interfere
            // with the animations and other critical functions of the power manager.
            mBatteryStats = BatteryStatsService.getService();
            
            //注意上面的注释，notifier 运行在 system_server 的主线程中，
            //并且参数中传入了一个 SuspendBlocker 对象，应该是在发送通知的时候点亮屏幕
            mNotifier = new Notifier(Looper.getMainLooper(), mContext, mBatteryStats,
                    mAppOps, createSuspendBlockerLocked("PowerManagerService.Broadcasts"),
                    mPolicy);
            //无线充电相关，参数中传入了 sensorManager，并且传入了一个 SuspendBlocker 对象，
            //也是为了有外部事件时点亮屏幕
            mWirelessChargerDetector = new WirelessChargerDetector(sensorManager,
                    createSuspendBlockerLocked("PowerManagerService.WirelessChargerDetector"),
                    mHandler);
            //监听电源相关的设置改变
            mSettingsObserver = new SettingsObserver(mHandler);

            mLightsManager = getLocalService(LightsManager.class);
            mAttentionLight = mLightsManager.getLight(LightsManager.LIGHT_ID_ATTENTION);

            // Initialize display power management.
            mDisplayManagerInternal.initPowerManagement(
                    mDisplayPowerCallbacks, mHandler, sensorManager);

            // Go.
            //读取资源文档中的电源相关设置
            readConfigurationLocked();
            //更新设置中电源相关的设置
            updateSettingsLocked();
            mDirty |= DIRTY_BATTERY_STATE;
            //更新电源状态，这里统一处理的所有的状态更新，该方法会频繁的调用
            updatePowerStateLocked();
        }

        final ContentResolver resolver = mContext.getContentResolver();
        mConstants.start(resolver);
        mBatterySaverPolicy.start(resolver);

        //监听系统中对电源的设置，如开关省电模式、默认休眠超时时间、屏幕亮度、充电是否亮屏等等
        resolver.registerContentObserver(Settings.Secure.getUriFor(
                Settings.Secure.SCREENSAVER_ENABLED),
                false, mSettingsObserver, UserHandle.USER_ALL);
        //...
        
        // 注册一些广播，用来监听如电量变化、用户切换
        IntentFilter filter = new IntentFilter();
        filter.addAction(Intent.ACTION_BATTERY_CHANGED);
        filter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);
        mContext.registerReceiver(new BatteryReceiver(), filter, null, mHandler);
        //...
    }
```

- updatePowerStateLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updatePowerStateLocked() {
        if (!mSystemReady || mDirty == 0) {
            return;
        }
        if (!Thread.holdsLock(mLock)) {
            Slog.wtf(TAG, "Power manager lock was not held when calling updatePowerStateLocked");
        }

        Trace.traceBegin(Trace.TRACE_TAG_POWER, "updatePowerState");
        try {
            // Phase 0: Basic state updates.
            updateIsPoweredLocked(mDirty);
            //设置 DIRTY_STAY_ON 的标志位
            updateStayOnLocked(mDirty);
            updateScreenBrightnessBoostLocked(mDirty);

            // Phase 1: Update wakefulness.
            // Loop because the wake lock and user activity computations are influenced
            // by changes in wakefulness.
            final long now = SystemClock.uptimeMillis();
            int dirtyPhase2 = 0;
            for (;;) {
                int dirtyPhase1 = mDirty;
                dirtyPhase2 |= dirtyPhase1;
                mDirty = 0;

                updateWakeLockSummaryLocked(dirtyPhase1);
                updateUserActivitySummaryLocked(now, dirtyPhase1);
                if (!updateWakefulnessLocked(dirtyPhase1)) {
                    break;
                }
            }

            // Phase 2: Update display power state.
            boolean displayBecameReady = updateDisplayPowerStateLocked(dirtyPhase2);

            // Phase 3: Update dream state (depends on display ready signal).
            updateDreamLocked(dirtyPhase2, displayBecameReady);

            // Phase 4: Send notifications, if needed.
            finishWakefulnessChangeIfNeededLocked();

            // Phase 5: Update suspend blocker.
            // Because we might release the last suspend blocker here, we need to make sure
            // we finished everything else first!
            updateSuspendBlockerLocked();
        } finally {
            Trace.traceEnd(Trace.TRACE_TAG_POWER);
        }
    }
```

第 0 阶段：基本状态更新：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateIsPoweredLocked(int dirty) {
        if ((dirty & DIRTY_BATTERY_STATE) != 0) {
            final boolean wasPowered = mIsPowered;
            final int oldPlugType = mPlugType;
            final boolean oldLevelLow = mBatteryLevelLow;
            //获取充电标志位，充电器类型、电量百分比、低电量标志位
            mIsPowered = mBatteryManagerInternal.isPowered(BatteryManager.BATTERY_PLUGGED_ANY);
            mPlugType = mBatteryManagerInternal.getPlugType();
            mBatteryLevel = mBatteryManagerInternal.getBatteryLevel();
            mBatteryLevelLow = mBatteryManagerInternal.getBatteryLevelLow();

            if (DEBUG_SPEW) {
                Slog.d(TAG, "updateIsPoweredLocked: wasPowered=" + wasPowered
                        + ", mIsPowered=" + mIsPowered
                        + ", oldPlugType=" + oldPlugType
                        + ", mPlugType=" + mPlugType
                        + ", mBatteryLevel=" + mBatteryLevel);
            }
            //充电器插拔事件或者充电器类型改变，则设置 DIRTY_IS_POWERED 标志位
            if (wasPowered != mIsPowered || oldPlugType != mPlugType) {
                mDirty |= DIRTY_IS_POWERED;

                // Update wireless dock detection state.
                //判断是否进行无线充电
                final boolean dockedOnWirelessCharger = mWirelessChargerDetector.update(
                        mIsPowered, mPlugType, mBatteryLevel);

                // Treat plugging and unplugging the devices as a user activity.
                // Users find it disconcerting when they plug or unplug the device
                // and it shuts off right away.
                // Some devices also wake the device when plugged or unplugged because
                // they don't have a charging LED.
                //上面注释的意思是说插拔充电器可以看做是用户行为，当插拔充电器时如果设备没有给出提示则用户比较迷惑
                //特别是在设备没有充电指示灯时，所以一般插拔充电器时会唤醒设备
                final long now = SystemClock.uptimeMillis();
                if (shouldWakeUpWhenPluggedOrUnpluggedLocked(wasPowered, oldPlugType,
                        dockedOnWirelessCharger)) {
                    wakeUpNoUpdateLocked(now, "android.server.power:POWER", Process.SYSTEM_UID,
                            mContext.getOpPackageName(), Process.SYSTEM_UID);
                }
                //如果设置了插拔充电器时需要唤醒设备，则在这里唤醒设备
                userActivityNoUpdateLocked(
                        now, PowerManager.USER_ACTIVITY_EVENT_OTHER, 0, Process.SYSTEM_UID);

                // Tell the notifier whether wireless charging has started so that
                // it can provide feedback to the user.
                //当无线充电器开始充电时给出提示音，在 mNotifier 中进行处理，播放一个 ogg 音频文件
                if (dockedOnWirelessCharger) {
                    mNotifier.onWirelessChargingStarted();
                }
            }
            //如果电源发生插拔时或者低电量标志位发生变化
            if (wasPowered != mIsPowered || oldLevelLow != mBatteryLevelLow) {
                if (oldLevelLow != mBatteryLevelLow && !mBatteryLevelLow) {
                    //当设备从低电量转换为非低电量，则设置自动打盹为 false
                    if (DEBUG_SPEW) {
                        Slog.d(TAG, "updateIsPoweredLocked: resetting low power snooze");
                    }
                    mAutoLowPowerModeSnoozing = false;
                }
                //发送广播 ACTION_POWER_SAVE_MODE_CHANGED，该广播在系统中多出进行处理，
                //在 SystemUI 中进行处理，如果低电量则给出提示
                updateLowPowerModeLocked();
            }
        }
    }
    
 private void updateScreenBrightnessBoostLocked(int dirty) {
        if ((dirty & DIRTY_SCREEN_BRIGHTNESS_BOOST) != 0) {
            if (mScreenBrightnessBoostInProgress) {
                final long now = SystemClock.uptimeMillis();
                //删除屏幕亮度提升超时广播
                mHandler.removeMessages(MSG_SCREEN_BRIGHTNESS_BOOST_TIMEOUT);
                if (mLastScreenBrightnessBoostTime > mLastSleepTime) {
                    final long boostTimeout = mLastScreenBrightnessBoostTime +
                            SCREEN_BRIGHTNESS_BOOST_TIMEOUT;
                    //如果超时还没有发生，则重新发送广播
                    if (boostTimeout > now) {
                        Message msg = mHandler.obtainMessage(MSG_SCREEN_BRIGHTNESS_BOOST_TIMEOUT);
                        msg.setAsynchronous(true);
                        mHandler.sendMessageAtTime(msg, boostTimeout);
                        return;
                    }
                }
                //进行到这里有两个条件
                //mLastScreenBrightnessBoostTime <= mLastSleepTime 说明还在睡眠中
                //boostTimeout <= now 说明亮度提升超时发生
                mScreenBrightnessBoostInProgress = false;
                mNotifier.onScreenBrightnessBoostChanged();
                userActivityNoUpdateLocked(now,
                        PowerManager.USER_ACTIVITY_EVENT_OTHER, 0, Process.SYSTEM_UID);
            }
        }
    }
```

第 1 阶段：基本状态更新：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateWakeLockSummaryLocked(int dirty) {
        if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_WAKEFULNESS)) != 0) {
            mWakeLockSummary = 0;
            //numWakeLocks 保存了用户创建的所有 wakelock
            final int numWakeLocks = mWakeLocks.size();
            for (int i = 0; i < numWakeLocks; i++) {
                final WakeLock wakeLock = mWakeLocks.get(i);
                switch (wakeLock.mFlags & PowerManager.WAKE_LOCK_LEVEL_MASK) {
                    case PowerManager.PARTIAL_WAKE_LOCK:
                        if (!wakeLock.mDisabled) {
                            // We only respect this if the wake lock is not disabled.
                            mWakeLockSummary |= WAKE_LOCK_CPU;
                        }
                        break;
                    case PowerManager.FULL_WAKE_LOCK:
                        mWakeLockSummary |= WAKE_LOCK_SCREEN_BRIGHT | WAKE_LOCK_BUTTON_BRIGHT;
                        break;
                    case PowerManager.SCREEN_BRIGHT_WAKE_LOCK:
                        mWakeLockSummary |= WAKE_LOCK_SCREEN_BRIGHT;
                        break;
                    case PowerManager.SCREEN_DIM_WAKE_LOCK:
                        mWakeLockSummary |= WAKE_LOCK_SCREEN_DIM;
                        break;
                    case PowerManager.PROXIMITY_SCREEN_OFF_WAKE_LOCK:
                        mWakeLockSummary |= WAKE_LOCK_PROXIMITY_SCREEN_OFF;
                        break;
                    case PowerManager.DOZE_WAKE_LOCK:
                        mWakeLockSummary |= WAKE_LOCK_DOZE;
                        break;
                    case PowerManager.DRAW_WAKE_LOCK:
                        mWakeLockSummary |= WAKE_LOCK_DRAW;
                        break;
                }
            }

            // Cancel wake locks that make no sense based on the current state.
            //根据 mWakefulness 的状态取消某些锁的作用，意思就是在系统处于特定状态时，
            //有些锁没有意义，需要取消 mWakeLockSummary 中相对应的标志位
            if (mWakefulness != WAKEFULNESS_DOZING) {
                mWakeLockSummary &= ~(WAKE_LOCK_DOZE | WAKE_LOCK_DRAW);
            }
            //注意这里，当 mWakefulless 为 asleep 时，WAKE_LOCK_SCREEN_BRIGHT、WAKE_LOCK_SCREEN_DIM、
            //WAKE_LOCK_BUTTON_BRIGHT、WAKE_LOCK_PROXIMITY_SCREEN_OFF 这几个中 WakeLock 的标志位都会
            //被清空，标志位被清空的作用就是类似系统释放了这些锁；
            //仔细看只有 WAKE_LOCK_CPU 标志位不变，说明 PARTIAL_WAKE_LOCK 在系统休眠的时候是不是自动清空的，
            //如果系统中存在 PARTIAL_WAKE_LOCK，那么除非手动释放，不然系统将没办法进入休眠。
            //如果第三方应用获取了 PARTIAL_WAKE_LOCK，但是系统休眠时又不是释放该怎么办呢？
            if (mWakefulness == WAKEFULNESS_ASLEEP
                    || (mWakeLockSummary & WAKE_LOCK_DOZE) != 0) {
                mWakeLockSummary &= ~(WAKE_LOCK_SCREEN_BRIGHT | WAKE_LOCK_SCREEN_DIM
                        | WAKE_LOCK_BUTTON_BRIGHT);
                if (mWakefulness == WAKEFULNESS_ASLEEP) {
                    mWakeLockSummary &= ~WAKE_LOCK_PROXIMITY_SCREEN_OFF;
                }
            }

            // Infer implied wake locks where necessary based on the current state.
            //根据 mWakefullness 的状态增加某些锁的作用，就是说当系统处于特定状态时，需要某些锁来保持系统的状态，
            //比如 WAKEFULNESS_AWAKE 状态肯定是要保持 CPU 运行的，
            //所以需要添加 WAKE_LOCK_CPU 标志位以确保 CPU 处于运行状态
            if ((mWakeLockSummary & (WAKE_LOCK_SCREEN_BRIGHT | WAKE_LOCK_SCREEN_DIM)) != 0) {
                if (mWakefulness == WAKEFULNESS_AWAKE) {
                    mWakeLockSummary |= WAKE_LOCK_CPU | WAKE_LOCK_STAY_AWAKE;
                } else if (mWakefulness == WAKEFULNESS_DREAMING) {
                    mWakeLockSummary |= WAKE_LOCK_CPU;
                }
            }
            if ((mWakeLockSummary & WAKE_LOCK_DRAW) != 0) {
                mWakeLockSummary |= WAKE_LOCK_CPU;
            }
        }
    }
    
    
private void updateUserActivitySummaryLocked(long now, int dirty) {
        // Update the status of the user activity timeout timer.
        if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY
                | DIRTY_WAKEFULNESS | DIRTY_SETTINGS)) != 0) {
            mHandler.removeMessages(MSG_USER_ACTIVITY_TIMEOUT);

            long nextTimeout = 0;
            if (mWakefulness == WAKEFULNESS_AWAKE
                    || mWakefulness == WAKEFULNESS_DREAMING
                    || mWakefulness == WAKEFULNESS_DOZING) {
                final int sleepTimeout = getSleepTimeoutLocked();
                final int screenOffTimeout = getScreenOffTimeoutLocked(sleepTimeout);
                final int screenDimDuration = getScreenDimDurationLocked(screenOffTimeout);
                final boolean userInactiveOverride = mUserInactiveOverrideFromWindowManager;

                mUserActivitySummary = 0;
                if (mLastUserActivityTime >= mLastWakeTime) {
                    nextTimeout = mLastUserActivityTime
                            + screenOffTimeout - screenDimDuration;
                    if (now < nextTimeout) {
                        mUserActivitySummary = USER_ACTIVITY_SCREEN_BRIGHT;
                    } else {
                        nextTimeout = mLastUserActivityTime + screenOffTimeout;
                        if (now < nextTimeout) {
                            mUserActivitySummary = USER_ACTIVITY_SCREEN_DIM;
                        }
                    }
                }
                if (mUserActivitySummary == 0
                        && mLastUserActivityTimeNoChangeLights >= mLastWakeTime) {
                    nextTimeout = mLastUserActivityTimeNoChangeLights + screenOffTimeout;
                    if (now < nextTimeout) {
                        if (mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_BRIGHT
                                || mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_VR) {
                            mUserActivitySummary = USER_ACTIVITY_SCREEN_BRIGHT;
                        } else if (mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_DIM) {
                            mUserActivitySummary = USER_ACTIVITY_SCREEN_DIM;
                        }
                    }
                }

                if (mUserActivitySummary == 0) {
                    if (sleepTimeout >= 0) {
                        final long anyUserActivity = Math.max(mLastUserActivityTime,
                                mLastUserActivityTimeNoChangeLights);
                        if (anyUserActivity >= mLastWakeTime) {
                            nextTimeout = anyUserActivity + sleepTimeout;
                            if (now < nextTimeout) {
                                mUserActivitySummary = USER_ACTIVITY_SCREEN_DREAM;
                            }
                        }
                    } else {
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
                    Message msg = mHandler.obtainMessage(MSG_USER_ACTIVITY_TIMEOUT);
                    msg.setAsynchronous(true);
                    mHandler.sendMessageAtTime(msg, nextTimeout);
                }
            } else {
                mUserActivitySummary = 0;
            }

            if (DEBUG_SPEW) {
                Slog.d(TAG, "updateUserActivitySummaryLocked: mWakefulness="
                        + PowerManagerInternal.wakefulnessToString(mWakefulness)
                        + ", mUserActivitySummary=0x" + Integer.toHexString(mUserActivitySummary)
                        + ", nextTimeout=" + TimeUtils.formatUptime(nextTimeout));
            }
        }
    }
    
private boolean updateWakefulnessLocked(int dirty) {
        boolean changed = false;
        if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY | DIRTY_BOOT_COMPLETED
                | DIRTY_WAKEFULNESS | DIRTY_STAY_ON | DIRTY_PROXIMITY_POSITIVE
                | DIRTY_DOCK_STATE)) != 0) {
            //注意这里改变 mWakefullness 的值，但是 mWakefullness 的值会影响锁的有效性，
            //因此阶段 2 的处理在一个 for 循环中
            if (mWakefulness == WAKEFULNESS_AWAKE && isItBedTimeYetLocked()) {
                if (DEBUG_SPEW) {
                    Slog.d(TAG, "updateWakefulnessLocked: Bed time...");
                }
                final long time = SystemClock.uptimeMillis();
                if (shouldNapAtBedTimeLocked()) {
                    changed = napNoUpdateLocked(time, Process.SYSTEM_UID);
                } else {
                    changed = goToSleepNoUpdateLocked(time,
                            PowerManager.GO_TO_SLEEP_REASON_TIMEOUT, 0, Process.SYSTEM_UID);
                }
            }
        }
        return changed;
    }
```

阶段 2：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

 private boolean updateDisplayPowerStateLocked(int dirty) {
        final boolean oldDisplayReady = mDisplayReady;
        if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY | DIRTY_WAKEFULNESS
                | DIRTY_ACTUAL_DISPLAY_POWER_STATE_UPDATED | DIRTY_BOOT_COMPLETED
                | DIRTY_SETTINGS | DIRTY_SCREEN_BRIGHTNESS_BOOST | DIRTY_VR_MODE_CHANGED |
                DIRTY_QUIESCENT)) != 0) {
            mDisplayPowerRequest.policy = getDesiredScreenPolicyLocked();

            // Determine appropriate screen brightness and auto-brightness adjustments.
            boolean brightnessSetByUser = true;
            int screenBrightness = mScreenBrightnessSettingDefault;
            float screenAutoBrightnessAdjustment = 0.0f;
            boolean autoBrightness = (mScreenBrightnessModeSetting ==
                    Settings.System.SCREEN_BRIGHTNESS_MODE_AUTOMATIC);
            if (!mBootCompleted) {
                // Keep the brightness steady during boot. This requires the
                // bootloader brightness and the default brightness to be identical.
                autoBrightness = false;
                brightnessSetByUser = false;
            } else if (mIsVrModeEnabled) {
                screenBrightness = mScreenBrightnessForVrSetting;
                autoBrightness = false;
            } else if (isValidBrightness(mScreenBrightnessOverrideFromWindowManager)) {
                screenBrightness = mScreenBrightnessOverrideFromWindowManager;
                autoBrightness = false;
                brightnessSetByUser = false;
            } else if (isValidBrightness(mTemporaryScreenBrightnessSettingOverride)) {
                screenBrightness = mTemporaryScreenBrightnessSettingOverride;
            } else if (isValidBrightness(mScreenBrightnessSetting)) {
                screenBrightness = mScreenBrightnessSetting;
            }
            if (autoBrightness) {
                screenBrightness = mScreenBrightnessSettingDefault;
                if (isValidAutoBrightnessAdjustment(
                        mTemporaryScreenAutoBrightnessAdjustmentSettingOverride)) {
                    screenAutoBrightnessAdjustment =
                            mTemporaryScreenAutoBrightnessAdjustmentSettingOverride;
                } else if (isValidAutoBrightnessAdjustment(
                        mScreenAutoBrightnessAdjustmentSetting)) {
                    screenAutoBrightnessAdjustment = mScreenAutoBrightnessAdjustmentSetting;
                }
            }
            screenBrightness = Math.max(Math.min(screenBrightness,
                    mScreenBrightnessSettingMaximum), mScreenBrightnessSettingMinimum);
            screenAutoBrightnessAdjustment = Math.max(Math.min(
                    screenAutoBrightnessAdjustment, 1.0f), -1.0f);

            // Update display power request.
            mDisplayPowerRequest.screenBrightness = screenBrightness;
            mDisplayPowerRequest.screenAutoBrightnessAdjustment =
                    screenAutoBrightnessAdjustment;
            mDisplayPowerRequest.brightnessSetByUser = brightnessSetByUser;
            mDisplayPowerRequest.useAutoBrightness = autoBrightness;
            mDisplayPowerRequest.useProximitySensor = shouldUseProximitySensorLocked();
            mDisplayPowerRequest.boostScreenBrightness = shouldBoostScreenBrightness();

            updatePowerRequestFromBatterySaverPolicy(mDisplayPowerRequest);

            if (mDisplayPowerRequest.policy == DisplayPowerRequest.POLICY_DOZE) {
                mDisplayPowerRequest.dozeScreenState = mDozeScreenStateOverrideFromDreamManager;
                if (mDisplayPowerRequest.dozeScreenState == Display.STATE_DOZE_SUSPEND
                        && (mWakeLockSummary & WAKE_LOCK_DRAW) != 0) {
                    mDisplayPowerRequest.dozeScreenState = Display.STATE_DOZE;
                }
                mDisplayPowerRequest.dozeScreenBrightness =
                        mDozeScreenBrightnessOverrideFromDreamManager;
            } else {
                mDisplayPowerRequest.dozeScreenState = Display.STATE_UNKNOWN;
                mDisplayPowerRequest.dozeScreenBrightness = PowerManager.BRIGHTNESS_DEFAULT;
            }

            mDisplayReady = mDisplayManagerInternal.requestPowerState(mDisplayPowerRequest,
                    mRequestWaitForNegativeProximity);
            mRequestWaitForNegativeProximity = false;

            if ((dirty & DIRTY_QUIESCENT) != 0) {
                sQuiescent = false;
            }
            if (DEBUG_SPEW) {
                Slog.d(TAG, "updateDisplayPowerStateLocked: mDisplayReady=" + mDisplayReady
                        + ", policy=" + mDisplayPowerRequest.policy
                        + ", mWakefulness=" + mWakefulness
                        + ", mWakeLockSummary=0x" + Integer.toHexString(mWakeLockSummary)
                        + ", mUserActivitySummary=0x" + Integer.toHexString(mUserActivitySummary)
                        + ", mBootCompleted=" + mBootCompleted
                        + ", mScreenBrightnessBoostInProgress=" + mScreenBrightnessBoostInProgress
                        + ", mIsVrModeEnabled= " + mIsVrModeEnabled
                        + ", sQuiescent=" + sQuiescent);
            }
        }
        return mDisplayReady && !oldDisplayReady;
    }
```

阶段3：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

 private void updateDreamLocked(int dirty, boolean displayBecameReady) {
        if ((dirty & (DIRTY_WAKEFULNESS
                | DIRTY_USER_ACTIVITY
                | DIRTY_WAKE_LOCKS
                | DIRTY_BOOT_COMPLETED
                | DIRTY_SETTINGS
                | DIRTY_IS_POWERED
                | DIRTY_STAY_ON
                | DIRTY_PROXIMITY_POSITIVE
                | DIRTY_BATTERY_STATE)) != 0 || displayBecameReady) {
            if (mDisplayReady) {
                scheduleSandmanLocked();
            }
        }
    }
    
private void scheduleSandmanLocked() {
        if (!mSandmanScheduled) {
            mSandmanScheduled = true;
            Message msg = mHandler.obtainMessage(MSG_SANDMAN);
            msg.setAsynchronous(true);
            mHandler.sendMessage(msg);
        }
    }
```

阶段4：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void finishWakefulnessChangeIfNeededLocked() {
        if (mWakefulnessChanging && mDisplayReady) {
            if (mWakefulness == WAKEFULNESS_DOZING
                    && (mWakeLockSummary & WAKE_LOCK_DOZE) == 0) {
                return; // wait until dream has enabled dozing
            }
            if (mWakefulness == WAKEFULNESS_DOZING || mWakefulness == WAKEFULNESS_ASLEEP) {
                logSleepTimeoutRecapturedLocked();
            }
            if (mWakefulness == WAKEFULNESS_AWAKE) {
                logScreenOn();
            }
            mWakefulnessChanging = false;
            mNotifier.onWakefulnessChangeFinished();
        }
    }
```

阶段5：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateSuspendBlockerLocked() {
        final boolean needWakeLockSuspendBlocker = ((mWakeLockSummary & WAKE_LOCK_CPU) != 0);
        final boolean needDisplaySuspendBlocker = needDisplaySuspendBlockerLocked();
        final boolean autoSuspend = !needDisplaySuspendBlocker;
        final boolean interactive = mDisplayPowerRequest.isBrightOrDim();

        // Disable auto-suspend if needed.
        // FIXME We should consider just leaving auto-suspend enabled forever since
        // we already hold the necessary wakelocks.
        if (!autoSuspend && mDecoupleHalAutoSuspendModeFromDisplayConfig) {
            setHalAutoSuspendModeLocked(false);
        }

        // First acquire suspend blockers if needed.
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

        // Then release suspend blockers if needed.
        //注意这个 needWakeLockSuspendBlocker 为 ture 的话是不会释放 mWakeLockSuspendBlocker 的，
        //所以系统无法待机，这样就能解释为什么 PARTIAL_WAKE_LOCK 级别的锁不会导致待机了:
        //app --> newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,flag) 
        ///--> PMS 设置 mWakeLockSummary 的 WAKE_LOCK_CPU 标志位
        //--> PMS 因为 WAKE_LOCK_CPU 标志位存在 mWakeLockSuspendBlocker.acquire() --> 待机失败
        if (!needWakeLockSuspendBlocker && mHoldingWakeLockSuspendBlocker) {
            mWakeLockSuspendBlocker.release();
            mHoldingWakeLockSuspendBlocker = false;
        }
        if (!needDisplaySuspendBlocker && mHoldingDisplaySuspendBlocker) {
            mDisplaySuspendBlocker.release();
            mHoldingDisplaySuspendBlocker = false;
        }

        // Enable auto-suspend if needed.
        //如果条件成立的话设置自动待机模式
        if (autoSuspend && mDecoupleHalAutoSuspendModeFromDisplayConfig) {
            setHalAutoSuspendModeLocked(true);
        }
    }
```


## startBootPhase() 分析

我们在 SystemServer.startBootstrapServices() 系统启动中可以看到，在启动的的各个阶段都会调用 `startBootPhase()` 方法，下面我们来看下这个方法的作用。

```Java
//frameworks/base/services/core/java/com/android/server/SystemServiceManager.java

public void startBootPhase(final int phase) {
        if (phase <= mCurrentPhase) {
            throw new IllegalArgumentException("Next phase must be larger than previous");
        }
        mCurrentPhase = phase;

        Slog.i(TAG, "Starting phase " + mCurrentPhase);
        try {
            Trace.traceBegin(Trace.TRACE_TAG_SYSTEM_SERVER, "OnBootPhase " + phase);
            final int serviceLen = mServices.size();
            //遍历已经服务列表
            for (int i = 0; i < serviceLen; i++) {
                final SystemService service = mServices.get(i);
                long time = System.currentTimeMillis();
                Trace.traceBegin(Trace.TRACE_TAG_SYSTEM_SERVER, service.getClass().getName());
                try {
                    //调用服务的 onBootPhase() 方法
                    service.onBootPhase(mCurrentPhase);
                } catch (Exception ex) {}
                warnIfTooLong(System.currentTimeMillis() - time, service, "onBootPhase");
                Trace.traceEnd(Trace.TRACE_TAG_SYSTEM_SERVER);
            }
        } finally {
            Trace.traceEnd(Trace.TRACE_TAG_SYSTEM_SERVER);
        }
    }
```

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@Override
public void onBootPhase(int phase) {
    synchronized (mLock) {
        if (phase == PHASE_THIRD_PARTY_APPS_CAN_START) {
            incrementBootCount();

        } else if (phase == PHASE_BOOT_COMPLETED) {
            final long now = SystemClock.uptimeMillis();
            //设置 mBootCompleted 状态
            mBootCompleted = true;
            mDirty |= DIRTY_BOOT_COMPLETED;
            //更新 userActivity 及 PowerState
            userActivityNoUpdateLocked(
                    now, PowerManager.USER_ACTIVITY_EVENT_OTHER, 0, Process.SYSTEM_UID);
            updatePowerStateLocked();

            if (!ArrayUtils.isEmpty(mBootCompletedRunnables)) {
                Slog.d(TAG, "Posting " + mBootCompletedRunnables.length + " delayed runnables");
                for (Runnable r : mBootCompletedRunnables) {
                    BackgroundThread.getHandler().post(r);
                }
            }
            mBootCompletedRunnables = null;
        }
    }
}
```

onBootPhase 中主要设置 mBootCompleted 状态，更新 PowerState 状态，并执行 mBootCompletedRunnables 中的 runnables方法(低电量模式会设置)。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private boolean userActivityNoUpdateLocked(long eventTime, int event, int flags, int uid) {
       //如果发生时间是上一次休眠或唤醒前，或当前没有开机完成到 systemReady，不采取操作直接返回
        if (eventTime < mLastSleepTime || eventTime < mLastWakeTime
                || !mBootCompleted || !mSystemReady) {
            return false;
        }

        Trace.traceBegin(Trace.TRACE_TAG_POWER, "userActivity");
        try {
            //更新 mLastInteractivePowerHintTime 时间
            if (eventTime > mLastInteractivePowerHintTime) {
                powerHintInternal(PowerHint.INTERACTION, 0);
                mLastInteractivePowerHintTime = eventTime;
            }

            //通过 mNotifier 通知 BatteryStats UserActivity 事件
            mNotifier.onUserActivity(event, uid);

            if (mUserInactiveOverrideFromWindowManager) {
                mUserInactiveOverrideFromWindowManager = false;
                mOverriddenTimeout = -1;
            }

            //如果系统处于休眠状态，不进行处理
            if (mWakefulness == WAKEFULNESS_ASLEEP
                    || mWakefulness == WAKEFULNESS_DOZING
                    || (flags & PowerManager.USER_ACTIVITY_FLAG_INDIRECT) != 0) {
                return false;
            }

            //根据 flag 是否在已变暗的情况下，是否重启活动超时更新 mLastUserActivityTimeNoChangeLights
            //或 mLastUserActivityTime，并且设置 mDirty -> DIRTY_USER_ACTIVITY
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


## userActivity





## WakeLock 分析

- WakeLock 客户端
- new WakeLock 分析
- acquire 分析
- PowerManagerService.acquireWakeLock

## LightService

## userActivity

## BatteryService

## BatteryStatsServic

## 参考资料

- [](http://www.robinheztto.com/2017/06/14/android-power-pms-1/)



