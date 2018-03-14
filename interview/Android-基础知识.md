# Android 基础知识

## 四大组件
### Activity 生命周期？为什么 Activity 要这么设计？这样设计有什么好处？

-------
- [Activity 生命周期](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity生命周期.md)

Activity 生命周期各种回调方法的设计，是为了确保提供一个流畅的用户体验，在 Activity 切换时，以及 Activity 停止或者销毁的意外中断情况下，保存好 Activity 状态。

### 下拉状态栏会影响 Activity 的生命周期吗？

----------

不会

### 弹出 Dialog 然后关闭过程中 Activity 的生命周期

----------

不变（全屏的 Dialog 或透明的 Activity 会影响生命周期）

### 屏幕旋转过程中 Activity 的生命周期

----------

没有配置 configChange：

- onCreate
- onStart
- onResume
- onPause
- onStop
- onDestroy
- onCreate
- onStart
- onResume

配置configChange：

- onCreate
- onStart
- onResume
- onConfigurationChanged


### Activity 上有 Dialog 的时候按 home 键时的生命周期

----------

- onCreate
- onStart
- onResume
- onPause
- onStop

### Activity 的 Launch mode（启动模式）以及使用场景 

----------

1. standard：默认标准模式，每启动一个都会创建一个实例，
2. singleTop：栈顶复用，如果在栈顶就调用 onNewIntent 复用，从 onResume() 开始
3. singleTask：栈内复用，本栈内只要用该类型 Activity 就会将其顶部的 Activity 出栈
4. singleInstance：单例模式，除了 3 中特性，系统会单独给该 Activity 创建一个栈。

设置了 singleTask 启动模式的 Activity，它在启动的时候，会先在系统中查找属性值 affinity 等于它的属性值 taskAffinity 的 Task 存在；如果存在这样的 Task，它就会在这个 Task 中启动，否则就会在新的任务栈中启动。因此， 如果我们想要设置了 singleTask 启动模式的 Activity 在新的任务中启动，就要为它设置一个独立的 taskAffinity 属性值。

如果设置了 singleTask 启动模式的 Activity 不是在新的任务中启动时，它会在已有的任务中查看是否已经存在相应的 Activity 实例，如果存在，就会把位于这个 Activity 实例上面的 Activity 全部结束掉，即最终这个 Activity 实例会位于任务的Stack顶端中。

在一个任务栈中只有一个 singleTask 启动模式的 Activity 存在。他的上面可以有其他的Activity。这点与 singleInstance 是有区别的。
singleInstance，回退栈中，只有这一个 Activity，没有其他 Activity。

SingleTop 适合接收通知启动的内容显示页面。

例如，某个新闻客户端的新闻内容页面，如果收到10个新闻推送，每次都打开一个新闻内容页面是很烦人的。

singleTask适合作为程序入口点。

例如浏览器的主界面。不管从多少个应用启动浏览器，只会启动主界面一次，其余情况都会走onNewIntent，并且会清空主界面上面的其他页面。

singleInstance应用场景：

闹铃的响铃界面。 你以前设置了一个闹铃：上午6点。在上午5点58分，你启动了闹铃设置界面，并按 Home 键回桌面；在上午5点59分时，你在微信和朋友聊天；在6点时，闹铃响了，并且弹出了一个对话框形式的 Activity(名为 AlarmAlertActivity) 提示你到6点了(这个 Activity 就是以 SingleInstance 加载模式打开的)，你按返回键，回到的是微信的聊天界面，这是因为 AlarmAlertActivity 所在的 Task 的栈只有他一个元素， 因此退出之后这个 Task 的栈空了。如果是以 SingleTask 打开 AlarmAlertActivity，那么当闹铃响了的时候，按返回键应该进入闹铃设置界面。

### Activity 缓存方法

----------

1. 配置改变导致 Activity 被杀死，横屏变竖屏：在 onStop 之前会调用 onSaveInstanceState() 保存数据在重建 Activity 之后，会在 onStart() 之后调用onRestoreInstanceState()，并把保存下来的 Bundle 传给 onCreate() 和它会默认重建 Activity 当前的视图，我们可以在 onCreate() 中，回复自己的数据。
2. 内存不足杀掉 Activity，优先级分别是：前台可见，可见非前台，后台。

### Activity 和 Fragment 之间怎么通信， Fragment 和 Fragment 怎么通信？

-------

Activity 传值给 Fragment：通过 Bundle 对象来传递，Activity 中构造 bundle 数据包，调用 Fragment 对象的 setArguments(Bundle b) 方法，Fragment 中使用 getArguments() 方法获取 Activity 传递过来的数据包取值。

Fragment 传值给 Activity：在 Fragment 中定义一个内部回调接口，Activity 实现该回调接口， Fragment 中获取 Activity 的引用，调用 Activity 实现的业务方法。接口回调机制式 Java 不同对象之间数据交互的通用方法。

Fragment 传值给 Fragment：一个 Fragment 通过 Activity 获取到另外一个 Fragment 直接调用方法传值。

### Android Service 与 Activity 之间通信的几种方式？

-------

- 通过Binder对象
- 通过Broadcast(广播)的形式

### 如何让 Service 不被杀死？

-------

- onStartCommand方法，返回START_STICKY

START_STICKY 在运行 onStartCommand 后 service 进程被 kill 后，那将保留在开始状态，但是不保留那些传入的 intent。不久后 service 就会再次尝试重新创建，因为保留在开始状态，在创建 service 后将保证调用 onStartCommand。如果没有传递任何开始命令给 service，那将获取到 null 的 intent。

START_NOT_STICKY 在运行 onStartCommand 后 service 进程被 kill 后，并且没有新的 intent 传递给它。Service 将移出开始状态，并且直到新的明显的方法 startService() 调用才重新创建。因为如果没有传递任何未决定的 intent 那么 service 是不会启动，也就是期间 onStartCommand() 不会接收到任何 null 的 intent。

START_REDELIVER_INTENT 在运行 onStartCommand() 后 service 进程被 kill 后，系统将会再次启动 service，并传入最后一个 intent 给 onStartCommand()。直到调用 stopSelf(int) 才停止传递 intent。如果在被 kill 后还有未处理好的 intent，那被 kill 后服务还是会自动启动。因此 onStartCommand 不会接收到任何 null 的 intent。

- 提升 service 优先级

在 AndroidManifest.xml 文件中对于 intent-filter 可以通过 android:priority="1000" 这个属性设置最高优先级，1000 是最高值，如果数字越小则优先级越低，同时适用于广播。

- 提升 service 进程优先级

Android 中的进程是托管的，当系统进程空间紧张的时候，会依照优先级自动进行进程的回收。Android 将进程分为 6 个等级,它们按优先级顺序由高到低依次是:

1. 前台进程( FOREGROUND_APP)
2. 可视进程(VISIBLE_APP )
3. 次要服务进程(SECONDARY_SERVER )
4. 后台进程 (HIDDEN_APP)
5. 内容供应节点(CONTENT_PROVIDER)
6. 空进程(EMPTY_APP)

当 service 运行在低内存的环境时，将会 kill 掉一些存在的进程。因此进程的优先级将会很重要，可以使用 startForeground 将 service 放到前台状态。这样在低内存时被 kill 的几率会低一些。

- onDestroy 方法里重启 service

service + broadcast 方式，就是当 service 走 onDestroy() 的时候，发送一个自定义的广播，当收到广播的时候，重新启动 service；

- Application 加上 Persistent 属性
- 监听系统广播判断Service状态

### Service 的生命周期，两种启动方法（start，bind），有什么区别?

-------

- context.startService() -> onCreate() -> onStart() -> Service running --> (如果调用 context.stopService()) -> onDestroy() -> Service shut down
1. 如果 Service 还没有运行，则调用 onCreate() 然后调用 onStart()；
2. 如果 Service 已经运行，则只调用 onStart()，所以一个 Service 的 onStart 方法可能会重复调用多次。
3. 调用 stopService 的时候直接 onDestroy，
4. 如果是调用者自己直接退出而没有调用 stopService 的话，Service 会一直在后台运行。该 Service 的调用者再启动起来后可以通过 stopService 关闭 Service。

- context.bindService() -> onCreate() -> onBind() -> Service running --> onUnbind() -> onDestroy() -> Service stop
1. onBind 将返回给客户端一个 IBind 接口实例，IBind 允许客户端回调服务的方法，比如得到 Service 运行的状态或其他操作。
2. 这个时候会把调用者和 Service 绑定在一起，Context 退出了，Service 就会调用 onUnbind -> onDestroy 相应退出。
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
2. charSequence: 主要用来传递String，char等
3. parcelable
4. Bundle

### 是否使用过 IntentService，作用是什么，AIDL 解决了什么问题？

-------

IntentService 使用队列的方式将请求的 Intent 加入队列，然后开启一个线程来处理队列中的 Intent，对于异步的 startService 请求，IntentService 会处理完成一个之后再处理第二个，每一个请求都会在一个单独的 worker thread 中处理，不会阻塞应用程序的主线程。只需重写 onHandIntent，工作线程会处理该方法实现的代码，完成请求后自动停止，解决了 service 不会专门启动一个单独的进程，不能直接处理耗时任务的问题。

Service 是依附于主线程的，也就是说不能进行耗时操作，而继承于它的子类 IntentService 说白了 IntentService 就是为了实现让 Service 能够进行耗时操作的功能。

https://www.cnblogs.com/raomengyang/p/5824327.html

### Activity、Window、View 三者的差别？

-------

Activity 像一个工匠（控制单元），Window 像窗户（承载模型），View 像窗花（显示视图）  LayoutInflater 像剪刀，Xml 配置像窗花图纸。

在 Activity 中调用 attach()，创建了一个 Window，创建的 window 是其子类 PhoneWindow，在 attach 中创建 PhoneWindow。在 Activity 中调用 setContentView(R.layout.xxx)，其中实际上是调用的 getWindow().setContentView()。调用 PhoneWindow 中的 setContentView() 方法。

创建 ParentView： 作为 ViewGroup 的子类，实际是创建的 DecorView(作为 FrameLayout 的子类）。将指定的 R.layout.xxx 进行填充，通过布局填充器进行填充(其中的 parent 指的就是 DecorView)。调用到 ViewGroup，调用 ViewGroup 的 removeAllView()，先将所有的view移除掉，添加新的 view.addView()。

### Fragment 特点

Fragment 可以作为 Activity界面的一部分组成出现；
可以在一个 Activity 中同时出现多个 Fragment，并且一个 Fragment 也可以在多个 Activity 中使用；
在 Activity 运行过程中，可以添加、移除或者替换 Fragment；
Fragment 可以响应自己的输入事件，并且有自己的生命周期，它们的生命周期会受宿主 Activity 的生命周期影响。

### Handler、Thread 和 HandlerThread 的差别？

http://blog.csdn.net/guolin_blog/article/details/9991569

http://droidyue.com/blog/2015/11/08/make-use-of-handlerthread/

从 Android 中 Thread（java.lang.Thread -> java.lang.Object）描述可以看出，Android的 Thread 没有对 Java 的 Thread 做任何封装，但是 Android 提供了一个继承自 Thread 的类 HandlerThread（android.os.HandlerThread -> java.lang.Thread），这个类对 Java 的 Thread 做了很多便利 Android 系统的封装。

android.os.Handler 可以通过 Looper 对象实例化，并运行于另外的线程中，Android 提供了让 Handler 运行于其它线程的线程实现，也就是 HandlerThread。HandlerThread 对象 start 后可以获得其 Looper 对象，并且使用这个 Looper 对象实例 Handler。

### RequestLayout，onLayout，onDraw，DrawChild 区别与联系

-------

requestLayout() 方法 ：会导致调用 measure() 过程和 layout() 过程 。说明：只是对 View 树重新布局 layout 过程包括 measure() 和 layout() 过程，不会调用 draw() 过程，但不会重新绘制任何视图包括该调用者本身。

onLayout() 方法(如果该 View 是 ViewGroup 对象，需要实现该方法，对每个子视图进行布局)。

调用 onDraw() 方法绘制视图本身(每个 View 都需要重载该方法，ViewGroup 不需要实现该方法)。

drawChild() 去重新回调每个子视图的 draw() 方法。

### invalidate() 和 postInvalidate() 的区别及使用

-------

http://blog.csdn.net/mars2639/article/details/6650876

### LinearLayout 对比 RelativeLayout

-------

RelativeLayout 会让子 View 调用 2 次 onMeasure；LinearLayout 在有 weight 时，也会调用子 View 2次 onMeasure

RelativeLayout 的子 View 如果高度和 RelativeLayout 不同，则会引发效率问题，当子 View 很复杂时，这个问题会更加严重。如果可以，尽量使用 padding 代替 margin。

在不影响层级深度的情况下,使用 LinearLayout 和 FrameLayout 而不是 RelativeLayout。

### ContentProvider

-------

https://www.jianshu.com/p/ea8bc4aaf057

### Application 和 Activity 的 context 对象的区别

----------

首先 Activity.this 和 getApplicationContext() 返回的不是同一个对象，一个是当前 Activity 的实例，一个是项目的 Application 的实例，这两者的生命周期是不同的，它们各自的使用场景不同，this.getApplicationContext() 取的是这个应用程序的 Context，它的生命周期伴随应用程序的存在而存在；而 Activity.this 取的是当前 Activity 的 Context，它的生命周期则只能存活于当前 Activity，这两者的生命周期是不同的。getApplicationContext() 生命周期是整个应用，当应用程序摧毁的时候，它才会摧毁；Activity.this 的 context 是属于当前 Activity 的，当前 Activity 摧毁的时候，它就摧毁。

### AsyncTask 原理及缺陷

----------

AsyncTask 是对 Handler 与线程池的封装。使用它的方便之处在于能够更新用户界面，当然这里更新用户界面的操作还是在主线程中完成的，但是由于 AsyncTask 内部包含一个 Handler，所以可以发送消息给主线程让它更新 UI。另外，AsyncTask 内还包含了一个线程池。使用线程池的主要原因是避免不必要的创建及销毁线程的开销。

AsyncTask的优点在于执行完后台任务后可以很方便的更新UI，然而使用它存在着诸多的限制。先抛开内存泄漏问题，使用AsyncTask主要存在以下局限性：

1. 在 Android 4.1 版本之前，AsyncTask 类必须在主线程中加载，这意味着对 AsyncTask 类的第一次访问必须发生在主线程中；在 Android 4.1 以及以上版本则不存在这一限制，因 为ActivityThread（代表了主线程）的 main 方法中会自动加载 AsyncTask。
2. AsyncTask 对象必须在主线程中创建 
3. AsyncTask 对象的 execute 方法必须在主线程中调用 
4. 一个 AsyncTask 对象只能调用一次 execute 方法


## 动画
### 动画有哪几类，各有什么特点？

-------

1. 动画的基本原理：其实就是利用插值器和估值器，来计算出各个时刻View的属性，然后通过改变 View 的属性来，实现View的动画效果。
2. View 动画：只是影像变化，view 的实际位置还在原来的地方。
3. 帧动画是在 xml 中定义好一系列图片之后，使用 AnimationDrawable 来播放的动画。
4. View 的属性动画：
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

		
### 图片加载原理

----------

http://b.codekk.com/detail/Trinea/Android%20%E4%B8%89%E5%A4%A7%E5%9B%BE%E7%89%87%E7%BC%93%E5%AD%98%E5%8E%9F%E7%90%86%E3%80%81%E7%89%B9%E6%80%A7%E5%AF%B9%E6%AF%94


### 图片压缩原理

----------

http://blog.csdn.net/newchenxf/article/details/51693753



## 核心机制
### Android 消息机制，Looper，消息队列

-------

1. MessageQueue：读取会自动删除消息，单链表维护，在插入和删除上有优势。在其 next() 中会无限循环，不断判断是否有消息，有就返回这条消息并移除。
2. Looper：Looper 创建的时候会创建一个 MessageQueue，调用 loop() 方法的时候消息循环开始，loop() 也是一个死循环，会不断调用 messageQueue 的 next()，当有消息就处理，否则阻塞在 messageQueue 的 next() 中。当 Looper 的 quit() 被调用的时候会调用 messageQueue 的 quit()，此时 next() 会返回 null，然后 loop() 方法也跟着退出。
3. Handler：在主线程构造一个 Handler，然后在其他线程调用 sendMessage()，此时主线程的 MessageQueue 中会插入一条 message，然后被 Looper 使用。
4. 系统的主线程在 ActivityThread 的 main() 为入口开启主线程，其中定义了内部类 Activity.H 定义了一系列消息类型，包含四大组件的启动停止。
5. MessageQueue 和 Looper 是一对一关系，Handler 和 Looper 是多对一

### 怎样退出终止 App

----------

自己设置一个 Activity 的栈，然后一个个 finish()。

### Activity 的加载过程（不是生命周期）

-------

- [Activity 创建过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity启动过程.md)

### Java 虚拟机和 Dalvik 虚拟机的区别？

-------

Dalvik 和标准 Java虚拟机（JVM）之间的首要差别之一，就是 Dalvik 基于寄存器，而 JVM 基于栈。 
Dalvik 和 Java 之间的另外一大区别就是运行环境 —— Dalvik 经过优化，允许在有限的内存中同时运行多个虚拟机的实例，并且每一个 Dalvik 应用作为一个独立的 Linux 进程执行。 

1. 虚拟机很小，使用的空间也小； 
2. Dalvik 没有 JIT 编译器； 
3. 常量池已被修改为只使用 32 位的索引，以简化解释器； 
4. 它使用自己的字节码，而非 Java 字节码。


### Binder 机制

-------

- [一篇文章了解相见恨晚的 Android Binder 进程间通讯](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Binder进程间通讯.md)

### Android 事件分发机制，请详细说下整个流程

-------

https://www.jianshu.com/p/38015afcdb58


### Android view 绘制机制和加载过程，请详细说下整个流程

-------

https://www.jianshu.com/p/bb7977990baa


### Android 四大组件的加载过程

-------


### 优化自定义 view

-------

为了加速你的 view，对于频繁调用的方法，需要尽量减少不必要的代码。先从 onDraw() 开始，需要特别注意不应该在这里做内存分配的事情，因为它会导致 GC，从而导致卡顿。在初始化或者动画间隙期间做分配内存的动作。不要在动画正在执行的时候做内存分配的事情。

你还需要尽可能的减少 onDraw() 被调用的次数，大多数时候导致 onDraw 都是因为调用了 invalidate()。因此请尽量减少调用 invaildate() 的次数。如果可能的话，尽量调用含有 4 个参数的 invalidate() 方法而不是没有参数的 invalidate()。没有参数的 invalidate 会强制重绘整个 view。

另外一个非常耗时的操作是请求 layout。任何时候执行 requestLayout()，会使得 Android UI 系统去遍历整个 View 的层级来计算出每一个 view 的大小。如果找到有冲突的值，它会需要重新计算好几次。另外需要尽量保持 View 的层级是扁平化的，这样对提高效率很有帮助。

如果你有一个复杂的 UI，你应该考虑写一个自定义的 ViewGroup 来执行他的 layout 操作。与内置的 view 不同，自定义的 view 可以使得程序仅仅测量这一部分，这避免了遍历整个 view 的层级结构来计算大小。这个 PieChart 例子展示了如何继承 ViewGroup 作为自定义 view 的一部分。PieChart  有子 views，但是它从来不测量它们。而是根据他自身的 layout 法则，直接设置它们的大小。


### Zygote 进程启动过程

-------

- [一篇文章看明白 Android 系统启动时都干了什么](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-系统启动过程.md)

### ThreadLocal 原理

----------

https://droidyue.com/blog/2016/03/13/learning-threadlocal-in-java/


### ClassLoader 加载过程，双亲委派模型

### 介绍下 SurfaceView

----------

https://www.jianshu.com/p/b037249e6d31


### 描述下点击 Android Studio 的 build 按钮后发生了什么？

----------

http://blog.csdn.net/yangxi_pekin/article/details/78612741


### 描述下一个应用程序安装到手机上时发生了什么？

----------

http://www.androidchina.net/6667.html


### App 是如何沙箱化，为什么要这么做？

----------

Android 中的沙箱化可以提升系统安全性和效率。
Android 的底层内核为 Linux，因此继承了 Linux 良好的安全性，并对其进行了优化。在 Linux 中，一个用户对应一个 uid，而在 Android 中，（通常）一个 App 对应一个 uid，拥有独立的资源和空间，与其他 App 互不干扰。如有两个App: A 和 B，A 并不能访问 B 的资源，A 的崩溃也不会对 B 造成影响，从而保证了安全性和效率。


### 权限管理系统（底层的权限是如何进行 grant 的）

----------

http://tbfungeek.github.io/2016/04/06/Android-%E5%88%9D%E6%AD%A5%E4%B9%8BAndroid-%E5%AE%89%E5%85%A8%E6%9C%BA%E5%88%B6/


## 性能优化
### Apk 瘦身

-------

1. classes.dex：通过代码混淆，删掉不必要的 jar 包和代码实现该文件的优化
2. 资源文件：通过 Lint 工具扫描代码中没有使用到的静态资源
3. 图片资源：使用 tinypng 和 webP，下面详细介绍图片资源优化的方案,矢量图
4. so 文件将不用的去掉，目前主流 app 一般只放一个 arm 的 so 包

### ANR 产生的原因（具体产生的类型有哪些）和解决步骤

-------

- 如果开发机器上出现问题，我们可以通过查看 /data/anr/traces.txt 即可，最新的 ANR 信息在最开始部分。
- 主线程被 IO 操作（从 4.0 之后网络 IO 不允许在主线程中）阻塞。
- 主线程中存在耗时的计算。
- 主线程中错误的操作，比如 Thread.wait 或者 Thread.sleep 等 Android 系统会监控程序的响应状况，一旦出现下面两种情况，则弹出 ANR 对话框。
- 应用在 5 秒内未响应用户的输入事件（如按键或者触摸）。
- BroadcastReceiver 未在 10 秒内完成相关的处理。
- Service 在特定的时间内无法处理完成 20 秒。

避免:

- 使用 AsyncTask 处理耗时 IO 操作。
- 使用 Thread 或者 HandlerThread 时，调用Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND) 设置优先级，否则仍然会降低程序响应，因为默认 Thread 的优先级和主线程相同。
- 使用 Handler 处理工作线程结果，而不是使用 Thread.wait() 或者 Thread.sleep() 来阻塞主线程。
- Activity 的 onCreate 和 onResume 回调中尽量避免耗时的代码
- BroadcastReceiver 中 onReceive 代码也要尽量减少耗时，建议使用 IntentService 处理。

### 什么情况导致 OOM 以及如何避免?

-------

http://blog.csdn.net/yangxuehui1990/article/details/44994763

http://blog.csdn.net/ljx19900116/article/details/50037627

### 内存泄漏的原因

-------

- 资源对象没关闭造成的内存泄漏

描述：资源性对象比如：Cursor，File 文件等，往往都用了一些缓冲，我们在不使用的时候，应该及时关闭它们，以便它们的缓冲及时回收内存。它们的缓冲不仅存在于 java 虚拟机内，还存在于 java 虚拟机外。如果我们仅仅是把它的引用设置为 null，而不关闭它们，往往会造成内存泄漏。因为有些资源性对象，比如：SQLiteCursor(在析构函数 finalize()，如果我们没有关闭它，它自己会调 close() 关闭)，如果我们没有关闭它，系统在回收它时也会关闭它，但是这样的效率太低了。因此对于资源性对象在不使用的时候，应该调用它的 close() 函数，将其关闭掉，然后才置为null。在我们的程序退出时一定要确保我们的资源性对象已经关闭。程序中经常会进行查询数据库的操作，但是经常会有使用完毕 Cursor 后没有关闭的情况。如果我们的查询结果集比较小，对内存的消耗不容易被发现，只有在常时间大量操作的情况下才会复现内存问题，这样就会给以后的测试和问题排查带来困难和风险。

- 构造 Adapter 时，没有使用缓存的 convertView

以构造 ListView 的 BaseAdapter 为例，在 BaseAdapter 中提供了方法： public View getView(int position, View convertView, ViewGroup parent) 来向 ListView 提供每一个 item 所需要的 view 对象。初始时 ListView 会从 BaseAdapter 中根据当前的屏幕布局实例化一定数量的 view 对象，同时 ListView 会将这些 view 对象缓存起来。当向上滚动 ListView 时，原先位于最上面的 list item 的 view 对象会被回收，然后被用来构造新出现的最下面的 list item。这个构造过程就是由 getView() 方法完成的，getView() 的第二个形参 View convertView 就是被缓存起来的 list item 的 view 对象(初始化时缓存中没有 view 对象则 convertView 是null)。由此可以看出，如果我们不去使用 convertView，而是每次都在 getView() 中重新实例化一个 View 对象的话，即浪费资源也浪费时间，也会使得内存占用越来越大。 ListView 回收 list item 的 view 对象的过程可以查看: android.widget.AbsListView.java --> void addScrapView(View scrap) 方法。 示例代码：

```Java
public View getView(int position, View convertView, ViewGroup parent) {
    View view = new Xxx(...); 
    ... ... 
    return view; 
} 
```

修正示例代码：

```Java
public View getView(int position, View convertView, ViewGroup parent) {
    View view = null; 
    if (convertView != null) { 
        view = convertView; 
        populate(view, getItem(position)); 
        ... 
    } else { 
        view = new Xxx(...); 
        ... 
    } 
    return view; 
} 
```

- Bitmap 对象不在使用时调用 recycle() 释放内存

有时我们会手工的操作 Bitmap 对象，如果一个 Bitmap 对象比较占内存，当它不在被使用的时候，可以调用 Bitmap.recycle() 法回收此对象的像素所占用的内存，但这不是必须的，视情况而定。

- 试着使用关于 application 的 context 来替代和 activity 相关的 context

这是一个很隐晦的内存泄漏的情况。有一种简单的方法来避免 context 相关的内存泄漏。最显著地一个是避免 context 逃出他自己的范围之外。使用 Application context。这个 context 的生存周期和你的应用的生存周期一样长，而不是取决于 activity 的生存周期。如果你想保持一个长期生存的对象，并且这个对象需要一个 context,记得使用 application 对象。你可以通过调用 Context.getApplicationContext() or Activity.getApplication() 来获得。

- 注册没反注册造成的内存泄漏

一些 Android 程序可能引用我们的 Anroid 程序的对象(比如：注册机制)。即使我们的 Android 程序已经结束了，但是别的引用程序仍然还有对我们的 Android 程序的某个对象的引用，泄漏的内存依然不能被垃圾回收。调用 registerReceiver 后未调用 unregisterReceiver。 比如:假设我们希望在锁屏界面 LockScreen 中，监听系统中的电话服务以获取一些信息(如：信号强度等)，则可以在 LockScreen 中定义一个 PhoneStateListener 的对象，同时将它注册到 TelephonyManager 服务中。对于 LockScreen 对象，当需要显示锁屏界面的时候就会创建一个 LockScreen 对象，而当锁屏界面消失的时候 LockScreen 对象就会被释放掉。 但是如果在释放 LockScreen 对象的时候忘记取消我们之前注册的 PhoneStateListener 对象，则会导致 LockScreen 无法被垃圾回收。如果不断的使锁屏界面显示和消失，则最终会由于大量的 LockScreen 对象没有办法被回收而引起 OutOfMemory，使得 system_process 进程挂掉。 虽然有些系统程序，它本身好像是可以自动取消注册的(当然不及时)，但是我们还是应该在我们的程序中明确的取消注册，程序结束时应该把所有的注册都取消掉。

- 集合中对象没清理造成的内存泄漏

我们通常把一些对象的引用加入到了集合中，当我们不需要该对象时，并没有把它的引用从集合中清理掉，这样这个集合就会越来越大。如果这个集合是 static 的话，那情况就更严重了。

### Merge 与 ViewStub 布局标签，布局优化

-------

- [Android 性能优化 - UI优化](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-性能优化-UI优化.md)

### 怎么去除重复代码？

### 内存优化

-------

- [Android 性能优化 - 内存优化](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-性能优化-内存优化.md)

### HashMap 源码，SpareArray 原理



## Android 与 iOS 差异
### Android 与 iOS 运行机制上有哪些不同？

-------

Android：沙盒运行机制，采用真后台运行，将所有的应用都保存在 RAM 中，按 Home 键，程序被挂在了后台，实际未退出，因程序在后台运行，所以可以收到推送消息，导致内存越用越低，越用越卡。

iOS：虚拟机运行机制，采用伪后台运行，按 Home 键，程序进入到后台会自动进入到休眠状态，Home 键调出多任务管理器，所有的应用都处于停止状态，iPhone 默认将应用的最后的运行记录在 RAM 中， iOS 得到推动消息，是因为当你开启应用的消息推送时，系统会增加一些进程，这些进程从苹果的服务器接收消息，然后在通过服务器发送到手机，苹果服务器起到了中转的作用，因此 IOS 运行流畅。



## 其他

### 模块化怎么实现，好处，原因？

### 视频加密传输


### 如果一个应用要升级需要注意哪些方面？

-------

1. 接口 API 兼容性
2. 本地数据兼容性
3. 签名

### Volley 框架原理？

-------

1. 缓存队列,以 url 为 key 缓存内容可以参考 Bitmap 的处理方式，这里单独开启一个线程。
2. 网络请求队列，使用线程池进行请求。
3. 提供各种不同类型的返回值的解析如 String，Json，图片等等。

### Android 5.0，6.0，7.0，8.0新特性

-------

Android 5.0新特性：

- Material Design
- 支持多种设备
- 全新通知中心设计
- 支持64位ART虚拟机
- Project Volta电池续航改进计划
- 全新的“最近应用程序”
- 改进安全性
- 不同数据独立保存
- 改进搜索
- 支持蓝牙4.1、USB Audio、多人分享等其它特性

Android 6.0 新特性：

- 动态权限管理
- 指纹识别（Fingerprint Support）
- APP关联（App Links）
- Android pay
- 电源管理
- 存储

Android 7.0 新特性：

- Android7.0提供新功能以提升性能、生产效率和安全性。

关于Android N的性能改进，Android N建立了先进的图形处理Vulkan系统，能少的减少对CPU的占用。与此同时，Android N加入了JIT编译器，安装程序快了75%，所占空间减少了50%。

- 分屏多任务
- 全新下拉快捷开关页
- 新通知消息
- 通知消息归拢
- 夜间模式
- 流量保护模式
- 全新设置样式
- 改进的 Doze 休眠机制
- 系统级电话黑名单功能
- 菜单键快速应用切换

Android 8.0 新特性：

- 通知功能
- 新表情符号
- 智能复制和粘贴
- 画中画功能
- 自动填充功能
- Vitals
- Google Play Protect
- 系统/应用启动程序加速
- Play Console Dashboard
- 自适应图标（Adaptive icons）
- 后台进程限制
- 字体

### Android 长连接，怎么处理心跳机制

-------

http://blog.csdn.net/rabbit_in_android/article/details/50119809

### UniversalImageLoader 原理解析，三级缓存，LRUCache 原理

-------

内存缓存，本地缓存，网络。

[UniversalImageLoader 源码分析](http://a.codekk.com/detail/Android/huxian99/Android%20Universal%20Image%20Loader%20%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90)

### Glide 原理解析

----------

http://blog.csdn.net/guolin_blog/article/details/53939176

### RecycleView 与 ListView 的区别，性能

----------

https://zhuanlan.zhihu.com/p/23339185

### EventBus 实现原理

----------

http://blog.csdn.net/HaveFerrair/article/details/50618346

### OkHttp 实现原理

----------

http://blog.csdn.net/mwq384807683/article/details/71173442?locationNum=8&fps=1


## 参考资料

https://github.com/Mr-YangCheng/ForAndroidInterview

https://github.com/helen-x/AndroidInterview

https://weibo.com/1666177401/E5Dn36GEO?type=comment#_rnd1519916273592

