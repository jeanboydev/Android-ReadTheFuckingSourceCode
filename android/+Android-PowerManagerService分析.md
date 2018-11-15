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
        //系统启动的各个阶段会调用 startBootPhase() 方法
        mSystemServiceManager.startBootPhase(xxx);
        //...
        mPackageManagerService.systemReady(mActivityManagerService.getAppOpsService());
        //...
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



## startBootPhase() 分析

onStart() 方法调用完毕后会回到 SytemServer 中，然后根据 SystemService 的生命周期，会开始执行 onBootPhase()，这个方法的功能是为所有的已启动的服务指定启动阶段，从而可以在指定的启动阶段来做指定的工作。

```Java
//frameworks/base/services/core/java/com/android/server/SystemServiceManager.java

public void startBootPhase(final int phase) {
        if (phase <= mCurrentPhase) {
            throw new IllegalArgumentException("Next phase must be larger than previous");
        }
        mCurrentPhase = phase;
        try {
            final int serviceLen = mServices.size();
            //遍历已经服务列表
            for (int i = 0; i < serviceLen; i++) {
                final SystemService service = mServices.get(i);
                try {
                    //调用服务的 onBootPhase() 方法
                    service.onBootPhase(mCurrentPhase);
                } catch (Exception ex) {}
            }
        } finally {}
    }
```

在 SystemServiceManager 的 startBootPhase() 中，调用 SystemService 的 onBootPhase(int) 方法，此时每个 SystemService 都会执行其对应的 onBootPhase() 方法。通过在 SystemServiceManager 中传入不同的形参，回调所有 SystemService的onBootPhase()，根据形参的不同，在方法实现中完成不同的工作，在 SystemService 中定义了五个阶段：

- SystemService.PHASE_WAIT_FOR_DEFAULT_DISPLAY：这是一个依赖 项，只有DisplayManagerService中进行了对应处理；
- SystemService.PHASE_LOCK_SETTINGS_READY：经过这个引导阶段后，服务才可以接收到wakelock相关设置数据；
- SystemService.PHASE_SYSTEM_SERVICES_READY：经过这个引导阶段 后，服务才可以安全地使用核心系统服务
- SystemService.PHASE_ACTIVITY_MANAGER_READY：经过这个引导阶 段后，服务可以发送广播
- SystemService.PHASE_THIRD_PARTY_APPS_CAN_START：经过这个引 导阶段后，服务可以启动第三方应用，第三方应用也可以通过Binder来调 用服务。
- SystemService.PHASE_BOOT_COMPLETED：经过这个引导阶段后，说明服务启动完成，这时用户就可以和设备进行交互。

因此，只要在其他模块中调用了 SystemServiceManager.startBootPhase()，都会触发各自的 onBootPhase()。PowerManagerService 的 onBootPhase() 方法只对引导阶段的 2 个阶段做了处理，具体代码如下：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

@Override
public void onBootPhase(int phase) {
    synchronized (mLock) {
        if (phase == PHASE_THIRD_PARTY_APPS_CAN_START) {
            //统计启动的 Apk 个数
            incrementBootCount();
        } else if (phase == PHASE_BOOT_COMPLETED) {
            final long now = SystemClock.uptimeMillis();
            //设置 mBootCompleted 状态
            mBootCompleted = true;
            mDirty |= DIRTY_BOOT_COMPLETED;
            //更新用户活动时间
            userActivityNoUpdateLocked(
                    now, PowerManager.USER_ACTIVITY_EVENT_OTHER, 0, Process.SYSTEM_UID);
            //更新电源状态信息
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

在这个方法中，mDirty 是一个二进制的标记位，用来表示电源状态哪一部分发生了改变，通过对其进行置位（| 操作）、清零（～ 操作），得到二进制数各个位的值(0 或 1)，进行不同的处理。我们接着来看下 userActivityNoUpdateLocked() 方法：


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

此外，这个方法中调用到了 updatePowerStateLocked() 方法，这是整个 PowerManagerService 中最重要的方法，这块会在下文中进行详细分析。此时，SystemServer.startBootstrapServices() 执行完毕，生命周期方法也执行完毕。接下来会执行到 systemReady()。


## systemReady()

SystemServer 创建完 PowerManagerService 后，继续调用 systemReady() 方法，再做一些初始化的工作。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

public void systemReady(IAppOpsService appOps) {
    synchronized (mLock) {
        mSystemReady = true;
        mAppOps = appOps;
        //和 DreamManagerService 交互
        mDreamManager = getLocalService(DreamManagerInternal.class);
        //和 DisplayManagerService 交互
        mDisplayManagerInternal = getLocalService(DisplayManagerInternal.class);
        //和 WindowManagerService 交互
        mPolicy = getLocalService(WindowManagerPolicy.class);
        //和 BatteryService 交互
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
        //获取 BatteryStatsService
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
        //和显示有关，如：亮灭屏、背光调节
        mDisplayManagerInternal.initPowerManagement(
                mDisplayPowerCallbacks, mHandler, sensorManager);

        // Go.
        //读取资源文档中的电源相关设置，详见下面分析
        readConfigurationLocked();
        //更新设置中电源相关的设置，详见下面分析
        updateSettingsLocked();
        mDirty |= DIRTY_BATTERY_STATE;
        //更新电源状态，这里统一处理的所有的状态更新，该方法会频繁的调用，详见下面分析
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
    //注册 BatteryService 中 ACTION_BATTERY_CHANGED广播
    IntentFilter filter = new IntentFilter();
    filter.addAction(Intent.ACTION_BATTERY_CHANGED);
    filter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);
    mContext.registerReceiver(new BatteryReceiver(), filter, null, mHandler);
    IntentFilter filter = new IntentFilter();
    //Dream 相关
    filter = new IntentFilter();
    filter.addAction(Intent.ACTION_DREAMING_STARTED);
    filter.addAction(Intent.ACTION_DREAMING_STOPPED);
    mContext.registerReceiver(new DreamReceiver(), filter, null, mHandler);
    //用户切换
    filter = new IntentFilter();
    filter.addAction(Intent.ACTION_USER_SWITCHED);
    mContext.registerReceiver(new UserSwitchedReceiver(), filter, null, mHandler);
    //Dock 相关
    filter = new IntentFilter();
    filter.addAction(Intent.ACTION_DOCK_EVENT);
    mContext.registerReceiver(new DockReceiver(), filter, null, mHandler);
}
```

- readConfigurationLocked()

调用 readConfigurationLocked() 方法读取配置文件中的默认值：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java
private void readConfigurationLocked() {
    final Resources resources = mContext.getResources();

    mDecoupleHalAutoSuspendModeFromDisplayConfig = resources.getBoolean(
            com.android.internal.R.bool.config_powerDecoupleAutoSuspendModeFromDisplay);
    mDecoupleHalInteractiveModeFromDisplayConfig = resources.getBoolean(
            com.android.internal.R.bool.config_powerDecoupleInteractiveModeFromDisplay);
    //插拔 USB 是否亮屏
    mWakeUpWhenPluggedOrUnpluggedConfig = resources.getBoolean(
            com.android.internal.R.bool.config_unplugTurnsOnScreen);
    //设备处于剧院模式时，插拔 USB 是否亮屏
    mWakeUpWhenPluggedOrUnpluggedInTheaterModeConfig = resources.getBoolean(
            com.android.internal.R.bool.config_allowTheaterModeWakeFromUnplug);
    //是否允许设备由于接近传感器而关闭屏幕时 CPU 挂起，进入 suspend 状态
    mSuspendWhenScreenOffDueToProximityConfig = resources.getBoolean(
            com.android.internal.R.bool.config_suspendWhenScreenOffDueToProximity);
    //是否支持屏保
    mDreamsSupportedConfig = resources.getBoolean(
            com.android.internal.R.bool.config_dreamsSupported);
    //是否屏保默认打开--false
    mDreamsEnabledByDefaultConfig = resources.getBoolean(
            com.android.internal.R.bool.config_dreamsEnabledByDefault);
    //睡眠是否打开屏保
    mDreamsActivatedOnSleepByDefaultConfig = resources.getBoolean(
            com.android.internal.R.bool.config_dreamsActivatedOnSleepByDefault);
    //Dock时屏保是否激活
    mDreamsActivatedOnDockByDefaultConfig = resources.getBoolean(
            com.android.internal.R.bool.config_dreamsActivatedOnDockByDefault);
    //放电时是否允许进入屏保
    mDreamsEnabledOnBatteryConfig = resources.getBoolean(
            com.android.internal.R.bool.config_dreamsEnabledOnBattery);
    //充电时允许屏保的最低电量，使用 -1 禁用此功能
    mDreamsBatteryLevelMinimumWhenPoweredConfig = resources.getInteger(
            com.android.internal.R.integer.config_dreamsBatteryLevelMinimumWhenPowered);
    //放电时允许屏保的最低电量，使用 -1 禁用此功能，默认 15
    mDreamsBatteryLevelMinimumWhenNotPoweredConfig = resources.getInteger(
            com.android.internal.R.integer.config_dreamsBatteryLevelMinimumWhenNotPowered);
    //电亮下降到该百分点，当用户活动超时后不进入屏保，默认5
    mDreamsBatteryLevelDrainCutoffConfig = resources.getInteger(
            com.android.internal.R.integer.config_dreamsBatteryLevelDrainCutoff);
    //如果为 true，则直到关闭屏幕并执行屏幕关闭动画之后，才开始 Doze，默认 false
    mDozeAfterScreenOffConfig = resources.getBoolean(
            com.android.internal.R.bool.config_dozeAfterScreenOff);
    //用户活动超时的最小时间，默认10000ms,必须大于0
    mMinimumScreenOffTimeoutConfig = resources.getInteger(
            com.android.internal.R.integer.config_minimumScreenOffTimeout);
    //用户活动超时进入且关闭屏幕前屏幕变暗的最大时间，默认 7000ms，必须大于 0
    mMaximumScreenDimDurationConfig = resources.getInteger(
            com.android.internal.R.integer.config_maximumScreenDimDuration);
    //屏幕变暗的时长比例，如果用于超时时间过短，则在 7000ms 的基础上按还比例减少，默认 20%
    mMaximumScreenDimRatioConfig = resources.getFraction(
            com.android.internal.R.fraction.config_maximumScreenDimRatio, 1, 1);
    //是否支持双击唤醒屏幕
    mSupportsDoubleTapWakeConfig = resources.getBoolean(
            com.android.internal.R.bool.config_supportDoubleTapWake);
}
```

- updateSettingsLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateSettingsLocked() {
    final ContentResolver resolver = mContext.getContentResolver();
    //屏保是否支持
    mDreamsEnabledSetting = (Settings.Secure.getIntForUser(resolver,
            Settings.Secure.SCREENSAVER_ENABLED,
            mDreamsEnabledByDefaultConfig ? 1 : 0,
            UserHandle.USER_CURRENT) != 0);
    //休眠时是否启用屏保
    mDreamsActivateOnSleepSetting = (Settings.Secure.getIntForUser(resolver,
            Settings.Secure.SCREENSAVER_ACTIVATE_ON_SLEEP,
            mDreamsActivatedOnSleepByDefaultConfig ? 1 : 0,
            UserHandle.USER_CURRENT) != 0);
    //插入基座时屏保是否激活
    mDreamsActivateOnDockSetting = (Settings.Secure.getIntForUser(resolver,
            Settings.Secure.SCREENSAVER_ACTIVATE_ON_DOCK,
            mDreamsActivatedOnDockByDefaultConfig ? 1 : 0,
            UserHandle.USER_CURRENT) != 0);
    //设备在一段时间不活动后进入休眠或者屏保状态的时间，15 * 1000ms
    mScreenOffTimeoutSetting = Settings.System.getIntForUser(resolver,
            Settings.System.SCREEN_OFF_TIMEOUT, DEFAULT_SCREEN_OFF_TIMEOUT,
            UserHandle.USER_CURRENT);
    //设备在一段时间不活动后完全进入休眠状态之前的超时时间，
    //该值必须大于 SCREEN_OFF_TIMEOUT，否则设置了屏保后来不及显示屏保就 sleep
    mSleepTimeoutSetting = Settings.Secure.getIntForUser(resolver,
            Settings.Secure.SLEEP_TIMEOUT, DEFAULT_SLEEP_TIMEOUT,
            UserHandle.USER_CURRENT);
    //充电时屏幕一直开启
    mStayOnWhilePluggedInSetting = Settings.Global.getInt(resolver,
            Settings.Global.STAY_ON_WHILE_PLUGGED_IN, BatteryManager.BATTERY_PLUGGED_AC);
    //是否支持剧院模式
    mTheaterModeEnabled = Settings.Global.getInt(mContext.getContentResolver(),
            Settings.Global.THEATER_MODE_ON, 0) == 1;
    //屏幕保持常亮
    mAlwaysOnEnabled = mAmbientDisplayConfiguration.alwaysOnEnabled(UserHandle.USER_CURRENT);

    //双击唤醒屏幕设置
    if (mSupportsDoubleTapWakeConfig) {
        boolean doubleTapWakeEnabled = Settings.Secure.getIntForUser(resolver,
                Settings.Secure.DOUBLE_TAP_TO_WAKE, DEFAULT_DOUBLE_TAP_TO_WAKE,
                        UserHandle.USER_CURRENT) != 0;
        if (doubleTapWakeEnabled != mDoubleTapWakeEnabled) {
            mDoubleTapWakeEnabled = doubleTapWakeEnabled;
            nativeSetFeature(POWER_FEATURE_DOUBLE_TAP_TO_WAKE, mDoubleTapWakeEnabled ? 1 : 0);
        }
    }

    final int oldScreenBrightnessSetting = getCurrentBrightnessSettingLocked();

    mScreenBrightnessForVrSetting = Settings.System.getIntForUser(resolver,
            Settings.System.SCREEN_BRIGHTNESS_FOR_VR, mScreenBrightnessForVrSettingDefault,
            UserHandle.USER_CURRENT);

    mScreenBrightnessSetting = Settings.System.getIntForUser(resolver,
            Settings.System.SCREEN_BRIGHTNESS, mScreenBrightnessSettingDefault,
            UserHandle.USER_CURRENT);

    //屏幕亮度
    if (oldScreenBrightnessSetting != getCurrentBrightnessSettingLocked()) {
        mTemporaryScreenBrightnessSettingOverride = -1;
    }

    final float oldScreenAutoBrightnessAdjustmentSetting =
            mScreenAutoBrightnessAdjustmentSetting;
    mScreenAutoBrightnessAdjustmentSetting = Settings.System.getFloatForUser(resolver,
            Settings.System.SCREEN_AUTO_BRIGHTNESS_ADJ, 0.0f,
            UserHandle.USER_CURRENT);
    if (oldScreenAutoBrightnessAdjustmentSetting != mScreenAutoBrightnessAdjustmentSetting) {
        mTemporaryScreenAutoBrightnessAdjustmentSettingOverride = Float.NaN;
    }

    //亮度调节模式，自动 1，正常 0
    mScreenBrightnessModeSetting = Settings.System.getIntForUser(resolver,
            Settings.System.SCREEN_BRIGHTNESS_MODE,
            Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL, UserHandle.USER_CURRENT);

    //低电量模式是否可用，1 表示 true
    final boolean lowPowerModeEnabled = Settings.Global.getInt(resolver,
            Settings.Global.LOW_POWER_MODE, 0) != 0;
    final boolean autoLowPowerModeConfigured = Settings.Global.getInt(resolver,
            Settings.Global.LOW_POWER_MODE_TRIGGER_LEVEL, 0) != 0;
    if (lowPowerModeEnabled != mLowPowerModeSetting
            || autoLowPowerModeConfigured != mAutoLowPowerModeConfigured) {
        mLowPowerModeSetting = lowPowerModeEnabled;
        mAutoLowPowerModeConfigured = autoLowPowerModeConfigured;
        //更新低电量模式
        updateLowPowerModeLocked();
    }

    //标志位置位
    mDirty |= DIRTY_SETTINGS;
}
```

至此 systemReady() 方法中已经分析完毕，PowerManagerService 的启动过程已经完成，还差一个 updatePowerStateLocked() 方法没有分析，它是 PowerManagerService 的核心方法，我们接着往下看。


## updatePowerStateLocked()

在 systemReady() 方法的最后，调用了 updatePowerStateLocked() 方法，它是整个 PowerManagerService 中的核心方法，也是整个 PowerManagerService 中最重要的一个方法，它用来更新整个电源状态的改变，并进行重新计算。PowerManagerService 中使用一个 int 值 mDirty 作为标志位判断电源状态是否发生变化。当电源状态发生改变时，如亮灭屏、电池状态改变、暗屏等等都会调用该方法，在该方法中调用了其他同级方法进行更新，下面逐个进行分析：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updatePowerStateLocked() {
        if (!mSystemReady || mDirty == 0) {
            return;
        }

        try {
            // Phase 0: Basic state updates.
            //更新电池信息
            updateIsPoweredLocked(mDirty);
            //更新屏幕保持唤醒标识值 mStayOn
            updateStayOnLocked(mDirty);
            //亮度增强相关
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

                //更新统计 wakelock 的标记值 mWakeLockSummary
                updateWakeLockSummaryLocked(dirtyPhase1);
                //更新统计 userActivity 的标记值 mUserActivitySummary 和休眠到达时间
                updateUserActivitySummaryLocked(now, dirtyPhase1);
                //用来更新屏幕唤醒状态，状态改变返回 true
                if (!updateWakefulnessLocked(dirtyPhase1)) {
                    break;
                }
            }

            // Phase 2: Update display power state.
            //和 Display 交互，请求 Display 状态
            boolean displayBecameReady = updateDisplayPowerStateLocked(dirtyPhase2);

            // Phase 3: Update dream state (depends on display ready signal).
            //更新屏保
            updateDreamLocked(dirtyPhase2, displayBecameReady);

            // Phase 4: Send notifications, if needed.
            //如果 wakefulness 改变，做最后的收尾工作
            finishWakefulnessChangeIfNeededLocked();

            // Phase 5: Update suspend blocker.
            // Because we might release the last suspend blocker here, we need to make sure
            // we finished everything else first!
            //更新 Suspend 锁
            updateSuspendBlockerLocked();
        } finally {
            Trace.traceEnd(Trace.TRACE_TAG_POWER);
        }
    }
```

如果没有进行特定场景的分析，这块可能很难理解，在后续的分析中会对特定场景进行分析，这样更能理解方法的使用，如果这里还不太理解，不用太担心。

- updateIsPoweredLocked()

这个方法主要功能有两个：

1. USB 插入亮屏；
2. 更新低电量模式；

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateIsPoweredLocked(int dirty) {
    if ((dirty & DIRTY_BATTERY_STATE) != 0) {
        final boolean wasPowered = mIsPowered;//是否充电
        final int oldPlugType = mPlugType;//充电类型
        final boolean oldLevelLow = mBatteryLevelLow;//是否处于低电量
        //获取充电标志位，充电器类型、电量百分比、低电量标志位
        mIsPowered = mBatteryManagerInternal.isPowered(BatteryManager.BATTERY_PLUGGED_ANY);
        mPlugType = mBatteryManagerInternal.getPlugType();
        mBatteryLevel = mBatteryManagerInternal.getBatteryLevel();
        mBatteryLevelLow = mBatteryManagerInternal.getBatteryLevelLow();

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
                //屏幕唤醒
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
                mAutoLowPowerModeSnoozing = false;
            }
            //发送广播 ACTION_POWER_SAVE_MODE_CHANGED，该广播在系统中多出进行处理，
            //在 SystemUI 中进行处理，如果低电量则给出提示
            updateLowPowerModeLocked();
        }
    }
}
```

因此可以看到，这个方法跟电池有关，只要电池状态发生变化，就能够调用执行到这个方法进行操作。

- wakeUpNoUpdateLocked()

未分析

- userActivityNoUpdateLocked()

上面已经分析过

- updateLowPowerModeLocked()

未分析


- updateStayOnLocked()

这个方法主要用于判断系统是否在 Settings 中设置了充电时保持屏幕亮屏后，根据是否充电来决定是否亮屏。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateStayOnLocked(int dirty) {
    if ((dirty & (DIRTY_BATTERY_STATE | DIRTY_SETTINGS)) != 0) {
        final boolean wasStayOn = mStayOn;
        //充电时亮屏 && DevicePolicyManager 中未设置最大关闭时间
        if (mStayOnWhilePluggedInSetting != 0
                && !isMaximumScreenOffTimeoutFromDeviceAdminEnforcedLocked()) {
            //保持亮屏取决于是否充电
            mStayOn = mBatteryManagerInternal.isPowered(mStayOnWhilePluggedInSetting);
        } else {
            mStayOn = false;
        }

        if (mStayOn != wasStayOn) {
            //如果 mStayOn 值改变 mDirty 置位
            mDirty |= DIRTY_STAY_ON;
        }
    }
}
```

- updateScreenBrightnessBoostLocked()


```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

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

### 第一阶段

- updateWakeLockSummaryLocked()

在这个方法中，会对当前所有的 WakeLock 锁进行统计，过滤所有的 wakelock 锁状态（wakelock 锁机制在后续进行分析），并更新mWakeLockSummary 的值以汇总所有活动的唤醒锁的状态。

mWakeLockSummary 是一个用来记录所有 WakeLock 锁状态的标识值，该值在请求 Display 状时会用到。当系统处于睡眠状态时，大多数唤醒锁都将被忽略，比如系统在处于唤醒状态(awake)时，会忽略 PowerManager.DOZE_WAKE_LOCK 类型的唤醒锁，系统在处于睡眠状态(asleep)或者 Doze 状态时，会忽略 PowerManager.SCREEN_BRIGHT 类型的锁等等。该方法如下：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void updateWakeLockSummaryLocked(int dirty) {
    if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_WAKEFULNESS)) != 0) {
        mWakeLockSummary = 0;
        //numWakeLocks 保存了用户创建的所有 wakelock
        final int numWakeLocks = mWakeLocks.size();
        //遍历所有的 wakelock
        for (int i = 0; i < numWakeLocks; i++) {
            final WakeLock wakeLock = mWakeLocks.get(i);
            switch (wakeLock.mFlags & PowerManager.WAKE_LOCK_LEVEL_MASK) {
                case PowerManager.PARTIAL_WAKE_LOCK:
                    if (!wakeLock.mDisabled) {
                        // We only respect this if the wake lock is not disabled.
                        //如果存在 PARTIAL_WAKE_LOCK 并且该 wakelock 可用，通过置位进行记录
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
        //设备不处于 Doze 状态时，通过置位操作忽略相关类型 wakelock
        //PowerManager.DOZE_WAKE_LOCK 和 WAKE_LOCK_DRAW 锁仅仅在 Doze 状态下有效
        if (mWakefulness != WAKEFULNESS_DOZING) {
            mWakeLockSummary &= ~(WAKE_LOCK_DOZE | WAKE_LOCK_DRAW);
        }
        //如果处于 Doze 状态，忽略三类 Wakelock
        //如果处于睡眠状态，忽略四类 wakelock
        if (mWakefulness == WAKEFULNESS_ASLEEP
                || (mWakeLockSummary & WAKE_LOCK_DOZE) != 0) {
            mWakeLockSummary &= ~(WAKE_LOCK_SCREEN_BRIGHT | WAKE_LOCK_SCREEN_DIM
                    | WAKE_LOCK_BUTTON_BRIGHT);
            if (mWakefulness == WAKEFULNESS_ASLEEP) {
                mWakeLockSummary &= ~WAKE_LOCK_PROXIMITY_SCREEN_OFF;
            }
        }

        // Infer implied wake locks where necessary based on the current state.
        //根据当前状态推断必要的 wakelock
        //比如 WAKEFULNESS_AWAKE 状态肯定是要保持 CPU 运行的，
        //所以需要添加 WAKE_LOCK_CPU 标志位以确保 CPU 处于运行状态
        if ((mWakeLockSummary & (WAKE_LOCK_SCREEN_BRIGHT | WAKE_LOCK_SCREEN_DIM)) != 0) {
            //处于 awake 状态，WAKE_LOCK_STAY_AWAKE 只用于 awake 状态时
            if (mWakefulness == WAKEFULNESS_AWAKE) {
                mWakeLockSummary |= WAKE_LOCK_CPU | WAKE_LOCK_STAY_AWAKE;
            } else if (mWakefulness == WAKEFULNESS_DREAMING) {//处于屏保状态(dream)
                mWakeLockSummary |= WAKE_LOCK_CPU;
            }
        }
        if ((mWakeLockSummary & WAKE_LOCK_DRAW) != 0) {
            mWakeLockSummary |= WAKE_LOCK_CPU;
        }
    }
}
```

- updateUserActivitySummaryLocked()

该方法用来更新用户活动时间，当设备和用户有交互时，都会根据当前时间和休眠时长、Dim 时长、所处状态而计算下次休眠的时间，从而完成用户活动超时时的操作。如：由亮屏进入 Dim 的时长、Dim 到灭屏的时长、亮屏到屏保的时长，就是在这里计算的。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java
    
private void updateUserActivitySummaryLocked(long now, int dirty) {
    // Update the status of the user activity timeout timer.
    if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY
            | DIRTY_WAKEFULNESS | DIRTY_SETTINGS)) != 0) {
        mHandler.removeMessages(MSG_USER_ACTIVITY_TIMEOUT);

        long nextTimeout = 0;
        //如果处于休眠状态，则不会执行该方法
        if (mWakefulness == WAKEFULNESS_AWAKE
                || mWakefulness == WAKEFULNESS_DREAMING
                || mWakefulness == WAKEFULNESS_DOZING) {
            //设备完全进入休眠所需时间，该值为 -1 表示禁用此值，默认 -1
            final int sleepTimeout = getSleepTimeoutLocked();
            //用户超时时间，既经过一段时间不活动进入休眠或屏保的时间
            //特殊情况外，该值为 Settings 中的休眠时长
            final int screenOffTimeout = getScreenOffTimeoutLocked(sleepTimeout);
            //Dim 时长，即亮屏不操作，变暗多久休眠
            final int screenDimDuration = getScreenDimDurationLocked(screenOffTimeout);
            //通过 WindowManager 的用户交互
            final boolean userInactiveOverride = mUserInactiveOverrideFromWindowManager;

            mUserActivitySummary = 0;
            //1.亮屏；2.亮屏后进行用户活动
            if (mLastUserActivityTime >= mLastWakeTime) {
                //下次睡眠时间 = 上次用户活动时间 + 休眠时间 - Dim时间
                nextTimeout = mLastUserActivityTime
                        + screenOffTimeout - screenDimDuration;
                //如果满足当前时间 < 下次屏幕超时时间，说明此时设备为亮屏状态，
                //则将用户活动状态置为表示亮屏的 USER_ACTIVITY_SCREEN_BRIGHT
                if (now < nextTimeout) {
                    mUserActivitySummary = USER_ACTIVITY_SCREEN_BRIGHT;
                } else {//如果当前时间 >下次活动时间，此时应有两种情况：已经休眠和 Dim
                    nextTimeout = mLastUserActivityTime + screenOffTimeout;
                    //如果当前时间 < 上次活动时间+屏幕超时时间，这个值约为 3s，
                    //说明此时设备为 Dim 状态，则将用户活动状态置为表示 Dim 的 USER_ACTIVITY_SCREEN_DIM
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

            //发送定时 Handler，到达时间后再次进行 updatePowerStateLocked()
            if (mUserActivitySummary != 0 && nextTimeout >= 0) {
                Message msg = mHandler.obtainMessage(MSG_USER_ACTIVITY_TIMEOUT);
                msg.setAsynchronous(true);
                mHandler.sendMessageAtTime(msg, nextTimeout);
            }
        } else {
            mUserActivitySummary = 0;
        }
    }
}
```

- updateWakefulnessLocked()

这个方法是退出循环的关键，如果这个方法返回 false，则循环结束，如果返回 true，则进行下一次循环。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java
    
private boolean updateWakefulnessLocked(int dirty) {
    boolean changed = false;
    if ((dirty & (DIRTY_WAKE_LOCKS | DIRTY_USER_ACTIVITY | DIRTY_BOOT_COMPLETED
            | DIRTY_WAKEFULNESS | DIRTY_STAY_ON | DIRTY_PROXIMITY_POSITIVE
            | DIRTY_DOCK_STATE)) != 0) {
        //当前屏幕保持唤醒 && 设备将要退出唤醒状态(睡眠 or 屏保)
        if (mWakefulness == WAKEFULNESS_AWAKE && isItBedTimeYetLocked()) {
            final long time = SystemClock.uptimeMillis();
            //是否在休眠时启用屏保
            if (shouldNapAtBedTimeLocked()) {
                changed = napNoUpdateLocked(time, Process.SYSTEM_UID);
            } else {//进入睡眠，返回 true
                changed = goToSleepNoUpdateLocked(time,
                        PowerManager.GO_TO_SLEEP_REASON_TIMEOUT, 0, Process.SYSTEM_UID);
            }
        }
    }
    return changed;
}
```

- isItBedTimeYetLocked()

该方法判断当前设备是否将要进入睡眠状态，由 mStayOn(是否屏幕常亮)、wakelockSummary、userActivitySummary、mProximityPositive 等决定，只要满足其中之一为 ture，则说明无法进入睡眠，也就说，要满足进入睡眠，相关属性值都为false。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java
    
private boolean isBeingKeptAwakeLocked() {
    return mStayOn//屏幕是否保持常亮
            || mProximityPositive//接近传感器接近屏幕时为 true
            || (mWakeLockSummary & WAKE_LOCK_STAY_AWAKE) != 0//处于awake状态
            || (mUserActivitySummary & (USER_ACTIVITY_SCREEN_BRIGHT
                    | USER_ACTIVITY_SCREEN_DIM)) != 0//屏幕处于亮屏或者dim状态
            || mScreenBrightnessBoostInProgress; //处于亮度增强中
}
```

- shouldNapAtBedTimeLocked()

这个方法用来判断设备是否进入屏保模式：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java
    
 private boolean shouldNapAtBedTimeLocked() {
    return mDreamsActivateOnSleepSetting//屏保是否开启
            || (mDreamsActivateOnDockSetting//插入基座时是否开启屏保
                    && mDockState != Intent.EXTRA_DOCK_STATE_UNDOCKED);
}
```

### 第二阶段

- updateDisplayPowerStateLocked()

该方法用于更新设备显示状态，在这个方法中，会计算出最终需要显示的亮度值和其他值，然后将这些值封装到 DisplayPowerRequest 对象中，向 DisplayMangerService 请求 Display 状态，完成屏幕亮度显示等。


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
            //封装到 DisplayPowerRequest 中
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

            //传给 DisplayManagerService 中处理
            mDisplayReady = mDisplayManagerInternal.requestPowerState(mDisplayPowerRequest,
                    mRequestWaitForNegativeProximity);
            mRequestWaitForNegativeProximity = false;

            if ((dirty & DIRTY_QUIESCENT) != 0) {
                sQuiescent = false;
            }
        }
        return mDisplayReady && !oldDisplayReady;
    }
```

- getDesiredScreenPolicyLocked()

在请求 DisplayManagerService 时，会将所有的信息封装到 DisplayPowerRequest 对象中，其中需要注意 policy 值。policy 作为 DisplayPowerRequset 的属性，有四种值，分别为 off、doze、dim、bright、vr。在向 DisplayManagerService 请求时，会根据当前 PowerManagerService 中的唤醒状态和统计的 wakelock 来决定要请求的 Display 状态，这部分源码如下：


```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private int getDesiredScreenPolicyLocked() {
    if (mIsVrModeEnabled) {
        return DisplayPowerRequest.POLICY_VR;
    }

    if (mWakefulness == WAKEFULNESS_ASLEEP || sQuiescent) {
        return DisplayPowerRequest.POLICY_OFF;
    }

    if (mWakefulness == WAKEFULNESS_DOZING) {
        if ((mWakeLockSummary & WAKE_LOCK_DOZE) != 0) {
            return DisplayPowerRequest.POLICY_DOZE;
        }
        if (mDozeAfterScreenOffConfig) {
            return DisplayPowerRequest.POLICY_OFF;
        }
        // Fall through and preserve the current screen policy if not configured to
        // doze after screen off.  This causes the screen off transition to be skipped.
    }

    if ((mWakeLockSummary & WAKE_LOCK_SCREEN_BRIGHT) != 0
            || (mUserActivitySummary & USER_ACTIVITY_SCREEN_BRIGHT) != 0
            || !mBootCompleted
            || mScreenBrightnessBoostInProgress) {
        return DisplayPowerRequest.POLICY_BRIGHT;
    }

    return DisplayPowerRequest.POLICY_DIM;
}
```

### 第三阶段

- updateDreamLocked()

该方法用来更新设备 Dream 状态，比如是否继续屏保、Doze 或者开始休眠。

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
            //通过 Handler 异步发送一个消息
            scheduleSandmanLocked();
        }
    }
}
```

从这里可以看到，该方法依赖于 mDisplayReady 值，这个值是上个方法在请求 Display 时的返回值，表示 Display 是否准备就绪，因此，只有在准备就绪的情况下才会进一步调用该方法的方法体。在 scheduleSandmanLocked() 方法中，通过 Handler 发送了一个异步消息，代码如下：

- scheduleSandmanLocked()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java
 
private void scheduleSandmanLocked() {
        if (!mSandmanScheduled) {
            //由于是异步处理，因此表示是否已经调用该方法且没有被 handler 处理，
            //如果为 true 就不会进入该方法了
            mSandmanScheduled = true;
            Message msg = mHandler.obtainMessage(MSG_SANDMAN);
            msg.setAsynchronous(true);
            mHandler.sendMessage(msg);
        }
    }
```

再来看看 handleMessage() 中对接受消息的处理：

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private final class PowerManagerHandler extends Handler {
    
    @Override
    public void handleMessage(Message msg) {
        switch (msg.what) {
            //...
            case MSG_SANDMAN:
                handleSandman();
                break;
            //...
        }
    }
}
```

因此，当 updateDreamLocked() 方法调用后，最终会异步执行这个方法，在这个方法中进行屏保相关处理，继续看看这个方法：

- handleSandman()

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void handleSandman() { // runs on handler thread
    //是否开始进入屏保
    final boolean startDreaming;
    final int wakefulness;
    synchronized (mLock) {
        //为 false 后下次 updateDreamLocked() 可处理
        mSandmanScheduled = false;
        wakefulness = mWakefulness;
        //在进入 asleep 状态后该值为 true，用于判断是否处于 Dream 状态
        if (mSandmanSummoned && mDisplayReady) {
            //当前状态能否进入 Dream || 当前 wakefulness 状态为 Doze
            startDreaming = canDreamLocked() || canDozeLocked();
            mSandmanSummoned = false;
        } else {
            startDreaming = false;
        }
    }

    //表示是否正在屏保
    final boolean isDreaming;
    if (mDreamManager != null) {
        //重启屏保
        if (startDreaming) {
            mDreamManager.stopDream(false /*immediate*/);
            mDreamManager.startDream(wakefulness == WAKEFULNESS_DOZING);
        }
        isDreaming = mDreamManager.isDreaming();
    } else {
        isDreaming = false;
    }

    synchronized (mLock) {
        //记录进入屏保时的电池电量
        if (startDreaming && isDreaming) {
            mBatteryLevelWhenDreamStarted = mBatteryLevel;
            if (wakefulness == WAKEFULNESS_DOZING) {
                Slog.i(TAG, "Dozing...");
            } else {
                Slog.i(TAG, "Dreaming...");
            }
        }

        //如果 mSandmanSummoned 改变或者 wakefulness 状态改变，
        //则 return 等待下次处理
        if (mSandmanSummoned || mWakefulness != wakefulness) {
            return; // wait for next cycle
        }

        //决定是否继续 Dream
        if (wakefulness == WAKEFULNESS_DREAMING) {
            if (isDreaming && canDreamLocked()) {
                //表示从开启屏保开始电池电量下降这个值就退出屏保，-1 表示禁用该值
                if (mDreamsBatteryLevelDrainCutoffConfig >= 0
                        && mBatteryLevel < mBatteryLevelWhenDreamStarted
                                - mDreamsBatteryLevelDrainCutoffConfig
                        && !isBeingKeptAwakeLocked()) {                    
                } else {
                    return; // continue dreaming
                }
            }

            //退出屏保，进入 Doze 状态
            if (isItBedTimeYetLocked()) {
                goToSleepNoUpdateLocked(SystemClock.uptimeMillis(),
                        PowerManager.GO_TO_SLEEP_REASON_TIMEOUT, 0, Process.SYSTEM_UID);
                updatePowerStateLocked();
            } else {
                //唤醒设备，reason为android.server.power:DREAM
                wakeUpNoUpdateLocked(SystemClock.uptimeMillis(), "android.server.power:DREAM",
                        Process.SYSTEM_UID, mContext.getOpPackageName(), Process.SYSTEM_UID);
                updatePowerStateLocked();
            }
        //如果处于 Doze 状态，在 power 键灭屏时，首次会将 wakefulness 设置为该值
        } else if (wakefulness == WAKEFULNESS_DOZING) {
            if (isDreaming) {
                return; // continue dozing
            }

            //进入 asleep 状态
            reallyGoToSleepNoUpdateLocked(SystemClock.uptimeMillis(), Process.SYSTEM_UID);
            updatePowerStateLocked();
        }
    }

    //如果正处在 Dream，则只要触发 updatePowerStateLocked()，立即退出 Dream
    if (isDreaming) {
        mDreamManager.stopDream(false /*immediate*/);
    }
}
```

### 第四阶段

- finishWakefulnessChangeIfNeededLocked()

该方法主要做 updateWakefulnessLocked() 方法的结束工作，可以说 updateWakefulnessLocked() 方法中做了屏幕改变的前半部分工作，而这个方法中做后半部分工作。当屏幕状态改变后，才会执行该方法。我们已经分析了，屏幕状态有四种：唤醒状态(awake)、休眠状态(asleep)、屏保状态(dream)、打盹状态(doze)，当前屏幕状态由 wakefulness 表示，当 wakefulness 发生改变，布尔值 mWakefulnessChanging 变为 true。该方法涉及 wakefulness 收尾相关内容，用来处理 wakefulness 改变完成后的工作。

```Java
//frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java

private void finishWakefulnessChangeIfNeededLocked() {
    if (mWakefulnessChanging && mDisplayReady) {
        //如果当前处于 Doze 状态，不进行处理
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
        //通过 Notifier 进行 wakefulness 改变后的处理
        mNotifier.onWakefulnessChangeFinished();
    }
}
```

可以看到，如果当前屏幕状态处于 Doze 模式，则不作处理直接 return。如果是其他模式，则通过调用 Notifier 的方法去处理了，Notifier 好比 PowerManagerService 的一个喇叭，用来发送广播，和其他组件交互等，都是通过 Notifier 进行处理的，这个类也会进行单独的分析。
此外，该方法中的 logScreenOn() 方法将打印出整个亮屏流程的耗时，在平时处理问题时也很有帮助。


### 第五阶段

在分析这个方法前，先来了解下什么是 Suspend 锁。Suspend 锁机制是 Android 电源管理框架中的一种机制，在前面还提到的 wakelock 锁也是，不过 wakelock 锁是上层向 framwork 层申请，而 Suspend 锁是 framework 层中对 wakelock 锁的表现，也就是说，上层应用申请了 wakelock 锁后，在 PowerManagerService 中最终都会表现为 Suspend 锁，通过 Suspend 锁向 Hal 层写入节点，Kernal 层会读取节点，从而进入唤醒或者休眠。

这里涉及到 WakeLock 相关的知识，我们将在下一章节进行介绍。

## 参考资料

- [](http://www.robinheztto.com/2017/06/14/android-power-pms-1/)
- [](https://blog.csdn.net/FightFightFight/article/details/79532191)



