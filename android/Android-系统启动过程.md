# Android - 系统启动过程

## 计算机是如何启动的？

首先熟悉一些概念，计算机的硬件包括：CPU，内存，硬盘，显卡，显示器，键盘鼠标等其他输入输出设备。 所有的软件（比如：操作系统）都是存放在硬盘上，程序执行时需要将程序从硬盘上读取到内存中然后加载到 CPU 中来运行。 当我们按下开机键时，此时内存中什么都没有，因此需要借助某种方式，将操作系统加载到内存中，而完成这项任务的就是 BIOS。

- 引导阶段

BIOS: Basic Input/Output System（基本输入输出系统），在 IBM PC 兼容系统上，是一种业界标准的固件接口（来自维基百科）。 BIOS 一般是主板芯片上的一个程序，计算机通电后，第一件事就是读取它。

BIOS 程序首先检查计算机硬件能否满足运行的基本条件，这叫做"硬件自检"（Power-On Self-Test），缩写为 POST。 如果硬件出现问题，主板会发出不同含义的蜂鸣，启动中止。 如果没有问题，屏幕就会显示出 CPU，内存，硬盘等信息。

硬件自检完成后，BIOS 把控制权转交给下一阶段的启动程序。 这时 BIOS 需要知道，下一阶段的启动程序到底存放在哪一个设备当中。 也就是说 BIOS 需要有一个外部存储设备的排序，排在前面的设备就是优先转交控制权的设备。 这种排序叫做启动排序，也就是我们平时进入 BIOS 界面时能看到的 Boot Sequence。

如果我们没有进行特殊操作的话，那么 BIOS 就会按照这个启动顺序将控制权交给下一个存储设备。 我们在使用 U 盘光盘之类的装系统时就是在这里将启动顺序改变了，将本来要移交给硬盘的控制权交给了 U 盘或者光盘。

第一存储设备被激活后，计算机读取该设备的第一个扇区，也就是读取最前面的 512 个字节。 如果这 512 个字节的最后两个字节是 0x55 和 0xAA ，表明这个设备可以用于启动；如果不是，表明设备不能用于启动，控制权于是被转交给“启动顺序”中的下一个设备。

这最前面的 512 个字节，就叫做"主引导记录"（Master boot record，缩写为 MBR）。 主引导记录 MBR 是位于磁盘最前边的一段引导代码。它负责磁盘操作系统对磁盘进行读写时分区合法性的判别、分区引导信息的定位，它由磁盘操作系统在对硬盘进行初始化时产生的。 硬盘的主引导记录 MBR 是不属于任何一个操作系统的，它先于所有的操作系统而被调入内存，并发挥作用，然后才将控制权交给主分区内的操作系统，并用主分区信息表来管理硬盘。

MBR 只有512个字节，放不了太多东西。 它的主要作用是，告诉计算机到硬盘的哪一个位置去找操作系统。 我们找到可用的 MBR 后，计算机从 MBR 中读取前面 446 字节的机器码之后，不再把控制权转交给某一个分区，而是运行事先安装的"启动管理器"（boot loader），由用户选择启动哪一个操作系统。

- 加载内核阶段

选择完操作系统后，控制权转交给操作系统，操作系统的内核首先被载入内存。

以 Linux 系统为例，先载入 /boot 目录下面的 kernel。 内核加载成功后，第一个运行的程序是 /sbin/init。 它根据配置文件（Debian 系统是 /etc/initab ）产生 init 进程。 这是 Linux 启动后的第一个进程，pid 进程编号为 1，其他进程都是它的后代。

然后，init 线程加载系统的各个模块，比如：窗口程序和网络程序，直至执行 /bin/login 程序，跳出登录界面，等待用户输入用户名和密码。

至此，全部启动过程完成。


## Android 手机的启动过程

Android 系统虽然也是基于 Linux 系统的，但是由于 Android 属于嵌入式设备，并没有像 PC 那样的 BIOS 程序。 取而代之的是 Bootloader —— 系统启动加载器。 它类似于 BIOS，在系统加载前，用以初始化硬件设备，建立内存空间的映像图，为最终调用系统内核准备好环境。 在 Android 里没有硬盘，而是 ROM，它类似于硬盘存放操作系统，用户程序等。 ROM 跟硬盘一样也会划分为不同的区域，用于放置不同的程序，在 Android 中主要划分为一下几个分区：

- /boot：存放引导程序，包括内核和内存操作程序
- /system：相当于电脑c盘，存放Android系统及系统应用
- /recovery：恢复分区，可以进入该分区进行系统恢复
- /data：用户数据区，包含了用户的数据：联系人、短信、设置、用户安装的程序
- /cache：安卓系统缓存区，保存系统最常访问的数据和应用程序
- /misc：包含一些杂项内容，如系统设置和系统功能启用禁用设置
- /sdcard：用户自己的存储区，可以存放照片，音乐，视频等文件

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/boot_image.png" alt=""/>

那么 Bootloader 是如何被加载的呢？跟 PC 启动过程类似，当开机通电时首先会加载 Bootloader，Bootloader 会读取 ROM 找到操作系统并将 Linux 内核加载到 RAM 中。

当 Linux 内核启动后会初始化各种软硬件环境，加载驱动程序，挂载根文件系统，Linux 内核加载的最后阶段会启动执行第一个用户空间进程 init 进程。

## init 进程

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/android-booting.png" alt=""/>

init 是 Linux 系统中用户空间的第一个进程(pid=1)，Kernel 启动后会调用 /system/core/init/Init.cpp 的 main() 方法。

- Init.main()

首先初始化 Kernel log，创建一块共享的内存空间，加载 /default.prop 文件，解析 init.rc 文件。

## init.rc 文件

init.rc 文件是 Android 系统的重要配置文件，位于 /system/core/rootdir/ 目录中。 主要功能是定义了系统启动时需要执行的一系列 action 及执行特定动作、设置环境变量和属性和执行特定的 service。 

init.rc 脚本文件配置了一些重要的服务，init 进程通过创建子进程启动这些服务，这里创建的 service 都属于 native 服务，运行在 Linux 空间，通过 socket 向上层提供特定的服务，并以守护进程的方式运行在后台。

通过 init.rc 脚本系统启动了以下几个重要的服务：
- service_manager：启动 binder IPC，管理所有的 Android 系统服务
- mountd：设备安装 Daemon，负责设备安装及状态通知
- debuggerd：启动 debug system，处理调试进程的请求
- rild：启动 radio interface layer daemon 服务，处理电话相关的事件和请求
- media_server：启动 AudioFlinger，MediaPlayerService 和 CameraService，负责多媒体播放相关的功能，包括音视频解码
- surface_flinger：启动 SurfaceFlinger 负责显示输出
- zygote：进程孵化器，启动 Android Java VMRuntime 和启动 systemserver，负责 Android 应用进程的孵化工作

在这个阶段你可以在设备的屏幕上看到 “Android” logo 了。

以上工作执行完，init 进程就会进入 loop 状态。

## service_manager 进程

ServiceManager 是 Binder IPC 通信过程中的守护进程，本身也是一个 Binder 服务。ServiceManager 进程主要是启动 Binder，提供服务的查询和注册。

具体过程详见 Binder：[Android Binder 进程间通讯](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Binder进程间通讯.md)

## surface_flinger 进程

SurfaceFlinger 负责图像绘制，是应用 UI 的核心，其功能是合成所有 Surface 并渲染到显示设备。SurfaceFlinger 进程主要是启动 FrameBuffer，初始化显示系统。

## media_server 进程

MediaServer 进程主要是启动 AudioFlinger 音频服务，CameraService 相机服务。负责处理音频解析播放，相机相关的处理。

## Zygote 进程

fork 创建进程过程：
<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/android-process.png" alt=""/>

Zygote 进程孵化了所有的 Android 应用进程，是 Android Framework 的基础，该进程的启动也标志着 Framework 框架初始化启动的开始。 

Zygote 服务进程的主要功能：
- 注册底层功能的 JNI 函数到虚拟机
- 预加载 Java 类和资源
- fork 并启动 system_server 核心进程
- 作为守护进程监听处理“孵化新进程”的请求

当 Zygote 进程启动后, 便会执行到 frameworks/base/cmds/app_process/App_main.cpp 文件的 main() 方法。 

```C
App_main.main() //设置进程名，并启动 AppRuntime。
AndroidRuntime::start() //创建 Java 虚拟机，注册 JNI 方法，调用 ZygoteInit.main() 方法。
ZygoteInit.main()   //为 Zygote 注册 socket，预加载类和资源，启动 system_server 进程。
```

然后 Zygote 进程会进入 loop 状态，等待下次 fork 进程。

## system_server 进程

system_server 进程 由 Zygote 进程 fork 而来。接下来看下 system_server 启动过程。

```C
//首先会调用 ZygoteInit.startSystemServer() 方法
ZygoteInit.startSystemServer()  
//fork 子进程 system_server，进入 system_server 进程。

ZygoteInit.handleSystemServerProcess()  
//设置当前进程名为“system_server”，创建 PathClassLoader 类加载器。

RuntimeInit.zygoteInit()    
//重定向 log 输出，通用的初始化（设置默认异常捕捉方法，时区等），初始化 Zygote -> nativeZygoteInit()。

nativeZygoteInit()  
//方法经过层层调用，会进入 app_main.cpp 中的 onZygoteInit() 方法。

app_main::onZygoteInit()// 启动新 Binder 线程。

applicationInit()   
//方法经过层层调用，会抛出异常 ZygoteInit.MethodAndArgsCaller(m, argv), ZygoteInit.main() 会捕捉该异常。

ZygoteInit.main()   
//开启 DDMS 功能，preload() 加载资源，预加载 OpenGL，调用 SystemServer.main() 方法。

SystemServer.main() 
//先初始化 SystemServer 对象，再调用对象的 run() 方法。

SystemServer.run()  
//准备主线程 looper，加载 android_servers.so 库，该库包含的源码在 frameworks/base/services/ 目录下。
```
system_server 进程启动后将初始化系统上下文（设置主题），创建系统服务管理 SystemServiceManager，然后启动各种系统服务：

```Java
startBootstrapServices(); // 启动引导服务
//该方法主要启动服务 ActivityManagerService，PowerManagerService，LightsService，DisplayManagerService，PackageManagerService，UserManagerService。
//设置 ActivityManagerService，启动传感器服务。

startCoreServices();      // 启动核心服务
//该方法主要
//启动服务 BatteryService 用于统计电池电量，需要 LightService。
//启动服务 UsageStatsService，用于统计应用使用情况。
//启动服务 WebViewUpdateService。

startOtherServices();     // 启动其他服务
//该方法主要启动服务 InputManagerService，WindowManagerService。
//等待 ServiceManager，SurfaceFlinger启动完成，然后显示启动界面。
//启动服务 StatusBarManagerService，
//准备好 window, power, package, display 服务：
//	- WindowManagerService.systemReady()
//	- PowerManagerService.systemReady()
//	- PackageManagerService.systemReady()
//	- DisplayManagerService.systemReady()
```

所有的服务启动完成后会注册到 ServiceManager。
ActivityManagerService 服务启动完成后，会进入 ActivityManagerService.systemReady()，然后启动 SystemUI，WebViewFactory，Watchdog，最后启动桌面 Launcher App。

最后会进入循环 Looper.loop()。

## ActivityManagerService 启动

启动桌面 Launcher App 需要等待 ActivityManagerService 启动完成。我们来看下 ActivityManagerService 启动过程。

```Java
ActivityManagerService(Context) 
//创建名为“ActivityManager”的前台线程，并获取mHandler。
//通过 UiThread 类，创建名为“android.ui”的线程。
//创建前台广播和后台广播接收器。
//创建目录 /data/system。
//创建服务 BatteryStatsService。

ActivityManagerService.start()  //启动电池统计服务，创建 LocalService，并添加到 LocalServices。

ActivityManagerService.startOtherServices() -> installSystemProviders()
//安装所有的系统 Provider。

ActivityManagerService.systemReady()
//恢复最近任务栏的 task。
//启动 WebView，SystemUI，开启 Watchdog，启动桌面 Launcher App。
//发送系统广播。
```

启动桌面 Launcher App，首先会通过 Zygote 进程 fork 一个新进程作为 App 进程，然后创建 Application，创建启动 Activity，最后用户才会看到桌面。

## 完整启动过程

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/android-bootloader.png" alt=""/>

## 参考资料

- [计算机是如何启动的？](http://www.ruanyifeng.com/blog/2013/02/booting.html)
- [按下电源键之后，电脑又默默干了很多事](http://daily.zhihu.com/story/8803295)
- [Android系统启动-概述](http://gityuan.com/2016/02/01/android-booting/)


