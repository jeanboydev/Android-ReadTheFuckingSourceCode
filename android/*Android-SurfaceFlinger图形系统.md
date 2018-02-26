# Android - SurfaceFlinger 图形系统

## 概述

- [Android 系统启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-系统启动过程.md)
- [Activity 创建过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity启动过程.md)
- [Activity 与 Window 与 View 之间的关系](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity与Window与View之间的关系.md)

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/android-bootloader.png" alt=""/>

通过前面的知识我们知道了，Android 系统从按下开机键到桌面，从桌面点击 App 图标到 Activity 显示的过程。但是 Activity 是怎么显示在屏幕上的呢？下面我们就来讨论下这一过程。

## SurfaceFlinger 启动过程

SurfaceFlinger 启动过程：
<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_surfaceflinger/surfaceflinger_start.png" alt=""/>

SurfaceFlinger 进程是由 init 进程创建的，运行在独立的 SurfaceFlinger 进程中。init 进程读取 init.rc 文件启动 SurfaceFlinger。

```C
service surfaceflinger /system/bin/surfaceflinger
    class core
    user system
    group graphics drmrpc
    onrestart restart zygote
    writepid /dev/cpuset/system-background/tasks
```

SurfaceFlinger 的创建会执行 main() 方法：
main_surfaceflinger.cpp
```C
int main(int, char**) {
    ProcessState::self()->setThreadPoolMaxThreadCount(4);

    sp<ProcessState> ps(ProcessState::self());
    ps->startThreadPool();

    //实例化 surfaceflinger
    sp<SurfaceFlinger> flinger =  new SurfaceFlinger();

    setpriority(PRIO_PROCESS, 0, PRIORITY_URGENT_DISPLAY);
    set_sched_policy(0, SP_FOREGROUND);

    //初始化
    flinger->init();

    //发布 surface flinger，注册到 ServiceManager
    sp<IServiceManager> sm(defaultServiceManager());
    sm->addService(String16(SurfaceFlinger::getServiceName()), flinger, false);

    // 运行在当前线程
    flinger->run();

    return 0;
}
```

SurfaceFlinger 的实例化会执行到：onFirstRef()
```C
void SurfaceFlinger::onFirstRef() {
    mEventQueue.init(this);
}
```

onFirstRef() 中会创建 Handler 并初始化。
MessageQueue.cpp：
```C
void MessageQueue::init(const sp<SurfaceFlinger>& flinger) {
    mFlinger = flinger;
    mLooper = new Looper(true);
    mHandler = new Handler(*this);
}
```

然后会执行到 SurfaceFlinger::init()：
```C
void SurfaceFlinger::init() {
    Mutex::Autolock _l(mStateLock);

    //初始化 EGL，作为默认的显示
    mEGLDisplay = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    eglInitialize(mEGLDisplay, NULL, NULL);

    // 初始化硬件 composer 对象
    mHwc = new HWComposer(this, *static_cast<HWComposer::EventHandler *>(this));

    //获取 RenderEngine 引擎
    mRenderEngine = RenderEngine::create(mEGLDisplay, mHwc->getVisualID());

    //检索创建的 EGL 上下文
    mEGLContext = mRenderEngine->getEGLContext();

    //初始化非虚拟显示屏
    for (size_t i=0 ; i<DisplayDevice::NUM_BUILTIN_DISPLAY_TYPES ; i++) {
        DisplayDevice::DisplayType type((DisplayDevice::DisplayType)i);
        //建立已连接的显示设备
        if (mHwc->isConnected(i) || type==DisplayDevice::DISPLAY_PRIMARY) {
            bool isSecure = true;
            createBuiltinDisplayLocked(type);
            wp<IBinder> token = mBuiltinDisplays[i];

            sp<IGraphicBufferProducer> producer;
            sp<IGraphicBufferConsumer> consumer;
            //创建 BufferQueue 的生产者和消费者
            BufferQueue::createBufferQueue(&producer, &consumer,
                    new GraphicBufferAlloc());

            sp<FramebufferSurface> fbs = new FramebufferSurface(*mHwc, i, consumer);
            int32_t hwcId = allocateHwcDisplayId(type);
            //创建显示设备
            sp<DisplayDevice> hw = new DisplayDevice(this,
                    type, hwcId, mHwc->getFormat(hwcId), isSecure, token,
                    fbs, producer,
                    mRenderEngine->getEGLConfig());
            if (i > DisplayDevice::DISPLAY_PRIMARY) {
                hw->setPowerMode(HWC_POWER_MODE_NORMAL);
            }
            mDisplays.add(token, hw);
        }
    }

    getDefaultDisplayDevice()->makeCurrent(mEGLDisplay, mEGLContext);

    //当应用和 sf 的 vsync 偏移量一致时，则只创建一个 EventThread 线程
    if (vsyncPhaseOffsetNs != sfVsyncPhaseOffsetNs) {
        sp<VSyncSource> vsyncSrc = new DispSyncSource(&mPrimaryDispSync,
                vsyncPhaseOffsetNs, true, "app");
        mEventThread = new EventThread(vsyncSrc);
        sp<VSyncSource> sfVsyncSrc = new DispSyncSource(&mPrimaryDispSync,
                sfVsyncPhaseOffsetNs, true, "sf");
        mSFEventThread = new EventThread(sfVsyncSrc);
        mEventQueue.setEventThread(mSFEventThread);
    } else {
        //创建 DispSyncSource 对象
        sp<VSyncSource> vsyncSrc = new DispSyncSource(&mPrimaryDispSync,
                vsyncPhaseOffsetNs, true, "sf-app");
        //创建线程 EventThread
        mEventThread = new EventThread(vsyncSrc);
        //设置 EventThread
        mEventQueue.setEventThread(mEventThread);
    }

    //创建 EventControl
    mEventControlThread = new EventControlThread(this);
    mEventControlThread->run("EventControl", PRIORITY_URGENT_DISPLAY);

    //当不存在 HWComposer 时，则设置软件 vsync
    if (mHwc->initCheck() != NO_ERROR) {
        mPrimaryDispSync.setPeriod(16666667);
    }

    //初始化绘图状态
    mDrawingState = mCurrentState;

    //初始化显示设备
    initializeDisplays();

    //启动开机动画
    startBootAnim();
}
```

该方法主要功能是：
1. 初始化 EGL
2. 创建 HWComposer
3. 初始化非虚拟显示屏
4. 启动 EventThread 线程
5. 启动开机动画

创建 HWComposer：

```C
HWComposer::HWComposer(const sp<SurfaceFlinger>& flinger, EventHandler& handler):mFlinger(flinger), mFbDev(0), mHwc(0), mNumDisplays(1), mCBContext(new cb_context), mEventHandler(handler), mDebugForceFakeVSync(false) {
    ...
    bool needVSyncThread = true;
    int fberr = loadFbHalModule(); //加载 framebuffer 的 HAL 层模块
    loadHwcModule(); //加载 HWComposer 模块

    //标记已分配的 display ID
    for (size_t i=0 ; i<NUM_BUILTIN_DISPLAYS ; i++) {
        mAllocatedDisplayIDs.markBit(i);
    }

    if (mHwc) {
        if (mHwc->registerProcs) {
            mCBContext->hwc = this;
            mCBContext->procs.invalidate = &hook_invalidate;
            //VSYNC 信号的回调方法
            mCBContext->procs.vsync = &hook_vsync;
            if (hwcHasApiVersion(mHwc, HWC_DEVICE_API_VERSION_1_1))
                mCBContext->procs.hotplug = &hook_hotplug;
            else
                mCBContext->procs.hotplug = NULL;
            memset(mCBContext->procs.zero, 0, sizeof(mCBContext->procs.zero));
            //注册回调函数
            mHwc->registerProcs(mHwc, &mCBContext->procs);
        }

        //进入此处，说明已成功打开硬件 composer 设备，则不再需要 vsync 线程
        needVSyncThread = false;
        eventControl(HWC_DISPLAY_PRIMARY, HWC_EVENT_VSYNC, 0);
        ...
    }
    ...
    if (needVSyncThread) {
        //不支持硬件的 VSYNC，则会创建线程来模拟定时 VSYNC 信号
        mVSyncThread = new VSyncThread(*this);
    }
}
```

HWComposer 代表着硬件显示设备，注册了 VSYNC 信号的回调。VSYNC 信号本身是由显示驱动产生的，在不支持硬件的 VSYNC，则会创建“VSyncThread”线程来模拟定时 VSYNC 信号。

当硬件产生VSYNC信号时，则会发送消息，handler 收到消息进行处理。当 SurfaceFlinger 进程收到 VSync 信号后经层层调用，最终调用到该对象的 handleMessageRefresh() 方法。

SurfaceFlinger.cpp：
```C
void SurfaceFlinger::handleMessageRefresh() {
    ATRACE_CALL();
    preComposition();//处理显示设备与 layers 的改变，更新光标
    rebuildLayerStacks();//重建所有可见 Layer 列表，根据Z轴排序
    setUpHWComposer();//更新 HWComposer 图层
    doDebugFlashRegions(); 
    doComposition();//生成 OpenGL 纹理图像
    postComposition();//将图像传递到物理屏幕
}
```

## Surface 创建过程

Surface 创建过程：
<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_surfaceflinger/surface_create.png" alt=""/>

Surface 创建的过程就是 Activity 显示的过程，在 ActivityThread.handleResumeActivity() 中调用了 Activity.makeVisible()，我们接着看下 Activity 是怎么显示出来的。

Activity.makeVisible：
```Java
void makeVisible() {
    if (!mWindowAdded) {
        ViewManager wm = getWindowManager();//此处 getWindowManager 获取的是 WindowManagerImpl 对象
        wm.addView(mDecor, getWindow().getAttributes());
        mWindowAdded = true;
    }
    mDecor.setVisibility(View.VISIBLE);
}
```

WindowManagerImpl.java：
```Java
public void addView(@NonNull View view, @NonNull ViewGroup.LayoutParams params) {
    applyDefaultToken(params);
    mGlobal.addView(view, params, mDisplay, mParentWindow);
}
```

WindowManagerGlobal.java：
```Java
public void addView(View view, ViewGroup.LayoutParams params, Display display, Window parentWindow) {
    ...
    final WindowManager.LayoutParams wparams = (WindowManager.LayoutParams) params;
    //创建 ViewRootImpl
    ViewRootImpl root = new ViewRootImpl(view.getContext(), display);
    view.setLayoutParams(wparams);
    mViews.add(view);
    mRoots.add(root);
    mParams.add(wparams);
    //设置 View
    root.setView(view, wparams, panelParentView);
    ...
}
```

创建 ViewRootImpl：
```Java
public final class ViewRootImpl implements ViewParent,
        View.AttachInfo.Callbacks, ThreadedRenderer.DrawCallbacks {
    ...
    final Surface mSurface = new Surface(); //创建 Surface，此时 Surface 创建完什么都没有，详见下面分析
    ...
    public ViewRootImpl(Context context, Display display) {
        mContext = context;
        //获取 IWindowSession 的代理类
        mWindowSession = WindowManagerGlobal.getWindowSession();
        mDisplay = display;
        mThread = Thread.currentThread(); //主线程
        mWindow = new W(this);
        mChoreographer = Choreographer.getInstance();
        ...
    }
}
```

WindowManagerGlobal.java：
```Java
public static IWindowSession getWindowSession() {
    synchronized (WindowManagerGlobal.class) {
        if (sWindowSession == null) {
            try {
                //获取 IMS 的代理类
                InputMethodManager imm = InputMethodManager.getInstance();
                //获取 WMS 的代理类
                IWindowManager windowManager = getWindowManagerService();
                //经过 Binder 调用，最终调用 WMS
                sWindowSession = windowManager.openSession(
                        new IWindowSessionCallback.Stub() {...},
                        imm.getClient(), imm.getInputContext());
            } catch (RemoteException e) {
                ...
            }
        }
        return sWindowSession
    }
}
```

WindowManagerService.openSession：
```Java
public IWindowSession openSession(IWindowSessionCallback callback, IInputMethodClient client, IInputContext inputContext) {
    //创建 Session 对象
    Session session = new Session(this, callback, client, inputContext);
    return session;
}
```

再次经过 Binder 将数据写回 app 进程，则获取的便是 Session 的代理对象 IWindowSession。

创建完 ViewRootImpl 对象后，接下来调用该对象的 setView() 方法。
ViewRootImpl：
```Java
public void setView(View view, WindowManager.LayoutParams attrs, View panelParentView) {
  synchronized (this) {
  
    requestLayout(); //详见下面分析
    ...
    //通过 Binder调用，进入 system 进程的 Session
    res = mWindowSession.addToDisplay(mWindow, mSeq, mWindowAttributes,
          getHostVisibility(), mDisplay.getDisplayId(),
          mAttachInfo.mContentInsets, mAttachInfo.mStableInsets,
          mAttachInfo.mOutsets, mInputChannel);
    ...
  }
}
```

```Java
final class Session extends IWindowSession.Stub implements IBinder.DeathRecipient {

    public int addToDisplay(IWindow window, int seq, WindowManager.LayoutParams attrs, int viewVisibility, int displayId, Rect outContentInsets, Rect outStableInsets, Rect outOutsets, InputChannel outInputChannel) {
        //调用 WMS.addWindow
        return mService.addWindow(this, window, seq, attrs, viewVisibility, displayId,
                outContentInsets, outStableInsets, outOutsets, outInputChannel);
    }
}
```

WindowManagerService.java：
```Java
public int addWindow(Session session, IWindow client, int seq, WindowManager.LayoutParams attrs, int viewVisibility, int displayId, Rect outContentInsets, Rect outStableInsets, Rect outOutsets, InputChannel outInputChannel) {
    ...
    WindowToken token = mTokenMap.get(attrs.token);
    //创建 WindowState
    WindowState win = new WindowState(this, session, client, token,
                attachedWindow, appOp[0], seq, attrs, viewVisibility, displayContent);
    ...
    //调整 WindowManager 的 LayoutParams 参数
    mPolicy.adjustWindowParamsLw(win.mAttrs);
    res = mPolicy.prepareAddWindowLw(win, attrs);
    addWindowToListInOrderLocked(win, true);
    // 设置 input
    mInputManager.registerInputChannel(win.mInputChannel, win.mInputWindowHandle);
    //详见下面分析
    win.attach();
    mWindowMap.put(client.asBinder(), win);
    
    if (win.canReceiveKeys()) {
        //当该窗口能接收按键事件，则更新聚焦窗口
        focusChanged = updateFocusedWindowLocked(UPDATE_FOCUS_WILL_ASSIGN_LAYERS,
                false /*updateInputWindows*/);
    }
    assignLayersLocked(displayContent.getWindowList());
    ...
}

//WindowState.java
void attach() {
    mSession.windowAddedLocked();
}
```

创建 SurfaceSession 对象，并将当前 Session 添加到 WMS.mSessions 成员变量。
Session.java：
```Java
void windowAddedLocked() {
    if (mSurfaceSession == null) {
        mSurfaceSession = new SurfaceSession();
        mService.mSessions.add(this);
        if (mLastReportedAnimatorScale != mService.getCurrentAnimatorScale()) {
            mService.dispatchNewAnimatorScaleLocked(this);
        }
    }
    mNumWindow++;
}
```

SurfaceSession 的创建会调用 JNI，在 JNI 调用 nativeCreate()。
android_view_SurfaceSession.cpp：
```C
static jlong nativeCreate(JNIEnv* env, jclass clazz) {
    SurfaceComposerClient* client = new SurfaceComposerClient();
    client->incStrong((void*)nativeCreate);
    return reinterpret_cast<jlong>(client);
}
```

创建 SurfaceComposerClient 对象， 作为跟 SurfaceFlinger 通信的代理对象。
```C
SurfaceComposerClient::SurfaceComposerClient() {
    //getComposerService() 将返回 SF 的 Binder 代理端的 BpSurfaceFlinger 对象
    sp<ISurfaceComposer> sm(getComposerService());
    
    //先调用 SF 的 createConnection()，再调用_init
    _init(sm, sm->createConnection());
    if(mClient != 0) {
       Mutex::Autolock _l(gLock);
       
       //gActiveConnections 是全局变量，把刚才创建的 client 保存到这个 map 中去
       gActiveConnections.add(mClient->asBinder(), this);
    }
}
```

SurfaceFlinger.cpp：
```C
sp<ISurfaceFlingerClient>SurfaceFlinger::createConnection() {
    Mutex::Autolock _l(mStateLock);
    uint32_t token = mTokens.acquire();

    //先创建一个Client
    sp<Client> client = new Client(token, this);

    //把这个Client对象保存到mClientsMap中，token是它的标识。
    status_t err = mClientsMap.add(token, client);

    /*
    创建一个用于 Binder 通信的 BClient，BClient 派生于 ISurfaceFlingerClient，
    它的作用是接受客户端的请求，然后把处理提交给 SF，注意，并不是提交给 Client。
    Client 会创建一块共享内存，该内存由 getControlBlockMemory 函数返回。
    */
    sp<BClient> bclient = new BClient(this, token,client->getControlBlockMemory());
    return bclient;
}


Client::Client(ClientID clientID, constsp<SurfaceFlinger>& flinger):ctrlblk(0), cid(clientID), mPid(0), mBitmap(0), mFlinger(flinger) {
const int pgsize = getpagesize();
    //下面这个操作会使 cblksize 为页的大小，目前是4096字节
    constint cblksize = ((sizeof(SharedClient)+(pgsize-1))&~(pgsize-1));
    mCblkHeap = new MemoryHeapBase(cblksize, 0, "SurfaceFlinger Clientcontrol-block");

    ctrlblk = static_cast<SharedClient *>(mCblkHeap->getBase());
    if(ctrlblk) {
       new(ctrlblk) SharedClient;//原来 Surface 的 CB 对象就是在共享内存中创建的这个 SharedClient 对象
    }
}
```

SharedClient：
```C
class SharedClient {

public:
   SharedClient();
   ~SharedClient();
   status_t validate(size_t token) const;
   uint32_t getIdentity(size_t token) const;

private:
    Mutexlock;
    Condition cv; //支持跨进程的同步对象

    //NUM_LAYERS_MAX 为 31，SharedBufferStack 是什么？
    SharedBufferStack surfaces[ NUM_LAYERS_MAX ];

};

//SharedClient的构造函数，没什么新意，不如Audio的CB对象复杂
SharedClient::SharedClient():lock(Mutex::SHARED), cv(Condition::SHARED) {
}
```

一个 Client 最多支持 31 个显示层。每一个显示层的生产/消费步调都由会对应的 SharedBufferStack 来控制。而它内部就用了几个成员变量来控制读写位置。

SharedBufferStack.h：
```C
class  SharedBufferStack{
     ......
    //Buffer 是按块使用的，每个 Buffer 都有自己的编号，其实就是数组中的索引号。
    volatile int32_t head;     //FrontBuffer 的编号
    volatile int32_t available; //空闲 Buffer 的个数
    volatile int32_t queued;  //脏 Buffer 的个数，脏 Buffer 表示有新数据的 Buffer
    volatile int32_t inUse; //SF 当前正在使用的 Buffer 的编号   
    volatilestatus_t status; //状态码
     ......
  }
```

SF 的一个 Client 分配一个跨进程共享的 SharedClient 对象。这个对象有31个 SharedBufferStack 元素，每一个 SharedBufferStack 对应于一个显示层。

一个显示层将创建两个 Buffer，后续的 PageFlipping 就是基于这两个 Buffer 展开的。

接着看 SurfaceComposerClient 中这个_init函数：
```C
void SurfaceComposerClient::_init(
       const sp<ISurfaceComposer>& sm, constsp<ISurfaceFlingerClient>& conn) {
    mPrebuiltLayerState = 0;
    mTransactionOpen = 0;
    mStatus = NO_ERROR;
    mControl = 0;

    mClient = conn;// mClient 就是 BClient 的客户端
    mControlMemory =mClient->getControlBlock();
    mSignalServer = sm;// mSignalServer 就是 BpSurfaceFlinger
    //mControl 就是那个创建于共享内存之中的 SharedClient
    mControl = static_cast<SharedClient*>(mControlMemory->getBase());
}
```

创建完 ViewRootImpl 对象后，接下来调用该对象的 setView() 方法。在 setView() 中调用了 requestLayout() 方法我们来看下这个方法：
```Java
public void requestLayout() {
   checkThread();
   mLayoutRequested = true;
   scheduleTraversals();
}

public void scheduleTraversals() {
    if(!mTraversalScheduled) {
       mTraversalScheduled = true;
       sendEmptyMessage(DO_TRAVERSAL); //发送 DO_TRAVERSAL 消息
    }
}

public void handleMessage(Message msg) {
   switch (msg.what) {
    ......
    case DO_TRAVERSAL:
        ......
        performTraversals();//调用 performTraversals()
        ......
        break;
    ......
    }
}

private void performTraversals() {
    finalView host = mView;//还记得这mView吗？它就是 DecorView
    booleaninitialized = false;
    booleancontentInsetsChanged = false;
    booleanvisibleInsetsChanged;
    
    try {
        relayoutResult= // 1. 关键函数relayoutWindow
        relayoutWindow(params, viewVisibility,insetsPending);
    }
    ......
    draw(fullRedrawNeeded);// 2. 开始绘制
    ......
}

private int relayoutWindow(WindowManager.LayoutParams params, int viewVisibility, boolean insetsPending)throws RemoteException {
       //原来是调用 IWindowSession 的 relayout()，暂且记住这个调用
       int relayoutResult = sWindowSession.relayout(mWindow, params, (int) (mView.mMeasuredWidth * appScale + 0.5f),  (int) (mView.mMeasuredHeight * appScale + 0.5f), viewVisibility, insetsPending, mWinFrame, mPendingContentInsets, mPendingVisibleInsets, mPendingConfiguration, mSurface); //mSurface 做为参数传进去了。
       }
   ......
}

private void draw(boolean fullRedrawNeeded) {
    Surface surface = mSurface;//mSurface 是 ViewRoot 的成员变量
    ......
    Canvascanvas;

    try {
       int left = dirty.left;
       int top = dirty.top;
       int right = dirty.right;
       int bottom = dirty.bottom;

       //从 mSurface 中 lock 一块 Canvas
       canvas = surface.lockCanvas(dirty);
       ......
       mView.draw(canvas);//调用 DecorView 的 draw 函数，canvas 就是画布
       ......
       //unlock 画布，屏幕上马上就能看到 View 的样子了
       surface.unlockCanvasAndPost(canvas);
    }
    ......
}
```

在 ViewRoot 构造时，会创建一个 Surface，它使用无参构造函数，代码如下所示：
```Java
final Surface mSurface = new Surface();
```
此时创建完的 Surface 是空的，什么都没有。接着继续分析 relayoutWindow()，在 relayoutWindow() 中会调用 IWindowSession 的 relayout()，这是一个跨进程方法会调用到 WMS 中的 Session.relayout()，最后调用到 WindowManagerService.relayoutWindow()。
```Java
public int relayoutWindow(Session session,IWindow client,
           WindowManager.LayoutParams attrs, int requestedWidth,
           int requestedHeight, int viewVisibility, boolean insetsPending,
           Rect outFrame, Rect outContentInsets, Rect outVisibleInsets,
            Configuration outConfig, SurfaceoutSurface){
        .....

    try {
         //win 就是 WinState，这里将创建一个本地的 Surface 对象
        Surfacesurface = win.createSurfaceLocked();
        if(surface != null) {
            //先创建一个本地 surface，然后在 outSurface 的对象上调用 copyFrom
            //将本地 Surface 的信息拷贝到 outSurface 中，为什么要这么麻烦呢？
            outSurface.copyFrom(surface);
        ......
}
```

## Surface 显示过程

## 参考资料

- [资料标题](http://www.baidu.com)


