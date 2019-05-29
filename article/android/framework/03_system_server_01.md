# 图解 Android 系列（三）探索 SystemServer 进程创建过程

## 介绍

这是一个连载的系列「图解 Android 系列」，我将持续为大家提供尽可能通俗易懂的 Android 源码分析。

所有引用的源码片段，我都会在第一行标明源文件完整路径。为了文章篇幅考虑源码中间可能有删减，删减部分会用省略号代替。

> 本系列源码基于：Android Oreo（8.0）

## SystemServer 进程

SystemServer 进程是由 zygote 进程 fork 出来的，进程名为 `system_server`，该进程承载着 Framework 的核心服务。

![SystemServer 启动](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/03_system_server_01/01.png)

在上篇 [深入理解 init 与 zygote 进程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/android/framework/02_init_zygote.md) 中介绍到 zygote 进程在启动过程中会调用到 `startSystemServer()` 方法，可得知该方法是 SystemServer 进程启动的起点，下面我们接着来分析 SystemServer 的启动流程。

## ZygoteInit.java

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

public static void main(String argv[]) {
  // ...
  try {
    // ...
    boolean startSystemServer = false;
    // ...
    for (int i = 1; i < argv.length; i++) {
      if ("start-system-server".equals(argv[i])) {
        startSystemServer = true;
      }
      // ...
    }
    // ...
    if (startSystemServer) { // 启动 system_server
      startSystemServer(abiList, socketName, zygoteServer);
    }

    // 进入循环模式
    zygoteServer.runSelectLoop(abiList);

    zygoteServer.closeServerSocket();
  } catch (Zygote.MethodAndArgsCaller caller) {
    caller.run();
  } catch (Throwable ex) {
    // ...
  }
}
```

可以看到这里调用了 `startSystemServer()` 方法来启动 SystemServer 进程。

## startSystemServer()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

private static boolean startSystemServer(String abiList, String socketName, ZygoteServer zygoteServer)
    throws Zygote.MethodAndArgsCaller, RuntimeException {
  long capabilities = posixCapabilitiesAsBits(
    OsConstants.CAP_IPC_LOCK,
    OsConstants.CAP_KILL,
    OsConstants.CAP_NET_ADMIN,
    OsConstants.CAP_NET_BIND_SERVICE,
    OsConstants.CAP_NET_BROADCAST,
    OsConstants.CAP_NET_RAW,
    OsConstants.CAP_SYS_MODULE,
    OsConstants.CAP_SYS_NICE,
    OsConstants.CAP_SYS_PTRACE,
    OsConstants.CAP_SYS_TIME,
    OsConstants.CAP_SYS_TTY_CONFIG,
    OsConstants.CAP_WAKE_ALARM
  );
  /* Containers run without this capability, so avoid setting it in that case */
  if (!SystemProperties.getBoolean(PROPERTY_RUNNING_IN_CONTAINER, 
                                   false)) {
    capabilities |= 
      posixCapabilitiesAsBits(OsConstants.CAP_BLOCK_SUSPEND);
  }
  /* Hardcoded command line to start the system server */
  // 准备参数
  String args[] = {
    "--setuid=1000",
    "--setgid=1000",
    "--setgroups=1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1018,1021,1023,1032,3001,3002,3003,3006,3007,3009,3010",
    "--capabilities=" + capabilities + "," + capabilities,
    "--nice-name=system_server",
    "--runtime-args",
    "com.android.server.SystemServer",
  };
  ZygoteConnection.Arguments parsedArgs = null;

  int pid;

  try {
    // 用于解析参数，生成目标格式
    parsedArgs = new ZygoteConnection.Arguments(args);
    ZygoteConnection.applyDebuggerSystemProperty(parsedArgs);
    ZygoteConnection.applyInvokeWithSystemProperty(parsedArgs);

    /* Request to fork the system server process */
    // fork 子进程，用于运行 system_server，下面分析
    pid = Zygote.forkSystemServer(
      parsedArgs.uid, parsedArgs.gid,
      parsedArgs.gids,
      parsedArgs.debugFlags,
      null,
      parsedArgs.permittedCapabilities,
      parsedArgs.effectiveCapabilities);
  } catch (IllegalArgumentException ex) {
    throw new RuntimeException(ex);
  }

  /* For child process */
  // 进入子进程 system_server
  if (pid == 0) { // pid==0 意味着子进程创建成功
    if (hasSecondZygote(abiList)) {
      waitForSecondaryZygote(socketName);
    }

    zygoteServer.closeServerSocket();
    // 完成 system_server 进程剩余的工作，下面分析
    handleSystemServerProcess(parsedArgs);
  }

  return true;
}
```

`startSystemServer()` 方法主要是准备参数并 fork 新进程，从上面可以看出 SystemServer 进程参数信息为 uid=1000，gid=1000，进程名为 sytem_server，从 zygote 进程 fork 新进程后，需要关闭 zygote 原有的 socket。另外，对于有两个 zygote 进程情况，需等待第 2 个 zygote 创建完成。

### forkSystemServer()

```java
//frameworks/base/core/java/com/android/internal/os/Zygote.java

public static int forkSystemServer(int uid, int gid, int[] gids, 
        int debugFlags, int[][] rlimits, long permittedCapabilities, 
        long effectiveCapabilities) {
  
  VM_HOOKS.preFork();
  // Resets nice priority for zygote process.
  resetNicePriority();
  // 调用 native 方法 fork system_server 进程，下面分析
  int pid = nativeForkSystemServer(uid, gid, gids, debugFlags, 
          rlimits, permittedCapabilities, effectiveCapabilities);
  // Enable tracing as soon as we enter the system_server.
  if (pid == 0) {
    Trace.setTracingEnabled(true);
  }
  VM_HOOKS.postForkCommon();
  return pid;
}

native private static int nativeForkSystemServer(int uid, int gid, 
        int[] gids, int debugFlags,int[][] rlimits, 
        long permittedCapabilities, long effectiveCapabilities);
```

nativeForkSystemServer() 是一个 JNI 方法在 AndroidRuntime.cpp 中注册的，调用com_android_internal_os_Zygote.cpp 中的 register_com_android_internal_os_Zygote() 方法建立 native 方法的映射关系。

### nativeForkSystemServer()

```C++
//frameworks/base/core/jni/com_android_internal_os_Zygote.cpp

static jint com_android_internal_os_Zygote_nativeForkSystemServer(
        JNIEnv* env, jclass, uid_t uid, gid_t gid, jintArray gids,
        jint debug_flags, jobjectArray rlimits, 
        jlong permittedCapabilities, jlong effectiveCapabilities) {
  // fork 子进程，下面分析
  pid_t pid = ForkAndSpecializeCommon(env, uid, gid, gids,
          debug_flags, rlimits, permittedCapabilities, 
          effectiveCapabilities, MOUNT_EXTERNAL_DEFAULT, NULL, 
          NULL, true, NULL, NULL, NULL, NULL);
  if (pid > 0) {
      // zygote 进程，检测 system_server 进程是否创建
      gSystemServerPid = pid;
      int status;
      if (waitpid(pid, &status, WNOHANG) == pid) {
          // 当 system_server 进程死亡后，重启 zygote 进程
          RuntimeAbort(env, __LINE__, 
                 "System server process has died. Restarting Zygote!");
      }
  }
  return pid;
}
```

当 system_server 进程创建失败时，将会重启 zygote 进程。这里需要注意，对于 Android 5.0 以上系统，有两个 zygote 进程，分别是 zygote、zygote64 两个进程，system_server 的父进程，一般来说 64 位系统其父进程是 zygote64 进程。

- 当 kill system_server 进程后，只重启 zygote64 和 system_server，不重启 zygote;
- 当 kill zygote64 进程后，只重启 zygote64 和 system_server，也不重启 zygote；
- 当 kill zygote 进程，则重启 zygote、zygote64 以及 system_server。

### ForkAndSpecializeCommon()

```c++
//frameworks/base/core/jni/com_android_internal_os_Zygote.cpp

static pid_t ForkAndSpecializeCommon(JNIEnv *env, uid_t uid, gid_t gid, 
        jintArray javaGids, jint debug_flags, jobjectArray javaRlimits,                  
        jlong permittedCapabilities, jlong effectiveCapabilities,
        jint mount_external, jstring java_se_info, jstring java_se_name,
        bool is_system_server, jintArray fdsToClose,
        jintArray fdsToIgnore, jstring instructionSet, jstring dataDir) {
  SetSigChldHandler(); // 设置子进程的 signal 信号处理函数
  // ...
  pid_t pid = fork(); // fork 子进程
  if (pid == 0) { // 进入子进程
    // The child process.
    gMallocLeakZygoteChild = 1;

    // Set the jemalloc decay time to 1.
    mallopt(M_DECAY_TIME, 1);

    // 关闭并清除文件描述符
    DetachDescriptors(env, fdsToClose);
    // ...
    if (!is_system_server) {
      // 对于非 system_server 子进程，则创建进程组
      int rc = createProcessGroup(uid, getpid());
      // ...
    }

    SetGids(env, javaGids); // 设置设置 group
    SetRLimits(env, javaRlimits); // 设置资源 limit

    if (use_native_bridge) {
      ScopedUtfChars isa_string(env, instructionSet);
      ScopedUtfChars data_dir(env, dataDir);
      android::PreInitializeNativeBridge(data_dir.c_str(), 
                                         isa_string.c_str());
    }

    int rc = setresgid(gid, gid, gid);
    // ...
    rc = setresuid(uid, uid, uid);
    // ...
    SetCapabilities(env, permittedCapabilities, 
                    effectiveCapabilities, permittedCapabilities);
    SetSchedulerPolicy(env); // 设置调度策略

    // ...
    // 创建 selinux 上下文
    rc = selinux_android_setcontext(uid, is_system_server, 
                                    se_info_c_str, se_name_c_str);
    // ...
    if (se_info_c_str == NULL && is_system_server) {
      se_name_c_str = "system_server";
    }
    if (se_info_c_str != NULL) {
      // 设置线程名为 system_server，方便调试
      SetThreadName(se_name_c_str);
    }

    delete se_info;
    delete se_name;

    // 设置子进程的 signal 信号处理函数为默认函数
    UnsetSigChldHandler();
    // 等价于调用 zygote.callPostForkChildHooks()
    env->CallStaticVoidMethod(gZygoteClass, gCallPostForkChildHooks,
                              debug_flags, is_system_server, 
                              instructionSet);
  } else if (pid > 0) {
    // 进入父进程，即 zygote 进程
    // ...
  }
  return pid;
}
```

fork() 创建新进程，采用 copy on write 方式，这是 Linux 创建进程的标准方法，会有两次 return，对于 pid==0 为子进程的返回，对于 pid>0 为父进程的返回。 

到此 system_server 进程已完成了创建的所有工作，接下来开始了system_server 进程的真正工作。在前面 startSystemServer() 方法中，zygote 进程执行完 forkSystemServer() 后，新创建出来的system_server 进程便进入 handleSystemServerProcess() 方法。

## handleSystemServerProcess()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

private static void handleSystemServerProcess(
            ZygoteConnection.Arguments parsedArgs)
            throws Zygote.MethodAndArgsCaller {

  Os.umask(S_IRWXG | S_IRWXO);

  if (parsedArgs.niceName != null) {
    // 设置当前进程名为 system_server
    Process.setArgV0(parsedArgs.niceName);
  }

  final String systemServerClasspath = 
    Os.getenv("SYSTEMSERVERCLASSPATH");
  if (systemServerClasspath != null) {
    // 执行 dex 优化操作
    performSystemServerDexOpt(systemServerClasspath);
    // ...
  }

  // 此处为空，走 else 分支
  if (parsedArgs.invokeWith != null) {
    String[] args = parsedArgs.remainingArgs;
    
    if (systemServerClasspath != null) {
      String[] amendedArgs = new String[args.length + 2];
      amendedArgs[0] = "-cp";
      amendedArgs[1] = systemServerClasspath;
      System.arraycopy(args, 0, amendedArgs, 2, args.length);
      args = amendedArgs;
    }
    // 启动应用进程
    WrapperInit.execApplication(parsedArgs.invokeWith,
           parsedArgs.niceName, parsedArgs.targetSdkVersion,
           VMRuntime.getCurrentInstructionSet(), null, args);
  } else {
    ClassLoader cl = null;
    if (systemServerClasspath != null) {
      cl = createPathClassLoader(systemServerClasspath, 
                                 parsedArgs.targetSdkVersion);
      // 创建类加载器，并赋予当前线程
      Thread.currentThread().setContextClassLoader(cl);
    }

    // system_server 进入此分支
    ZygoteInit.zygoteInit(parsedArgs.targetSdkVersion, 
                          parsedArgs.remainingArgs, cl);
  }

  /* should never reach here */
}
```

到这里 `SystemServer` 进程已经创建完了，SystemServer 进程是 Zygote 进程 fork 出来的第一个进程。Zygote 进程和 SystemServer 进程是 Java 世界的基础，任何一个进程死亡都会导致 Java 世界的奔溃。所以如果子进程 SystemServer 挂了，Zygote 进程就会自杀，导致 Zygote 进程会重启。

![SystemServer fork 过程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/03_system_server_01/02.png)

## zygoteInit()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

public static final void zygoteInit(int targetSdkVersion, String[] argv,
            ClassLoader classLoader) throws Zygote.MethodAndArgsCaller {
  
  RuntimeInit.redirectLogStreams(); // 重定向 log 输出
  RuntimeInit.commonInit(); // 通用的一些初始化
  ZygoteInit.nativeZygoteInit(); // zygote 初始化
  // 应用初始化
  RuntimeInit.applicationInit(targetSdkVersion, argv, classLoader);
}
```

SystemServer 进程创建完成后会调用 ZygoteInit.zygoteInit() 进行初始化。

### commonInit()

```java
//frameworks/base/core/java/com/android/internal/os/RuntimeInit.java

protected static final void commonInit() {
  // 设置默认的未捕捉异常处理方法
  Thread.setUncaughtExceptionPreHandler(new LoggingHandler());
  Thread.setDefaultUncaughtExceptionHandler(new KillApplicationHandler());

  // 设置市区，中国时区为"Asia/Shanghai"
  TimezoneGetter.setInstance(new TimezoneGetter() {
    @Override
    public String getId() {
      return SystemProperties.get("persist.sys.timezone");
    }
  });
  TimeZone.setDefault(null);

  // 重置 log 配置
  LogManager.getLogManager().reset();
  new AndroidConfig();

  // 设置默认的 HTTP User-agent 格式，用于 HttpURLConnection
  String userAgent = getDefaultUserAgent();
  System.setProperty("http.agent", userAgent);

  // 设置 socket 的 tag，用于网络流量统计
  NetworkManagementSocketTagger.install();

  initialized = true;
}
```

### nativeZygoteInit()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

private static final native void nativeZygoteInit();
```

nativeZygoteInit() 方法在 AndroidRuntime.cpp 中，进行了 JNI 映射，对应下面的方法。

```c++
//frameworks/base/core/jni/AndroidRuntime.cpp

static void com_android_internal_os_ZygoteInit_nativeZygoteInit(JNIEnv* env, jobject clazz) {
  // 此处的 gCurRuntime 为 AppRuntime，是在 AndroidRuntime.cpp 中定义的
  gCurRuntime->onZygoteInit();
}

//frameworks/base/cmds/app_process/app_main.cpp

virtual void onZygoteInit() {
  sp<ProcessState> proc = ProcessState::self();
  proc->startThreadPool(); // 启动新 binder 线程
}
```

ProcessState::self() 是单例模式，主要工作是调用 open() 打开 `/dev/binder` 驱动设备，再利用 mmap() 映射内核的地址空间，将 Binder 驱动的 fd 赋值 ProcessState 对象中的变量 mDriverFD，用于交互操作。startThreadPool() 是创建一个新的 binder 线程，不断进行 talkWithDriver()，这里先有个印象，关于 Binder 驱动相关细节我们在后面章节再讨论。

#### applicationInit()

```java
//frameworks/base/core/java/com/android/internal/os/RuntimeInit.java

protected static void applicationInit(int targetSdkVersion, 
            String[] argv, ClassLoader classLoader)
            throws Zygote.MethodAndArgsCaller {
  // true 代表应用程序退出时不调用 AppRuntime.onExit()，否则会在退出前调用
  nativeSetExitWithoutCleanup(true);

  // 设置虚拟机的内存利用率参数值为 0.75
  VMRuntime.getRuntime().setTargetHeapUtilization(0.75f);
  VMRuntime.getRuntime().setTargetSdkVersion(targetSdkVersion);

  final Arguments args;
  try {
    args = new Arguments(argv); // 解析参数
  } catch (IllegalArgumentException ex) {
    Slog.e(TAG, ex.getMessage());
    // let the process exit
    return;
  }

  // The end of of the RuntimeInit event (see #zygoteInit).
  Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);

  // 调用 startClass 的 static 方法 main()
  invokeStaticMain(args.startClass, args.startArgs, classLoader);
}
```

在 startSystemServer() 方法中通过硬编码初始化参数，可知此处 args.startClass 为 `com.android.server.SystemServer`。

#### invokeStaticMain()

```java
//frameworks/base/core/java/com/android/internal/os/RuntimeInit.java

private static void invokeStaticMain(String className, String[] argv,
            ClassLoader classLoader)
            throws Zygote.MethodAndArgsCaller {
  Class<?> cl;

  try {
    cl = Class.forName(className, true, classLoader);
  } catch (ClassNotFoundException ex) {
    // ...
  }

  Method m;
  try {
    m = cl.getMethod("main", new Class[] { String[].class });
  } catch (NoSuchMethodException ex) {
    // ...
  } catch (SecurityException ex) {
    // ...
  }

  int modifiers = m.getModifiers();
  if (! (Modifier.isStatic(modifiers) 
         && Modifier.isPublic(modifiers))) {
    // ...
  }

  // 通过抛出异常，回到 ZygoteInit.main() 的 catch 中
  // 这样做好处是能清空栈帧，提高栈帧利用率
  throw new Zygote.MethodAndArgsCaller(m, argv);
}
```

## MethodAndArgsCaller

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

public static void main(String argv[]) {
  // ...
  try {
    // ...
    if (startSystemServer) { // 启动 system_server
      startSystemServer(abiList, socketName, zygoteServer);
    }
    // ...
  } catch (Zygote.MethodAndArgsCaller caller) {
    caller.run();
  } catch (Throwable ex) {
    // ...
  }
}
```

从文章开头启动 SystemServer 进程到现在可以看到，是 `invokeStaticMain()` 方法中抛出的异常 `Zygote.MethodAndArgsCaller`，从而进入 `caller.run()` 方法。

```java
//frameworks/base/core/java/com/android/internal/os/Zygote.java

public static class MethodAndArgsCaller extends Exception
            implements Runnable {
  private final Method mMethod;
  private final String[] mArgs;

  public MethodAndArgsCaller(Method method, String[] args) {
    mMethod = method;
    mArgs = args;
  }

  public void run() {
    try {
      // 根据传递过来的参数，
      // 可知此处通过反射机制调用的是 SystemServer.main() 方法
      mMethod.invoke(null, new Object[] { mArgs });
    } catch (IllegalAccessException ex) {
      throw new RuntimeException(ex);
    } catch (InvocationTargetException ex) {
      Throwable cause = ex.getCause();
      if (cause instanceof RuntimeException) {
        throw (RuntimeException) cause;
      } else if (cause instanceof Error) {
          throw (Error) cause;
      }
      throw new RuntimeException(ex);
    }
  }
}
```

到此，总算是进入到了 SystemServer 类的 main() 方法。

## SystemServer.main()

```java
//frameworks/base/services/java/com/android/server/SystemServer.java

public static void main(String[] args) {
  // 先初始化 SystemServer 对象，再调用对象的 run() 方法
  new SystemServer().run();
}

private void run() {
  try {
    // 当系统时间比 1970 年更早，就设置当前系统时间为 1970 年
    if (System.currentTimeMillis() < EARLIEST_SUPPORTED_TIME) {
      SystemClock.setCurrentTimeMillis(EARLIEST_SUPPORTED_TIME);
    }

    // 将 timezone 默认设置为 GMT
    String timezoneProperty =
      SystemProperties.get("persist.sys.timezone");
    if (timezoneProperty == null || timezoneProperty.isEmpty()) {
      SystemProperties.set("persist.sys.timezone", "GMT");
    }

    // 根据配置设置系统语言
    if (!SystemProperties.get("persist.sys.language").isEmpty()) {
      final String languageTag = Locale.getDefault().toLanguageTag();

      SystemProperties.set("persist.sys.locale", languageTag);
      SystemProperties.set("persist.sys.language", "");
      SystemProperties.set("persist.sys.country", "");
      SystemProperties.set("persist.sys.localevar", "");
    }

    // The system server should never make non-oneway calls
    Binder.setWarnOnBlocking(true);

    // Here we go!
    Slog.i(TAG, "Entered the Android system server!");
    int uptimeMillis = (int) SystemClock.elapsedRealtime();
    EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_SYSTEM_RUN, 
                        uptimeMillis);
    if (!mRuntimeRestart) {
      MetricsLogger.histogram(null, "boot_system_server_init", 
                              uptimeMillis);
    }

    SystemProperties.set("persist.sys.dalvik.vm.lib.2", 
                         VMRuntime.getRuntime().vmLibrary());

    // Enable the sampling profiler.
    if (SamplingProfilerIntegration.isEnabled()) {
      SamplingProfilerIntegration.start();
      mProfilerSnapshotTimer = new Timer();
      mProfilerSnapshotTimer.schedule(new TimerTask() {
        @Override
        public void run() {
          SamplingProfilerIntegration.writeSnapshot("system_server",
                                                    null);
        }
      }, SNAPSHOT_INTERVAL, SNAPSHOT_INTERVAL);
    }

    // 清除 vm 内存增长上限，由于启动过程需要较多的虚拟机内存空间
    VMRuntime.getRuntime().clearGrowthLimit();

    // 设置内存的可能有效使用率为 0.8
    VMRuntime.getRuntime().setTargetHeapUtilization(0.8f);

    // 针对部分设备依赖于运行时就产生指纹信息，因此需要在开机完成前已经定义
    Build.ensureFingerprintProperty();

    // 访问环境变量前，需要明确地指定用户
    Environment.setUserRequired(true);

    // 确保当前系统进程的 binder 调用，
    // 总是运行在前台优先级（foreground priority）
    BaseBundle.setShouldDefuse(true);

    // Ensure binder calls into the system always run at foreground priority.
    BinderInternal.disableBackgroundScheduling(true);

    // 增加 system_server 中的  binder 线程数
    BinderInternal.setMaxThreads(sMaxBinderThreads);

    // 准备主线程 looper
    android.os.Process.setThreadPriority(
      android.os.Process.THREAD_PRIORITY_FOREGROUND);
    android.os.Process.setCanSelfBackground(false);
    // 主线程 looper 就在当前线程运行
    Looper.prepareMainLooper();

    // 加载 android_servers.so 库，
    // 该库包含的源码在 frameworks/base/services/ 目录下
    System.loadLibrary("android_servers");

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
  if (!mRuntimeRestart && !isFirstBootOrUpgrade()) {
    int uptimeMillis = (int) SystemClock.elapsedRealtime();
    MetricsLogger.histogram(null, "boot_system_server_ready", 
                            uptimeMillis);
    final int MAX_UPTIME_MILLIS = 60 * 1000;
    if (uptimeMillis > MAX_UPTIME_MILLIS) {
      Slog.wtf(SYSTEM_SERVER_TIMING_TAG,
               "SystemServer init took too long. uptimeMillis=" + 
               uptimeMillis);
    }
  }

  // 一直循环执行
  Looper.loop();
  throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

`run()` 方法中的主要工作如下：

- 检验时间：如果当前时间早于1970年，则设置当前时间为1970年，防止初始化出错。
- 设置系统的语言环境等。
- 设置当前虚拟机的运行库路径 `persist.sys.dalvik.vm.lib.2`。
- 设置虚拟机的堆内存，虚拟机堆利用率为 0.8。
- 调用 prepareMainLooper() 初始化当前线程的 Looper。
- 加载 ibandroid_servers.so 库。
- 调用 createSystemContext() 创建 System 的 context。
- 创建大管家 SystemServiceManager 的对象 mSystemServiceManager，负责系统 Service 的管理。
- 调用 `startBootstrapServices()`、 `startCoreServices()`、`startOtherServices()`，创建和运行系统中所有的服务。
- 调用 Looper.loop()，开启消息循环。

## 总结

到这里 SystemServer 进程已经启动起来了，我们来回顾下创建过程，如下图：

![SystemServer 创建过程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/03_system_server_01/03.png)

可以看到 SystemServer 进程由 Zygote 进程 fork 出来，接着会初始化虚拟机环境，然后创建 SystemServiceManager 大管家，启动系统服务，最后进入 loop 状态。

这篇文章我们分析到这里了，下一篇我们继续分析 SystemServer 进程的后续流程。

## 参考资料

- [Android系统启动-SystemServer上篇](http://gityuan.com/2016/02/14/android-system-server/)
- [Android进程系列第三篇---SystemServer进程的创建流程](https://www.jianshu.com/p/9282f5d9c4f0)