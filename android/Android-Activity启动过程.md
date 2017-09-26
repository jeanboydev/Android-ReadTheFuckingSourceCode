# Android - Activity 启动过程

## 概述

Activity 是四大组件之一，在应用启动的时候，一般情况下首先启动的就是 Activity。 下面就来讨论下 Activity 是如何启动的？

本篇文章需要 Binder 进程间通讯的知识，不了解的请先看下 [Binder 进程间通讯](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Binder进程间通讯.md)

## 启动流程

Activity 的整体启动流程如图所示：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_activity/activity_start.jpg" alt="Activity 启动过程"/>

## 1. 发送 START_ACTIVITY_TRANSACTION 命令

```Java
Intent intent = new Intent(this, TestActivity.class);
startActivity(intent);
```

这段代码大家已经很熟悉，通过追踪代码可以发现最后调用了 startActivityForResult()。

- startActivityForResult(intent, -1)

默认 requestCode = -1，也可通过调用 startActivityForResult() 传入 requestCode。 然后通过 MainThread 获取到 ApplicationThread 传入下面方法。

- execStartActivity()

通过 ActivityManagerNative.getDefault() 获取到 ActivityManagerService 的代理为进程通讯作准备。

- ActivityManagerProxy.startActivity()

调用代理对象的 startActivity() 方法，发送 START_ACTIVITY_TRANSACTION 命令。


## 2. 发送创建进程的请求

在 system_server 进程中的服务端 ActivityManagerService 收到 START_ACTIVITY_TRANSACTION 命令后进行处理，调用 startActivity() 方法。

- ActivityManagerService.startActivity() -> startActivityAsUser(intent, requestCode, userId)

通过 UserHandle.getCallingUserId() 获取到 userId 并调用 startActivityAsUser() 方法。

- ActivityStackSupervisor.startActivityMayWait() -> resolveActivity()

通过 intent 创建新的 intent 对象，即使之前 intent 被修改也不受影响。 然后调用 resolveActivity()。

然后通过层层调用获取到 ApplicationPackageManager 对象。

- PackageManagerService.resolveIntent() ->  queryIntentActivities()

获取 intent 所指向的 Activity 信息，并保存到 Intent 对象。

- PackageManagerService.chooseBestActivity()

当存在多个满足条件的 Activity 则会弹框让用户来选择。

- ActivityStackSupervisor.startActivityLocked()

获取到调用者的进程信息。 通过 Intent.FLAG_ACTIVITY_FORWARD_RESULT 判断是否需要进行 startActivityForResult 处理。 检查调用者是否有权限来调用指定的 Activity。 创建 ActivityRecord 对象，并检查是否运行 App 切换。

- ActivityStackSupervisor.startActivityUncheckedLocked() -> startActivityLocked()

进行对 launchMode 的处理，创建 Task 等操作。 启动 Activity 所在进程，已存在则直接 onResume()，不存在则创建 Activity 并处理是否触发 onNewIntent()。

launchMode 可参考 [Activity 启动模式](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity启动模式&IntentFilter匹配规则.md)

- ActivityStack.resumeTopActivityInnerLocked()

找到 resume 状态的 Activity，执行 startPausingLocked() 暂停该 Activity，同时暂停所有处于后台栈的 Activity，找不到 resume 状态的 Activity 则回桌面。

如果需要启动的 Activity 进程已存在，直接设置 Activity 状态为 resumed。 调用下面方法。

- ActivityStackSupervisor.startSpecificActivityLocked()

进程存在调用 realStartActivityLocked() 启动 Activity，进程不存在则调用下面方法。

## 3. fork 新进程

- ActivityManagerService.startProcessLocked()

进程不存在请求 Zygote 创建新进程。 创建成功后切换到新进程。


### 切换至 App 进程

进入 app 进程后将 ActivityThread 类加载到新进程，并调用 ActivityThread.main() 方法

- ActivityThread.main()

创建主线程的 Looper 对象，创建 ActivityThread 对象，ActivityThread.attach() 建立 Binder 通道，开启 Looper.loop() 消息循环。

- ActivityThread.attach()

开启虚拟机各项功能，创建 ActivityManagerProxy 对象，调用基于 IActivityManager 接口的 Binder 通道 ActivityManagerProxy.attachApplication()。

- ActivityManagerProxy.attachApplication()

发送 ATTACH_APPLICATION_TRANSACTION 命令

## 4. 发送 ATTACH_APPLICATION_TRANSACTION 命令

在 system_server 进程中的服务端 ActivityManagerService 收到 ATTACH_APPLICATION_TRANSACTION 命令后进行处理，调用 attachApplication()。

- ActivityMangerService.attachApplication() -> attachApplicationLocked()

首先会获取到进程信息 ProcessRecord。 绑定死亡通知，移除进程启动超时消息。 获取到应用 ApplicationInfo 并绑定应用 IApplicationThread.bindApplication(appInfo)。

然后检查 App 所需组件。

Activity: 检查最顶层可见的 Activity 是否等待在该进程中运行，调用 ActivityStackSupervisor.attachApplicationLocked()。

Service：寻找所有需要在该进程中运行的服务，调用 ActiveServices.attachApplicationLocked()。

Broadcast：检查是否在这个进程中有下一个广播接收者，调用 sendPendingBroadcastsLocked()。

此处讨论 Activity 的启动过程，只讨论 ActivityStackSupervisor.attachApplicationLocked() 方法。

## 5. 调用 realStartActivityLocked()

- ActivityStackSupervisor.attachApplicationLocked() -> realStartActivityLocked()

将该进程设置为前台进程 PROCESS_STATE_TOP，调用 ApplicationThreadProxy.scheduleLaunchActivity()。

- ApplicationThreadProxy.scheduleLaunchActivity()

发送 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令

## 6. 发送 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令

发送送完 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令，还会发送 BIND_APPLICATION_TRANSACTION 命令来创建 Application。

- ApplicationThreadProxy.bindApplication()

发送 BIND_APPLICATION_TRANSACTION 命令


### BIND_APPLICATION_TRANSACTION 命令处理

在 app 进程中，收到 BIND_APPLICATION_TRANSACTION 命令后调用 ActivityThread.bindApplication()。

- ActivityThread.bindApplication()

缓存 Service，初始化 AppBindData，发送消息 H.BIND_APPLICATION。

- ActivityThread.handleBindApplication()

设置进程名，获取 LoadedApk 对象，创建 ContextImpl 上下文，LoadedApk.makeApplication() 创建 Application 对象，调用 Application.onCreate() 回调方法。


### SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令处理

app 进程中，收到 SCHEDULE_LAUNCH_ACTIVITY_TRANSACTION 命令后调用 ApplicationThread.scheduleLaunchActivity()。

- ApplicationThread.scheduleLaunchActivity()

发送消息 H.LAUNCH_ACTIVITY。

## 7. 发送消息 H.LAUNCH_ACTIVITY

- ActivityThread.handleLaunchActivity()

最终回调目标 Activity 的 onConfigurationChanged()，初始化 WindowManagerService。

- ActivityThread.performLaunchActivity()

检查 Application 是否创建，最终回调目标 Activity 的 onCreate()。

## 8. handleResumeActivity

- ActivityThread.handleResumeActivity()

最终回调目标 Activity 的 onStart()，onResume()。

## 参考资料

- [startActivity启动过程分析](http://gityuan.com/2016/03/12/start-activity/)
- [ Android应用程序的Activity启动过程简要介绍和学习计划](http://blog.csdn.net/luoshengyang/article/details/6685853/)
- 《深入理解 Android 内核设计思想》