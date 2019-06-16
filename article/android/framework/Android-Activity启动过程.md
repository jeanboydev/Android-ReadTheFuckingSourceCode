# Android - Activity 启动过程

## 概述

从点击桌面应用图标到应用显示的过程我们再熟悉不过了，下面我们来分析下这个过程都做了什么。

本文主要对以下问题分析：

- ActivityThread 是什么，它是一个线程吗，如何被启动的？
- ActivityClientRecord 与 ActivityRecord 是什么？
- Context 是什么，ContextImpl，ContextWapper 是什么？
- Instrumentation 是什么？
- Application 是什么，什么时候创建的，每个应用程序有几个 Application？
- 点击 Launcher 启动 Activity 和应用内部启动 Activity 的区别？
- Activity 启动过程，onCreate()，onResume() 回调时机及具体作用？

## Launcher

如不了解 Android 是如何从开机到 Launcher 启动的过程，请先阅读[Android - 系统启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-系统启动过程.md)。

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_boot_loader/android-bootloader.png" alt=""/>

我们知道 Android 系统启动后已经启动了 Zygote，ServiceManager，SystemServer 等系统进程；ServiceManager 进程中完成了 Binder 初始化；SystemServer 进程中 ActivityManagerService，WindowManagerService，PackageManagerService 等系统服务在 ServiceManager 中已经注册；最后启动了 Launcher 桌面应用。

其实 Launcher 本身就是一个应用程序，运行在自己的进程中，我们看到的桌面就是 Launcher 中的一个 Activity。

应用安装的时候，通过 PackageManagerService 解析 apk 的 AndroidManifest.xml 文件，提取出这个 apk 的信息写入到 packages.xml 文件中，这些信息包括：权限、应用包名、icon、apk 的安装位置、版本、userID 等等。packages.xml 文件位于系统目录下/data/system/packages.xml。

同时桌面 Launcher 会为安装过的应用生成不同的应用入口，对应桌面上的应用图标，下面分析点击应用图标的到应用启动的过程。

## 点击 Launcher 中应用图标

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity/app_start.png" alt=""/>

点击 Launcher 中应用图标将会执行以下方法

```Java
Launcher.startActivitySafely()
Launcher.startActivity()
//以上两个方法主要是检查将要打开的 Activity 是否存在

Activity.startActivity()
//这段代码大家已经很熟悉，经常打开 Activity 用的就是这个方法

Activity.startActivityForResult()
//默认 requestCode = -1，也可通过调用 startActivityForResult() 传入 requestCode。 
//然后通过 MainThread 获取到 ApplicationThread 传入下面方法。

Instrumentation.execStartActivity()
//通过 ActivityManagerNative.getDefault() 获取到 ActivityManagerService 的代理为进程通讯作准备。

ActivityManagerNative.getDefault().startActivity()
ActivityManagerProxy.startActivity()
//调用代理对象的 startActivity() 方法，发送 START_ACTIVITY_TRANSACTION 命令。
```

在 system_server 进程中的服务端 ActivityManagerService 收到 START_ACTIVITY_TRANSACTION 命令后进行处理，调用 startActivity() 方法。

```Java
ActivityManagerService.startActivity() -> startActivityAsUser(intent, requestCode, userId)
//通过 UserHandle.getCallingUserId() 获取到 userId 并调用 startActivityAsUser() 方法。

ActivityStackSupervisor.startActivityMayWait() -> resolveActivity()
//通过 intent 创建新的 intent 对象，即使之前 intent 被修改也不受影响。 然后调用 resolveActivity()。
//然后通过层层调用获取到 ApplicationPackageManager 对象。

PackageManagerService.resolveIntent() -> queryIntentActivities()
//获取 intent 所指向的 Activity 信息，并保存到 Intent 对象。

PackageManagerService.chooseBestActivity()
//当存在多个满足条件的 Activity 则会弹框让用户来选择。

ActivityStackSupervisor.startActivityLocked()
//获取到调用者的进程信息。 通过 Intent.FLAG_ACTIVITY_FORWARD_RESULT 判断是否需要进行 startActivityForResult 处理。 
//检查调用者是否有权限来调用指定的 Activity。 
//创建 ActivityRecord 对象，并检查是否运行 App 切换。

ActivityStackSupervisor.startActivityUncheckedLocked() -> startActivityLocked()
//进行对 launchMode 的处理[可参考 Activity 启动模式]，创建 Task 等操作。
//启动 Activity 所在进程，已存在则直接 onResume()，不存在则创建 Activity 并处理是否触发 onNewIntent()。

ActivityStack.resumeTopActivityInnerLocked()
//找到 resume 状态的 Activity，执行 startPausingLocked() 暂停该 Activity，同时暂停所有处于后台栈的 Activity，找不到 resume 状态的 Activity 则回桌面。
//如果需要启动的 Activity 进程已存在，直接设置 Activity 状态为 resumed。 调用下面方法。

ActivityStackSupervisor.startSpecificActivityLocked()
//进程存在调用 realStartActivityLocked() 启动 Activity，进程不存在则调用下面方法。
```
## fork 新进程

从 Launcher 点击图标，如果应用没有启动过，则会 fork 一个新进程。创建新进程的时候，ActivityManagerService 会保存一个 ProcessRecord 信息，Activity 应用程序中的AndroidManifest.xml 配置文件中，我们没有指定 Application 标签的 process 属性，系统就会默认使用 package 的名称。每一个应用程序都有自己的 uid，因此，这里 uid + process 的组合就可以为每一个应用程序创建一个 ProcessRecord。每次在新建新进程前的时候会先判断这个 ProcessRecord 是否已存在，如果已经存在就不会新建进程了，这就属于应用内打开 Activity 的过程了。

```Java
ActivityManagerService.startProcessLocked()
//进程不存在请求 Zygote 创建新进程。 创建成功后切换到新进程。
```

进程创建成功切换至 App 进程，进入 app 进程后将 ActivityThread 类加载到新进程，并调用 ActivityThread.main() 方法

```Java
ActivityThread.main()
//创建主线程的 Looper 对象，创建 ActivityThread 对象，ActivityThread.attach() 建立 Binder 通道，开启 Looper.loop() 消息循环。

ActivityThread.attach()
//开启虚拟机各项功能，创建 ActivityManagerProxy 对象，调用基于 IActivityManager 接口的 Binder 通道 ActivityManagerProxy.attachApplication()。

ActivityManagerProxy.attachApplication()
//发送 ATTACH_APPLICATION_TRANSACTION 命令
```

此时只创建了应用程序的 ActivityThread 和 ApplicationThread，和开启了 Handler 消息循环机制，其他的都还未创建， ActivityThread.attach(false) 又会最终到 ActivityMangerService 的 attachApplication，这个工程其实是将本地的 ApplicationThread 传递到 ActivityMangerService。然后 ActivityMangerService 就可以通过 ApplicationThread 的代理 ApplicationThreadProxy 来调用应用程序 ApplicationThread.bindApplication，通知应用程序的 ApplicationThread 已和 ActivityMangerService 绑定，可以不借助其他进程帮助直接通信了。此时 Launcher 的任务也算是完成了。

在 system_server 进程中的服务端 ActivityManagerService 收到 ATTACH_APPLICATION_TRANSACTION 命令后进行处理，调用 attachApplication()。

```Java
ActivityMangerService.attachApplication() -> attachApplicationLocked()
//首先会获取到进程信息 ProcessRecord。 绑定死亡通知，移除进程启动超时消息。 获取到应用 ApplicationInfo 并绑定应用 IApplicationThread.bindApplication(appInfo)。
//然后检查 App 所需组件。
```

- Activity: 检查最顶层可见的 Activity 是否等待在该进程中运行，调用 ActivityStackSupervisor.attachApplicationLocked()。
- Service：寻找所有需要在该进程中运行的服务，调用 ActiveServices.attachApplicationLocked()。
- Broadcast：检查是否在这个进程中有下一个广播接收者，调用 sendPendingBroadcastsLocked()。

此处讨论 Activity 的启动过程，只讨论 ActivityStackSupervisor.attachApplicationLocked() 方法。

```Java
ActivityStackSupervisor.attachApplicationLocked() -> realStartActivityLocked()
//将该进程设置为前台进程 PROCESS_STATE_TOP，调用 ApplicationThreadProxy.scheduleLaunchActivity()。

ApplicationThreadProxy.scheduleLaunchActivity()
//发送 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令
```

发送送完 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令，还会发送 BIND_APPLICATION_TRANSACTION 命令来创建 Application。

```Java
ApplicationThreadProxy.bindApplication()
//发送 BIND_APPLICATION_TRANSACTION 命令
```

## App 进程初始化 

在 app 进程中，收到 BIND_APPLICATION_TRANSACTION 命令后调用 ActivityThread.bindApplication()。

```Java
ActivityThread.bindApplication()
//缓存 Service，初始化 AppBindData，发送消息 H.BIND_APPLICATION。
```

ApplicationThreadProxy.bindApplication(…) 会传来这个应用的一些信息，如ApplicationInfo，Configuration 等，在 ApplicationThread.bindApplication 里会待信息封装成A ppBindData，通过

```Java
sendMessage(H.BIND_APPLICATION, data)
```

将信息放到应用里的消息队列里，通过 Handler 消息机制，在 ActivityThread.handleMeaasge 里处理 H.BIND_APPLICATION 的信息，调用 AplicationThread.handleBindApplication。

```Java
handleBindApplication(AppBindData data) {
    Process.setArgV0(data.processName);//设置进程名
    ...
    //初始化 mInstrumentation
    if(data.mInstrumentation!=null) {
        mInstrumentation = (Instrumentation) cl.loadClass(data.instrumentationName.getClassName()).newInstance();
    } else {
        mInstrumentation = new Instrumentation();
    }
    //创建Application，data.info 是个 LoadedApk 对象。
    Application app = data.info.makeApplication(data.restrictedBackupMode, null);
    mInitialApplication = app;
    //调用 Application 的 onCreate()方法。
    mInstrumentation.callApplicationOnCreate(app);
}

public Application makeApplication(boolean forceDefaultAppClass,Instrumentation instrumentation) {
    
    if (mApplication != null) {   
       return mApplication;
    }
    
    String appClass = mApplicationInfo.className;
    java.lang.ClassLoader cl = getClassLoader();
    
    //此时新建一个 Application 的 ContextImpl 对象，
    ContextImpl appContext = ContextImpl.createAppContext(mActivityThread, this);
    
    //通过在 handleBindApplication 创建的 mInstrumentation 对象新建一个 Application 对象，同时进行 attach。
    app = mActivityThread.mInstrumentation.newApplication(cl, appClass, appContext);
    appContext.setOuterContext(app);
}

//设置进程名，获取 LoadedApk 对象，创建 ContextImpl 上下文
//LoadedApk.makeApplication() 创建 Application 对象，调用 Application.onCreate() 方法。
```

Instrumentation：

```Java
public Application newApplication(ClassLoader cl, String className, Context context) {    
    return newApplication(cl.loadClass(className), context);
}
Instrumentation类：
static public Application newApplication(Class<?> clazz, Context context)  {
    //实例化 Application
    Application app = (Application)clazz.newInstance();     
    
    // Application 和 context绑定
    app.attach(context);    
    return app;
}
//attach 就是将新建的 ContextImpl 赋值到 mBase，这个 ContextImpl 对象就是所有Application 内 Context 的具体实现，同时赋值一些其他的信息如 mLoadedApk。
final void attach(Context context) {    
    mBase = base;  
    mLoadedApk = ContextImpl.getImpl(context).mPackageInfo;
}
```

这时 Application 就创建好了，这点很重要，很多资料里说 Application 是在performLaunchActivity() 里创建的，因为 performLaunchActivity() 也有mInstrumentation.newApplication 这个调用，newApplication() 函数中可看出会先判断是否以及创建了 Application，如果之前已经创建，就返回已创建的 Application 对象。

## Activity 启动

上面 fork 进程时会发送 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令，在 app 进程中，收到 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令后调用 ApplicationThread.scheduleLaunchActivity()。

```Java
ApplicationThread.scheduleLaunchActivity()
//发送消息 H.LAUNCH_ACTIVITY。

sendMessage(H.LAUNCH_ACTIVITY, r);

ActivityThread.handleLaunchActivity()
//最终回调目标 Activity 的 onConfigurationChanged()，初始化 WindowManagerService。
//调用 ActivityThread.performLaunchActivity()

ActivityThread.performLaunchActivity() {
    //类似 Application 的创建过程，通过 classLoader 加载到 activity.
    activity = mInstrumentation.newActivity(classLoader, 
               component.getClassName(), r.intent);
    //因为 Activity 有界面，所以其 Context 是 ContextThemeWrapper 类型，但实现类仍是ContextImpl.
    Context appContext = createBaseContextForActivity(r, activity);
    activity.attach(context,mInstrumentation,application,...);
    //与 Window 进行关联
    
    //attach 后调用 activity 的 onCreate()方法。
    mInstrumentation.callActivityOnCreate(activity,...)
    
}
//在ActivityThread.handleLaunchActivity里，接着调用

Activity.performCreate() -> onCreate()
//最终回调目标 Activity 的 onCreate()。

Activity.setContentView()
//设置 layout 布局

ActivityThread.performResumeActivity()
//最终回调目标 Activity 的 onResume()。

```

与 Window 进行关联，具体过程详见：[Activity，Window，View 之间的关系](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity与Window与View之间的关系.md)

## 总结

Activity 的整体启动流程如图所示：

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity/activity_start.jpg" alt="Activity 启动过程"/>

- ActivityThread 是什么，它是一个线程吗，如何被启动的？

它不是一个线程，它是运行在 App 进程中的主线程中的一个方法中。当 App 进程创建时会执行 ActivityThread.main()，ActivityThread.main() 首先会创建 Looper 执行 Looper.prepareMainLooper()；然后创建 ActivityThread 并调用 ActivityThread.attach() 方法告诉 ActivityManagerService 我们创建了一个应用 并将 ApplicationThread 传给 ActivityManagerService；最后调用 Looper.loop()。

- ActivityClientRecord 与 ActivityRecord 是什么？

记录 Activity 相关信息，比如：Window，configuration，ActivityInfo 等。
ActivityClientRecord 是客户端的，ActivityRecord 是 ActivityManagerService 服务端的。

- Context 是什么，ContextImpl，ContextWapper 是什么？

Context 定义了 App 进程的相关环境，Context 是一个接口，ContextImpl 是子类，ContextWapper 是具体实现。

应用资源是在 Application 初始化的时候，也就是创建 Application，ContextImpl 的时候，ContextImpl 就包含这个路径，主要就是对就是 ResourcesManager 这个单例的引用。

可以看出每次创建 Application 和 Acitvity 以及 Service 时就会有一个 ContextImpl 实例，ContentProvider 和B roadcastReceiver 的 Context 是其他地方传入的。

所以 Context 数量 = Application 数量 + Activity 数量 + Service 数量，单进程情况下 Application 数量就是 1。

- Instrumentation 是什么？

管理着组件 Application，Activity，Service 等的创建，生命周期调用。

- Application 是什么，什么时候创建的，每个应用程序有几个 Application？

Application 是在 ActivityThread.handleBindApplication() 中创建的，一个进程只会创建一个 Application，但是一个应用如果有多个进程就会创建多个 Application 对象。

- 点击 Launcher 启动 Activity 和应用内部启动 Activity 的区别？

点击 Launcher 时会创建一个新进程来开启 Activity，而应用内打开 Activity，如果 Activity 不指定新进程，将在原来进程打开，是否开启新进程实在 ActivityManagerService 进行控制的，上面分析得到，每次开启新进程时会保存进程信息，默认为 应用包名 + 应用UID，打开 Activity 时会检查请求方的信息来判断是否需要新开进程。Launcher 打开 Activity 默认 ACTIVITY_NEW_TASK，新开一个 Activity 栈来保存 Activity 的信息。

- Activity 启动过程，onCreate()，onResume() 回调时机及具体作用？

Activity.onCreate() 完成了 App 进程，Application，Activity 的创建，调用 setContentView() 给 Activity 设置了 layout 布局。

Activity.onResume() 完成了 Activity 中 Window 与 WindowManager 的关联，并对所有子 View 进行渲染并显示。

## 参考资料

- [startActivity启动过程分析](http://gityuan.com/2016/03/12/start-activity/)
- [Android应用程序的Activity启动过程简要介绍和学习计划](http://blog.csdn.net/luoshengyang/article/details/6685853/)
- [Android 应用点击图标到Activity界面显示的过程分析](https://silencedut.github.io/2016/08/02/Android%20应用点击图标到Activity界面显示的过程分析/)
- 《深入理解 Android 内核设计思想》


## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！

