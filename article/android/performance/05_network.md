# 网络性能优化

移动互联网时代，用户对网络越来越依赖。虽然网络环境在逐渐变好，但也对网络的应用提出了更高的要求，同时开发人员对网络的重视度却在下降。确实 WiFi 场景下用户的网络质量变好了，而且用户对网络流量消耗的敏感度也在下降。

由于对网络问题的忽视，在网络情况不好的情况下，用户体验会极度下降，这时网络性能优化变得尤为重要。作为一名移动开发者，面对复杂多变的移动网络我们该如何去优化呢？

## 优化哪些方面？

一个数据包从手机发出经过无线网络、基站、互联网最后到达我们的服务器，其中任何一个环节出现问题都会影响用户的体验。用户的网络环境、基站的负载能力、DNS 服务器、CDN 节点的连接速度等这些因素，对移动端应用来说不受控制。移动端的网络优化，主要分为以下三个方面：

- 速度

在网络正常或者良好的时候，怎样更好地利用带宽，进一步提升网络请求的速度。

- 弱网络

移动端网络复杂多变，在出现网络连接不稳定的时候，怎样最大程度保证网络的连贯性。

- 安全

网路安全不容忽视，怎样有效防止被第三方劫持、窃听甚至篡改。

除了这三个问题，我们还可能会关心网络请求造成的耗电、流量问题。对于速度、弱网络以及安全的优化，又该从哪些方面入手呢？首先我们应该搞清楚一个网络请求的整个过程（对这个过程不熟悉的小伙伴，推荐看下《图解 HTTP》）。

![网络请求](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/05_network/01.png)



由上图可以看到，整个网络请求主要分为几个步骤，而整个请求耗时可以细分到每一个步骤里面。

- DNS 解析

通过 DNS 服务器，拿到对应域名的 IP 地址。在这个步骤，我们比较关注 DNS 解析耗时情况、运营商 LocalDNS 的劫持、DNS 调度这些问题。

- 创建连接

跟服务器建立连接，这里包括 TCP 三次握手、TLS 密钥协商等工作。多个 IP/端口该如何选择、是否要使用 HTTPS、能否可以减少甚至省下创建连接的时间，这些问题都是我们优化的关键。

- 发送/接收数据

在成功建立连接之后，就可以愉快地跟服务器交互，进行组装数据、发送数据、接收数据、解析数据。我们关注的是，如何根据网络状况将带宽利用好，怎样快速地侦测到网络延时，在弱网络下如何调整包大小等问题。

- 关闭连接

连接的关闭看起来非常简单，其实这里的水也很深。这里主要关注主动关闭和被动关闭两种情况，一般我们都希望客户端可以主动关闭连接。

所谓网络优化，就是围绕速度、弱网络、安全这三个核心内容，减少每一个步骤的耗时，打造快速、稳定且安全的高质量网络。

## 网络库

在实际的开发工作中，我们很少会像《UNIX 网络编程》那样直接去操作底层的网络接口，一般都会使用网络库。Square 出品的 [OkHttp](https://github.com/square/okhttp) 是目前最流行的 Android 网络库，它还被 Google 加入到 Android 系统内部，为广大开发者提供网络服务。

网络库屏蔽的下层复杂的网络接口，让我们可以更高效的使用网络请求，极大的提高了我们的开发效率。我经常看到一些开发者会使用基于网络库再次封装的开源库，这里很不建议开发者使用这些库。

首先不清楚这些库是否能完全符合我们的需求；然后这些库的质量参差不齐，往往在使用中遇到问题无法快速修复。这里强烈建议大家使用一手资源，推荐自己封装，不仅可以提升开发效率，还可以提高下自己的编码水平。

### 大平台网络库

据了解业内大厂[蘑菇街](https://www.infoq.cn/article/mogujie-app-chromium-network-layer?useSponsorshipSuggestions=true%2F)、头条、UC 浏览器都在 [Chromium](https://chromium.googlesource.com/chromium/src/+/master/components/cronet/) 网络库上做了二次开发，而微信 [Mars](https://github.com/Tencent/mars) 在弱网络方面做了大量优化，拼多多、虎牙、链家、美丽说这些应用都在使用 Mars。

下面我们来一起对比下各个网络库的核心实现。

![网络库](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/05_network/02.png)

为什么大厂都不使用 OkHttp 呢？主要是因为它不支持跨平台，对于大型应用来说跨平台是非常重要的。我们不希望所有的优化 Android 和 iOS 都要各自去实现一套，不仅浪费人力而且还容易出现问题。

对于大厂来说，不能只局限在客户端网络库的双端统一上，网络优化不仅仅是客户端的事情，所以一般都有统一的网络中台，它负责提供前台一整套网络解决方案。

阿里的 [ACCS](https://www.infoq.cn/article/taobao-mobile-terminal-access-gateway-infrastructure)、蚂蚁的 [mPaas](https://mp.weixin.qq.com/s/nz8Z3Uj9840KHluWjwyelw)、携程的[网络服务](https://www.infoq.cn/article/how-ctrip-improves-app-networking-performance)都是公司级的网络中台服务，这样所有的网络优化可以让整个集团的所有接入应用受益。

## 监听网络状态

根据网络状态对网络请求进行区别对待，2G 与 WiFi 状态下网络质量肯定是不一样的，那对应的网络策略也应该是不一样的。

> 例如：在 WiFi 场景下可以进行数据的预取、一些统计的集中上传等；而在 2G 场景下此类操作以及网络请求的次数策略都应该调低。

### 网络是否连接

通过 ConnectivityManager 可以获取当前是否已连接网络。

```java
public static boolean isNetworkConnected(Context context) {
  if (context == null) return false;
  ConnectivityManager manager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
  if (manager == null) return false;
  NetworkInfo networkInfo = manager.getActiveNetworkInfo();
  if (networkInfo == null) return false;
  return networkInfo.isAvailable() && networkInfo.isConnected();
}
```

isAvailable() 与 isConnected() 的区别：

| 状态                                           | isConnected() | isAvailable() |
| ---------------------------------------------- | :-----------: | :-----------: |
| 显示连接已保存，但标题栏没有，即没有实质连接上 |     false     |     true      |
| 显示连接已保存，标题栏也有已连接上的图标       |     true      |     true      |
| 选择不保存后                                   |     false     |     true      |
| 选择连接，在正在获取 IP 地址时                 |     false     |     false     |

### 网络连接类型

通过 NetworkInfo 中的 getNetworkType() 方法可以获取当前网络类型。

```java
public static final int NETWORK_NONE = 0;
public static final int NETWORK_WIFI = 1;
public static final int NETWORK_MOBILE = 10;
public static final int NETWORK_2G = 12;
public static final int NETWORK_3G = 13;
public static final int NETWORK_4G = 14;
/**
 * 获取当前的网络状态
 *
 * @param context
 * @return 没有网络:0; WIFI:1; 手机网络:10; 2G:12; 3G:13; 4G:14;
 */
public static int getNetworkType(Context context) {
  ConnectivityManager connectivityManager = (ConnectivityManager) 
    						context.getSystemService(Context.CONNECTIVITY_SERVICE);
  if (connectivityManager == null) return NETWORK_NONE;

  NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();
  if (networkInfo == null || !networkInfo.isAvailable()) 
    return NETWORK_NONE;

  int type = networkInfo.getType();
  if (type == ConnectivityManager.TYPE_WIFI) {
    return NETWORK_WIFI; // WiFi
  }

  if (type == ConnectivityManager.TYPE_MOBILE) {
    TelephonyManager telephonyManager = (TelephonyManager)
      					context.getSystemService(Context.TELEPHONY_SERVICE);
    if (telephonyManager == null) return NETWORK_NONE;

    int networkType = telephonyManager.getNetworkType();
    switch (networkType) {
        // 2G
      case TelephonyManager.NETWORK_TYPE_GPRS:
      case TelephonyManager.NETWORK_TYPE_CDMA:
      case TelephonyManager.NETWORK_TYPE_EDGE:
      case TelephonyManager.NETWORK_TYPE_1xRTT:
      case TelephonyManager.NETWORK_TYPE_IDEN:
        return NETWORK_2G;
        // 3G
      case TelephonyManager.NETWORK_TYPE_EVDO_A:
      case TelephonyManager.NETWORK_TYPE_UMTS:
      case TelephonyManager.NETWORK_TYPE_EVDO_0:
      case TelephonyManager.NETWORK_TYPE_HSDPA:
      case TelephonyManager.NETWORK_TYPE_HSUPA:
      case TelephonyManager.NETWORK_TYPE_HSPA:
      case TelephonyManager.NETWORK_TYPE_EVDO_B:
      case TelephonyManager.NETWORK_TYPE_EHRPD:
      case TelephonyManager.NETWORK_TYPE_HSPAP:
        return NETWORK_3G;
        // 4G
      case TelephonyManager.NETWORK_TYPE_LTE:
        return NETWORK_4G;
      default:
        return NETWORK_MOBILE;
    }
  }
  return NETWORK_NONE;
}
```

### 监听网络变化

首先，创建一个 NetworkReceiver。

```java
public class NetworkReceiver extends BroadcastReceiver {

  @Override
  public void onReceive(Context context, Intent intent) {
    Log.d("NetworkReceiver", "网络发生变化");
    String action = intent.getAction();
    if (ConnectivityManager.CONNECTIVITY_ACTION.equals(action)) {
      int networkType = NetworkUtil.getNetworkType(context);
      Log.e("NetworkReceiver", "networkType = " + networkType);
      Toast.makeText(context, "当前网络：" + networkType,
                     Toast.LENGTH_SHORT).show();
    }
  }
}
```

然后，在 AndroidManifest.xml 文件中注册 NetworkReceiver。

```xml
<receiver android:name=".ui.broadcast.NetworkReceiver">
  <intent-filter>
    <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    <action android:name="android.net.wifi.WIFI_STATE_CHANGED" />
    <action android:name="android.net.wifi.STATE_CHANGE" />
  </intent-filter>
</receiver>
```

并添加监听网络需要的相关权限。

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
```

在 Android 7.0 之后静态注册广播的方式被取消了，所以我们这里还需要采用动态注册的方式。

```java
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
  NetworkReceiver networkReceiver = new NetworkReceiver();
  IntentFilter filter = new IntentFilter();
  filter.addAction(ConnectivityManager.CONNECTIVITY_ACTION);
  filter.addAction(WifiManager.WIFI_STATE_CHANGED_ACTION);
  filter.addAction(WifiManager.NETWORK_STATE_CHANGED_ACTION);
  registerReceiver(networkReceiver, filter);
}
```

## 设置网络缓存

在一定时间内，对服务端返回的数据进行缓存，比如一些接口的数据不会更新（10 分钟或更久变化一次），我们就可以缓存该接口的数据，设定有效时间，可以减少不必要的流量消耗。

Android 系统上关于网络请求的 Http Response Cache 是默认关闭的，这样会导致每次即使请求的数据内容是一样的也会需要重复被调用执行，效率低下。

我们可以通过下面的代码示例开启 [HttpResponseCache](http://developer.android.com/reference/android/net/http/HttpResponseCache.html)。

```java
protected void onCreate(Bundle savedInstanceState) {
  // ...
  try {
    File httpCacheDir = new File(context.getCacheDir(), "http");
    long httpCacheSize = 10 * 1024 * 1024; // 10 MiB
    HttpResponseCache.install(httpCacheDir, httpCacheSize);
  } catch (IOException e) {
    Log.i(TAG, "HTTP response cache installation failed:" + e);
  }
}

protected void onStop() {
  // ...
  HttpResponseCache cache = HttpResponseCache.getInstalled();
  if (cache != null) {
    cache.flush();
  }
}
```

开启 Http Response Cache 之后，Http 操作相关的返回数据就会缓存到文件系统上，不仅仅是主程序自己编写的网络请求相关的数据会被缓存，另外引入的 library 库中的网络相关的请求数据也会被缓存到这个 Cache 中。

> 备注：如果全部自己从头开始写会比较繁琐复杂，有不少著名的开源框架 Volley、Okhttp 都很好的支持实现自定义缓存。

## 减小传输数据量

为了能够减小网络传输的数据量，我们需要对传输的数据做压缩的处理，这样能够提高网络操作的性能。首先不同的网络环境，下载速度以及网络延迟是存在差异的，如下图所示：

![asset load](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/05_network/03.png)

如果我们选择在网速更低的网络环境下进行数据传输，这就意味着需要执行更长的时间，而更长的网络操作行为，会导致电量消耗更加严重。另外传输的数据如果不做压缩处理，也同样会增加网络传输的时间，消耗更多的电量。不仅如此，未经过压缩的数据，也会消耗更多的流量，使得用户需要付出更多的流量费。

通常来说，网络传输数据量的大小主要由两部分组成：图片与序列化的数据，那么我们需要做的就是减少这两部分的数据传输大小，分下面两个方面来讨论。

- 使用不同分辨率的图片

首先需要做的是减少图片的大小，选择合适的图片保存格式是第一步。下图展示了 PNG、JPEG、WEBP 三种主流格式在占用空间与图片质量之间的对比：

![png jpg webp](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/05_network/04.png)

对于 JPEG 与 WEBP 格式的图片，不同的清晰度对占用空间的大小也会产生很大的影响，适当的减少 JPG 质量，可以大大的缩小图片占用的空间大小。

另外，我们需要为不同的使用场景提供当前场景下最合适的图片大小，例如针对全屏显示的情况我们会需要一张清晰度比较高的图片，而如果只是显示为缩略图的形式，就只需要服务器提供一个相对清晰度低很多的图片即可。

服务器应该支持到为不同的使用场景分别准备多套清晰度不一样的图片，以便在对应的场景下能够获取到最适合自己的图片。这虽然会增加服务端的工作量，可是这个付出却十分值得！

- 压缩序列化数据

其次需要做的是减少序列化数据的大小，不直接使用 JSON 和 XML 格式数据。

JSON 与 XM L为了提高可读性，在文件中加入了大量的符号，空格等等字符，而这些字符对于程序来说是没有任何意义的。我们应该使用 Protocal Buffers，Nano-Proto-Buffers，FlatBuffer 来减小序列化的数据的大小。

[Protocol Buffer](https://github.com/protocolbuffers/protobuf) 是 Google 开发的一种数据交换的格式，它独立于语言，独立于平台。相较于目前常用的 JSON，数据量更小，意味着传输速度也更快。

## IP 直连与 DNS

DNS 解析的失败率占联网失败中很大一种，而且首次域名解析一般需要几百毫秒。针对此，我们可以不用域名，采用 IP 直连省去 DNS 解析过程，节省这部分时间。

另外熟悉阿里云的小伙伴肯定知道 HTTPDNS，HTTPDNS 基于 HTTP 协议的域名解析，替代了基于 DNS 协议向运营商 Local DNS 发起解析请求的传统方式，可以避免 Local DNS 造成的域名劫持和跨网访问问题，解决域名解析异常带来的困扰。

## 文件下载与上传

文件、图片等的下载，采用断点续传，不浪费用户之前消耗过的流量。

文件的上传失败率比较高，不仅仅因为大文件，同时带宽、时延、稳定性等因素在此场景下的影响也更加明显。

- 避免整文件传输，采用分片传输；
- 根据网络类型以及传输过程中的变化动态的修改分片大小；
- 每个分片失败重传的机会。

## HTTP 协议优化

使用最新的协议，HTTP 协议有多个版本：0.9、1.0、1.1、2 等。

新版本的协议经过再次的优化，例如：

- HTTP 1.1 版本引入了「持久连接」，多个请求被复用，无需重建 TCP 连接，而 TCP 连接在移动互联网的场景下成本很高，节省了时间与资源。
- HTTP 2 引入了「多工」、头信息压缩、服务器推送等特性。

新的版本不仅可以节省资源，同样可以减少流量。

## 请求打包

合并网络请求，减少请求次数。对于一些接口类如统计，无需实时上报，将统计信息保存在本地，然后根据策略统一上传。这样头信息仅需上传一次，减少了流量也节省了资源。

## Network Monitor

Network Profiler 是 [Android Profiler](https://developer.android.com/studio/preview/features/android-profiler.html) 中的一个组件，可帮助开发者识别导致应用卡顿、OOM 和内存泄露。 它显示一个应用内存使用量的实时图表，可以捕获堆转储、强制执行垃圾回收以及跟踪内存分配。

可以在 **View > Tool Windows > Android Profiler** 中打开 Network Profiler 界面。

![Network Monitor](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/05_network/05.png)

Network Profiler 的具体使用可查看 [Android 开发文档 - 利用 Network Profiler 检查网络流量](https://developer.android.com/studio/profile/network-profiler)、[Android Studio 3.0 利用 Android Profiler 测量应用性能](https://juejin.im/post/5b7cbf6f518825430810bcc6#heading-15) 这两篇文章。

## 抓包工具

使用 [Charles](https://www.charlesproxy.com/)、[Fiddler](https://www.telerik.com/fiddler) 等抓包工具同样可以实现 Network Monitor 的功能，而且更加强大。

## Stetho

[Stetho](http://facebook.github.io/stetho/) 是 Facebook 出品的一个 Android 应用的调试工具。无需 Root 即可通过 Chrome，在 Chrome Developer Tools 中可视化查看应用布局、网络请求、SQLite，Preference 等。同样集成了 Stetho 之后也可以很方便的查看网络请求的各种情况。

![Network Inspection](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/05_network/06.png)

## 参考资料

- [YouTube - Android 性能优化典范第 4 季](https://www.youtube.com/watch?v=7lxVqqWwTb0&list=PL8cvstvtecscVxHNy2evUa9M5zOsI3unW)
- [Android 性能优化（八）之网络优化](https://juejin.im/post/58ef22e3b123db0058214c60)
- [张绍文 - Android 开发高手课之网络优化](https://time.geekbang.org/column/article/78585)
- [OkHttp](https://github.com/square/okhttp)
- [Chromium](https://chromium.googlesource.com/chromium/src/+/master/components/cronet/)
- [Mars](https://github.com/Tencent/mars)
- [蘑菇街](https://www.infoq.cn/article/mogujie-app-chromium-network-layer?useSponsorshipSuggestions=true%2F)
- [阿里 - ACCS](https://www.infoq.cn/article/taobao-mobile-terminal-access-gateway-infrastructure)
- [蚂蚁金服 - mPaas](https://mp.weixin.qq.com/s/nz8Z3Uj9840KHluWjwyelw)
- [携程 - 网络服务](https://www.infoq.cn/article/how-ctrip-improves-app-networking-performance)
- [Android 开发文档 - HttpResponseCache](http://developer.android.com/reference/android/net/http/HttpResponseCache.html)
- [Protocol Buffer](https://github.com/protocolbuffers/protobuf)
- [Android 开发文档 - 利用 Network Profiler 检查网络流量](https://developer.android.com/studio/profile/network-profiler)
- [Android Studio 3.0 利用 Android Profiler 测量应用性能](https://juejin.im/post/5b7cbf6f518825430810bcc6#heading-15)
- [Charles](https://www.charlesproxy.com/)
- [Fiddler](https://www.telerik.com/fiddler)
- [Stetho](http://facebook.github.io/stetho/)
