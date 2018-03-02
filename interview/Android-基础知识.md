# Android 基础知识

## 四大组件
### Activity 生命周期？为什么 Activity 要这么设计？这样设计有什么好处？

-------

### Activity 的启动模式以及使用场景 

1. standard：默认标准模式，每启动一个都会创建一个实例，
2. singleTop：栈顶复用，如果在栈顶就调用 onNewIntent 复用，从 onResume() 开始
3. singleTask：栈内复用，本栈内只要用该类型 Activity 就会将其顶部的 Activity 出栈
4. singleInstance：单例模式，除了 3 中特性，系统会单独给该 Activity 创建一个栈。

### Activity 缓存方法

1. 配置改变导致 Activity 被杀死，横屏变竖屏：在 onStop 之前会调用 onSaveInstanceState() 保存数据在重建 Activity 之后，会在 onStart() 之后调用onRestoreInstanceState()，并把保存下来的 Bundle 传给 onCreate() 和它会默认重建 Activity 当前的视图，我们可以在 onCreate() 中，回复自己的数据。
2. 内存不足杀掉 Activity，优先级分别是：前台可见，可见非前台，后台。

### Activity 和 Fragment 之间怎么通信， Fragment 和 Fragment 怎么通信？

-------

### 如何让 Service 不被杀死？

-------

1. 提升 Service 优先级
2. 提升 Service 进程优先级
3. onDestroy 方法里重启 Service

### Service的生命周期，两种启动方法（start，bind），有什么区别?

-------

- context.startService() ->onCreate()- >onStart()->Service running-->(如果调用context.stopService() )->onDestroy() ->Service shut down
1. 如果 Service 还没有运行，则调用 onCreate() 然后调用 onStart()；
2. 如果 Service 已经运行，则只调用 onStart()，所以一个 Service 的 onStart 方法可能会重复调用多次。
3. 调用 stopService 的时候直接 onDestroy，
4. 如果是调用者自己直接退出而没有调用 stopService 的话，Service 会一直在后台运行。该 Service 的调用者再启动起来后可以通过 stopService 关闭 Service。

- context.bindService()->onCreate()->onBind()->Service running-->onUnbind() -> onDestroy() ->Service stop
1. onBind 将返回给客户端一个 IBind 接口实例，IBind 允许客户端回调服务的方法，比如得到 Service 运行的状态或其他操作。
2. 这个时候会把调用者和 Service 绑定在一起，Context 退出了，Service 就会调用 onUnbind->onDestroy 相应退出。
3. 所以调用 bindService 的生命周期为：onCreate --> onBind(只一次，不可多次绑定) --> onUnbind --> onDestory。

### 静态的 Broadcast 和动态的有什么区别？

-------

1. 动态的比静态的安全
2. 静态在 App 启动的时候就初始化了 动态使用代码初始化
3. 静态需要配置 动态不需要
4. 生存期，静态广播的生存期可以比动态广播的长很多
5. 优先级动态广播的优先级比静态广播高

### Intent 可以传递哪些数据类型？

-------

1. Serializable
2. charsequence: 主要用来传递String，char等
3. parcelable
4. Bundle





## 动画
### 动画有哪几类，各有什么特点？

-------

1. 动画的基本原理：其实就是利用插值器和估值器，来计算出各个时刻View的属性，然后通过改变 View 的属性来，实现View的动画效果。
2. View动画：只是影像变化，view 的实际位置还在原来的地方。
3. 帧动画是在 xml 中定义好一系列图片之后，使用 AnimationDrawable 来播放的动画。
4. View的属性动画：
- 插值器：作用是根据时间的流逝的百分比来计算属性改变的百分比
- 估值器：在 1 的基础上由这个东西来计算出属性到底变化了多少数值的类





## 数据存储
### Json 有什么优劣势、解析的原理

-------

1. JSON 的速度要远远快于 XML
2. JSON 相对于 XML 来讲，数据的体积小
3. JSON 对数据的描述性比 XML 较差
4. 解析的基本原理是：词法分析



## 图片处理
### Bitmap 的处理，加载大图

-------

- 当使用 ImageView 的时候，可能图片的像素大于 ImageView，此时就可以通过 BitmapFactory.Option 来对图片进行压缩，inSampleSize 表示缩小 2^(inSampleSize-1)倍。
- BitMap 的缓存：
	1. 使用 LruCache 进行内存缓存。
	2. 使用 DiskLruCache 进行硬盘缓存。
	3. 实现一个 ImageLoader 的流程：同步异步加载、图片压缩、内存硬盘缓存、网络拉取
	
		- 同步加载只创建一个线程然后按照顺序进行图片加载
		- 异步加载使用线程池，让存在的加载任务都处于不同线程
		- 为了不开启过多的异步任务，只在列表静止的时候开启图片加载




## 核心机制
### Android 消息机制，Looper，消息队列

-------

1. MessageQueue：读取会自动删除消息，单链表维护，在插入和删除上有优势。在其 next() 中会无限循环，不断判断是否有消息，有就返回这条消息并移除。
2. Looper：Looper 创建的时候会创建一个 MessageQueue，调用 loop() 方法的时候消息循环开始，loop() 也是一个死循环，会不断调用 messageQueue 的 next()，当有消息就处理，否则阻塞在 messageQueue 的 next() 中。当 Looper 的 quit() 被调用的时候会调用 messageQueue 的 quit()，此时 next() 会返回 null，然后 loop() 方法也跟着退出。
3. Handler：在主线程构造一个 Handler，然后在其他线程调用 sendMessage()，此时主线程的 MessageQueue 中会插入一条 message，然后被 Looper 使用。
4. 系统的主线程在 ActivityThread 的 main() 为入口开启主线程，其中定义了内部类 Activity.H 定义了一系列消息类型，包含四大组件的启动停止。
5. MessageQueue 和 Looper 是一对一关系，Handler 和 Looper 是多对一

### 怎样退出终止 App

自己设置一个 Activity 的栈，然后一个个 finish()。

### Activity 的加载过程（不是生命周期）

-------

### java 虚拟机和 Dalvik 虚拟机的区别？

-------

### Binder 机制

-------

### Android 事件分发机制，请详细说下整个流程

-------

### Android view 绘制机制和加载过程，请详细说下整个流程

-------

### Android 四大组件的加载过程

-------

### 如何自定义 View？

-------

### Zygote 进程启动过程

-------



## 性能优化
### Apk 瘦身

-------

1. classes.dex：通过代码混淆，删掉不必要的 jar 包和代码实现该文件的优化
2. 资源文件：通过 Lint 工具扫描代码中没有使用到的静态资源
3. 图片资源：使用 tinypng 和 webP，下面详细介绍图片资源优化的方案,矢量图
4. so 文件将不用的去掉，目前主流 app 一般只放一个 arm 的 so 包

### ANR 产生的原因（具体产生的类型有哪些）和解决步骤

-------

### 内存泄漏的原因

-------

1. 资源对象没关闭。如：Cursor、File 等资源。他们会在 finalize 中关闭，但这样效率太低。容易造成内存泄露。SQLiteCursor，当数据量大的时候容易泄露
2. 使用 Adapter 时，没有使用系统缓存的 converView。
3. 即时调用 recycle() 释放不再使用的 Bitmap。适当降低 Bitmap 的采样率   
4. 使用 application 的 context 来替代 activity 相关的 context。尽量避免 activity 的 context 在自己的范围外被使用，这样会导致 activity 无法释放。
5. 注册没取消造成内存泄露。如：广播。
6. 集合中的对象没清理造成的内存泄露我们通常把一些对象的引用加入到了集合中，当我们不需要该对象时，并没有把它的引用从集合中清理掉，这样这个集合就会越来越大。如果这个集合是 static 的话，那情况就更严重了。
7. Handler 应该申明为静态对象， 并在其内部类中保存一个对外部类的弱引用。

### Merge 与 ViewStub 布局标签，布局优化

-------

### 如何加速启动 Activity

-------





## Android 与 iOS 差异
### Android 与 iOS 运行机制上有哪些不同？

-------

### 为什么 Android 用起来没有 iOS 流畅？为了让 Android 系统更流畅，应该从哪些方面做好？

-------




## 其他
### 如果一个应用要升级需要注意哪些方面？

-------

### Volley 框架原理？

-------

1. 缓存队列,以 url 为 key 缓存内容可以参考 Bitmap 的处理方式，这里单独开启一个线程。
2. 网络请求队列，使用线程池进行请求。
3. 提供各种不同类型的返回值的解析如 String，Json，图片等等。

### Android 5.0，6.0，7.0，8.0新特性

-------

### Android 长连接，怎么处理心跳机制

-------


### UniversalImageLoader 原理解析，三级缓存

-------

内存缓存，本地缓存，网络 




## 参考资料

https://github.com/Mr-YangCheng/ForAndroidInterview

https://github.com/helen-x/AndroidInterview

https://weibo.com/1666177401/E5Dn36GEO?type=comment#_rnd1519916273592

