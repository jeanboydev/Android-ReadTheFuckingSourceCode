# Android 基础知识

## 四大组件
### Activity 生命周期？为什么 Activity 要这么设计？这样设计有什么好处？

-------

### Activity 的 Launch mode（启动模式）以及使用场景 

1. standard：默认标准模式，每启动一个都会创建一个实例，
2. singleTop：栈顶复用，如果在栈顶就调用 onNewIntent 复用，从 onResume() 开始
3. singleTask：栈内复用，本栈内只要用该类型 Activity 就会将其顶部的 Activity 出栈
4. singleInstance：单例模式，除了 3 中特性，系统会单独给该 Activity 创建一个栈。

设置了"singleTask"启动模式的Activity，它在启动的时候，会先在系统中查找属性值affinity等于它的属性值taskAffinity的Task存在； 如果存在这样的Task，它就会在这个Task中启动，否则就会在新的任务栈中启动。因此， 如果我们想要设置了"singleTask"启动模式的Activity在新的任务中启动，就要为它设置一个独立的taskAffinity属性值。

如果设置了"singleTask"启动模式的Activity不是在新的任务中启动时，它会在已有的任务中查看是否已经存在相应的Activity实例， 如果存在，就会把位于这个Activity实例上面的Activity全部结束掉，即最终这个Activity 实例会位于任务的Stack顶端中。

在一个任务栈中只有一个”singleTask”启动模式的Activity存在。他的上面可以有其他的Activity。这点与singleInstance是有区别的。
singleInstance，回退栈中，只有这一个Activity，没有其他Activity。

SingleTop适合接收通知启动的内容显示页面。

例如，某个新闻客户端的新闻内容页面，如果收到10个新闻推送，每次都打开一个新闻内容页面是很烦人的。

singleTask适合作为程序入口点。

例如浏览器的主界面。不管从多少个应用启动浏览器，只会启动主界面一次，其余情况都会走onNewIntent，并且会清空主界面上面的其他页面。

singleInstance应用场景：

闹铃的响铃界面。 你以前设置了一个闹铃：上午6点。在上午5点58分，你启动了闹铃设置界面，并按 Home 键回桌面；在上午5点59分时，你在微信和朋友聊天；在6点时，闹铃响了，并且弹出了一个对话框形式的 Activity(名为 AlarmAlertActivity) 提示你到6点了(这个 Activity 就是以 SingleInstance 加载模式打开的)，你按返回键，回到的是微信的聊天界面，这是因为 AlarmAlertActivity 所在的 Task 的栈只有他一个元素， 因此退出之后这个 Task 的栈空了。如果是以 SingleTask 打开 AlarmAlertActivity，那么当闹铃响了的时候，按返回键应该进入闹铃设置界面。

### Activity 缓存方法

1. 配置改变导致 Activity 被杀死，横屏变竖屏：在 onStop 之前会调用 onSaveInstanceState() 保存数据在重建 Activity 之后，会在 onStart() 之后调用onRestoreInstanceState()，并把保存下来的 Bundle 传给 onCreate() 和它会默认重建 Activity 当前的视图，我们可以在 onCreate() 中，回复自己的数据。
2. 内存不足杀掉 Activity，优先级分别是：前台可见，可见非前台，后台。

### Activity 和 Fragment 之间怎么通信， Fragment 和 Fragment 怎么通信？

-------

### Android Service与Activity之间通信的几种方式？

-------

- 通过Binder对象
- 通过Broadcast(广播)的形式

### 如何让 Service 不被杀死？

-------

- onStartCommand方法，返回START_STICKY

START_STICKY 在运行onStartCommand后service进程被kill后，那将保留在开始状态，但是不保留那些传入的intent。不久后service就会再次尝试重新创建，因为保留在开始状态，在创建     service后将保证调用onstartCommand。如果没有传递任何开始命令给service，那将获取到null的intent。

START_NOT_STICKY 在运行onStartCommand后service进程被kill后，并且没有新的intent传递给它。Service将移出开始状态，并且直到新的明显的方法（startService）调用才重新创建。因为如果没有传递任何未决定的intent那么service是不会启动，也就是期间onstartCommand不会接收到任何null的intent。

START_REDELIVER_INTENT 在运行onStartCommand后service进程被kill后，系统将会再次启动service，并传入最后一个intent给onstartCommand。直到调用stopSelf(int)才停止传递intent。如果在被kill后还有未处理好的intent，那被kill后服务还是会自动启动。因此onstartCommand不会接收到任何null的intent。

- 提升service优先级

在AndroidManifest.xml文件中对于intent-filter可以通过android:priority="1000"这个属性设置最高优先级，1000是最高值，如果数字越小则优先级越低，同时适用于广播。

提升service进程优先级

Android中的进程是托管的，当系统进程空间紧张的时候，会依照优先级自动进行进程的回收。Android将进程分为6个等级,它们按优先级顺序由高到低依次是:

前台进程( FOREGROUND_APP)

可视进程(VISIBLE_APP )

次要服务进程(SECONDARY_SERVER )

后台进程 (HIDDEN_APP)

内容供应节点(CONTENT_PROVIDER)

空进程(EMPTY_APP)

当service运行在低内存的环境时，将会kill掉一些存在的进程。因此进程的优先级将会很重要，可以使用startForeground 将service放到前台状态。这样在低内存时被kill的几率会低一些。

- onDestroy方法里重启service

service+broadcast方式，就是当service走ondestory的时候，发送一个自定义的广播，当收到广播的时候，重新启动service；

- Application加上Persistent属性

- 监听系统广播判断Service状态

### Service 的生命周期，两种启动方法（start，bind），有什么区别?

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

### 是否使用过 IntentService，作用是什么，AIDL 解决了什么问题？

-------

生成一个默认的且与主线程互相独立的工作者线程来执行所有传送至onStartCommand() 方法的Intetnt。

生成一个工作队列来传送Intent对象给你的onHandleIntent()方法，同一时刻只传送一个Intent对象，这样一来，你就不必担心多线程的问题。在所有的请求(Intent)都被执行完以后会自动停止服务，所以，你不需要自己去调用stopSelf()方法来停止。

该服务提供了一个onBind()方法的默认实现，它返回null

提供了一个onStartCommand()方法的默认实现，它将Intent先传送至工作队列，然后从工作队列中每次取出一个传送至onHandleIntent()方法，在该方法中对Intent对相应的处理。

AIDL (Android Interface Definition Language) 是一种IDL 语言，用于生成可以在Android设备上两个进程之间进行进程间通信(interprocess communication, IPC)的代码。如果在一个进程中（例如Activity）要调用另一个进程中（例如Service）对象的操作，就可以使用AIDL生成可序列化的参数。 AIDL IPC机制是面向接口的，像COM或Corba一样，但是更加轻量级。它是使用代理类在客户端和实现端传递数据。

### Activity、Window、View 三者的差别？

-------

Activity像一个工匠（控制单元），Window像窗户（承载模型），View像窗花（显示视图） LayoutInflater像剪刀，Xml配置像窗花图纸。

在Activity中调用attach，创建了一个Window，创建的window是其子类PhoneWindow，在attach中创建PhoneWindow。在Activity中调用setContentView(R.layout.xxx)，其中实际上是调用的getWindow().setContentView()。调用PhoneWindow中的setContentView方法。

创建ParentView： 作为ViewGroup的子类，实际是创建的DecorView(作为FramLayout的子类）。将指定的R.layout.xxx进行填充，通过布局填充器进行填充【其中的parent指的就是DecorView】。调用到ViewGroup，调用ViewGroup的removeAllView()，先将所有的view移除掉，添加新的view：addView()

### Fragment 特点

Fragment可以作为Activity界面的一部分组成出现；
可以在一个Activity中同时出现多个Fragment，并且一个Fragment也可以在多个Activity中使用；
在Activity运行过程中，可以添加、移除或者替换Fragment；
Fragment可以响应自己的输入事件，并且有自己的生命周期，它们的生命周期会受宿主Activity的生命周期影响。

### Handler、Thread 和 HandlerThread 的差别？

http://blog.csdn.net/guolin_blog/article/details/9991569

http://droidyue.com/blog/2015/11/08/make-use-of-handlerthread/

从Android中Thread（java.lang.Thread -> java.lang.Object）描述可以看出，Android的Thread没有对Java的Thread做任何封装，但是Android提供了一个继承自Thread的类HandlerThread（android.os.HandlerThread -> java.lang.Thread），这个类对Java的Thread做了很多便利Android系统的封装。

android.os.Handler可以通过Looper对象实例化，并运行于另外的线程中，Android提供了让Handler运行于其它线程的线程实现，也就是HandlerThread。HandlerThread对象start后可以获得其Looper对象，并且使用这个Looper对象实例Handler。

### RequestLayout，onLayout，onDraw，DrawChild 区别与联系

-------

requestLayout()方法 ：会导致调用measure()过程 和 layout()过程 。说明：只是对View树重新布局layout过程包括measure()和layout()过程，不会调用draw()过程，但不会重新绘制 任何视图包括该调用者本身。

onLayout()方法(如果该View是ViewGroup对象，需要实现该方法，对每个子视图进行布局)

调用onDraw()方法绘制视图本身(每个View都需要重载该方法，ViewGroup不需要实现该方法)

drawChild()去重新回调每个子视图的draw()方法

### invalidate() 和 postInvalidate() 的区别及使用

-------

http://blog.csdn.net/mars2639/article/details/6650876

### LinearLayout 对比 RelativeLayout

-------

RelativeLayout会让子View调用2次onMeasure，LinearLayout 在有weight时，也会调用子View2次onMeasure

RelativeLayout的子View如果高度和RelativeLayout不同，则会引发效率问题，当子View很复杂时，这个问题会更加严重。如果可以，尽量使用padding代替margin。

在不影响层级深度的情况下,使用LinearLayout和FrameLayout而不是RelativeLayout。

### ContentProvider

-------

https://www.jianshu.com/p/ea8bc4aaf057


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

https://www.jianshu.com/p/38015afcdb58


### Android view 绘制机制和加载过程，请详细说下整个流程

-------

https://www.jianshu.com/p/bb7977990baa


### Android 四大组件的加载过程

-------

### 如何自定义 View？

-------

### 优化自定义 view

-------

为了加速你的view，对于频繁调用的方法，需要尽量减少不必要的代码。先从onDraw开始，需要特别注意不应该在这里做内存分配的事情，因为它会导致GC，从而导致卡顿。在初始化或者动画间隙期间做分配内存的动作。不要在动画正在执行的时候做内存分配的事情。

你还需要尽可能的减少onDraw被调用的次数，大多数时候导致onDraw都是因为调用了invalidate().因此请尽量减少调用invaildate()的次数。如果可能的话，尽量调用含有4个参数的invalidate()方法而不是没有参数的invalidate()。没有参数的invalidate会强制重绘整个view。

另外一个非常耗时的操作是请求layout。任何时候执行requestLayout()，会使得Android UI系统去遍历整个View的层级来计算出每一个view的大小。如果找到有冲突的值，它会需要重新计算好几次。另外需要尽量保持View的层级是扁平化的，这样对提高效率很有帮助。

如果你有一个复杂的UI，你应该考虑写一个自定义的ViewGroup来执行他的layout操作。与内置的view不同，自定义的view可以使得程序仅仅测量这一部分，这避免了遍历整个view的层级结构来计算大小。这个PieChart 例子展示了如何继承ViewGroup作为自定义view的一部分。PieChart 有子views，但是它从来不测量它们。而是根据他自身的layout法则，直接设置它们的大小。


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

- 如果开发机器上出现问题，我们可以通过查看/data/anr/traces.txt即可，最新的ANR信息在最开始部分。
- 主线程被IO操作（从4.0之后网络IO不允许在主线程中）阻塞。
- 主线程中存在耗时的计算
- 主线程中错误的操作，比如Thread.wait或者Thread.sleep等 Android系统会监控程序的响应状况，一旦出现下面两种情况，则弹出ANR对话框
- 应用在5秒内未响应用户的输入事件（如按键或者触摸）
- BroadcastReceiver未在10秒内完成相关的处理
- Service在特定的时间内无法处理完成 20秒

避免:

- 使用AsyncTask处理耗时IO操作。
- 使用Thread或者HandlerThread时，调用Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND)设置优先级，否则仍然会降低程序响应，因为默认Thread的优先级和主线程相同。
- 使用Handler处理工作线程结果，而不是使用Thread.wait()或者Thread.sleep()来阻塞主线程。
- Activity的onCreate和onResume回调中尽量避免耗时的代码
- BroadcastReceiver中onReceive代码也要尽量减少耗时，建议使用IntentService处理。

### 什么情况导致OOM以及如何避免?

-------

http://blog.csdn.net/yangxuehui1990/article/details/44994763

http://blog.csdn.net/ljx19900116/article/details/50037627

### 内存泄漏的原因

-------

- 资源对象没关闭造成的内存泄漏

描述： 资源性对象比如(Cursor，File文件等)往往都用了一些缓冲，我们在不使用的时候，应该及时关闭它们，以便它们的缓冲及时回收内存。它们的缓冲不仅存在于 java虚拟机内，还存在于java虚拟机外。如果我们仅仅是把它的引用设置为null,而不关闭它们，往往会造成内存泄漏。因为有些资源性对象，比如 SQLiteCursor(在析构函数finalize(),如果我们没有关闭它，它自己会调close()关闭)，如果我们没有关闭它，系统在回收它时也会关闭它，但是这样的效率太低了。因此对于资源性对象在不使用的时候，应该调用它的close()函数，将其关闭掉，然后才置为null.在我们的程序退出时一定要确保我们的资源性对象已经关闭。 程序中经常会进行查询数据库的操作，但是经常会有使用完毕Cursor后没有关闭的情况。如果我们的查询结果集比较小，对内存的消耗不容易被发现，只有在常时间大量操作的情况下才会复现内存问题，这样就会给以后的测试和问题排查带来困难和风险。

- 构造Adapter时，没有使用缓存的convertView

以构造ListView的BaseAdapter为例，在BaseAdapter中提供了方法： public View getView(int position, ViewconvertView, ViewGroup parent) 来向ListView提供每一个item所需要的view对象。初始时ListView会从BaseAdapter中根据当前的屏幕布局实例化一定数量的 view对象，同时ListView会将这些view对象缓存起来。当向上滚动ListView时，原先位于最上面的list item的view对象会被回收，然后被用来构造新出现的最下面的list item。这个构造过程就是由getView()方法完成的，getView()的第二个形参View convertView就是被缓存起来的list item的view对象(初始化时缓存中没有view对象则convertView是null)。由此可以看出，如果我们不去使用 convertView，而是每次都在getView()中重新实例化一个View对象的话，即浪费资源也浪费时间，也会使得内存占用越来越大。 ListView回收list item的view对象的过程可以查看: android.widget.AbsListView.java --> voidaddScrapView(View scrap) 方法。 示例代码：

```Java
public View getView(int position, ViewconvertView, ViewGroup parent) {
    View view = new Xxx(...); 
    ... ... 
    return view; 
} 
```

修正示例代码：

```Java
public View getView(int position, ViewconvertView, ViewGroup parent) {
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

- Bitmap对象不在使用时调用recycle()释放内存

有时我们会手工的操作Bitmap对象，如果一个Bitmap对象比较占内存，当它不在被使用的时候，可以调用Bitmap.recycle()方法回收此对象的像素所占用的内存，但这不是必须的，视情况而定。

- 试着使用关于application的context来替代和activity相关的context

这是一个很隐晦的内存泄漏的情况。有一种简单的方法来避免context相关的内存泄漏。最显著地一个是避免context逃出他自己的范围之外。使用Application context。这个context的生存周期和你的应用的生存周期一样长，而不是取决于activity的生存周期。如果你想保持一个长期生存的对象，并且这个对象需要一个context,记得使用application对象。你可以通过调用 Context.getApplicationContext() or Activity.getApplication()来获得。更多的请看这篇文章如何避免 Android内存泄漏。

- 注册没反注册造成的内存泄漏

一些Android程序可能引用我们的Anroid程序的对象(比如注册机制)。即使我们的Android程序已经结束了，但是别的引用程序仍然还有对我们的Android程序的某个对象的引用，泄漏的内存依然不能被垃圾回收。调用registerReceiver后未调用unregisterReceiver。 比如:假设我们希望在锁屏界面(LockScreen)中，监听系统中的电话服务以获取一些信息(如信号强度等)，则可以在LockScreen中定义一个 PhoneStateListener的对象，同时将它注册到TelephonyManager服务中。对于LockScreen对象，当需要显示锁屏界面的时候就会创建一个LockScreen对象，而当锁屏界面消失的时候LockScreen对象就会被释放掉。 但是如果在释放 LockScreen对象的时候忘记取消我们之前注册的PhoneStateListener对象，则会导致LockScreen无法被垃圾回收。如果不断的使锁屏界面显示和消失，则最终会由于大量的LockScreen对象没有办法被回收而引起OutOfMemory,使得system_process 进程挂掉。 虽然有些系统程序，它本身好像是可以自动取消注册的(当然不及时)，但是我们还是应该在我们的程序中明确的取消注册，程序结束时应该把所有的注册都取消掉。

- 集合中对象没清理造成的内存泄漏

我们通常把一些对象的引用加入到了集合中，当我们不需要该对象时，并没有把它的引用从集合中清理掉，这样这个集合就会越来越大。如果这个集合是static的话，那情况就更严重了。

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

