

# 电量性能优化

## 耗电设备

手机各个硬件模块的耗电量是不一样的，有些模块非常耗电，而有些模块则相对显得耗电量小很多。

电量消耗的计算与统计是一件麻烦而且矛盾的事情，记录电量消耗本身也是一个费电量的事情。唯一可行的方案是使用第三方监测电量的设备，这样才能够获取到真实的电量消耗。

### 屏幕

当设备处于待机状态时消耗的电量是极少的，以 Nexus 5 为例，打开飞行模式，可以待机接近 1 个月。可是点亮屏幕，味着系统的各组件要开始进行工作，界面也需要开始执行渲染，这会需要消耗很多电量。

### 蜂窝网络

通常情况下，使用移动网络传输数据，电量的消耗有三种状态：

- Full Power

能量最高的状态，移动网络连接被激活，允许设备以最大的传输速率进行操作。

- Low power

一种中间状态，对电量的消耗差不多是 Full power 状态下的 50%。

- Standby

最低的状态，没有数据连接需要传输，电量消耗最少。

总之，为了减少电量的消耗，在蜂窝移动网络下，最好做到批量执行网络请求，尽量避免频繁的间隔网络请求。

使用 Battery Historian 我们可以得到设备的电量消耗数据，如果数据中的移动蜂窝网络（Mobile Radio）电量消耗呈现下面的情况，间隔很小，又频繁断断续续的出现，说明电量消耗性能很不好：

![battery bad](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/01.png)

经过优化之后，如果呈现下面的图示，说明电量消耗的性能是良好的：

![battery good](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/02.png)

另外 WiFi 连接下，网络传输的电量消耗要比移动网络少很多，应该尽量减少移动网络下的数据传输，多在 WiFi 环境下传输数据。

![battery wifi](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/03.png)

那么如何才能够把任务缓存起来，做到批量化执行呢？我们可以使用 JobScheduler 来优化。

## 跟踪充电状态

我们可以通过下面的代码来获取手机的当前充电状态：

```java
IntentFilter filter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
Intent batteryStatus = this.registerReceiver(null, filter);
int chargePlug = batteryStatus.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1);
boolean acCharge = (chargePlug == BatteryManager.BATTERY_PLUGGED_AC);
if (acCharge) {
    Log.v(LOG_TAG, "The phone is charging!");
}
```

在上面的例子演示了如何立即获取到手机的充电状态，得到充电状态信息之后，我们可以有针对性的对部分代码做优化。

> 比如：我们可以判断只有当前手机为 AC 充电状态时 才去执行一些非常耗电的操作。

```java
private boolean checkForPower() {
  IntentFilter filter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
  Intent batteryStatus = this.registerReceiver(null, filter);

  int chargePlug = batteryStatus.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1);
  boolean usbCharge = (chargePlug == BatteryManager.BATTERY_PLUGGED_USB);
  boolean acCharge = (chargePlug == BatteryManager.BATTERY_PLUGGED_AC);
  boolean wirelessCharge = false;
  if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
    wirelessCharge = 
      (chargePlug == BatteryManager.BATTERY_PLUGGED_WIRELESS);
  }
  return (usbCharge || acCharge || wirelessCharge);
}
```

### 监听充电状态变化

在清单文件中注册一个 BroadcastReceiver，通过在一个 Intent 过滤器内定义 `ACTION_POWER_CONNECTED` 和 `ACTION_POWER_DISCONNECTED` 来同时侦听这两种事件。

```xml
<receiver android:name=".PowerConnectionReceiver">
  <intent-filter>
    <action android:name="android.intent.action.ACTION_POWER_CONNECTED"/>
    <action android:name="android.intent.action.ACTION_POWER_DISCONNECTED"/>
  </intent-filter>
</receiver>
```

创建监听充电状态变化的 PowerConnectionReceiver。

```java
public class PowerConnectionReceiver extends BroadcastReceiver {
  @Override
  public void onReceive(Context context, Intent intent) {
    int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS,
                                   BatteryManager.BATTERY_STATUS_UNKNOWN);
    String batteryStatus = "";
    switch (status) {
      case BatteryManager.BATTERY_STATUS_CHARGING:
        batteryStatus = "正在充电";
        break;
      case BatteryManager.BATTERY_STATUS_DISCHARGING:
        batteryStatus = "正在放电";
        break;
      case BatteryManager.BATTERY_STATUS_NOT_CHARGING:
        batteryStatus = "未充电";
        break;
      case BatteryManager.BATTERY_STATUS_FULL:
        batteryStatus = "充满电";
        break;
      case BatteryManager.BATTERY_STATUS_UNKNOWN:
        batteryStatus = "未知道状态";
        break;
    }
    Toast.makeText(context, "batteryStatus = " + batteryStatus, 
                   Toast.LENGTH_LONG).show();
    int plugged = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED,
                                     BatteryManager.BATTERY_PLUGGED_AC);
    String chargePlug = "";
    switch (plugged) {
      case BatteryManager.BATTERY_PLUGGED_AC:
        chargePlug = "AC充电";
        break;
      case BatteryManager.BATTERY_PLUGGED_USB:
        chargePlug = "USB充电";
        break;
      case BatteryManager.BATTERY_PLUGGED_WIRELESS:
        chargePlug = "无线充电";
        break;
    }
    Toast.makeText(context, "chargePlug=" + chargePlug, 
                   Toast.LENGTH_LONG).show();
  }
}
```

最后注册 PowerConnectionReceiver，这时当充电状态发生变化时 PowerConnectionReceiver 就会收到通知。

```java
IntentFilter intentFilter = new IntentFilter();
intentFilter.addAction(Intent.ACTION_BATTERY_CHANGED);
this.registerReceiver(new PowerConnectionReceiver(), intentFilter);
```

### 监听电池电量变化

在清单文件中注册一个 BroadcastReceiver，通过侦听 `ACTION_BATTERY_LOW` 和 `ACTION_BATTERY_OKAY`，每当设备电池电量不足或退出不足状态时，便会触发该接收器。

```xml
<receiver android:name=".BatteryLevelReceiver">
	<intent-filter>
  	<action android:name="android.intent.action.ACTION_BATTERY_LOW"/>
  	<action android:name="android.intent.action.ACTION_BATTERY_OKAY"/>
  </intent-filter>
</receiver>
```

创建监听电池电量变化的 BatteryLevelReceiver。

```java
public class BatteryLevelReceiver extends BroadcastReceiver {
  @Override
  public void onReceive(Context context, Intent intent) {
    // 当前剩余电量
    int level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
    // 电量最大值
    int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
    // 电量百分比
    float batteryPct = level / (float) scale;
    Log.d("BatteryLevelReceiver", "batteryPct = " + batteryPct);
    Toast.makeText(context, "batteryPct = " + batteryPct, 
                   Toast.LENGTH_LONG).show();
  }
}
```

最后注册 BatteryLevelReceiver，这时当电池电量发生变化时 BatteryLevelReceiver 就会收到通知。

```java
IntentFilter intentFilter = new IntentFilter();
intentFilter.addAction(Intent.ACTION_BATTERY_CHANGED);
this.registerReceiver(new BatteryLevelReceiver(), intentFilter);
```

通常，如果设备连接了交流充电器，您应该最大限度提高后台更新的频率；而如果设备是通过 USB 充电，则应降低更新频率，如果电池正在放电，则应进一步降低更新频率；在电池电量极低时停用所有后台更新。

## WakeLock

WakeLock 是一种锁的机制，只要有应用拿着这个锁，CPU 就无法进入休眠状态，一直处于工作状态。

> 比如，手机屏幕在屏幕关闭的时候，有些应用依然可以唤醒屏幕提示用户消息，这里就是用到了 Wakelock 锁机制，虽然手机屏幕关闭了，但是这些应用依然在运行着。

手机耗电的问题，大部分是开发人员没有正确使用这个锁，成为「待机杀手」。

Android 手机有两个处理器，一个叫 Application Processor（AP），一个叫 Baseband Processor（BP）。

AP 是 ARM 架构的处理器，用于运行 Linux + Android 系统；BP 用于运行实时操作系统（RTOS），通讯协议栈运行于 BP 的 RTOS 之上。非通话时间，BP 的能耗基本上在 5mA 左右，而 AP 只要处于非休眠状态，能耗至少在 50mA 以上，执行图形运算时会更高。另外 LCD 工作时功耗在 100mA 左右，WiFi 也在 100mA 左右。

一般手机待机时，AP、LCD、WIFI 均进入休眠状态，这时 Android 中应用程序的代码也会停止执行。

Android 为了确保应用程序中关键代码的正确执行，提供了 Wake Lock 的 API，使得应用程序有权限通过代码阻止 AP 进入休眠状态。但如果不领会 Android 设计者的意图而滥用 Wake Lock API，为了自身程序在后台的正常工作而长时间阻止 AP 进入休眠状态，就会成为待机电池杀手。

那么 Wake Lock API 具体有啥用呢？心跳包从请求到应答，断线重连重新登陆等关键逻辑的执行过程，就需要 Wake Lock 来保护。而一旦一个关键逻辑执行成功，就应该立即释放掉 Wake Lock 了。两次心跳请求间隔 5 到 10 分钟，基本不会怎么耗电。

### WakeLock 使用

```java
PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE); 
WakeLock wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,
                                   "MyWakelockTag");
```

`newWakeLock(int levelAndFlags, String tag)` 中 `PowerManager.PARTIIAL_WAKE_LOCK` 是一个标志位，标志位是用来控制获取的 WakeLock 对象的类型，主要控制 CPU 工作时屏幕是否需要亮着以及键盘灯需要亮着，标志位说明如下：

| **levelAndFlags**       | **CPU是否运行** | **屏幕是否亮着** | **键盘灯是否亮着** |
| ----------------------- | --------------- | ---------------- | ------------------ |
| PARTIAL_WAKE_LOCK       | 是              | 否               | 否                 |
| SCREEN_DIM_WAKE_LOCK    | 是              | 低亮度           | 否                 |
| SCREEN_BRIGHT_WAKE_LOCK | 是              | 高亮度           | 否                 |
| FULL_WAKE_LOCK          | 是              | 是               | 是                 |

> 特殊说明：自 API 等级 17 开始，FULL_WAKE_LOCK 将被弃用。应用应使用 **FLAG_KEEP_SCREEN_ON**。

WakeLock 类可以用来控制设备的工作状态。使用该类中的 acquire 可以使 CPU 一直处于工作的状态，如果不需要使 CPU 处于工作状态就调用 release 来关闭。

- 自动 release

如果我们调用的是 acquire(long timeout)，那么就无需我们自己手动调用 release() 来释放锁，系统会帮助我们在 timeout 时间后释放。

- 手动 release

如果我们调用的是 acquire() 那么就需要我们自己手动调用 release() 来释放锁。

最后使用 WakeLock 类记得加上如下权限：

```xml
<uses-permission android:name="android.permission.WAKE_LOCK" />   
```

> 注意：在使用该类的时候，必须保证 acquire 和 release 是成对出现的。

### 屏幕保持常亮

当设备从休眠状态中，被应用程序唤醒一瞬间会耗电过多，我们可以保持屏幕常亮来节省电量，代码声明：

```java
// 屏幕保持常亮
getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
// 一般不需要人为的去掉 FLAG_KEEP_SCREEN_ON 的 flag，
// windowManager 会管理好程序进入后台回到前台的的操作
//getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
```

或者，直接在布局中加上 keepScreenOn = true ：

```xml
<android.support.constraint.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:keepScreenOn="true"
    tools:context="com.jeanboy.app.batterysample.MainActivity">
</android.support.constraint.ConstraintLayout>
```

## JobScheduler

在 API 21，Google 提供了一个新叫做 Job Scheduler API 的组件来处理这样的场景。Job Scheduler API 允许同时执行多个任务，执行某些指定的任务时不需要考虑时机控制引起的电池消耗。

使用 [Job Scheduler](https://developer.android.com/reference/android/app/job/JobScheduler.html)，应用需要做的事情就是判断哪些任务是不紧急的，可以交给 Job Scheduler 来处理，Job Scheduler 集中处理收到的任务，选择合适的时间，合适的网络，再一起进行执行。

下面是使用 Job Scheduler 的一段简要示例，需要先有一个 JobService：

```java
public class MyJobService extends JobService {

  @Override
  public boolean onStartJob(JobParameters params) {
    Log.i("MyJobService", "Totally and completely working on job " 
          + params.getJobId());
    // 检查网络状态
    if (isNetworkConnected()) {
      new SimpleDownloadTask() .execute(params);
      // 返回 true，表示该工作耗时，
      // 同时工作处理完成后需要调用 onStopJob 销毁（jobFinished）
      return true;
    } else {
      Log.i("MyJobService", "No connection on job " + params.getJobId() 
            + "; sad face");
    }
    // 返回 false，任务运行不需要很长时间，到 return 时已完成任务处理
    return false;
  }

  @Override
  public boolean onStopJob(JobParameters params) {
    Log.i("MyJobService", "Something changed, so I'm calling it on job " 
          + params.getJobId());
    // 有且仅有 onStartJob 返回值为 true 时，才会调用 onStopJob 来销毁 job
    // 返回 false 来销毁这个工作
    return false;
  }

  private boolean isNetworkConnected() {
    ConnectivityManager connectivityManager =
      (ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);
    NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();
    return (networkInfo != null && networkInfo.isConnected());
  }
  
  private class SimpleDownloadTask extends AsyncTask<JobParameters,
  																										Void, String> {
    protected JobParameters mJobParam;

    @Override
    protected String doInBackground(JobParameters... params) {
      mJobParam = params[0];
      try {
        InputStream is = null;
        int len = 50;

        URL url = new URL("https://www.google.com");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setReadTimeout(10000); // 10 sec
        conn.setConnectTimeout(15000); // 15 sec
        conn.setRequestMethod("GET");
        //Starts the query
        conn.connect();
        int response = conn.getResponseCode();
        Log.d(LOG_TAG, "The response is: " + response);
        is = conn.getInputStream();

        // Convert the input stream to a string
        Reader reader = null;
        reader = new InputStreamReader(is, "UTF-8");
        char[] buffer = new char[len];
        reader.read(buffer);
        return new String(buffer);

      } catch (IOException e) {
        return "Unable to retrieve web page.";
      }
    }

    @Override
    protected void onPostExecute(String result) {
      // 当任务完成时，需要调用 jobFinished() 让系统知道完成了哪项任务
      jobFinished(mJobParam, false);
      Log.i("SimpleDownloadTask", result);
    }
  }
}
```

定义了 JobService 的子类后，然后需要在 AndroidManifest.xml 中进行声明：

```xml
<service android:name="pkgName.JobSchedulerService"
    android:permission="android.permission.BIND_JOB_SERVICE" />
```

最后模拟通过点击 Button 触发 N 个任务，交给 JobService 来处理：

```java
public class FreeTheWakelockActivity extends ActionBarActivity {
  public static final String LOG_TAG = "FreeTheWakelockActivity";

  TextView mWakeLockMsg;
  ComponentName mServiceComponent;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_wakelock);

    mWakeLockMsg = (TextView) findViewById(R.id.wakelock_txt);
    mServiceComponent = new ComponentName(this, MyJobService.class);
    Intent startServiceIntent = new Intent(this, MyJobService.class);
    startService(startServiceIntent);

    Button theButtonThatWakelocks = 
      (Button) findViewById(R.id.wakelock_poll);
    theButtonThatWakelocks.setText(R.string.poll_server_button);

    theButtonThatWakelocks.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        pollServer();
      }
    });
  }

  public void pollServer() {
    JobScheduler scheduler = 
      (JobScheduler) getSystemService(Context.JOB_SCHEDULER_SERVICE);
    for (int i = 0; i < 10; i++) {
      JobInfo jobInfo = new JobInfo.Builder(i, mServiceComponent)
        .setMinimumLatency(5000) // 5 seconds
        .setOverrideDeadline(60000) // 60 seconds
        .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY) // WiFi or data connections
        .build();

      mWakeLockMsg.append("Scheduling job " + i + "!\n");
      scheduler.schedule(jobInfo);
    }
  }
}
```

官方 demo 地址：https://github.com/googlesamples/android-JobScheduler

## Energy Profiler

Energy Profiler 是 [Android Profiler](https://developer.android.com/studio/preview/features/android-profiler.html) 中的一个组件，可帮助开发者找到应用程序能量消耗的位置。

Energy Profiler 通过监控 CPU、网络和 GPS 传感器的使用情况，并以图形化显示每个组件使用多少能量。Energy Profiler 还会显示可能影响能耗的系统事件（WakeLock、Alarms、Jobs 和 Location），Energy Profiler 不直接测量能耗，相反，它使用一种模型来估算设备上每种资源的能耗。

可以在 **View > Tool Windows > Android Profiler** 中打开 Energy Profiler 界面。

![Energy Profiler](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/04.png)

Energy Profiler 的具体使用可查看 [Android 开发文档 - 使用 Energy Profiler 检查能源使用情况](https://developer.android.com/studio/profile/energy-profiler)。

> Energy Profiler 支持 Android 8.0 (API 26) 及以上的系统，Android 8.0 (API 26) 以下请使用 Battery Historian。

## Battery Historian

Battery Historian 是一款由 Google 提供的 Android 系统电量分析工具，能够以网页形式展示手机的电量消耗过程。

GitHub 地址：https://github.com/google/battery-historian

> 本文以 macOS 环境为例，介绍 Battery Historian 的使用。
>
> Windows 环境请参考：[Battery Historian 2.0 for windows 环境搭建](http://www.07net01.com/linux/2016/01/1207924.html)。

### 安装 Docker

手动下载 Docker 安装包，下载链接：[https://download.docker.com/mac/stable/Docker.dmg](https://download.docker.com/mac/stable/Docker.dmg)。

安装好之后点击图标运行，在顶部菜单栏可以看到一个鲸鱼图标，说明 Docker 正在运行。

然后在控制台输入：

> $ docker --version

看到如下内容，说明 Docker 可以正常使用：

```text
Docker version 19.03.1, build 74b1e89
```

### 安装 Battery Historian

通过下面命令安装 Battery Historian：

> $ docker run -d -p 9999:9999 bhaavan/battery-historian

上面的步骤都完成之后就可以启动 Battery Historian 了，默认端口是 9999。

之后在浏览器中输入 `http://localhost:9999` 就可以看到效果，然后上传 bugreport 文件进行分析了。

![Battery Historian](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/05.png)

### 获取 bugreport

根据系统版本不同 bugreport 的获取方式略有差别：

如果 是Android 7.0 及以上版本，通过下面命令来获取 bugreport：

> $ adb bugreport bugreport.zip

如果是 Android 6.0 及以下版本，通过下面命令来获取 bugreport：

> $ adb bugreport > bugreport.txt

获取到 bugreport 文件之后，我们就可以将其上传到 Battery Historian 上进行分析，下面是它的输出结果。

![Battery Historian](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/06.png)

### 分析结果

在页面的下方我们可以查看这段时间内系统的状态 system stats，也可以选择某个应用查看应用的状态 app stats。

![systrm stats](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/07.png)

其中我们可以看到 `Device estimated power use` 中显示了估算的应用耗电量值为 `0.18%`。

Battery Historian 还有个比较功能，在首页选择 Switch to Bugreport Comparisor，然后就可以上传两个不同的 bugreport 文件，submit 之后就可以看到它们的对比结果了，这个功能用来分析同一个应用的两个不同版本前后的耗电量非常有用。

![bugreport](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/04_battery/08.png)

需要注意的是，一般开始统计数据之前需要使用下面的命令将以前的累积数据清空：

> $ adb shell dumpsys batterystats --enable full-wake-history
>
> $ adb shell dumpsys batterystats --reset

上面的操作相当于初始化操作，如果不这么做会有一大堆的干扰的数据，看起来会比较痛苦。

关于 bugreport 相关的知识推荐阅读 [Android adb bugreport 工具分析和使用](http://blog.csdn.net/createchance/article/details/51954142) 这篇文章，作者简单地从源码角度分析了 `adb bugreport` 命令的运行原理，结论是 bugreport 其实是启动了 dumpstate 服务来输出数据，其中数据来源包括：

- 系统属性
- `/proc` 和 `/sys` 节点文件
- 执行 shell 命令获得相关输出
- logcat 输出
- Android Framework Services 信息基本使用 dumpsys 命令通过 binder 调用服务中的 dump 函数获得信息

结果分析参考：https://testerhome.com/topics/3733

## 参考资料

- [YouTube - Android 性能优化典范第 2 季](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)
- [Udacity 学院 - Android 性能优化](https://www.udacity.com/course/ud825)
- [胡凯 - Android 性能优化之电量篇](http://hukai.me/android-performance-battery/)
- [Android 电量优化](http://wuxiaolong.me/2017/04/27/AndroidBattery/)
- [Android 开发文档 - Optimize for battery life](https://developer.android.google.cn/topic/performance/power)
- [Android 开发文档 - 使用 Energy Profiler 检查能源使用情况](https://developer.android.com/studio/profile/energy-profiler)
- [Android adb bugreport 工具分析和使用](http://blog.csdn.net/createchance/article/details/51954142)
- [Battery Historian 2.0 for windows 环境搭建](http://www.07net01.com/linux/2016/01/1207924.html)