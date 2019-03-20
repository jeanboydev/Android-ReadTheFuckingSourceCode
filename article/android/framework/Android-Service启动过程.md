# Android - Service 启动过程

## 概述

Service 启动过程与 Activity 启动过程比较相似，不了解 Activity 启动过程的可以先看一下：[Activity 启动过程]()。

Service 的启动分两种情况：startService，bindService。

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_service/service_start.png" alt=""/>

## startService

通常情况我们在调用 startService 启动 Service 是运行在 App 进程中的。下面主要讨论下运行在单独进程中的情况。

在 AndroidManifest 文件中把 Service 配置 android:process 上属性，Service 就可以启动在单独进程中了。

首先要明白一个问题，在 Activity 中使用的 startService 方法是定义在 Context 的抽象类中，它的真正实现者是 ContextImpl，所以我们首先进入 ContextImpl 类。

- ContextImpl.startService()

```Java
@Override
public ComponentName startService(Intent service) {
    warnIfCallingFromSystemProcess();
    return startServiceCommon(service, mUser);
 }

private ComponentName startServiceCommon(Intent service, UserHandle user) {
    try {
        validateServiceIntent(service);
        service.prepareToLeaveProcess();
        ComponentName cn = ActivityManagerNative.getDefault().
			startService(mMainThread.getApplicationThread(),
			service,service.resolveTypeIfNeeded(getContentResolver()), user.getIdentifier());
        //......
        return cn;
    } catch (RemoteException e) {
        return null;
    }
}
```

从 ContextImpl 类的 startService 开始，然后进入本类的 startServiceCommon 方法，并最终调用 ActivityManagerNative.getDefault() 对象的 startService 方法。其实这里的 ActivityManagerNative.getDefault() 就是 ActivityManagerProxy 对象。这里涉及到 Binder 相关知识，不了解的请看：[Binder 机制]()。

- ActivityManagerProxy.startService()

```Java
public ComponentName startService(IApplicationThread caller, Intent service,
            String resolvedType, int userId) throws RemoteException {
    Parcel data = Parcel.obtain();
    Parcel reply = Parcel.obtain();
    data.writeInterfaceToken(IActivityManager.descriptor);
    data.writeStrongBinder(caller != null ? caller.asBinder() : null);
    service.writeToParcel(data, 0);
    data.writeString(resolvedType);
    data.writeInt(userId);
    mRemote.transact(START_SERVICE_TRANSACTION, data, reply, 0);
    reply.readException();
    ComponentName res = ComponentName.readFromParcel(reply);
    data.recycle();
    reply.recycle();
    return res;
}
```

通过 Binder 调用 ActivityManagerNative 类中 onTransact 方法，其识别码为 START_SERVICE_TRANSACTION，并最终调用 ActivityManagerNative 的实现类 ActivityManagerService 的 startService 方法。

- ActivityManagerService.startService()

```Java
@Override
public ComponentName startService(IApplicationThread caller, Intent service,
            String resolvedType, int userId) {
    enforceNotIsolatedCaller("startService");
    //......
    synchronized(this) {
        final int callingPid = Binder.getCallingPid();
        final int callingUid = Binder.getCallingUid();
        final long origId = Binder.clearCallingIdentity();
        ComponentName res = mServices.startServiceLocked(caller, service,
                resolvedType, callingPid, callingUid, userId);
        Binder.restoreCallingIdentity(origId);
        return res;
    }
}
```

在这里调用 mServices 对象的 startServiceLocked 方法，这里的 mServices 对象是 ActiveServices 类。

- ActiveServices.startServiceLocked()

```Java
ComponentName startServiceLocked(IApplicationThread caller, Intent service, 
	String resolvedType, int callingPid, int callingUid, int userId) {

    //......
    ServiceLookupResult res = retrieveServiceLocked(service, resolvedType, 
		callingPid, callingUid, userId, true, callerFg);
    ServiceRecord r = res.record;
    //......
    //这里紧接着会调用 startServiceInnerLocked 方法
    return startServiceInnerLocked(smap, service, r, callerFg, addToStarting);
}


ComponentName startServiceInnerLocked(ServiceMap smap, Intent service,
            ServiceRecord r, boolean callerFg, boolean addToStarting) {

        //......
        synchronized (r.stats.getBatteryStats()) {
            r.stats.startRunningLocked();
        }
        //这里紧接着会调用 bringUpServiceLocked 方法
        String error = bringUpServiceLocked(r, service.getFlags(), callerFg, false);
        //......
}

```

首先通过 retrieveServiceLocked 方法来解析 service 这个 Intent，就是解析前面我们在 AndroidManifest.xml 定义的 Service 标签的 intent-filter 相关内容，然后将解析结果放在 res.record 中，再调用 startServiceInnerLocked 方法。startServiceInnerLocked 方法中会调用 bringUpServiceLocked 方法。

- ActiveServices.bringUpServiceLocked()

```Java

private final String bringUpServiceLocked(ServiceRecord r,
            int intentFlags, boolean execInFg, boolean whileRestarting) {

    //（1）这里如果当前的 ProcessRecord 不为 null，那就不需要重新创建进程，
	//而是调用 realStartServiceLocked 方法来启动 Service
    if (app != null && app.thread != null) {
                try {
                    app.addPackage(r.appInfo.packageName, r.appInfo.versionCode, mAm.mProcessStats);
                    realStartServiceLocked(r, app, execInFg);
                    return null;
                } catch (RemoteException e) {
                    Slog.w(TAG, "Exception when starting service " + r.shortName, e);
                }

                // If a dead object exception was thrown -- fall through to
                // restart the application.
            }

    //（2）如果是需要创建新进程，那么将调用 ActivityManagerService.startProcessLocked 方法来启动新进程
    if (app == null) {
            if ((app=mAm.startProcessLocked(procName, r.appInfo, true, intentFlags,
                    "service", r.name, false, isolated, false)) == null) {
                //......
                bringDownServiceLocked(r);
                return msg;
            }
            if (isolated) {
                r.isolatedProc = app;
            }
        }

    //最后将 ServiceRecord 保存到成员变量 mPendingServices 中
    if (!mPendingServices.contains(r)) {
            mPendingServices.add(r);
    }
}
```

这个方法比较重要，这里有两种选择，当 Service 所在的进程存在时，将调用realStartServiceLocked 方法来启动 Service，否则的话调用 startProcessLocked 方法来启动新进程。

- ActivityManagerService.startProcessLocked()

```Java
private final void startProcessLocked(ProcessRecord app, String hostingType, 
	String hostingNameStr, String abiOverride, String entryPoint, String[] entryPointArgs) {

    boolean isActivityProcess = (entryPoint == null);
    if (entryPoint == null) 
        entryPoint = "android.app.ActivityThread";
    checkTime(startTime, "startProcess: asking zygote to start proc");
    //通过 processName，uid 等启动新进程
    Process.ProcessStartResult startResult = Process.start(entryPoint, 
			app.processName, uid, uid, gids, debugFlags, mountExternal, 
			app.info.targetSdkVersion, app.info.seinfo, requiredAbi, 
			instructionSet, app.info.dataDir, entryPointArgs);
}
```

这里通过 Process 的 start 方法启动 ActivityThread 的新进程，我们进入该类的 main 方法。

- ActivityThread.main()

```Java
public static void main(String[] args) {
    //......

    Process.setArgV0("<pre-initialized>");

    Looper.prepareMainLooper();
    //创建 ActivityThread 对象，并调用其 attach 方法
    ActivityThread thread = new ActivityThread();
    thread.attach(false);

    if (sMainThreadHandler == null) {
        sMainThreadHandler = thread.getHandler();
    }

    if (false) {
        Looper.myLooper().setMessageLogging(new
                LogPrinter(Log.DEBUG, "ActivityThread"));
    }
    
    Looper.loop();
    throw new RuntimeException("Main thread loop unexpectedly exited");
}

private void attach(boolean system) {
    final IActivityManager mgr = ActivityManagerNative.getDefault();
    try {
        //这里调用了 ActivityManagerProxy.attachApplication 方法。
        mgr.attachApplication(mAppThread);
    } catch (RemoteException ex) {
        // Ignore
    }
}
```

在 Android 应用程序中，每一个进程对应一个 ActivityThread 实例，然后这里创建了 ActivityThread 对象并调用了其 attach 方法，在 attach 方法中又调用了 ActivityManagerProxy.attachApplication 方法。

- ActivityManagerProxy.attachApplication()

```Java
public void attachApplication(IApplicationThread app) throws RemoteException {
    Parcel data = Parcel.obtain();
    Parcel reply = Parcel.obtain();
    data.writeInterfaceToken(IActivityManager.descriptor);
    data.writeStrongBinder(app.asBinder());
    mRemote.transact(ATTACH_APPLICATION_TRANSACTION, data, reply, 0);
    reply.readException();
    data.recycle();
    reply.recycle();
}
```

通过 Binder 机制会调用 ActivityManagerNative 中的 onTransact 方法，其识别码为 ATTACH_APPLICATION_TRANSACTION，并最终调用 ActivityManagerService 中的 attachApplication 方法。

- ActivityManagerService.attachApplication()

```Java
@Override
public final void attachApplication(IApplicationThread thread) {
    synchronized (this) {
        int callingPid = Binder.getCallingPid();
        final long origId = Binder.clearCallingIdentity();
        //调用 attachApplicationLocked
        attachApplicationLocked(thread, callingPid);
        Binder.restoreCallingIdentity(origId);

        //......
    }
}

private final boolean attachApplicationLocked(IApplicationThread thread,
            int pid) {

    // See if the top visible activity is waiting to run in this process...
    if (normalMode) {
        try {
            if (mStackSupervisor.attachApplicationLocked(app)) {
                didSomething = true;
            }
        } catch (Exception e) {
            Slog.wtf(TAG, "Exception thrown launching activities in " + app, e);
            badApp = true;
        }
    }

    // Find any services that should be running in this process...
    if (!badApp) {
        try {
        //这里会调用 ActiveServices 对象的 attachApplicationLocked 方法
            didSomething |= mServices.attachApplicationLocked(app, processName);
        } catch (Exception e) {
            Slog.wtf(TAG, "Exception thrown starting services in " + app, e);
            badApp = true;
        }
    }
}
```

这里如果是启动 Service 将调用 ActiveServices 对象的 attachApplicationLocked 方法，而如果是启动 Activity 将调用 ActivityStackSupervisor 对象的 attachApplicationLocked 方法。

- ActiveServices.attachApplicationLocked() -> realStartServiceLocked()

```Java
private final void realStartServiceLocked(ServiceRecord r,
            ProcessRecord app, boolean execInFg) throws RemoteException {

    if (app.thread == null) {
            throw new RemoteException();
        }

    //......

    app.thread.scheduleCreateService(r, r.serviceInfo,
mAm.compatibilityInfoForPackageLocked(r.serviceInfo.applicationInfo),
                    app.repProcState);
}
```

此处的 app.thread 是一个 IApplicationThread 对象，而 IApplicationThread 的代理类是 ApplicationThreadProxy，我们进入 app.thread 对象的 scheduleCreateService 方法。

- ApplicationThreadProxy.scheduleCreateService()

```Java
public final void scheduleCreateService(IBinder token, ServiceInfo info, 
	CompatibilityInfo compatInfo, int processState) throws RemoteException {

    Parcel data = Parcel.obtain();
    data.writeInterfaceToken(IApplicationThread.descriptor);
    data.writeStrongBinder(token);
    info.writeToParcel(data, 0);
    compatInfo.writeToParcel(data, 0);
    data.writeInt(processState);
    mRemote.transact(SCHEDULE_CREATE_SERVICE_TRANSACTION, data, null,
            IBinder.FLAG_ONEWAY);
    data.recycle();
}
```

通过 Binder 对象调用 ApplicationThreadNative 的 onTransact 方法，在其方法中调用子类的 scheduleCreateService 方法，即最终调用 ApplicationThreadNative 的子类 ApplicationThread 的 scheduleCreateService 方法。

- ApplicationThread.scheduleCreateService()

```Java
public final void scheduleCreateService(IBinder token,  ServiceInfo info, 
	CompatibilityInfo compatInfo, int processState) {

    updateProcessState(processState, false);
    CreateServiceData s = new CreateServiceData();
    s.token = token;
    s.info = info;
    s.compatInfo = compatInfo;

    sendMessage(H.CREATE_SERVICE, s);
}
```

通过 Handler 发送 Message 来处理该操作，并进入到 H 的 handleMessage 方法中，其识别码为 CREATE_SERVICE。

- H.handleMessage()

```Java
private class H extends Handler {

    public void handleMessage(Message msg) {
        Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER, "serviceCreate");
        //这里调用 handleCreateService 方法
        handleCreateService((CreateServiceData)msg.obj);
        Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
    }
}
```

- ApplicationThread.handleCreateService()

```Java
private void handleCreateService(CreateServiceData data) {

    Service service = null;
    try {
        //（1）通过类加载器来加载 Service 对象
        java.lang.ClassLoader cl = packageInfo.getClassLoader();
        service = (Service) cl.loadClass(data.info.name).newInstance();
    } catch (Exception e) {
        //......
    }

    //（2）这里创建 ContextImpl 对象
    ContextImpl context = ContextImpl.createAppContext(this, packageInfo);
    context.setOuterContext(service);

    Application app = packageInfo.makeApplication(false, mInstrumentation);
    service.attach(context, this, data.info.name, data.token, app,
                    ActivityManagerNative.getDefault());
    //（3）这里调用 Service 的 onCreate 方法
    service.onCreate();
    mServices.put(data.token, service);
}
```

1. 处通过类加载器 ClassLoader 来加载 Service 对象，此处的 data.info.name 就是我们要启动的 Service，加载完成后需要将其强转换为 Service 对象，也就是说我们的 Service 必须要继承于 Service 基类。 
2. 处这里先创建一个 ContextImpl 对象，每个 Activity 和 Service 都有一个 Context 对象。 
3. 处这里调用 Service 的 onCreate 方法。

## bindService

- 如何 bind 一个 Service？

```Java
private void test(){
    Intent intent = new Intent(this, XXXService.class);
    // bindService 的具体实现在 ContextImpl
    // BIND_AUTO_CREATE 参数具体使用的代码 ActivityServices
    bindService(intent, conn, BIND_AUTO_CREATE);
}

private ServiceConnection conn = new ServiceConnection() {  

    @Override  
    public void onServiceConnected(ComponentName name, IBinder service) {  
       // 绑定成功
       ...
    }  

    @Override  
    public void onServiceDisconnected(ComponentName name) { 
      // 绑定结束 
       ...  
    }
}
```

- ContextImpl.bindServce()

```Java
@Override
public boolean bindService(Intent service, ServiceConnection conn,
        int flags) {
    // mMainThread.getHandler()，传入的 handle 是主线程的 Handle
    return bindServiceCommon(service, conn, flags, mMainThread.getHandler(),
            Process.myUserHandle());
}

private boolean bindServiceCommon(Intent service, ServiceConnection conn, 
	int flags, Handler handler, UserHandle user) {

    IServiceConnection sd;
    //...
    if (mPackageInfo != null) {
        // 1，将传入的 ServiceConnection 转化为 IServiceConnection 返回
        // mPackgeInfo 是 LoadedApk
        sd = mPackageInfo.getServiceDispatcher(conn, getOuterContext(), handler, flags);
    }
    validateServiceIntent(service);
    try {
        IBinder token = getActivityToken();
        ...
        // 2，Binder 调用 AMS 的 bindService 方法，下面具体分析
        int res = ActivityManagerNative.getDefault().bindService(
            mMainThread.getApplicationThread(), getActivityToken(), service,
            service.resolveTypeIfNeeded(getContentResolver()),
            sd, flags, getOpPackageName(), user.getIdentifier());
        return res != 0;
    } 
    //...
}
```

- LoadedApk

LoadedApk 对象是 Apk 文件在内存中的表示。 Apk 文件的相关信息，诸如 Apk 文件的代码和资源，甚至代码里面的 Activity，Service 等组件的信息我们都可以通过此对象获取。

```Java
public final IServiceConnection getServiceDispatcher(ServiceConnection c, 
	Context context, Handler handler, int flags) {

    synchronized (mServices) {
        LoadedApk.ServiceDispatcher sd = null;
        // private final ArrayMap<Context,
        // ArrayMap<ServiceConnection, LoadedApk.ServiceDispatcher>> mServices
        // 根据当前的 Context 获取 ArrayMap<ServiceConnection,  LoadedApk.ServiceDispatcher>
        ArrayMap<ServiceConnection, LoadedApk.ServiceDispatcher> map = mServices.get(context);
        if (map != null) {
            // 如果存在，尝试根据当前的 ServiceConnection 获取 ServiceDispatcher
            sd = map.get(c);
        }
        if (sd == null) {
            // 如果与 ServiceConnection 对应的 ServiceDispatcher 不存在，创建一个保存了当前 
			// ServiceConnection 的 ServiceDispatcher 对象，
            // 并将之前传入的主线的 Handle 保存，同时创建一个 InnerConnection 对象保存
            sd = new ServiceDispatcher(c, context, handler, flags);
            if (map == null) {
                map = new ArrayMap<ServiceConnection, LoadedApk.ServiceDispatcher>();
                mServices.put(context, map);
            }
            // 将该 ServiceConnection 与 ServiceDispatcher 关系保存
            map.put(c, sd);
        } else {
            // 如果最开始就获取到 ServiceDispatcher，比如多次 bindService，
            // 就会调用 ServiceDispatcher 的 validate 判断此次 bindService 是否合法
            // validate 的判断逻辑比较简单：
			// 1.判断当前的 context 是否和之前 bindService 的一样 
			// 2.判断当前 handler 是否是主线程的 handle
            // 以上两个条件都满足的情况下正常执行，反之抛出相应的异常
            sd.validate(context, handler);
        }
        return sd.getIServiceConnection();
    }
}
```

- ActivityManagerService.bindService()

```Java
public int bindService(IApplicationThread caller, IBinder token, Intent service, 
	String resolvedType, IServiceConnection connection, 
	int flags, String callingPackage, int userId) throws TransactionTooLargeException {

    //...
    synchronized(this) {
        // 调用 ActiveServices 的 bindServiceLocked 方法
        return mServices.bindServiceLocked(caller, token, service,
                resolvedType, connection, flags, callingPackage, userId);
    }
}
```

- ActiveServices.bindServiceLocked() -> bringUpServiceLocked() -> realStartServiceLocked()

```Java
private final void realStartServiceLocked(ServiceRecord r, ProcessRecord app, 
	boolean execInFg) throws RemoteException {
    //...
    try {
        //...
        // 第一步，调用 ApplicationThread 的 scheduleCreateService 方法，
		// 之后会实例化 Service 并调用 Service 的 onCreate 方法，这里的过程跟上面 startService 中一样。
        // 不会调用 onStartCommand
        app.thread.scheduleCreateService(r, r.serviceInfo, 
				mAm.compatibilityInfoForPackageLocked(r.serviceInfo.applicationInfo),
                app.repProcState);

    } 
    //...
    // 第二步，调用 requestServiceBindingLocked
    requestServiceBindingLocked(r, execInFg);
    updateServiceClientActivitiesLocked(app, null, true);

    // 第三步
    // If the service is in the started state, and there are no
    // pending arguments, then fake up one so its onStartCommand() will
    // be called.
    if (r.startRequested && r.callStart && r.pendingStarts.size() == 0) {
        r.pendingStarts.add(new ServiceRecord.StartItem(r, false, 
			r.makeNextStartId(), null, null));
    }
    // StartItem 的 taskRemoved 如果是 false 的话，
	// 调用下面方法会调用 Service 的 onStartCommand
    sendServiceArgsLocked(r, execInFg, true);
    //...
}

private final boolean requestServiceBindingLocked(ServiceRecord r, 
	IntentBindRecord i, boolean execInFg, boolean rebind) 
	throws TransactionTooLargeException {

    //...
    if ((!i.requested || rebind) && i.apps.size() > 0) {
        try {
            //...
            // 调用 ApplicationThread 的 scheduleBindService 方法
            r.app.thread.scheduleBindService(r, i.intent.getIntent(), rebind,
                    r.app.repProcState);
        } 
        //...
    }
    //...
    return true;
}
```

- ApplicationThread.scheduleBindService()

```Java
private void handleBindService(BindServiceData data) {
   // 根据 token 获取 Service token 具体分析
    Service s = mServices.get(data.token);
    if (s != null) {
        try {
            // rebind 具体分析
            if (!data.rebind) {
                // 调用 Service 的 onBind，返回给客户端调用的 Binder
                IBinder binder = s.onBind(data.intent);
                // 调用 AMS 的 publishService，进而通知客户端连接成功
                ActivityManagerNative.getDefault()
                    .publishService(data.token, data.intent, binder);
            } else {
                s.onRebind(data.intent);
                ActivityManagerNative.getDefault()
                    .serviceDoneExecuting(data.token, SERVICE_DONE_EXECUTING_ANON,
                     0, 0);
            }
            ensureJitEnabled();
        }
        ...
    }
}
```

调用 ApplicationThread 的 scheduleBindService，scheduleBindService 通过 mH 发送一个 H.BIND_SERVICE 消息，mH 收到该消息调用 handleBindService(BindServiceData data)。

## 总结

- startService

使用这种 start 方式启动的 Service 的生命周期如下：
onCreate() -> onStartCommand()（onStart()方法已过时） -> onDestory()

说明：如果服务已经开启，不会重复的执行 onCreate()， 而是会调用 onStart() 和onStartCommand()。
服务停止的时候调用 onDestory()。服务只会被停止一次。

特点：一旦服务开启跟调用者(开启者)就没有任何关系了。
开启者退出了，开启者挂了，服务还在后台长期的运行。
开启者不能调用服务里面的方法。

- bindService

使用这种 start 方式启动的 Service 的生命周期如下：
onCreate() -> onBind() -> onUnbind() -> onDestory()

注意：绑定服务不会调用 onStart() 或者 onStartCommand() 方法

特点：bind 的方式开启服务，绑定服务，调用者挂了，服务也会跟着挂掉。
绑定者可以调用服务里面的方法。


## 参考资料

- [startService 启动过程分析](http://gityuan.com/2016/03/06/start-service/)
- 《深入理解 Android 内核设计思想》


## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！

