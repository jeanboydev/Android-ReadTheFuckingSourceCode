# Android - Activity 与 Window 与 View 之间的关系

## 概述

我们知道 Activity 启动后就可以看到我们写的 Layout 布局界面，Activity 从 setContentView() 到显示中间做了什么呢？下面我们就来分析下这个过程。

如不了解 Activity 的启动过程请参阅：[Activity 启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity启动过程.md)

本文主要对于以下问题进行分析：

- Window 是什么，一个 Activity 几个 Window？
- Activity 与 Window 与 View 之间什么关系？
- PhoneWindow，ViewRoot，DecorView 是什么？

## onCreate() - Window 创建过程

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_activity/app_start.png" alt=""/>

在 Activity 创建过程中执行 scheduleLaunchActivity() 之后便调用到了 handleLaunchActivity() 方法。

ActivityThread.handleLaunchActivity()：

```Java
private void handleLaunchActivity(ActivityClientRecord r, Intent customIntent) {
    handleConfigurationChanged(null, null);
    //初始化 WindowManagerService，主要是获取到 WMS 代理对象
    WindowManagerGlobal.initialize();
    //详情见下面分析
    Activity a = performLaunchActivity(r, customIntent);

    if (a != null) {
        r.createdConfig = new Configuration(mConfiguration);
        //详见下面分析 [onResume() - Window 显示过程]
        handleResumeActivity(r.token, false, r.isForward,
                !r.activity.mFinished && !r.startsNotResumed);
        ...
    }
    ...
}

...

private Activity performLaunchActivity(ActivityClientRecord r, Intent customIntent) {
    ...
    Activity activity = null;
    //获取 ClassLoader
    java.lang.ClassLoader cl = r.packageInfo.getClassLoader();
    //创建目标 Activity 对象
    activity = mInstrumentation.newActivity(
            cl, component.getClassName(), r.intent);
    StrictMode.incrementExpectedActivityCount(activity.getClass());
    r.intent.setExtrasClassLoader(cl);
    r.intent.prepareToEnterProcess();
    if (r.state != null) {
        r.state.setClassLoader(cl);
    }

    //创建 Application 对象
    Application app = r.packageInfo.makeApplication(false, mInstrumentation);
    if (activity != null) {
        Context appContext = createBaseContextForActivity(r, activity);
        CharSequence title = r.activityInfo.loadLabel(appContext.getPackageManager());
        Configuration config = new Configuration(mCompatConfiguration);
        //详情见下面分析
        activity.attach(appContext, this, getInstrumentation(), r.token,
                r.ident, app, r.intent, r.activityInfo, title, r.parent,
                r.embeddedID, r.lastNonConfigurationInstances, config,
                r.referrer, r.voiceInteractor);
        ...
        //回调 Activity.onCreate()
        if (r.isPersistable()) {
            mInstrumentation.callActivityOnCreate(activity, r.state, r.persistentState);
        } else {
            mInstrumentation.callActivityOnCreate(activity, r.state);
        }
        ...
    return activity;
}

...

final void attach(Context context, ActivityThread aThread, Instrumentation instr, IBinder token, int ident, Application application, Intent intent, ActivityInfo info, CharSequence title, Activity parent, String id, NonConfigurationInstances lastNonConfigurationInstances, Configuration config, String referrer, IVoiceInteractor voiceInteractor) {
    attachBaseContext(context);

    mWindow = new PhoneWindow(this); //创建 PhoneWindow
    mWindow.setCallback(this);
    mWindow.setOnWindowDismissedCallback(this);
    mWindow.getLayoutInflater().setPrivateFactory(this);
    ...
    mApplication = application; //所属的 Application
    ...
    //设置并获取 WindowManagerImpl 对象
    mWindow.setWindowManager(
            (WindowManager)context.getSystemService(Context.WINDOW_SERVICE),
            mToken, mComponent.flattenToString(),
            (info.flags & ActivityInfo.FLAG_HARDWARE_ACCELERATED) != 0);
    if (mParent != null) {
        mWindow.setContainer(mParent.getWindow());
    }
    mWindowManager = mWindow.getWindowManager();
    mCurrentConfig = config;
}
```

可看出 Activity 里新建一个 PhoneWindow 对象。在 Android 中，Window 是个抽象的概念， Android 中 Window 的具体实现类是 PhoneWindow，Activity 和 Dialog 中的 Window 对象都是 PhoneWindow。

同时得到一个 WindowManager 对象，WindowManager 是一个抽象类，这个 WindowManager 的具体实现是在 WindowManagerImpl 中，对比 Context 和 ContextImpl。

Window.setWindowManager：

```Java
public void setWindowManager(WindowManager wm, IBinder appToken, String appName, boolean hardwareAccelerated) { 
    ...    
    mWindowManager = ((WindowManagerImpl)wm).createLocalWindowManager(this);
    ...
}
```

每个 Activity 会有一个 WindowManager 对象，这个 mWindowManager 就是和 WindowManagerService(WMS) 进行通信，也是 WMS 识别 View 具体属于那个 Activity 的关键，创建时传入 IBinder 类型的 mToken。

```Java
mWindow.setWindowManager(...,mToken, ...,...)
```

这个 Activity 的 mToken，这个 mToken 是一个 IBinder，WMS 就是通过这个 IBinder 来管理 Activity 里的 View。

接着执行 onCreate() 中的 setContentView() 方法将我们写的 Layout 布局页面设置给 Activity。

Activity.setContentView()：

```Java
public void setContentView(@LayoutRes int layoutResID) {
    getWindow().setContentView(layoutResID);        
    initWindowDecorActionBar();    
}
```

PhoneWindow.setContentView()：

```Java
public void setContentView(int layoutResID) {
    ...    
    installDecor(); 
    ... 
}
```

PhoneWindow.installDecor()：

```Java
private void installDecor() {    
//根据不同的 Theme，创建不同的 DecorView，DecorView 是一个 FrameLayout 
}
```
这时只是创建了 PhoneWindow，和DecorView，但目前二者也没有任何关系，产生关系是在ActivityThread.performResumeActivity 中，再调用 r.activity.performResume()，调用 r.activity.makeVisible，将 DecorView 添加到当前的 Window 上。

## onResume() - Window 显示过程

ActivityThread.performResumeActivity()：

```Java
final void handleResumeActivity(IBinder token, boolean clearHide, boolean isForward, boolean reallyResume) {
    //执行到 onResume()
    ActivityClientRecord r = performResumeActivity(token, clearHide);

    if (r != null) {
        final Activity a = r.activity;
        boolean willBeVisible = !a.mStartedActivity;
        ...
        if (r.window == null && !a.mFinished && willBeVisible) {
            r.window = r.activity.getWindow();
            View decor = r.window.getDecorView();
            decor.setVisibility(View.INVISIBLE);
            ViewManager wm = a.getWindowManager();
            WindowManager.LayoutParams l = r.window.getAttributes();
            a.mDecor = decor;
            l.type = WindowManager.LayoutParams.TYPE_BASE_APPLICATION;
            l.softInputMode |= forwardBit;
            if (a.mVisibleFromClient) {
                a.mWindowAdded = true;
                wm.addView(decor, l);
            }

        }
        ...
        if (!r.activity.mFinished && willBeVisible
                && r.activity.mDecor != null && !r.hideForNow) {
            ...
            mNumVisibleActivities++;
            if (r.activity.mVisibleFromClient) {
                //添加视图，详见下面分析
                r.activity.makeVisible(); 
            }
        }

        //resume 完成
        if (reallyResume) {
              ActivityManagerNative.getDefault().activityResumed(token);
        }
    } else {
        ...
    }
}


public final ActivityClientRecord performResumeActivity(IBinder token, boolean clearHide) {
    ActivityClientRecord r = mActivities.get(token);
    if (r != null && !r.activity.mFinished) {
        ...
        //回调 onResume()
        r.activity.performResume();
        ...
    }
    return r;
}
```


Activity.makeVisible()：

```Java
void makeVisible() {
    if (!mWindowAdded) {
        ViewManager wm = getWindowManager();
        //详见下面分析
        wm.addView(mDecor, getWindow().getAttributes());
        mWindowAdded = true;
    }
    mDecor.setVisibility(View.VISIBLE);
}
```

WindowManager 的 addView 的具体实现在 WindowManagerImpl 中，而 WindowManagerImpl 的 addView 又会调用 WindowManagerGlobal.addView()。

WindowManagerGlobal.addView()：

```Java
public void addView(View view, ViewGroup.LayoutParams params,Display display, Window parentWindow) {
    ...
    ViewRootImpl root = new ViewRootImpl(view.getContext(), display);        
    view.setLayoutParams(wparams);    
    mViews.add(view);    
    mRoots.add(root);    
    mParams.add(wparams);        
    root.setView(view, wparams, panelParentView);
    ...
}
```

这个过程创建一个 ViewRootImpl，并将之前创建的 DecoView 作为参数传入，以后 DecoView 的事件都由 ViewRootImpl 来管理了，比如，DecoView 上添加 View，删除 View。ViewRootImpl 实现了 ViewParent 这个接口，这个接口最常见的一个方法是 requestLayout()。

ViewRootImpl 是个 ViewParent，在 DecoView 添加的 View 时，就会将 View 中的 ViewParent 设为 DecoView 所在的 ViewRootImpl，View 的 ViewParent 相同时，理解为这些 View 在一个 View 链上。所以每当调用 View 的 requestLayout()时，其实是调用到 ViewRootImpl，ViewRootImpl 会控制整个事件的流程。可以看出一个 ViewRootImpl 对添加到 DecoView 的所有 View 进行事件管理。

## 参考资料

- [以Window视角来看startActivity](http://gityuan.com/2017/01/22/start-activity-wms/)
- [Android视图框架Activity,Window,View,ViewRootImpl理解](https://silencedut.github.io/2016/08/10/Android视图框架Activity,Window,View,ViewRootImpl理解)
- 《深入理解 Android 内核设计思想》

