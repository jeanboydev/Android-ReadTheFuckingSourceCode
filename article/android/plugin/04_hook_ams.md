# Hook 实战之 Hook AMS

> 本文 Android 系统源码基于 9.0

我们知道新建一个 Activity 之后我们需要在 manifest 中注册，否则启动的时候就会崩溃，现在使用 Hook 的方法绕过检查来启动一个没有注册的 Activity。

如果我们不注册的话就会报下面的错误：

```java
Caused by: android.content.ActivityNotFoundException: Unable to find explicit activity class {com.jeanboy.app.hooktrainning/com.jeanboy.app.hooktrainning.UnregisterActivity}; have you declared this activity in your AndroidManifest.xml?
```

## 寻找第一个 Hook 点

```java
startActivity(new Intent(this, UnregisterActivity.class));
```

我们从 startActivity() 可以看到：

```java
@Override
public void startActivity(Intent intent) {
  this.startActivity(intent, null);
}

@Override
public void startActivity(Intent intent, @Nullable Bundle options) {
  if (options != null) {
    startActivityForResult(intent, -1, options);
  } else {
    startActivityForResult(intent, -1);
  }
}

public void startActivityForResult(@RequiresPermission Intent intent, int requestCode) {
  startActivityForResult(intent, requestCode, null);
}

public void startActivityForResult(@RequiresPermission Intent intent, int requestCode,
                                   @Nullable Bundle options) {
  if (mParent == null) {
    options = transferSpringboardActivityOptions(options);
    // 关键代码
    Instrumentation.ActivityResult ar =
      mInstrumentation.execStartActivity(
      this, mMainThread.getApplicationThread(), mToken, this,
      intent, requestCode, options);
    if (ar != null) {
      mMainThread.sendActivityResult(
        mToken, mEmbeddedID, requestCode, ar.getResultCode(),
        ar.getResultData());
    }
    if (requestCode >= 0) {
      mStartedActivity = true;
    }

    cancelInputsAndStartExitTransition(options);
  } else {
    if (options != null) {
      mParent.startActivityFromChild(this, intent, requestCode, options);
    } else {
      mParent.startActivityFromChild(this, intent, requestCode);
    }
  }
}
```

可以看到进入到了 Instrumentation 这个类中的 execStartActivity() 方法。

```java
public ActivityResult execStartActivity(
  Context who, IBinder contextThread, IBinder token, Activity target,
  Intent intent, int requestCode, Bundle options) {
  IApplicationThread whoThread = (IApplicationThread) contextThread;
  // ...
  try {
    intent.migrateExtraStreamToClipData();
    intent.prepareToLeaveProcess(who);
    int result = ActivityManager.getService()
      .startActivity(whoThread, who.getBasePackageName(), intent,
                     intent.resolveTypeIfNeeded(who.getContentResolver()),
                     token, target != null ? target.mEmbeddedID : null,
                     requestCode, 0, null, options);
    checkStartActivityResult(result, intent);
  } catch (RemoteException e) {
    throw new RuntimeException("Failure from system", e);
  }
  return null;
}
```

可以看到 ActivityManager.getService() 是拿到 ActivityManagerService 服务在本地的代理对象，然后通过它操作 ActivityManagerService 执行 startActivity() 方法返回一个结果，最后执行 checkStartActivityResult() 方法。

```java
public static void checkStartActivityResult(int res, Object intent) {
  if (!ActivityManager.isStartResultFatalError(res)) {
    return;
  }

  switch (res) {
    case ActivityManager.START_INTENT_NOT_RESOLVED:
    case ActivityManager.START_CLASS_NOT_FOUND:
      if (intent instanceof Intent && ((Intent)intent).getComponent() != null)
        throw new ActivityNotFoundException(
        "Unable to find explicit activity class "
        + ((Intent)intent).getComponent().toShortString()
        + "; have you declared this activity in your AndroidManifest.xml?");
      throw new ActivityNotFoundException(
        "No Activity found to handle " + intent);
    // ...
  }
}
```

在 checkStartActivityResult() 方法中可以看到，当 res 返回是 START_CLASS_NOT_FOUND 的时候就会报出一开始的错误了。因为我们传过去的 Activity ActivityManagerService 找不到。

所以我们就可以把检查方法之前的 ActivityManager.getService().startActivity() 作为一个 Hook 点，我们给它随便传一个注册过的 Acivity，这样就可以欺骗 ActivityManagerService 了。

## ActivityManager.getService()

```java
public static IActivityManager getService() {
  return IActivityManagerSingleton.get();
}

private static final Singleton<IActivityManager> IActivityManagerSingleton =
  new Singleton<IActivityManager>() {
  @Override
  protected IActivityManager create() {
    final IBinder b = ServiceManager.getService(Context.ACTIVITY_TASK_SERVICE);
    return IActivityManager.Stub.asInterface(b);
  }
};
```

- Singleton

```java
public abstract class Singleton<T> {
  public Singleton() { }
  private T mInstance;
  protected abstract T create();
  public final T get() {
    synchronized (this) {
      if (mInstance == null) {
        mInstance = create();
      }
      return mInstance;
    }
  }
}
```

可以看到 Singleton 是一个系统的单例类，`getService()` 方法调用的时候，就会 create() 方法，最终会调用 IActivityManagerSingleton 中的 create() 方法创建一个 IActivityManager 返回。

IActivityManager 就是 ActivityManagerService 在本地的代理对象。用来进行进程间的 Binder 通信。

## Hook IActivityManager

我们来 Hook IActivityManager，替换成我们自己的。

先定义一个空的 ProxyActivity，并在 AnroidManifest 中注册：

```java
public class ProxyActivity extends AppCompatActivity {

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_proxy);
  }
}
```

然后在 Application 中 Hook 住 ActivityManagerService。

```java
public class MainApplication extends Application {

  @Override
  public void onCreate() {
    super.onCreate();
    HookAMS.hookStartActivity(this);
  }
}
```

- HookAMS

```java
public class HookAMS {

  public static void hookStartActivity(final Context context) {
    try {
      // 获取到 ActivityTaskManager 的 Class 对象
      @SuppressLint("PrivateApi")
      Class<?> amClass = Class.forName("android.app.ActivityManager");
      // 获取到 IActivityTaskManagerSingleton 成员变量
      Field iActivityTaskManagerSingletonField = amClass.getDeclaredField("IActivityManagerSingleton");
      iActivityTaskManagerSingletonField.setAccessible(true);
      // 获取 IActivityTaskManagerSingleton 成员变量的值
      Object IActivityTaskManagerSingleton = iActivityTaskManagerSingletonField.get(null);

      // 获取 getService() 方法
      @SuppressLint("BlockedPrivateApi")
      Method getService = amClass.getDeclaredMethod("getService");
      getService.setAccessible(true);
      // 执行 getService() 方法
      final Object IActivityTaskManager = getService.invoke(null);

      // 获取到 IActivityTaskManager 的 Class 对象
      @SuppressLint("PrivateApi")
      Class<?> iamClass = Class.forName("android.app.IActivityManager");
      // 创建代理类 IActivityTaskManager
      Object proxyIActivityManager = Proxy.newProxyInstance(context.getClassLoader(), new Class[]{iamClass}, new InvocationHandler() {
        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
          if ("startActivity".equals(method.getName())) {
            Intent proxyIntent = new Intent(context, ProxyActivity.class);
            // startActivity 第三个参数为 Intent
            proxyIntent.putExtra("targetIntent", (Intent) args[2]);
            args[2] = proxyIntent;
          }
          return method.invoke(IActivityTaskManager, args);
        }
      });

      // 获取到 Singleton 的 Class 对象
      @SuppressLint("PrivateApi")
      Class<?> sClass = Class.forName("android.util.Singleton");
      // 获取到 mInstance 成员变量
      Field mInstanceField = sClass.getDeclaredField("mInstance");
      mInstanceField.setAccessible(true);
      // 赋值 proxyIActivityManager 给 mInstance 成员变量
      mInstanceField.set(IActivityTaskManagerSingleton, proxyIActivityManager);
    } catch (ClassNotFoundException | NoSuchFieldException | IllegalAccessException | NoSuchMethodException | InvocationTargetException e) {
      e.printStackTrace();
    }
  }
}
```

我们的目的很清楚，通过反射拿到 IActivityManager 的实例，然后把它替换成我们自己的 proxyIActivityManager。动态代理对象中，我们把 intent 替换成一个注册过的 Activity 也就是 ProxyActivity。现在我们就拦截住了，当我们跳转到 UnregisterActivity 这个没有注册的 Activity 的时候，就会先跳转到该 ProxyActivity。

当然这不是我们想要的效果，我们需要在检查完之后再给它替换回来，所以在检查完后还要 Hook 一个地方给它换回来。

## 寻找第二个 Hook 点

熟悉 Activity 的启动流程的都知道，ActivityManagerService 处理完成之后，会执行到 realStartActivityLocked()。最终会回到 ActivityThread 类中的 mH 这个 Handler 中进行最后的处理。

![Activity 启动流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/plugin/04.jpg)

```java
class H extends Handler {
  // ...
  public void handleMessage(Message msg) {
    switch (msg.what) {
      // ...
      case EXECUTE_TRANSACTION:
        final ClientTransaction transaction = (ClientTransaction) msg.obj;
        mTransactionExecutor.execute(transaction);
        if (isSystem()) {
          transaction.recycle();
        }
        break;
    }
    Object obj = msg.obj;
    if (obj instanceof SomeArgs) {
      ((SomeArgs) obj).recycle();
    }
  }
}
```

ClientTransaction 内部有一个 ClientTransactionItem 的集合。

```java
public class ClientTransaction implements Parcelable, ObjectPoolItem {
  private List<ClientTransactionItem> mActivityCallbacks;
  // ...
}
```

在 realStartActivityLocked() 方法中可以看到将一个 LaunchActivityItem 添加到 ClientTransaction 中的集合中，也就是 mActivityCallbacks 中。

```java
public class LaunchActivityItem extends ClientTransactionItem {
  private Intent mIntent;
  private int mIdent;
  private ActivityInfo mInfo;
  private Configuration mCurConfig;
  private Configuration mOverrideConfig;
  private CompatibilityInfo mCompatInfo;
  private String mReferrer;
  private IVoiceInteractor mVoiceInteractor;
  private int mProcState;
  private Bundle mState;
  private PersistableBundle mPersistentState;
  private List<ResultInfo> mPendingResults;
  private List<ReferrerIntent> mPendingNewIntents;
  private boolean mIsForward;
  private ProfilerInfo mProfilerInfo;
  private IBinder mAssistToken;
	// ...
}
```

LaunchActivityItem 中存储了 Activity 的各种信息，这里有一个 mIntent 参数，它现在的跳转是我们在上一个 Hook 点改变成的 ProxyActivity，所以这里我们需要重新给他还原会我们的 UnregisterActivity，这样才能顺利跳转到 UnregisterActivity 中。

因此，我们需要在执行 Handler 中的 handleMessage() 方法之前将它给改了。

我们知道 Handler 的消息分发机制中有一个 dispatchMessage() 方法：

```java
public void dispatchMessage(@NonNull Message msg) {
  if (msg.callback != null) {
    handleCallback(msg);
  } else {
    if (mCallback != null) {
      if (mCallback.handleMessage(msg)) {
        return;
      }
    }
    handleMessage(msg);
  }
}
```

Activity 的启动最终会执行 handleMessage() 方法，而在这个之前有一个判断，如果 mCallback 不为 null 就执行 mCallback.handleMessage(msg) 方法。所以我们可以给它传一个我们自己的 CallBack，在内部将 mIntent 给改了，然后返回 false 它还是会继续执行下面的 handleMessage 方法，这样就完成了替换。

## Hook ActivityThread

然后在 Application 中 Hook 住 ActivityThread。

```java
public class MainApplication extends Application {

  @Override
  public void onCreate() {
    super.onCreate();
    HookAMS.hookStartActivity(this);
    HookAMS.hookActivityThread();
  }
}
```

- hookActivityThread()

```java
public class HookAMS {
  // ...
  public static void hookActivityThread() {
    try {
      // 获取到 mH 对象
      @SuppressLint("PrivateApi")
      Class<?> atClass = Class.forName("android.app.ActivityThread");
      Field mHField = atClass.getDeclaredField("mH");
      mHField.setAccessible(true);
      // 获取到 ActivityThread 对象
      @SuppressLint("DiscouragedPrivateApi")
      Method currentActivityThreadMethod = atClass.getDeclaredMethod("currentActivityThread");
      Object currentActivityThread = currentActivityThreadMethod.invoke(null);
      Object mH = mHField.get(currentActivityThread);
      // 拿到 mCallback 替换成我们自己的
      Field mCallbackField = Handler.class.getDeclaredField("mCallback");
      mCallbackField.setAccessible(true);
      mCallbackField.set(mH, new MyCallback());
    } catch (ClassNotFoundException | NoSuchFieldException | NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
      e.printStackTrace();
    }
  }

  private static class MyCallback implements Handler.Callback {

    @Override
    public boolean handleMessage(@NonNull Message msg) {
      Object clientTransactionObj = msg.obj;

      try {
        @SuppressLint("PrivateApi")
        Class<?> laiClass = Class.forName("android.app.servertransaction.LaunchActivityItem");

        Field mActivityCallbacksField = clientTransactionObj.getClass().getDeclaredField("mActivityCallbacks");
        mActivityCallbacksField.setAccessible(true);
        List activityCallbackList = (List) mActivityCallbacksField.get(clientTransactionObj);
        if (activityCallbackList == null || activityCallbackList.size() == 0) {
          return false;
        }
        Object mLaunchActivityItem = activityCallbackList.get(0);
        if (!laiClass.isInstance(mLaunchActivityItem)) {
          return false;
        }
        Field mIntentField = laiClass.getDeclaredField("mIntent");
        mIntentField.setAccessible(true);
        // 获取代理的 Intent
        Intent proxyIntent = (Intent) mIntentField.get(mLaunchActivityItem);
        if (proxyIntent == null) {
          return false;
        }
        // 获取到前面传入的 targetIntent
        Intent targetIntent = proxyIntent.getParcelableExtra("targetIntent");
        if (targetIntent != null) {
          // 替换 Intent
          mIntentField.set(mLaunchActivityItem, targetIntent);
        }
      } catch (ClassNotFoundException | NoSuchFieldException | IllegalAccessException e) {
        e.printStackTrace();
      }
      return false;
    }
  }
}
```

这样就完成了对 ActivityManagerService 的欺骗，可以启动没有在 manifest 中注册过的 Activity 了。

## 参考资料

- [Andorid-Hook进阶](https://chsmy.github.io/2019/08/16/architecture/Andorid-Hook进阶/)
- [Android插件化——高手必备的Hook技术](https://juejin.im/post/5d7a0d045188250f871b8e9e)