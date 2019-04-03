# 如何正确的使用 Service？

## 简介

Service（服务）是 Android 四大组件之一，它的主要作用是执行后台操作，Activity 提供了 UI 界面来跟用户交互，而 Service 则没有 UI 界面，所有的操作都是在后台完成。

Service 跟 Activity 一样也可以由其它应用程序启动，即使用户切换到了其它应用，Service 仍然保持在后台运行。

此外，一个组件可以与 Service 进行绑定（bind）来跟 Service 进行交互，甚至是进行进程间通信（IPC）。

通常情况下可以使用 Service 进行网络请求、播放音乐、文件 I/O 等操作。

## 创建服务

要创建一个 Service 首先需要继承 Service 来实现一个子类。

```java
public class TestService extends Service {

  @Override
  public void onCreate() {
    super.onCreate();
  }

  @Override
  public int onStartCommand(Intent intent, int flags,
                            int startId) {
    return super.onStartCommand(intent, flags, startId);
  }

  @Nullable
  @Override
  public IBinder onBind(Intent intent) {
    return null;
  }

  @Override
  public boolean onUnbind(Intent intent) {
    return super.onUnbind(intent);
  }

  @Override
  public void onDestroy() {
    super.onDestroy();
  }
}
```

类似于 Activity，所有的 Service 都要在 Manifest 里面进行声明，如下：

```xml
<manifest ... >
  ...
  <application ... >
    <service android:name="xxx.xxxs.TestService" />
    ...
  </application>
</manifest>
```

通过在 `<service>` 标签里将 `android:exported` 设置为 `false`。可以防止其他的程序来启动你的 Service。

## 启动服务

通常情况下有两种方式来启动 Service，`startService()` 和 `bindService()`。

### startService()

```java
Intent intent = new Intent(this, TestService.class);
startService(intent); // 开启服务
stopService(intent); // 停止服务
```

当组件通过调用 `startService()` 启动 Service 后，Service 就可以在后台无限期的运行，即使启动 Service 的组件被销毁也不受影响。

一般情况下 `startService()` 是执行单一操作，并且不会将执行结果返回给调用者。例如，它可能是下载文件或者上传文件，通常操作完成后会自动停止。

该方式允许多个组件同时对相同的 Service 进行 `startService()` 操作，但是如果只要有其中有一个组件调用了 `stopSelf()` 或 `stopService()`， 该 Service 就会被销毁。

### bindService()

```java
Intent intent = new Intent(this, TestService.class);
ServiceConnection connection = new ServiceConnection() {
  @Override
  public void onServiceConnected(ComponentName name, 
                                 IBinder service) {
  }

  @Override
  public void onServiceDisconnected(ComponentName name) {
  }
};
// 绑定服务
bindService(intent, connection, Context.BIND_AUTO_CREATE);
// 解绑服务
unbindService(aidlConnection);
```

当组件通过调用 `bindService()` 启动 Service 后，Service 就处于绑定状态了。这种方式提供了 client - service 的接口，可以让调用者与 Service 进行发送请求和返回结果的操作，甚至可以进行进程间的通信（IPC）。

只要有一个组件对该 Service 进行了绑定，那该 Service 就不会销毁。如果多个组件可以同时对一个 Service 进行绑定，只有所有绑定的该 Service 的组件都解绑后，该 Service 才会销毁。

尽管两种方式是分开讨论的，但是并不是互斥的关系，使用 `startService()` 启动了 Service 后，也是可以进行绑定的。

> 注意：虽然 Service 是在后台运行的，但其实还是在主线程中进行所有的操作。Service 启动时除非单独进行了定义，否则没有单独开启线程或者进程都是运行在主线程中。
>
> 所以任何能阻塞主线程的操作（例如：播放音乐或者网络请求），都应该在 Service 中单独开启新的线程来进行操作，否则很容易出现 ANR。

## 系统方法

在创建一个 Service 时，必须要去继承 Service，并且需要重写父类的一些方法来实现功能。以下是主要方法的介绍。

### onStartCommand()

当另一个组件（如：Activity）通过调用 `startService()` 来启动 Service 时，系统会调用该方法。一旦执行该方法，Service 就会启动并在后台无限期执行。

如果实现该方法，在 Service 执行完后，需要调用 stopSelf() 或 stopService() 来停结束Service。

如果只是会通过绑定的方式（bind）的方式来启动 Service 则不需要重写该方法。

### onBind()

系统会调用这个函数当某个组件（例如：activity，fragment）通过调用 `bindService()` 绑定的方式来启动 Service 的时候。在实现这个函数的时候，必须要返回一个 IBinder 的继承类，来与 Service 进行通信。

这个函数是默认必须要重写的，但是如果不想通过绑定的方式来启动 Service，则可以直接返回 `null`。

### onCreate()

系统会调用此方法在第一次启动 Service 的时候，用于初始化一些一次性的变量。如果 Service 已经启动了，则此方法就不会再别调用。

### onDestroy()

系统在 Service 已经不需要准备被销毁的时候会调用此方法。Service 中如有用到 thread、listeners、receivers 等的时候，应该将这些的清理方法写在此方法内。

## 生命周期

与 Activity 类似，Service 也有生命周期回调方法，可以实现这些方法来监控 Service 状态的变化来执行相关操作。

![Service 生命周期](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/03_service/01.png)

### startService()

`onCreate()` -> `onStartCommand()` -> `onDestroy()`

### bindService()

`onCreate()` -> `onBind()` -> `onUnbind()` -> `onDestroy()`

## 系统资源回收

当系统内存不足的时候，系统会强制回收一些 Activity 和 Service 来获取更多的资源给那些用户正在交互的程序或页面。当资源充足的时候可以通过  `onStartCommand()`  的返回值，来实现 Service 自动重启。

```java
public int onStartCommand(Intent intent, int flags, int startId) {
  return START_NOT_STICKY | START_STICKY | START_REDELIVER_INTENT;
}
```

### START_NOT_STICKY

当系统因回收资源而销毁了 Service，当资源再次充足时不再自动启动 Service，除非有未处理的 Intent 准备发送。

### START_STICKY

当系统因回收资源而销毁了 Service，当资源再次充足时自动启动 Service。而且再次调用 `onStartCommand()` 方法，但是不会传递最后一次的 Intent，相反系统在回调 `onStartCommand()` 的时候会传一个空 Intent，除非有未处理的 Intent 准备发送。

### START_REDELIVER_INTENT

当系统因回收资源而销毁了 Service，当资源再次充足时自动启动 Service，并且再次调用 `onStartCommand()` 方法，并会把最后一次 Intent 再次传递给 `onStartCommand()`，相应的在队列里的 Intent 也会按次序一次传递。此模式适用于下载等服务。

## IntentService

Service 本身默认是运行在主线程里的，所以如果在 Service 要进行一些会堵塞线程的操作，一定要将这些操作放在一个新的线程里。

为了满足后台运行异步线程的需求，Android 的框架提供了 IntentService。

IntentService 是 Service 的子类，并且所有的请求操作都是在异步线程里。如果不需要 Service 来同时处理多个请求的话，IntentService 将会是最佳的选择。

使用该服务只需要继承并重写 IntentService 中的 `onHandleIntent()` 方法，就可以对接受到的 `Intent` 做后台的异步线程操作了。

```java
public class TestIntentService extends IntentService {

  public TestIntentService() {
    super("TestIntentService");
  }

  public TestIntentService(String name) {
    super(name);
  }

  @Override
  public void onCreate() {
    super.onCreate();
  }

  @Override
  protected void onHandleIntent(@Nullable Intent intent) {
    //TODO: 耗时操作，运行在子线程中
  }

  @Override
  public void onDestroy() {
    super.onDestroy();
  }
}
```

## 前台服务

### 什么是前台服务？

前台服务是那些被认为用户知道（用户所认可的），且在系统内存不足的时候不允许系统杀死的服务。

前台服务必须给状态栏提供一个通知，它被放到正在运行（Ongoing）标题之下 —— 这就意味着通知只有在这个服务被终止或从前台主动移除通知后才能被解除。

### 为什么要使用前台服务？

在一般情况下，Service 几乎都是在后台运行，一直默默地做着辛苦的工作。但这种情况下，后台运行的Service系统优先级相对较低，当系统内存不足时，在后台运行的 Service 就有可能被回收。

那么，如果我们希望 Service 可以一直保持运行状态，且不会在内存不足的情况下被回收时，可以选择将需要保持运行的 Service 设置为前台服务。

> 例如：App中的**音乐播放服务**应被设置在前台运行（前台服务）——在 App 后台运行时，便于用户明确知道它的当前操作、在状态栏中指明当前歌曲信息、提供对应操作。

### 如何创建一个前台服务？

新建一个服务。

```java
public class ForegroundService extends Service {
  
  private static final int RESULT_CODE = 0;
  private static final int ID = 1;
  
  public ForegroundService() { }

  @Override
  public void onCreate() {
    super.onCreate();
    Intent intent = new Intent(this, MainActivity.class);
    PendingIntent pendingIntent = PendingIntent.getActivity(this, RESULT_CODE, 
                              intent, PendingIntent.FLAG_UPDATE_CURRENT);
    NotificationCompat.Builder builder;
    // 兼容 Android 8.0
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
      String channelId = "foreground_service";
      NotificationChannel channel = new NotificationChannel(channelId, 
                              "channel_1", NotificationManager.IMPORTANCE_HIGH);
      channel.enableLights(true);
      channel.setLightColor(Color.GREEN);
      channel.setShowBadge(true);
      NotificationManager notificationManager = 
        											getSystemService(NotificationManager.class);
      notificationManager.createNotificationChannel(channel);
      builder = new NotificationCompat.Builder(this, channelId);
    } else {
      builder = new NotificationCompat.Builder(this);
    }
    builder.setContentIntent(pendingIntent)
      .setContentTitle("这是前台通知标题")
      .setContentText("这是内容")
      .setWhen(System.currentTimeMillis())
      .setSmallIcon(R.mipmap.ic_launcher_round)
      .setLargeIcon(BitmapFactory.decodeResource(getResources(), 
                                                 R.mipmap.ic_launcher))
      .setPriority(NotificationManager.IMPORTANCE_HIGH)
      .setDefaults(Notification.DEFAULT_SOUND);

    startForeground(ID, builder.build());
  }
  
  @Override
  public int onStartCommand(Intent intent, int flags,
                            int startId) {
    return super.onStartCommand(intent, flags, startId);
  }

  @Override
  public IBinder onBind(Intent intent) {
    return super.onBind(intent);
  }
}
```

启动与停止前台服务

```java
Intent foregroundIntent = new Intent(this, ForegroundService.class);
startService(foregroundIntent); // 启动前台服务
stopService(foregroundIntent); // 停止前台服务
```

### 前台服务与普通服务的区别

- 前台 Service 的系统优先级更高、不易被回收；
- 前台 Service 会一直有一个正在运行的图标在系统的状态栏显示，下拉状态栏后可以看到更加详细的信息，非常类似于通知的效果。

## 服务保活

通过前面的介绍我们了解到 Service 是后台服务来执行一些特定的任务，但是当后台服务在系统资源不足的时候可能会回收销毁掉 Service。

那么如何让后台服务尽量不被杀死呢？基本解决思路如下：

### 提升 Service 的优先级

为防止 Service 被系统回收，可以尝试通过提高服务的优先级解决。优先级数值最高为 1000，数字越小，优先级越低。

```xml
<service android:name=".ui.service.TestService" >
  <intent-filter android:priority="1000"/>
</service>
```

### persistent 属性

在 Manifest.xml 文件中设置 persistent 属性为 true，则可使该服务免受 out-of-memory killer 的影响。但是这种做法一定要谨慎，系统服务太多将严重影响系统的整体运行效率。 

```xml
<application android:persistent="true">
</application>
```

该属性的特点如下：

- 在系统启动的时候会被系统启动起来。
- 在该 App 被强制杀掉后系统会重新启动该 App，这种情况只针对系统内置App，第三方安装的 App 不会被重启。

### 将服务改成前台服务

重写 onStartCommand 方法，使用 `startForeground(int, Notification)` 方法来启动 Service。利用 Android 的系统广播

利用 Android 的系统广播检查 Service 的运行状态，如果被杀掉就重启。系统广播是 `Intent.ACTION_TIME_TICK`，这个广播每分钟发送一次。我们可以每分钟检查一次 Service 的运行状态，如果已经被销毁了，就重新启动 Service。 

## 参考资料

- [官方文档 - 服务](https://developer.android.com/guide/components/services?hl=zh-cn)
- [Service 前台服务的使用](https://www.jianshu.com/p/5505390503fa)

