# 图解 Android 系列（二）深入理解 init 与 zygote 进程

## 介绍

这是一个连载的系列「图解 Android 系列」，我将持续为大家提供尽可能通俗易懂的 Android 源码分析。

所有引用的源码片段，我都会在第一行标明源文件完整路径。为了文章篇幅考虑源码中间可能有删减，删减部分会用省略号代替。

> 本系列源码基于：Android Oreo（8.0）

## init 进程

在上篇文章 [揭秘 Android 系统启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/android/framework/01_system_start.md) 中介绍到，init 进程启动分为前后两部分，前一部分是在内核启动的，主要是完成创建和内核初始化工作，内容都是跟 Linux 内核相关的；后一部分是在用户空间启动的，主要完成 Android 系统的初始化工作。

Android 系统一般会在根目录下放一个 init 的可执行文件，也就是说 Linux 系统的 init 进程在内核初始化完成后，就直接执行 init 这个文件，这个文件的源代码在 `/system/core/init/init.cpp`。

![init 进程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/07.png)



init 进程是 Linux 系统中用户空间的第一个进程（pid = 1），我们熟悉的 App 应用程序都是以它为父进程的，init 进程入口函数是 main 函数。这个函数做的事情还是比较多的，主要分为三个部分：

- init 进程第一阶段
- init 进程第二阶段
- init.rc 文件解析

### 第一阶段

我们先来看第一阶段主要有以下内容：。

- ueventd/watchdogd 跳转及环境变量设置。
- 挂载文件系统并创建目录。
- 初始化日志输出、挂载分区设备。
- 启用 SELinux 安全策略。
- 开始第二阶段前的准备。

```c++
//system/core/init/init.cpp

int main(int argc, char** argv) {
  if (!strcmp(basename(argv[0]), "ueventd")) {
    // 1 表示 true，也就执行 ueventd_main,ueventd
    // 主要是负责设备节点的创建、权限设定等一些列工作
    return ueventd_main(argc, argv);
  }
  // watchdogd 俗称看门狗，用于系统出问题时重启系统
  if (!strcmp(basename(argv[0]), "watchdogd")) {
    return watchdogd_main(argc, argv);
  }

  if (REBOOT_BOOTLOADER_ON_PANIC) {
    //初始化重启系统的处理信号，内部通过 sigaction 注册信号，
    //当监听到该信号时重启系统
    install_reboot_signal_handlers();
  }
  //注册环境变量PATH
  add_environment("PATH", _PATH_DEFPATH);
  // init 的 main 方法会执行两次，由 is_first_stage 控制，
  // first_stage 就是第一阶段要做的事
  bool is_first_stage = (getenv("INIT_SECOND_STAGE") == nullptr);
  // 只执行一次，因为在方法体中有设置 INIT_SECOND_STAGE
  if (is_first_stage) {
    // 清空文件权限
    umask(0);
    // on / and then we'll let the rc file figure out the rest.
    mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755");
    mkdir("/dev/pts", 0755);
    mkdir("/dev/socket", 0755);
    mount("devpts", "/dev/pts", "devpts", 0, NULL);
    #define MAKE_STR(x) __STRING(x)
    mount("proc", "/proc", "proc", 0, 
          "hidepid=2,gid=" MAKE_STR(AID_READPROC));
    // Don't expose the raw commandline to unprivileged processes.
    chmod("/proc/cmdline", 0440);
    gid_t groups[] = { AID_READPROC };
    setgroups(arraysize(groups), groups);
    mount("sysfs", "/sys", "sysfs", 0, NULL);
    mount("selinuxfs", "/sys/fs/selinux", "selinuxfs", 0, NULL);
    mknod("/dev/kmsg", S_IFCHR | 0600, makedev(1, 11));
    mknod("/dev/random", S_IFCHR | 0666, makedev(1, 8));
    mknod("/dev/urandom", S_IFCHR | 0666, makedev(1, 9));
    // 初始化日志输出
    InitKernelLogging(argv);

    LOG(INFO) << "init first stage started!";

    if (!DoFirstStageMount()) {
      LOG(ERROR) << "Failed to mount required partitions early ...";
      panic();
    }
    // 在刷机模式下初始化avb的版本，不是刷机模式直接跳过
    SetInitAvbVersionInRecovery();

    // 加载S ELinux policy，也就是安全策略
    selinux_initialize(true);

    // We're in the kernel domain, so re-exec init to transition to the init domain now
    // that the SELinux policy has been loaded.
    if (restorecon("/init") == -1) {
      PLOG(ERROR) << "restorecon failed";
      security_failure(); // 失败则重启系统
    }

    setenv("INIT_SECOND_STAGE", "true", 1);

    static constexpr uint32_t kNanosecondsPerMillisecond = 1e6;
    uint64_t start_ms = start_time.time_since_epoch().count()
      / kNanosecondsPerMillisecond;
    setenv("INIT_STARTED_AT", StringPrintf("%" PRIu64, start_ms).c_str(), 1);

    char* path = argv[0];
    char* args[] = { path, nullptr };
    execv(path, args); // 重新执行 main 方法，进入第二阶段

    // execv() only returns if an error happened, in which case we
    // panic and never fall through this conditional.
    PLOG(ERROR) << "execv(\"" << path << "\") failed";
    security_failure();
  }

  // ...
}
```

init 进程第一阶段做的主要工作是挂载分区，创建设备节点和一些关键目录，初始化日志输出系统，启用 SELinux 安全策略。

### 第二阶段

我们接着看第二阶段，主要有以下内容：

- 创建进程会话密钥并初始化属性系统。
- 进行 SELinux 第二阶段并恢复一些文件安全上下文。
- 新建 epoll 并初始化子进程终止信号处理函数。
- 设置其他系统属性并开启系统属性服务。

```c++
//system/core/init/init.cpp

int main(int argc, char** argv) {
  // 同样进行 ueventd/watchdogd 跳转及环境变量设置
  // 之前准备工作时将 INIT_SECOND_STAGE设 置为 true，
  // 已经不为 nullptr，所以 is_first_stage 为 false
  bool is_first_stage = (getenv("INIT_SECOND_STAGE") == nullptr);
  // is_first_stage为false，直接跳过
  if (is_first_stage) {
    // ...
  }
  // 初始化日志输出
  InitKernelLogging(argv);
  // ...
  // 初始化属性系统，并从指定文件读取属性
  property_init();
  // ...
  // 初始化子进程退出的信号处理函数
  signal_handler_init();
  // 加载 default.prop 文件
  property_load_boot_defaults();
  export_oem_lock_status();
  // 启动属性服务器
  start_property_service();
  set_usb_controller();
  //...
}
```

init 进程第二阶段主要工作是初始化属性系统，解析 SELinux 的匹配规则，处理子进程终止信号，启动系统属性服务，可以说每一项都很关键。如果说第一阶段是为属性系统、SELinux 做准备，那么第二阶段就是真正去把这些落实的。

### 解析 init.rc 文件

```c++
//system/core/init/init.cpp

int main(int argc, char** argv) {
  // ...
  const BuiltinFunctionMap function_map;
  // 将 function_map 存放到 Action 中作为成员属性
  Action::set_function_map(&function_map);
  // 解析 init.rc 文件
  Parser& parser = Parser::GetInstance();
  parser.AddSectionParser("service",std::make_unique<ServiceParser>());
  parser.AddSectionParser("on", std::make_unique<ActionParser>());
  parser.AddSectionParser("import", std::make_unique<ImportParser>());
  std::string bootscript = GetProperty("ro.boot.init_rc", "");
  // 如果 ro.boot.init_rc 没有对应的值，
  // 则解析 /init.rc 以及 /system/etc/init、/vendor/etc/init、
  // /odm/etc/init 这三个目录下的 .rc 文件
  if (bootscript.empty()) {
    parser.ParseConfig("/init.rc");
    parser.set_is_system_etc_init_loaded(
      parser.ParseConfig("/system/etc/init"));
    parser.set_is_vendor_etc_init_loaded(
      parser.ParseConfig("/vendor/etc/init"));
    parser.set_is_odm_etc_init_loaded(
      parser.ParseConfig("/odm/etc/init"));
  } else { // 如果 ro.boot.init_rc 属性有值就解析属性值
    parser.ParseConfig(bootscript);
    parser.set_is_system_etc_init_loaded(true);
    parser.set_is_vendor_etc_init_loaded(true);
    parser.set_is_odm_etc_init_loaded(true);
  }

  // ...
  ActionManager& am = ActionManager::GetInstance();
  am.QueueEventTrigger("early-init");

  // 等冷插拔设备初始化完成
  am.QueueBuiltinAction(wait_for_coldboot_done_action,
                        "wait_for_coldboot_done");
  // ... so that we can start queuing up actions that require stuff from /dev.
  am.QueueBuiltinAction(mix_hwrng_into_linux_rng_action, 
                        "mix_hwrng_into_linux_rng");
  am.QueueBuiltinAction(set_mmap_rnd_bits_action, "set_mmap_rnd_bits");
  am.QueueBuiltinAction(set_kptr_restrict_action, "set_kptr_restrict");
  // 设备组合键的初始化操作
  am.QueueBuiltinAction(keychord_init_action, "keychord_init");
  // 屏幕上显示 Android 静态 Logo，很熟悉的感觉有没有
  am.QueueBuiltinAction(console_init_action, "console_init");

  // Trigger all the boot actions to get us started.
  am.QueueEventTrigger("init");

  // 执行 rc 文件中触发器为 on init 的语句
  am.QueueBuiltinAction(mix_hwrng_into_linux_rng_action, 
                        "mix_hwrng_into_linux_rng");

  // 当处于充电模式，则 charger 加入执行队列，否则 late-init 加入队列。
  std::string bootmode = GetProperty("ro.bootmode", "");
  if (bootmode == "charger") {
    am.QueueEventTrigger("charger");
  } else {
    am.QueueEventTrigger("late-init"); // 触发 late-init
  }

  // 触发器为属性是否设置
  am.QueueBuiltinAction(queue_property_triggers_action, 
                        "queue_property_triggers");

  while (true) {
    // By default, sleep until something happens.
    int epoll_timeout_ms = -1;

    if (!(waiting_for_prop 
          || ServiceManager::GetInstance().IsWaitingForExec())) {
      am.ExecuteOneCommand();
    }
    if (!(waiting_for_prop 
          || ServiceManager::GetInstance().IsWaitingForExec())) {
      // 根据需要重启服务  
      restart_processes();

      // If there's a process that needs restarting, wake up in time for that.
      if (process_needs_restart_at != 0) {
        epoll_timeout_ms =
          (process_needs_restart_at - time(nullptr)) * 1000;
        if (epoll_timeout_ms < 0) epoll_timeout_ms = 0;
      }

      // If there's more work to do, wake up again immediately.
      if (am.HasMoreCommands()) epoll_timeout_ms = 0;
    }

    epoll_event ev;
    // 循环等待事件发生
    int nr = TEMP_FAILURE_RETRY(epoll_wait(epoll_fd, &ev, 1, 
                                           epoll_timeout_ms));
    if (nr == -1) {
      PLOG(ERROR) << "epoll_wait failed";
    } else if (nr == 1) {
      ((void (*)()) ev.data.ptr)();
    }
  }

  return 0;
}
```

这一阶段 init 进程做了许多重要的事情，比如解析 init.rc 文件，这里配置了所有需要执行的 action 和需要启动的 service，init 进程根据语法一步步去解析 init.rc，将这些配置转换成一个个数组、队列，然后开启无限循环去处理这些数组、队列中的 command 和 service，并且通过 epoll 监听子进程结束和属性设置。

## init.rc 文件

init.rc 文件是 Android 系统的重要配置文件，位于 `/system/core/rootdir/` 目录中。 主要功能是定义了系统启动时需要执行的一系列 action 及执行特定动作、设置环境变量和属性和执行特定的 service。 

```C
//system/core/rootdir/init.rc

import /init.environ.rc
import /init.usb.rc
import /init.${ro.hardware}.rc
import /vendor/etc/init/hw/init.${ro.hardware}.rc
import /init.usb.configfs.rc
import /init.${ro.zygote}.rc // 稍后分析

on early-init
    // ... 
on init
    // ...
on late-init
    // ...
    trigger zygote-start
on post-fs // 挂载文件系统
    load_system_props
    # start essential services
    start logd
    // 熟悉的 servermanager，后面章节再讨论
    start servicemanager
    start hwservicemanager
    start vndservicemanager
    // ...
on post-fs-data // 挂载 data
    # We chown/chmod /data again so because mount is run as root + defaults
    chown system system /data
    chmod 0771 /data
    # We restorecon /data in case the userdata partition has been reset.
    restorecon /data

    # Make sure we have the device encryption key.
    start vold
    // ...

# It is recommended to put unnecessary data/ initialization from post-fs-data
# to start-zygote in device's init.rc to unblock zygote start.
on zygote-start && property:ro.crypto.state=unencrypted // 启动 zygote，稍后分析
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start netd
    start zygote
    start zygote_secondary

on zygote-start && property:ro.crypto.state=unsupported
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start netd
    start zygote
    start zygote_secondary

on zygote-start && property:ro.crypto.state=encrypted && property:ro.crypto.type=file
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start netd
    start zygote
    start zygote_secondary

on boot
    // ...
    # Start standard binderized HAL daemons
    class_start hal

    class_start core

```

init 进程会解析 `.rc` 文件，然后得到一些 service 去启动，这些 service 通常不是普通的服务，文档里面的称呼是daemon（守护进程）。

所谓守护进程就是这些服务进程会在系统初始化时启动，并一直运行于后台，直到系统关闭时终止。

到这里 init 进程的主要流程已经分析完了，我们总结下 init 进程启动主要做了哪些工作。

![init 进程启动流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/02_init_zygote/01.png)

首先在 Kernel 内核加载完后会调用 `/system/core/init/init.cpp` 文件中的 `main()` 方法。该方法执行分为三个阶段，前两个的阶段都是初始化环境，我们主要关注下第三个阶段 `解析 .rc` 文件。

在第三阶段中通过解析 .rc 文件启动了 `servicemanager` 和 `zygote` 等服务，最后 init 进程进入了 loop。

## zygote 进程

zygote 进程就是 daemon 其中之一，zygote 进程主要负责创建 Java 虚拟机，加载系统资源，启动 SystemServer 进程，以及在后续运行过程中启动普通的应用程序。

![zygote 进程启动流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/02_init_zygote/02.png)

在 init.rc 文件头部有这么一句：

```C
import /init.${ro.zygote}.rc
```

其中 `${ro.zygote}` 会被替换成 ro.zyogte 的属性值，这个是由不同的硬件厂商自己定制的。 有四个值：zygote32、zygote64、zygote32_64、zygote64_32 ，也就是说可能有四种 .rc 文件，分别是：

- init.zygote32.rc：zygote 进程对应的执行程序是 app_process（纯 32bit 模式）。
- init.zygote64.rc：zygote 进程对应的执行程序是 app_process64（纯 64bit 模式）。
- init.zygote32_64.rc：启动两个 zygote 进程（名为 zygote 和 zygote_secondary），对应的执行程序分别是 app_process32（主模式）、app_process64。
- init.zygote64_32.rc：启动两个 zygote 进程（名为 zygote 和 zygote_secondary），对应的执行程序分别是 app_process64（主模式）、app_process32。

为什么要定义这么多种情况呢？直接定义一个不就好了，这主要是因为 Android 5.0 以后开始支持 64 位程序，为了兼容 32 位和 64 位才这样定义。

不同的 zygote.rc 内容大致相同，主要区别体现在启动的是 32 位，还是 64 位的进程。init.zygote32_64.rc 和 init.zygote64_32.rc 会启动两个进程，且存在主次之分。我们以`init.zygote64_32.rc` 为例。

```C
//system/core/rootdir/init.zygote64_32.rc

// 进程名称是 zygote，运行的二进制文件在 /system/bin/app_process64，稍后分析
service zygote /system/bin/app_process64 -Xzygote /system/bin --zygote --start-system-server --socket-name=zygote
    class main
    priority -20
    user root
    group root readproc
    //创建一个 socket，名字叫 zygote，以 tcp 形式
    socket zygote stream 660 root system
    onrestart write /sys/android_power/request_state wake
    onrestart write /sys/power/state on
    onrestart restart audioserver
    onrestart restart cameraserver
    onrestart restart media
    onrestart restart netd
    onrestart restart wificond
    writepid /dev/cpuset/foreground/tasks
    
// 另一个 service，名字 zygote_secondary
service zygote_secondary /system/bin/app_process32 -Xzygote /system/bin --zygote --socket-name=zygote_secondary --enable-lazy-preload
    class main
    priority -20
    user root
    group root readproc
    socket zygote_secondary stream 660 root system
    onrestart restart zygote
    writepid /dev/cpuset/foreground/tasks
```

在 init.rc 文件中可以找到一句 `start zygote`，这是调用 zygote 服务的启动方式。

```C
//system/core/rootdir/init.rc

// ...
# It is recommended to put unnecessary data/ initialization from post-fs-data
# to start-zygote in device's init.rc to unblock zygote start.
// 启动 zygote，稍后分析
on zygote-start && property:ro.crypto.state=unencrypted
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start netd
    start zygote
    start zygote_secondary

on zygote-start && property:ro.crypto.state=unsupported
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start netd
    start zygote
    start zygote_secondary

on zygote-start && property:ro.crypto.state=encrypted && property:ro.crypto.type=file
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start netd
    start zygote
    start zygote_secondary
```

在 init.zygote64_32.rc 文件中的头部我们可以看到 zygote 对应的二进制文件是 `/system/bin/app_process64` （以此为例），我们看一下对应的mk文件， 对应的目录在 `platform/frameworks/base/cmds/app_process/Android.mk`，其实不管是 app_process、app_process32 还是 app_process64，对应的源文件都是 app_main.cpp。

```C
//frameworks/base/cmds/app_process/Android.mk

// ...
app_process_src_files := \
    app_main.cpp \
// ...
LOCAL_SRC_FILES:= $(app_process_src_files)
// ...
LOCAL_MODULE:= app_process
LOCAL_MULTILIB := both
LOCAL_MODULE_STEM_32 := app_process32
LOCAL_MODULE_STEM_64 := app_process64
// ...
```

### app_main.cpp

在 app_main.cpp 的 main 函数中，主要做的事情就是参数解析。 这个函数有两种启动模式：

- 一种是 zygote 模式，也就是初始化 zygote 进程，传递的参数有 --start-system-server --socket-name=zygote，前者表示启动 SystemServer，后者指定 socket 的名称。
- 一种是 application 模式，也就是启动普通应用程序，传递的参数有 class 名字以及 class 带的参数。

两者最终都是调用 AppRuntime 对象的 start 函数，加载 ZygoteInit 或 RuntimeInit 两个 Java 类，并将之前整理的参数传入进去。

```c++
//frameworks/base/cmds/app_process/app_main.cpp

int main(int argc, char* const argv[]) {
  // 将参数 argv 放到 argv_String 字符串中，然后打印出来
  if (!LOG_NDEBUG) { 
    String8 argv_String;
    for (int i = 0; i < argc; ++i) {
      argv_String.append("\"");
      argv_String.append(argv[i]);
      argv_String.append("\" ");
    }
  }

  AppRuntime runtime(argv[0], computeArgBlockSize(argc, argv));
  // Process command line arguments
  // ignore argv[0]
  argc--;
  argv++;

  // 所有在 "--" 后面的非 "-" 开头的参数都将传入 vm, 
  // 但是有个例外是 spaced commands 数组中的参数
  const char* spaced_commands[] = { "-cp", "-classpath" };
  // Allow "spaced commands" to be succeeded by exactly 1 argument (regardless of -s).
  bool known_command = false;

  int i;
  for (i = 0; i < argc; i++) {
    // 将 spaced_commands 中的参数额外加入 VM
    if (known_command == true) {
      runtime.addOption(strdup(argv[i]));
      known_command = false;
      continue;
    }

    for (int j = 0;
         j < static_cast<int>(sizeof(spaced_commands) 
                              / sizeof(spaced_commands[0]));
         ++j) {
      if (strcmp(argv[i], spaced_commands[j]) == 0) {
        known_command = true;
      }
    }

    if (argv[i][0] != '-') {
      break;
    }
    if (argv[i][1] == '-' && argv[i][2] == 0) {
      ++i; // Skip --.
      break;
    }

    runtime.addOption(strdup(argv[i]));
  }

  // Parse runtime arguments.  Stop at first unrecognized option.
  bool zygote = false;
  bool startSystemServer = false;
  bool application = false;
  String8 niceName;
  String8 className;

  ++i;  // Skip unused "parent dir" argument.
  while (i < argc) {
    const char* arg = argv[i++];
    if (strcmp(arg, "--zygote") == 0) {
      zygote = true;
      niceName = ZYGOTE_NICE_NAME;
    } else if (strcmp(arg, "--start-system-server") == 0) {
      startSystemServer = true;
    } else if (strcmp(arg, "--application") == 0) {
      // 表示是 application 启动模式，也就是普通应用程序
      application = true;
    } else if (strncmp(arg, "--nice-name=", 12) == 0) {
      // 进程别名
      niceName.setTo(arg + 12);
    } else if (strncmp(arg, "--", 2) != 0) {
      // application 启动的 class
      className.setTo(arg);
      break;
    } else {
      --i;
      break;
    }
  }

  Vector<String8> args;
  if (!className.isEmpty()) {
    // className 不为空，说明是 application 启动模式
    args.add(application ? String8("application") : String8("tool"));
    // 将 className 和参数设置给 runtime
    runtime.setClassNameAndArgs(className, argc - i, argv + i);

    if (!LOG_NDEBUG) {
      String8 restOfArgs;
      char* const* argv_new = argv + i;
      int argc_new = argc - i;
      for (int k = 0; k < argc_new; ++k) {
        restOfArgs.append("\"");
        restOfArgs.append(argv_new[k]);
        restOfArgs.append("\" ");
      }
    }
  } else { // zygote 启动模式
    // We're in zygote mode.
    maybeCreateDalvikCache(); // 新建 Dalvik 的缓存目录

    if (startSystemServer) { // 加入 start-system-server 参数
      args.add(String8("start-system-server"));
    }

    char prop[PROP_VALUE_MAX];
    if (property_get(ABI_LIST_PROPERTY, prop, NULL) == 0) {
      LOG_ALWAYS_FATAL("app_process: Unable to determine ABI list from property %s.",
                       ABI_LIST_PROPERTY);
      return 11;
    }

    String8 abiFlag("--abi-list=");
    abiFlag.append(prop);
    args.add(abiFlag); // 加入 --abi-list= 参数

    // In zygote mode, pass all remaining arguments to the zygote
    // main() method.
    for (; i < argc; ++i) {
      args.add(String8(argv[i]));
    }
  }

  if (!niceName.isEmpty()) { // 设置进程别名
    runtime.setArgv0(niceName.string(), true /* setProcName */);
  }

  if (zygote) { // 如果是 zygote 启动模式，则加载 ZygoteInit
    runtime.start("com.android.internal.os.ZygoteInit", args, zygote);
  } else if (className) {
    // 如果是 application 启动模式，则加载 RuntimeInit
    runtime.start("com.android.internal.os.RuntimeInit", args, zygote);
  } else {
    fprintf(stderr, "Error: no class name or --zygote supplied.\n");
    app_usage();
    LOG_ALWAYS_FATAL("app_process: no class name or --zygote supplied.");
  }
}
```

我们看到，在最后调用的是 runtime.start 函数，这个就是要启动虚拟机了，接下来我们分析 start 函数。

### 创建虚拟机

```c
//frameworks/base/core/jni/AndroidRuntime.cpp

void AndroidRuntime::start(const char* className, 
                           const Vector<String8>& options, bool zygote) {
  // ...
  // 打印一些日志，获取 ANDROID_ROOT 环境变量
  // ...

  /* start the virtual machine */
  JniInvocation jni_invocation;
  // 初始化JNI，加载 libart.so
  jni_invocation.Init(NULL);
  JNIEnv* env;
  // 创建虚拟机
  if (startVm(&mJavaVM, &env, zygote) != 0) {
    return;
  }
  // 表示虚拟创建完成，但是里面是空实现
  onVmCreated(env);

  /*
   * Register android functions.
   * 注册 JNI 函数
   */
  if (startReg(env) < 0) {
    ALOGE("Unable to register all android natives\n");
    return;
  }
  // JNI 方式调用 ZygoteInit 类的 main 函数
  // ...
}
```

虚拟机创建完成后，我们就可以用 JNI 反射调用 Java 了，其实接下来的语法用过 JNI 的都应该比较熟悉了，直接是 CallStaticVoidMethod 反射调用 ZygoteInit 的 main 函数。

```C
//frameworks/base/core/jni/AndroidRuntime.cpp

void AndroidRuntime::start(const char* className, const Vector<String8>& options,
                           bool zygote) {
  // 接下来的这些语法大家应该比较熟悉了，都是 JNI 里的语法，
  // 主要作用就是调用 ZygoteInit 类的 main 函数 
  jclass stringClass;
  jobjectArray strArray;
  jstring classNameStr;

  stringClass = env->FindClass("java/lang/String");
  assert(stringClass != NULL);
  strArray = env->NewObjectArray(options.size() + 1, stringClass, NULL);
  assert(strArray != NULL);
  classNameStr = env->NewStringUTF(className);
  assert(classNameStr != NULL);
  env->SetObjectArrayElement(strArray, 0, classNameStr);

  for (size_t i = 0; i < options.size(); ++i) {
    jstring optionsStr = env->NewStringUTF(options.itemAt(i).string());
    assert(optionsStr != NULL);
    env->SetObjectArrayElement(strArray, i + 1, optionsStr);
  }

  /*
     * Start VM.  This thread becomes the main thread of the VM, and will
     * not return until the VM exits.
     */
  // 将 "com.android.internal.os.ZygoteInit" 
  // 转换为 "com/android/internal/os/ZygoteInit"
  char* slashClassName = toSlashClassName(className);
  // 找到 class
  jclass startClass = env->FindClass(slashClassName);
  if (startClass == NULL) {
    ALOGE("JavaVM unable to locate class '%s'\n", slashClassName);
    /* keep going */
  } else {
    jmethodID startMeth = env->GetStaticMethodID(startClass, "main",
                                  "[Ljava/lang/String;)V");
    if (startMeth == NULL) {
      ALOGE("JavaVM unable to find main() in '%s'\n", className);
      /* keep going */
    } else {// 调用 ZygoteInit.main() 方法
      env->CallStaticVoidMethod(startClass, startMeth, strArray);

      #if 0
      if (env->ExceptionCheck())
        threadExitUncaughtException(env);
      #endif
    }
  }
  free(slashClassName);

  ALOGD("Shutting down VM\n");
  // 退出当前线程
  if (mJavaVM->DetachCurrentThread() != JNI_OK)
    ALOGW("Warning: unable to detach main thread\n");
  // 创建一个线程，该线程会等待所有子线程结束后关闭虚拟机
  if (mJavaVM->DestroyJavaVM() != 0) 
    ALOGW("Warning: VM did not shut down cleanly\n");
}
```

zygote 进程启动主要创建了 Java 虚拟机，有了虚拟机，就可以执行 Java 代码了。

### ZygoteInit.java

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

public static void main(String argv[]) {
  ZygoteServer zygoteServer = new ZygoteServer();

  // 标记 zygote 进程已启动
  ZygoteHooks.startZygoteNoThreadCreation();

  // 进入 Zygote 进程
  try {
    Os.setpgid(0, 0);
  } catch (ErrnoException ex) {
    throw new RuntimeException("Failed to setpgid(0,0)", ex);
  }

  try {
    RuntimeInit.enableDdms(); // 开启 DDMS 功能

    boolean startSystemServer = false;
    String socketName = "zygote";
    String abiList = null;
    boolean enableLazyPreload = false;
    for (int i = 1; i < argv.length; i++) {
      if ("start-system-server".equals(argv[i])) {
        startSystemServer = true;
      } else if ("--enable-lazy-preload".equals(argv[i])) {
        enableLazyPreload = true;
      } else if (argv[i].startsWith(ABI_LIST_ARG)) {
        abiList = argv[i].substring(ABI_LIST_ARG.length());
      } else if (argv[i].startsWith(SOCKET_NAME_ARG)) {
        socketName = argv[i].substring(SOCKET_NAME_ARG.length());
      } else {
        throw new RuntimeException("Unknown command line argument: "
                                   + argv[i]);
      }
    }

    if (abiList == null) {
      throw new RuntimeException("No ABI list supplied.");
    }

    // 为 zygote 注册 socket
    zygoteServer.registerServerSocket(socketName);
    // 预加载处理
    if (!enableLazyPreload) {
      // zygote 预加载，下面介绍
      preload(bootTimingsTraceLog);
    } else {
      Zygote.resetNicePriority();
    }

    gcAndFinalize(); // GC 操作

    // Zygote process unmounts root storage spaces.
    Zygote.nativeUnmountStorageOnInit();

    // Set seccomp policy
    Seccomp.setPolicy();

    ZygoteHooks.stopZygoteNoThreadCreation();

    if (startSystemServer) { // 启动 system_server，下面介绍
      startSystemServer(abiList, socketName, zygoteServer);
    }

    // 进入循环模式，下面介绍
    zygoteServer.runSelectLoop(abiList);

    zygoteServer.closeServerSocket();
  } catch (Zygote.MethodAndArgsCaller caller) {
    caller.run();
  } catch (Throwable ex) {
    zygoteServer.closeServerSocket();
    throw ex;
  }
}
```

这里 `startSystemServer()` 方法会抛出一个 `Zygote.MethodAndArgsCaller` 异常，然后调用到 `caller.run()`，这里会在 SystemServer 章节继续分析。

### preload()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

static void preload(BootTimingsTraceLog bootTimingsTraceLog) {
  // ...
  // 预加载位于 /system/etc/preloaded-classes 文件中的类
  preloadClasses();
  // 预加载资源，包含 drawable 和 color 资源
  preloadResources();
  // 预加载 OpenGL
  preloadOpenGL();
  // 通过 System.loadLibrary() 方法，
  // 预加载 "android"，"compiler_rt"，"jnigraphics" 这 3 个共享库
  preloadSharedLibraries();
  // 预加载 文本连接符资源
  preloadTextResources();
  // 仅用于 zygote 进程，用于内存共享的进程
  WebViewFactory.prepareWebViewInZygote();
  endIcuCachePinning();
  warmUpJcaProviders();
  Log.d(TAG, "end preload");

  sPreloadComplete = true;
}
```

执行 zygote 进程的初始化，对于类加载，采用反射机制 `Class.forName()` 方法来加载。对于资源加载，主要是  com.android.internal.R.array.preloaded_drawables 和 com.android.internal.R.array.preloaded_color_state_lists，在应用程序中以 com.android.internal.R.xxx 开头的资源，便是此时由 Zygote 加载到内存的。

zygote 进程内加载了 preload() 方法中的所有资源，当需要 fork 新进程时，采用 copy on write 技术，如下：

![zygote 进程 fork 进程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/02_init_zygote/03.png)

### startSystemServer()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteInit.java

private static boolean startSystemServer(String abiList, 
                       String socketName, ZygoteServer zygoteServer)
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
    // fork 子进程，用于运行 system_server
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
  if (pid == 0) {
    if (hasSecondZygote(abiList)) {
      waitForSecondaryZygote(socketName);
    }

    zygoteServer.closeServerSocket();
    // 完成 system_server 进程剩余的工作
    handleSystemServerProcess(parsedArgs);
  }

  return true;
}
```

可以看到 zygote 进程 fork 出一个新进程名为 `system_server` 也就是 SystemServer 进程。该方法是 SystemServer 进程启动的起点，关于 SystemServer 启动流程我们在后面的章节在讨论，这里先分析完 zygote 的主要流程。

### runSelectLoop()

```java
//frameworks/base/core/java/com/android/internal/os/ZygoteServer.java

void runSelectLoop(String abiList) throws Zygote.MethodAndArgsCaller {
  ArrayList<FileDescriptor> fds = new ArrayList<FileDescriptor>();
  ArrayList<ZygoteConnection> peers = new ArrayList<ZygoteConnection>();
  // mServerSocket 是 socket 通信中的服务端，即 zygote 进程。保存到 fds[0]
  fds.add(mServerSocket.getFileDescriptor());
  peers.add(null);

  while (true) {
    StructPollfd[] pollFds = new StructPollfd[fds.size()];
    for (int i = 0; i < pollFds.length; ++i) {
      pollFds[i] = new StructPollfd();
      pollFds[i].fd = fds.get(i);
      pollFds[i].events = (short) POLLIN;
    }
    try {
      // 处理轮询状态，当 pollFds 有事件到来则往下执行，否则阻塞在这里
      Os.poll(pollFds, -1);
    } catch (ErrnoException ex) {
      throw new RuntimeException("poll failed", ex);
    }
    for (int i = pollFds.length - 1; i >= 0; --i) {
      // 采用 I/O 多路复用机制，当接收到客户端发出连接请求
      // 或者数据处理请求到来，则往下执行；
      // 否则进入continue，跳出本次循环。
      if ((pollFds[i].revents & POLLIN) == 0) {
        continue;
      }
      if (i == 0) {
        ZygoteConnection newPeer = acceptCommandPeer(abiList);
        peers.add(newPeer);
        fds.add(newPeer.getFileDesciptor());
      } else {
        // i>0，则代表通过 socket 接收来自对端的数据，并执行相应操作
        boolean done = peers.get(i).runOnce(this);
        if (done) {
          peers.remove(i);
          fds.remove(i); // 处理完则从 fds 中移除该文件描述符
        }
      }
    }
  }
}
```

zygote 采用高效的 I/O 多路复用机制，保证在没有客户端连接请求或数据处理时休眠，否则响应客户端的请求。在调用 `runSelectLoop()` 后 zygote 进入了轮询状态，随时待命当接收到请求创建新进程请求时，立即唤醒并执行相应工作。

## 总结

到这里 zygote 进程已经启动完成了，Android 系统到目前已经启动了第一个用户进程 zygote。我们来回顾下目前 Android 系统启动的流程：

![zygote 启动流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/02_init_zygote/04.png)

当我们按下电源按键后会启动 Bootloader，Bootloader 会加载 Kernel 内核到内存中，然后会启动内核中的 idle 进程，idle 进程会启动 kthreadd 和 init 两个进程。

init 进程在启动的时候会初始化运行环境，然后解析 init.rc 文件，解析 init.rc 文件的过程中会启动 servicemanager、zygote 等服务，最后进入 loop 状态。

zygote 服务启动时会创建 Java 虚拟机并初始化 Java 运行环境，然后启动 SystemServer 服务，最后进入 loop 状态。

这篇文章我们分析到这里，下一篇我们接着分析 zygote 进程启动中调用 startSystemServer() 方法后 SystemServer 进程启动的流程。

## 参考资料

- [Android内核开发：图解Android系统的启动过程](https://blog.51cto.com/ticktick/1659473)
- [Android 8.0 : 系统启动流程之Linux内核](https://juejin.im/post/59f1ef1d6fb9a0452206bc76)
- [Android bootloader/fastboot mode and recovery mode explained/Android boot process](https://tektab.com/2015/10/31/android-bootloaderfastboot-mode-and-recovery-mode-explained)
- [Android is NOT just 'Java on Linux'](https://www.slideshare.net/tetsu.koba/android-is-not-just-java-on-linux/19-Zygote_forkZygote_process_Child_process)
- [Android 启动流程简介](https://www.cnblogs.com/shed/p/3726878.html)