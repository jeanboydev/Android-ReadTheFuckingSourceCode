# Android 基础知识

### Activity 生命周期？为什么 Activity 要这么设计？这样设计有什么好处？

### Android 与 iOS 运行机制上有哪些不同？

### 为什么 Android 用起来没有 iOS 流畅？为了让 Android 系统更流畅，应该从哪些方面做好？

### 如何让 Service 不被杀死？

1. 提升service优先级
2. 提升service进程优先级
3. onDestroy方法里重启service

### Service的生命周期，两种启动方法（start，bind），有什么区别?

- context.startService() ->onCreate()- >onStart()->Service running-->(如果调用context.stopService() )->onDestroy() ->Service shut down
1. 如果Service还没有运行，则调用onCreate()然后调用onStart()；
2. 如果Service已经运行，则只调用onStart()，所以一个Service的onStart方法可能会重复调用多次。
3. 调用stopService的时候直接onDestroy，
4. 如果是调用者自己直接退出而没有调用stopService的话，Service会一直在后台运行。该Service的调用者再启动起来后可以通过stopService关闭Service。

- context.bindService()->onCreate()->onBind()->Service running-->onUnbind() -> onDestroy() ->Service stop
1. onBind将返回给客户端一个IBind接口实例，IBind允许客户端回调服务的方法，比如得到Service运行的状态或其他操作。
2. 这个时候会把调用者和Service绑定在一起，Context退出了,Service就会调用onUnbind->onDestroy相应退出。
3. 所以调用bindService的生命周期为：onCreate --> onBind(只一次，不可多次绑定) --> onUnbind --> onDestory。

### 静态的 Broadcast 和动态的有什么区别？

1. 动态的比静态的安全
2. 静态在app启动的时候就初始化了 动态使用代码初始化
3. 静态需要配置 动态不需要
4. 生存期，静态广播的生存期可以比动态广播的长很多
5. 优先级动态广播的优先级比静态广播高

### Intent 可以传递哪些数据类型？

1. Serializable
2. charsequence: 主要用来传递String，char等
3. parcelable
4. Bundle

### Json 有什么优劣势、解析的原理

1. JSON的速度要远远快于XML
2. JSON相对于XML来讲，数据的体积小
3. JSON对数据的描述性比XML较差
4. 解析的基本原理是：词法分析

### 动画有哪几类，各有什么特点？

1. 动画的基本原理：其实就是利用插值器和估值器，来计算出各个时刻View的属性，然后通过改变View的属性来，实现View的动画效果。
2. View动画:只是影像变化，view的实际位置还在原来的地方。
3. 帧动画是在xml中定义好一系列图片之后，使用AnimationDrawable来播放的动画。
4. View的属性动画：
- 插值器：作用是根据时间的流逝的百分比来计算属性改变的百分比
- 估值器：在1的基础上由这个东西来计算出属性到底变化了多少数值的类

### 如果一个应用要升级需要注意哪些方面？

### Android 消息机制，Looper，消息队列

1. MessageQueue：读取会自动删除消息，单链表维护，在插入和删除上有优势。在其next()中会无限循环，不断判断是否有消息，有就返回这条消息并移除。
2. Looper：Looper创建的时候会创建一个MessageQueue，调用loop()方法的时候消息循环开始，loop()也是一个死循环，会不断调用messageQueue的next()，当有消息就处理，否则阻塞在messageQueue的next()中。当Looper的quit()被调用的时候会调用messageQueue的quit(),此时next()会返回null，然后loop()方法也跟着退出。
3. Handler：在主线程构造一个Handler，然后在其他线程调用sendMessage(),此时主线程的MessageQueue中会插入一条message，然后被Looper使用。
4. 系统的主线程在ActivityThread的main()为入口开启主线程，其中定义了内部类Activity.H定义了一系列消息类型，包含四大组件的启动停止。
5. MessageQueue和Looper是一对一关系，Handler和Looper是多对一

### 怎样退出终止 App

自己设置一个 Activity 的栈，然后一个个 finish()

### Bitmap 的处理，加载大图

- 当使用ImageView的时候，可能图片的像素大于ImageView，此时就可以通过BitmapFactory.Option来对图片进行压缩，inSampleSize表示缩小2^(inSampleSize-1)倍。
- BitMap的缓存：
	1. 使用LruCache进行内存缓存。
	2. 使用DiskLruCache进行硬盘缓存。
	3. 实现一个ImageLoader的流程：同步异步加载、图片压缩、内存硬盘缓存、网络拉取
	
		- 同步加载只创建一个线程然后按照顺序进行图片加载
		- 异步加载使用线程池，让存在的加载任务都处于不同线程
		- 为了不开启过多的异步任务，只在列表静止的时候开启图片加载


### Android 事件分发机制，请详细说下整个流程

### Android view 绘制机制和加载过程，请详细说下整个流程

### Android 四大组件的加载过程

### 自定义 View

### Volley 框架原理？

1. 缓存队列,以url为key缓存内容可以参考Bitmap的处理方式，这里单独开启一个线程。
2. 网络请求队列，使用线程池进行请求。
3. 提供各种不同类型的返回值的解析如String，Json，图片等等。

### Activity 的启动模式以及使用场景 

1. standard:默认标准模式，每启动一个都会创建一个实例，
2. singleTop：栈顶复用，如果在栈顶就调用onNewIntent复用，从onResume()开始
3. singleTask：栈内复用，本栈内只要用该类型Activity就会将其顶部的activity出栈
4. singleInstance：单例模式，除了3中特性，系统会单独给该Activity创建一个栈。

### Activity 缓存方法

1. 配置改变导致Activity被杀死，横屏变竖屏：在onStop之前会调用onSaveInstanceState()保存数据在重建Activity之后，会在onStart()之后调用onRestoreInstanceState(),并把保存下来的Bundle传给onCreate()和它会默认重建Activity当前的视图，我们可以在onCreate()中，回复自己的数据。
2. 内存不足杀掉Activity，优先级分别是：前台可见，可见非前台，后台。

### Activty 的加载过程

### 说下安卓虚拟机和 java 虚拟机的原理和不同点 

### Binder 机制

### apk 瘦身

1. classes.dex：通过代码混淆，删掉不必要的jar包和代码实现该文件的优化
2. 资源文件：通过Lint工具扫描代码中没有使用到的静态资源
3. 图片资源：使用tinypng和webP，下面详细介绍图片资源优化的方案,矢量图
4. SO文件将不用的去掉，目前主流app一般只放一个arm的so包

### ANR 产生的原因（具体产生的类型有哪些）和解决步骤

### Activty和Fragmengt之间怎么通信，Fragmengt和Fragmengt怎么通信

### Android 5.0，6.0，7.0，8.0新特性

### 内存泄漏的原因

1. 资源对象没关闭。
如Cursor、File等资源。他们会在finalize中关闭，但这样效率太低。容易造成内存泄露。
SQLiteCursor，当数据量大的时候容易泄露
2. 使用Adapter时，没有使用系统缓存的converView。
3. 即时调用recycle（）释放不再使用的Bitmap。适当降低Bitmap的采样率   
4. 使用application的context来替代activity相关的context。
尽量避免activity的context在自己的范围外被使用，这样会导致activity无法释放。
5. 注册没取消造成内存泄露
如：广播
6. 集合中的对象没清理造成的内存泄露我们通常把一些对象的引用加入到了集合中，当我们不需要该对象时，并没有把它的引用从集合中清理掉，这样这个集合就会越来越大。如果这个集合是static的话，那情况就更严重了。
7. Handler应该申明为静态对象， 并在其内部类中保存一个对外部类的弱引用

### Android长连接，怎么处理心跳机制

### Merge与ViewStub布局标签，布局优化

### UIL原理解析，三级缓存

内存缓存，本地缓存，网络 

### Zygote进程启动过程

### 如何加速启动Activity

### java虚拟机和Dalvik虚拟机的区别 



## Java 基础

### Java 中的多线程：Thread，Runnable

### Java中的同步问题？Lock，Synchronized

### Java 类的加载过程？

1. 加载时机：创建实例、访问静态变量或方法、反射、加载子类之前
2. 验证：验证文件格式、元数据、字节码、符号引用的正确性
3. 加载：根据全类名获取文件字节流、将字节流转化为静态储存结构放入方法区、生成 class 对象
4. 准备：在堆上为静态变量划分内存
5. 解析：将常量池中的符号引用转换为直接引用
6. 初始化：初始化静态变量

### 如何做到多个线程访问同一个数组，既要线程安全，同时提高读写效率

### Java 那些类是 final？

String，Match

### hashcode 与 equals 区别？

### HashMap 里面的 hash 映射？如何实现根据 Key 的 hashcode 找到下标？HashMap 做了哪些优化？

### 如何判断对象的生死？垃圾回收算法？新生代，老生代？

### Java NIO 是啥？

### 进程和线程区别？

### ArrayList、LinkedList、Vector 区别

### HashMap 和 HashTable 区别

### ClassLoader 的基础知识

- 双亲委托：一个ClassLoader类负责加载这个类所涉及的所有类，在加载的时候会判断该类是否已经被加载过，然后会递归去他父ClassLoader中找。
- 可以动态加载Jar通过URLClassLoader
- ClassLoader 隔离问题 JVM识别一个类是由：ClassLoader id+PackageName+ClassName。
- 加载不同Jar包中的公共类：
	1. 让父ClassLoader加载公共的Jar，子ClassLoader加载包含公共Jar的Jar，此时子ClassLoader在加载公共Jar的时候会先去父ClassLoader中找。(只适用Java)
	2. 重写加载包含公共Jar的Jar的ClassLoader，在loadClass中找到已经加载过公共Jar的ClassLoader，也就是把父ClassLoader替换掉。(只适用Java)
	3. 在生成包含公共Jar的Jar时候把公共Jar去掉。

### 线程中 sleep() 和 wait() 有什么区别，各有什么含义？





## 算法

### 简单的算法：打印100以内的所有质数

### 10 万个整数中找出排序后的前 10 个数（Top N 问题），及其对应算法复杂度

### 堆排序的算法复杂度

### 手写冒泡算法




### 网络基础

### 3次握手和4次挥手过程

### TCP 与 UDP 区别及其各自优缺点

### http 与 https 区别？

### 加密算法你学过哪些？

### Http1.1和Http1.0,http2.0的区别

### Http怎么处理长连接



## 人事相关

### 为啥离职呢  对待加班看法

### 你擅长什么，做了那些东西。

### 自我评价下你的优缺点

### 说下项目中遇到的棘手问题，包括技术，交际和沟通。

### 说下你进几年的规划

### 给你一个项目，你怎么看待他的市场和技术的关系

### 你一般喜欢从什么渠道获取技术信息，和提高自己的能力

### 你还要什么了解和要问的吗


## 参考资料

https://github.com/Mr-YangCheng/ForAndroidInterview

https://github.com/helen-x/AndroidInterview

https://weibo.com/1666177401/E5Dn36GEO?type=comment#_rnd1519916273592