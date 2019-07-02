# 图解 Android 系列（四）原来 SystemServer 启动时干了这么多

## 介绍

这是一个连载的系列「图解 Android 系列」，我将持续为大家提供尽可能通俗易懂的 Android 源码分析。

所有引用的源码片段，我都会在第一行标明源文件完整路径。为了文章篇幅考虑源码中间可能有删减，删减部分会用省略号代替。

> 本系列源码基于：Android Oreo（8.0）

## SystemServer.main()

![SystemServer 创建过程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/03_system_server_01/03.png)

在上篇 [探索 SystemServer 进程创建过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/android/framework/03_system_server_01.md) 中介绍了 SystemServer 进程是从 zygote 进程中 fork 出来的过程，在最后通过反射机制调用到了 SystemServer.main() 方法，我们接下来继续分析 SystemServer 进程后续启动的流程。

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

public static void main(String[] args) {
  // 先初始化 SystemServer 对象，再调用对象的 run() 方法
  new SystemServer().run();
}

private void run() {
  try {
    // ...
    // 检测上次关机过程是否失败，该方法可能不会返回
    performPendingShutdown();

    // 初始化系统上下文
    createSystemContext();

    // 创建系统服务管理
    mSystemServiceManager = new SystemServiceManager(mSystemContext);
    mSystemServiceManager.setRuntimeRestarted(mRuntimeRestart);
    // 将 mSystemServiceManager 添加到本地服务的成员 sLocalServiceObjects
    LocalServices.addService(SystemServiceManager.class, 
                             mSystemServiceManager);
    // Prepare the thread pool for init tasks that can be parallelized
    SystemServerInitThreadPool.get();
  } finally {
    traceEnd();  // InitBeforeStartServices
  }

  // 启动各种系统服务
  try {
    // 启动引导服务
    startBootstrapServices();
    // 启动核心服务
    startCoreServices();
    // 启动其他服务
    startOtherServices();
    SystemServerInitThreadPool.shutdown();
  } catch (Throwable ex) {
    throw ex;
  } finally {
    traceEnd();
  }

  // 用于 debug 版本，将 log 事件不断循环地输出到 dropbox（用于分析）
  if (StrictMode.conditionallyEnableDebugLogging()) {
    Slog.i(TAG, "Enabled StrictMode for system server main thread.");
  }
  // ...
  // 一直循环执行
  Looper.loop();
  throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

可以看到 SystemServer 进程由 Zygote 进程 fork 出来，接着会初始化虚拟机环境，然后创建 SystemServiceManager 大管家，启动系统服务，最后进入 loop 状态。

## performPendingShutdown()

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void performPendingShutdown() {
  // 获取上次的关机信息
  final String shutdownAction = SystemProperties.get(
    ShutdownThread.SHUTDOWN_ACTION_PROPERTY, "");
  if (shutdownAction != null && shutdownAction.length() > 0) {
    // 关机信息第一位表示关机是否是为了重启
    boolean reboot = (shutdownAction.charAt(0) == '1');
    final String reason;
    if (shutdownAction.length() > 1) {
      // 第一位往后表示关机的原因
      reason = shutdownAction.substring(1, shutdownAction.length());
    } else {
      reason = null;
    }

    if (reason != null 
        && reason.startsWith(PowerManager.REBOOT_RECOVERY_UPDATE)) {
      // 关机原因是否是 REBOOT_RECOVERY_UPDATE，
      // 也就是 recovery 模式下，为了执行系统更新而关的机。
      // 这种情况下，一定会多重启一次，多的这一次重启，
      // 原因就不是 REBOOT_RECOVERY_UPDATE 了。
      File packageFile = new File(UNCRYPT_PACKAGE_FILE);
      if (packageFile.exists()) {
        String filename = null;
        try {
          // 读取 uncrypt_file 的内容，获取的是一个文件名
          filename = FileUtils.readTextFile(packageFile, 0, null);
        } catch (IOException e) {
          Slog.e(TAG, "Error reading uncrypt package file", e);
        }
        // 如果读出来的文件名以 /data 开头，也就是在 data 目录内
        if (filename != null && filename.startsWith("/data")) {
          // 如果 block.map 文件不存在，直接抛异常，重启失败
          if (!new File(BLOCK_MAP_FILE).exists()) {
            return;
          }
        }
      }
    }
    // 当 "sys.shutdown.requested" 值不为空，则会重启或者关机
    ShutdownThread.rebootOrShutdown(null, reboot, reason);
  }
}
```

这个方法主要是针对 recovery 模式下系统更新引起的重启，这种情况要多重启一次。

## createSystemContext()

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void createSystemContext() {
  // 创建 system_server 进程的上下文信息
  ActivityThread activityThread = ActivityThread.systemMain();
  mSystemContext = activityThread.getSystemContext();
  mSystemContext.setTheme(DEFAULT_SYSTEM_THEME);
	// 设置主题
  final Context systemUiContext = activityThread.getSystemUiContext();
  systemUiContext.setTheme(DEFAULT_SYSTEM_THEME);
}
```

该方法主要是创建系统进程上下文，具体细节暂不深入分析，先走完主流程，后面单独详细分析。

## LocalServices

```java
//frameworks/base/core/java/com/android/server/LocalServices.java

public final class LocalServices {
  private LocalServices() {}

  private static final ArrayMap<Class<?>, Object> sLocalServiceObjects =
    new ArrayMap<Class<?>, Object>();

  @SuppressWarnings("unchecked")
  public static <T> T getService(Class<T> type) {
    synchronized (sLocalServiceObjects) {
      return (T) sLocalServiceObjects.get(type);
    }
  }

  public static <T> void addService(Class<T> type, T service) {
    synchronized (sLocalServiceObjects) {
      if (sLocalServiceObjects.containsKey(type)) {
        throw new IllegalStateException("Overriding service registration");
      }
      sLocalServiceObjects.put(type, service);
    }
  }

  @VisibleForTesting
  public static <T> void removeServiceForTest(Class<T> type) {
    synchronized (sLocalServiceObjects) {
      sLocalServiceObjects.remove(type);
    }
  }
}
```

可以看到 LocalServices 就是一个 静态的 ArrayMap。

## startBootstrapServices()

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startBootstrapServices() {
  final String TAG_SYSTEM_CONFIG = "ReadingSystemConfig";
  SystemServerInitThreadPool.get().submit(SystemConfig::getInstance,
                                          TAG_SYSTEM_CONFIG);
  // 阻塞等待与 installd 建立 socket 通道
  Installer installer = 
    mSystemServiceManager.startService(Installer.class);

  mSystemServiceManager.startService(DeviceIdentifiersPolicyService
                                     .class);
  // 启动服务 ActivityManagerService
  mActivityManagerService = mSystemServiceManager.startService(
    ActivityManagerService.Lifecycle.class).getService();
  mActivityManagerService.setSystemServiceManager(
    mSystemServiceManager);
  mActivityManagerService.setInstaller(installer);

  // 启动服务 PowerManagerService
  mPowerManagerService = mSystemServiceManager.startService(
    PowerManagerService.class);

  // 初始化 power management
  mActivityManagerService.initPowerManagement();

  // Bring up recovery system in case a rescue party needs a reboot
  if (!SystemProperties.getBoolean("config.disable_noncore", false)) {
    mSystemServiceManager.startService(RecoverySystemService.class);
  }

  RescueParty.noteBoot(mSystemContext);

  // 启动服务 LightsService
  mSystemServiceManager.startService(LightsService.class);

  // 启动服务 DisplayManagerService
  mDisplayManagerService = mSystemServiceManager.startService(DisplayManagerService.class);

  // Phase 100: 在初始化 package manager 之前，需要默认的显示
  mSystemServiceManager.startBootPhase(
    SystemService.PHASE_WAIT_FOR_DEFAULT_DISPLAY);

  // 当设备正在加密时，仅运行核心
  String cryptState = SystemProperties.get("vold.decrypt");
  if (ENCRYPTING_STATE.equals(cryptState)) {
  } else if (ENCRYPTED_STATE.equals(cryptState)) {
    mOnlyCore = true;
  }

  // 启动服务 PackageManagerService
  if (!mRuntimeRestart) {
    MetricsLogger.histogram(null, "boot_package_manager_init_start",
                            (int) SystemClock.elapsedRealtime());
  }
  mPackageManagerService = PackageManagerService.main(mSystemContext,
           installer, mFactoryTestMode != FactoryTest.FACTORY_TEST_OFF, 
                                                      mOnlyCore);
  mFirstBoot = mPackageManagerService.isFirstBoot();
  mPackageManager = mSystemContext.getPackageManager();
  if (!mRuntimeRestart && !isFirstBootOrUpgrade()) {
    MetricsLogger.histogram(null, "boot_package_manager_init_ready",
                            (int) SystemClock.elapsedRealtime());
  }
 
  if (!mOnlyCore) {
    boolean disableOtaDexopt = SystemProperties
      .getBoolean("config.disable_otadexopt", false);
    if (!disableOtaDexopt) {
      OtaDexoptService.main(mSystemContext, mPackageManagerService);
    }
  }

  // 启动服务 UserManagerService，新建目录 /data/user/
  mSystemServiceManager.startService(UserManagerService
                                     .LifeCycle.class);

  AttributeCache.init(mSystemContext);

  // 设置 ActivityManagerService
  mActivityManagerService.setSystemProcess();

  mDisplayManagerService.setupSchedulerPolicies();

  // Manages Overlay packages
  mSystemServiceManager.startService(
    new OverlayManagerService(mSystemContext, installer));

  // 启动传感器服务
  mSensorServiceStart = SystemServerInitThreadPool.get().submit(() -> {
    BootTimingsTraceLog traceLog = new BootTimingsTraceLog(
      SYSTEM_SERVER_TIMING_ASYNC_TAG, Trace.TRACE_TAG_SYSTEM_SERVER);
    startSensorService();
  }, START_SENSOR_SERVICE);
}
```

可以看到该方法创建了 ActivityManagerService、PowerManagerService、LightsService、DisplayManagerService、PackageManagerService、UserManagerService、SensorService 这些服务。

## startCoreServices()

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startCoreServices() {
  // 启动服务 DropBoxManagerService，用于记录错误日志
  mSystemServiceManager.startService(DropBoxManagerService.class);

  // 启动服务 BatteryService，用于统计电池电量，需要 LightService.
  mSystemServiceManager.startService(BatteryService.class);

  // 启动服务 UsageStatsService，用于统计应用使用情况
  mSystemServiceManager.startService(UsageStatsService.class);
  mActivityManagerService.setUsageStatsManager(
    LocalServices.getService(UsageStatsManagerInternal.class));

  // 启动服务 WebViewUpdateService
  mWebViewUpdateService = mSystemServiceManager
    .startService(WebViewUpdateService.class);
}
```

可以看到该方法创建了 DropBoxManagerService、BatteryService、UsageStatsService、WebViewUpdateService 这些服务。

## startOtherServices()

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startOtherServices() {
  final Context context = mSystemContext;
  // ...
  try {
    // ... 
    telephonyRegistry = new TelephonyRegistry(context);
    ServiceManager.addService("telephony.registry", telephonyRegistry);
    // ...
    mContentResolver = context.getContentResolver();

    if (!disableCameraService) {
      mSystemServiceManager.startService(CameraServiceProxy.class);
    }
    // ...
    // 启动服务 InputManagerService
    mSystemServiceManager.startService(AlarmManagerService.class);
		// 启动 Watchdog
    final Watchdog watchdog = Watchdog.getInstance();
    watchdog.init(context, mActivityManagerService);
    // 创建服务 InputManagerService
    inputManager = new InputManagerService(context);

    // WMS needs sensor service ready
    ConcurrentUtils.waitForFutureNoInterrupt(mSensorServiceStart, 
                                             START_SENSOR_SERVICE);
    mSensorServiceStart = null;
    // 启动服务 WindowManagerService
    wm = WindowManagerService.main(context, inputManager,
             mFactoryTestMode != FactoryTest.FACTORY_TEST_LOW_LEVEL,
             !mFirstBoot, mOnlyCore, new PhoneWindowManager());
    ServiceManager.addService(Context.WINDOW_SERVICE, wm);
    ServiceManager.addService(Context.INPUT_SERVICE, inputManager);
    // ...
    mActivityManagerService.setWindowManager(wm);
    // 启动服务 InputManagerService
    inputManager.setWindowManagerCallbacks(wm.getInputMonitor());
    inputManager.start();

    mDisplayManagerService.windowManagerAndInputReady();

    if (isEmulator) {
      // ...
    } else { // 非模拟器，启动服务 BluetoothService
      mSystemServiceManager.startService(BluetoothService.class);
    }
    // ...
  } catch (RuntimeException e) {
  }
  // ...
  // Bring up services needed for UI.
  if (mFactoryTestMode != FactoryTest.FACTORY_TEST_LOW_LEVEL) {
    mSystemServiceManager.startService(InputMethodManagerService
                                       .Lifecycle.class);
    ServiceManager.addService(Context.ACCESSIBILITY_SERVICE,
                              new AccessibilityManagerService(context));
  }
  wm.displayReady();
  // ...
  if (mFactoryTestMode != FactoryTest.FACTORY_TEST_LOW_LEVEL) {
    // ...
    if (!disableSystemUI) {
      // 创建服务 StatusBarManagerService
      statusBar = new StatusBarManagerService(context, wm);
      ServiceManager.addService(Context.STATUS_BAR_SERVICE,
                                  statusBar);
    }
    // 启动服务 JobSchedulerService
    mSystemServiceManager.startService(JobSchedulerService.class);
    // ...
    if (!disableNonCoreServices) {
      // 启动服务 DreamManagerService
      mSystemServiceManager.startService(DreamManagerService.class);
    }
    // ...
    mSystemServiceManager.startService(LauncherAppsService.class);
  }
  // ...
  // phase 480
  mSystemServiceManager.startBootPhase(SystemService
                                       .PHASE_LOCK_SETTINGS_READY);
  // phase 500
  mSystemServiceManager.startBootPhase(SystemService
                                       .PHASE_SYSTEM_SERVICES_READY);

  // 准备好 window、power、package、display 服务
  wm.systemReady();
  // ...
  mPowerManagerService.systemReady(mActivityManagerService
                                     .getAppOpsService());
  mPackageManagerService.systemReady();
  mDisplayManagerService.systemReady(safeMode, mOnlyCore);
  // ...
  mActivityManagerService.systemReady(() -> {
    // phase 550
    mSystemServiceManager.startBootPhase(SystemService
                                         .PHASE_ACTIVITY_MANAGER_READY);
    // ...
    // phase 600
    mSystemServiceManager.startBootPhase(
                    SystemService.PHASE_THIRD_PARTY_APPS_CAN_START);
  }, BOOT_TIMINGS_TRACE_LOG);
}
```

SystemServer 启动各种服务中最后的一个环节便是 AMS.systemReady()。

到此，System_server 主线程的启动工作总算完成，进入 Looper.loop() 状态，等待其他线程通过 handler 发送消息到主线再处理。

## 服务启动阶段

![SystemServer 启动过程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/04_system_server_02/01.jpg)

```java
//frameworks/base/services/core/java/com/android/server/SystemService.java

public static final int PHASE_WAIT_FOR_DEFAULT_DISPLAY = 100;
public static final int PHASE_LOCK_SETTINGS_READY = 480;
public static final int PHASE_SYSTEM_SERVICES_READY = 500;
public static final int PHASE_ACTIVITY_MANAGER_READY = 550;
public static final int PHASE_THIRD_PARTY_APPS_CAN_START = 600;
public static final int PHASE_BOOT_COMPLETED = 1000;
```

在 `startBootstrapServices()` 方法中创建了四大引导服务：

- ActivityManagerService
- PowerManagerService
- LightsService
- DisplayManagerService

接着进入阶段 `PHASE_WAIT_FOR_DEFAULT_DISPLAY = 100` 回调服务。

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startBootstrapServices() {
  // ...
  // 启动服务 ActivityManagerService
  mActivityManagerService = mSystemServiceManager.startService(
    ActivityManagerService.Lifecycle.class).getService();
  // ...
  // 启动服务 PowerManagerService
  mPowerManagerService = mSystemServiceManager.startService(
    PowerManagerService.class);
  // ...
  // 启动服务 LightsService
  mSystemServiceManager.startService(LightsService.class);
  
  // 启动服务 DisplayManagerService
  mDisplayManagerService = mSystemServiceManager.startService(DisplayManagerService.class);

  // Phase 100: 在初始化 package manager 之前，需要默认的显示
  mSystemServiceManager.startBootPhase(
    SystemService.PHASE_WAIT_FOR_DEFAULT_DISPLAY);
  // ...
}
```

### Phase 100

```java
//frameworks/base/services/core/java/com/android/server/SystemServiceManager.java

public void startBootPhase(final int phase) {
  if (phase <= mCurrentPhase) {
    throw new IllegalArgumentException("Next phase must be larger than previous");
  }
  mCurrentPhase = phase;

  try {
    final int serviceLen = mServices.size();
    for (int i = 0; i < serviceLen; i++) {
      final SystemService service = mServices.get(i);
      // ...
      try {
        service.onBootPhase(mCurrentPhase);
      } catch (Exception ex) {
        // ...
      }
    }
  } finally {
		// ...
  }
}
```

可以看到这里遍历了一下服务列表，然后回调到各服务的 `onBootPhase()` 方法中了。这里不再继续分析，等详细分析具体服务时再详细分析。

然后继续创建服务：

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startBootstrapServices() {
  // ...
  // Phase 100: 在初始化 package manager 之前，需要默认的显示
  mSystemServiceManager.startBootPhase(
    SystemService.PHASE_WAIT_FOR_DEFAULT_DISPLAY);
  // ...
  // 启动服务 PackageManagerService
  mPackageManagerService = PackageManagerService.main(mSystemContext,
           installer, mFactoryTestMode != FactoryTest.FACTORY_TEST_OFF, 
                                                      mOnlyCore);
 	// ...
  // 启动服务 UserManagerService，新建目录 /data/user/
  mSystemServiceManager.startService(UserManagerService
                                     .LifeCycle.class);
  // 设置 ActivityManagerService
  mActivityManagerService.setSystemProcess();
  // ...
  // Manages Overlay packages
  mSystemServiceManager.startService(
    new OverlayManagerService(mSystemContext, installer));
  // 启动传感器服务
  mSensorServiceStart = SystemServerInitThreadPool.get().submit(() -> {
    BootTimingsTraceLog traceLog = new BootTimingsTraceLog(
      SYSTEM_SERVER_TIMING_ASYNC_TAG, Trace.TRACE_TAG_SYSTEM_SERVER);
    startSensorService();
  }, START_SENSOR_SERVICE);
}
```

继续执行到 `startOtherServices()` 方法中创建服务：

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startOtherServices() {
  try {
    // ...
    // 启动服务 InputManagerService
    mSystemServiceManager.startService(AlarmManagerService.class);
		// 启动 Watchdog
    final Watchdog watchdog = Watchdog.getInstance();
    watchdog.init(context, mActivityManagerService);
    // 创建服务 InputManagerService
    inputManager = new InputManagerService(context);
    // 启动服务 WindowManagerService
    wm = WindowManagerService.main(context, inputManager,
             mFactoryTestMode != FactoryTest.FACTORY_TEST_LOW_LEVEL,
             !mFirstBoot, mOnlyCore, new PhoneWindowManager());
    // ...
    mActivityManagerService.setWindowManager(wm);
    // 启动服务 InputManagerService
    inputManager.setWindowManagerCallbacks(wm.getInputMonitor());
    inputManager.start();

    mDisplayManagerService.windowManagerAndInputReady();
    // ...
  } catch (RuntimeException e) {
  }
  wm.displayReady();
  // ...
  if (mFactoryTestMode != FactoryTest.FACTORY_TEST_LOW_LEVEL) {
    // ...
    if (!disableSystemUI) {
      // 创建服务 StatusBarManagerService
      statusBar = new StatusBarManagerService(context, wm);
      ServiceManager.addService(Context.STATUS_BAR_SERVICE,
                                  statusBar);
    }
    // 启动服务 JobSchedulerService
    mSystemServiceManager.startService(JobSchedulerService.class);
    // ...
    if (!disableNonCoreServices) {
      // 启动服务 DreamManagerService
      mSystemServiceManager.startService(DreamManagerService.class);
    }
    // ...
    mSystemServiceManager.startService(LauncherAppsService.class);
  }
  // ...
  // phase 480
  mSystemServiceManager.startBootPhase(SystemService
                                       .PHASE_LOCK_SETTINGS_READY);
  // ...
}
```

###  Phase 480

进入 480 阶段后马上进入了 500 阶段。

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startOtherServices() {
  // ...
  // phase 480
  mSystemServiceManager.startBootPhase(SystemService
                                       .PHASE_LOCK_SETTINGS_READY);
  // phase 500
  mSystemServiceManager.startBootPhase(SystemService
                                       .PHASE_SYSTEM_SERVICES_READY);
  // ...
}
```

### Phase 500

进入此启动阶段后，服务可以安全地调用核心系统服务了，如 PowerManage r或 PackageManager。

各大服务执行 systemReady()：

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

private void startOtherServices() {
  // ...
  // phase 500
  mSystemServiceManager.startBootPhase(SystemService
                                       .PHASE_SYSTEM_SERVICES_READY);

  // 准备好 window、power、package、display 服务
  wm.systemReady();
  // ...
  mPowerManagerService.systemReady(mActivityManagerService
                                     .getAppOpsService());
  mPackageManagerService.systemReady();
  mDisplayManagerService.systemReady(safeMode, mOnlyCore);
  // ...
  mActivityManagerService.systemReady(() -> {
    // phase 550
    mSystemServiceManager.startBootPhase(SystemService
                                         .PHASE_ACTIVITY_MANAGER_READY);
    // ...
    // phase 600
    mSystemServiceManager.startBootPhase(
                    SystemService.PHASE_THIRD_PARTY_APPS_CAN_START);
  }, BOOT_TIMINGS_TRACE_LOG);
}
```

最后是 `AMS.systemReady()` 方法。

### Phase 550

进入此启动阶段后，服务可以发送广播 Intents 了，但是 system_server 主线程并没有就绪。

### Phase 600

进入此启动阶段后，服务可以启动/绑定到第三方应用程序。 此时，应用程序可以使用 Binder 服务了。

### Phase 1000

在经过一系列流程，再调用 `AMS.finishBooting()` 时，则进入 `Phase 1000` 阶段。

到此，系统服务启动阶段完成就绪，system_server 进程启动完成则进入 `Looper.loop()` 状态，随时待命，等待消息队列 MessageQueue 中的消息到来，则马上进入执行状态。

`systemReady()` 函数调用完成之后，桌面就可见了，用户就真正见到了 Android 系统的可操作界面。

## 参考资料

- [Android系统启动-SystemServer下篇](http://gityuan.com/2016/02/20/android-system-server-2/)
- [Android进程系列第四篇---SystemServer进程的启动流程](https://www.jianshu.com/p/99e0b480666a?utm_source=oschina-app)
- [ActivityManagerService的启动过程](https://duanqz.github.io/2016-07-15-AMS-LaunchProcess)