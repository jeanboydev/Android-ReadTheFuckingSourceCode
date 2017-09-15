# Android-性能优化-内存优化

## 概述

## JVM 内存分配机制

- 详见：[JVM 内存分配机制](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/JVM/JVM-内存分配机制.md)

## JVM 垃圾回收机制

- 详见：[JVM 垃圾回收机制](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/JVM/JVM-垃圾回收机制.md)

## DVM 与 JVM 的区别

- 虚拟机区别

Dalvik 虚拟机（DVM）是 Android 系统在 java虚拟机（JVM）基础上优化得到的，DVM 是基于寄存器的，而 JVM 是基于栈的，由于寄存器高效快速的特性，DVM 的性能相比 JVM 更好。

- 字节码区别

Dalvik 执行 **.dex** 格式的字节码文件，JVM 执行的是 **.class** 格式的字节码文件，Android 程序在编译之后产生的 .class 文件会被 aapt 工具处理生成 R.class 等文件，然后 dx 工具会把 .class 文件处理成 .dex 文件，最终资源文件和 .dex 文件等打包成 .apk 文件。

## OOM 代码相关优化

当应用程序申请的 java heap 空间超过 Dalvik VM HeapGrowthLimit 时溢出。 OOM 并不代表内存不足，只要申请的 heap 超过 Dalvik VM HeapGrowthLimit 时，即使内存充足也会溢出。 效果是能让较多进程常驻内存。

- Bitmap

Bitmap 非常消耗内存，而且在 Android 中，读取 bitmap 时， 一般分配给虚拟机的图片堆栈只有 8M，所以经常造成 OOM 问题。 所以有必要针对 Bitmap 的使用作出优化：

图片显示：加载合适尺寸的图片，比如显示缩略图的地方不要加载大图。
图片回收：使用完 bitmap，及时使用 Bitmap.recycle() 回收。
> 问题：Android不是自身具备垃圾回收机制吗？此处为何要手动回收。
Bitmap对象不是new生成的，而是通过BitmapFactory生产的。而且通过源码可发现是通过调用JNI生成Bitmap对象（nativeDecodeStream()等方法）。所以，加载bitmap到内存里包括两部分，Dalvik内存和Linux kernel内存。前者会被虚拟机自动回收。而后者必须通过recycle()方法，内部调用nativeRecycle()让linux kernel回收。

捕获OOM异常：程序中设定如果发生OOM的应急处理方式。
图片缓存：内存缓存、硬盘缓存等
图片压缩：直接使用ImageView显示Bitmap时会占很多资源，尤其当图片较大时容易发生OOM。可以使用BitMapFactory.Options对图片进行压缩。
图片像素：android默认颜色模式为ARGB_8888，显示质量最高，占用内存最大。若要求不高时可采用RGB_565等模式。图片大小：图片长度*宽度*单位像素所占据字节数
ARGB_4444：每个像素占用2byte内存
ARGB_8888：每个像素占用4byte内存 （默认）
RGB_565：每个像素占用2byte内存



计算 Bitmap 内存大小

我们知道 ARGB 指的是一种色彩模式，里面 A 代表 Alpha，R 表示 Red，G 表示 Green，B 表示 Blue。 所有的可见色都是由红绿蓝组成的，所以红绿蓝又称为三原色，每个原色都存储着所表示颜色的信息值,下表中对四种颜色模式的详细描述，以及每种色彩模式占用的字节数。

| 模式		| 描述													| 占用字节 |
| :------	| :--------------------------------						| :------ |
| ALPHA		| Alpha 由 8 位组成										| 1B	  |
| ARGB_4444	| 4 个 4 位组成 16 位，每个色彩元素站 4 位					| 2B	  |
| ARGB_8888	| 4 个 8 为组成 32 位，每个色彩元素站 8 位					| 4B	  |
| RGB_565	| R 为 5 位，G 为 6 位，B 为 5 位共 16 位，没有Alpha		| 2B	  |



- 对象引用类型

强引用，软引用，弱引用，虚引用

- 强引用（Strong Reference）:JVM宁愿抛出OOM，也不会让GC回收的对象 
- 软引用（Soft Reference） ：只有内存不足时，才会被GC回收。 
- 弱引用（weak Reference）：在GC时，一旦发现弱引用，立即回收 
- 虚引用（Phantom Reference）：任何时候都可以被GC回收，当垃圾回收器准备回收一个对象时，如果发现它还有虚引用，就会在回收对象的内存之前，把这个虚引用加入到与之关联的引用队列中。程序可以通过判断引用队列中是否存在该对象的虚引用，来了解这个对象是否将要被回收。可以用来作为GC回收Object的标志。 


- 对象池

对象池：如果某个对象在创建时，需要较大的资源开销，那么可以将其放入对象池，即将对象保存起来，下次需要时直接取出使用，而不用再次创建对象。当然，维护对象池也需要一定开销，故要衡量。
线程池：与对象池差不多，将线程对象放在池中供反复使用，减少反复创建线程的开销。

- 缓存

## 内存泄露相关优化

当一个对象已经不需要再使用了，本该被回收时，而有另外一个正在使用的对象持有它的引用从而导致它不能被回收，这导致本该被回收的对象不能被回收而停留在堆内存中，这就产生了内存泄漏。

- 单例造成的内存泄漏

单例模式非常受开发者的喜爱，不过使用的不恰当的话也会造成内存泄漏，由于单例的静态特性使得单例的生命周期和应用的生命周期一样长，这就说明了如果一个对象已经不需要使用了，而单例对象还持有该对象的引用，那么这个对象将不能被正常回收，这就导致了内存泄漏。

如下这个典例：

```Java
public class AppManager {
    private static AppManager instance;
    private Context context;
    private AppManager(Context context) {
        this.context = context;
    }
    public static AppManager getInstance(Context context) {
        if (instance != null) {
            instance = new AppManager(context);
        }
        return instance;
    }
}
```

这是一个普通的单例模式，当创建这个单例的时候，由于需要传入一个 Context，所以这个 Context 的生命周期的长短至关重要：

	1. 传入的是 Application 的 Context：这将没有任何问题，因为单例的生命周期和 Application 的一样长。
	2. 传入的是 Activity 的 Context：当这个 Context 所对应的 Activity 退出时，由于该 Context 和 Activity 的生命周期一样长（Activity 间接继承于 Context），所以当前 Activity 退出时它的内存并不会被回收，因为单例对象持有该 Activity 的引用。

所以正确的单例应该修改为下面这种方式：

```Java
public class AppManager {
    private static AppManager instance;
    private Context context;
    private AppManager(Context context) {
        this.context = context.getApplicationContext();
    }
    public static AppManager getInstance(Context context) {
        if (instance != null) {
            instance = new AppManager(context);
        }
        return instance;
    }
}
```
这样不管传入什么 Context 最终将使用 Application 的 Context，而单例的生命周期和应用的一样长，这样就防止了内存泄漏。


- 非静态内部类创建静态实例造成的内存泄漏

有的时候我们可能会在启动频繁的Activity中，为了避免重复创建相同的数据资源，可能会出现这种写法：

```Java
public class MainActivity extends AppCompatActivity {
    private static TestResource mResource = null;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        if(mResource == null){
            mResource = new TestResource();
        }
        //...
    }
    class TestResource {
    //...
    }
}
```

这样就在 Activity 内部创建了一个非静态内部类的单例，每次启动 Activity 时都会使用该单例的数据，这样虽然避免了资源的重复创建，不过这种写法却会造成内存泄漏，因为非静态内部类默认会持有外部类的引用，而又使用了该非静态内部类创建了一个静态的实例，该实例的生命周期和应用的一样长，这就导致了该静态实例一直会持有该 Activity 的引用，导致 Activity 的内存资源不能正常回收。

正确的做法为：

将该内部类设为静态内部类或将该内部类抽取出来封装成一个单例，如果需要使用 Context，请使用 ApplicationContext。

- Handler 造成的内存泄漏

Handler 的使用造成的内存泄漏问题应该说最为常见了，平时在处理网络任务或者封装一些请求回调等 api 都应该会借助 Handler 来处理，对于 Handler 的使用代码编写一不规范即有可能造成内存泄漏，如下示例：

```Java
public class MainActivity extends AppCompatActivity {
	private Handler mHandler = new Handler() {
	    @Override
	    public void handleMessage(Message msg) {
	    //...
	    }
	};
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        loadData();
    }
    private void loadData(){
        //...request
        Message message = Message.obtain();
        mHandler.sendMessage(message);
    }
}
```

这种创建 Handler 的方式会造成内存泄漏，由于 mHandler 是 Handler 的非静态匿名内部类的实例，所以它持有外部类 Activity 的引用，我们知道消息队列是在一个 Looper 线程中不断轮询处理消息，那么当这个 Activity 退出时消息队列中还有未处理的消息或者正在处理消息，而消息队列中的 Message 持有 mHandler 实例的引用，mHandler 又持有 Activity 的引用，所以导致该 Activity 的内存资源无法及时回收，引发内存泄漏，所以另外一种做法为：

```Java
public class MainActivity extends AppCompatActivity {
    private MyHandler mHandler = new MyHandler(this);
    private TextView mTextView ;
    private static class MyHandler extends Handler {
        private WeakReference<Context> reference;
        public MyHandler(Context context) {
        reference = new WeakReference<>(context);
        }
        @Override
        public void handleMessage(Message msg) {
            MainActivity activity = (MainActivity) reference.get();
            if(activity != null){
            activity.mTextView.setText("");
            }
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mTextView = (TextView)findViewById(R.id.textview);
        loadData();
    }

    private void loadData() {
        //...request
        Message message = Message.obtain();
        mHandler.sendMessage(message);
    }
}
```

创建一个静态 Handler 内部类，然后对 Handler 持有的对象使用弱引用，这样在回收时也可以回收 Handler 持有的对象，这样虽然避免了 Activity 泄漏，不过 Looper 线程的消息队列中还是可能会有待处理的消息，所以我们在 Activity 的 Destroy 时或者 Stop 时应该移除消息队列中的消息，更准确的做法如下：

```Java
public class MainActivity extends AppCompatActivity {
    private MyHandler mHandler = new MyHandler(this);
    private TextView mTextView ;
    private static class MyHandler extends Handler {
        private WeakReference<Context> reference;
        public MyHandler(Context context) {
        reference = new WeakReference<>(context);
        }
        @Override
        public void handleMessage(Message msg) {
            MainActivity activity = (MainActivity) reference.get();
            if(activity != null){
            activity.mTextView.setText("");
            }
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mTextView = (TextView)findViewById(R.id.textview);
        loadData();
    }

    private void loadData() {
        //...request
        Message message = Message.obtain();
        mHandler.sendMessage(message);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mHandler.removeCallbacksAndMessages(null);
    }
}
```

使用 mHandler.removeCallbacksAndMessages(null); 是移除消息队列中所有消息和所有的 Runnable。 当然也可以使用 mHandler.removeCallbacks(); 或 mHandler.removeMessages(); 来移除指定的 Runnable 和 Message。

- 线程造成的内存泄漏

对于线程造成的内存泄漏，也是平时比较常见的，异步任务和 Runnable 都是一个匿名内部类，因此它们对当前 Activity 都有一个隐式引用。 如果 Activity 在销毁之前，任务还未完成，那么将导致 Activity 的内存资源无法回收，造成内存泄漏。 正确的做法还是使用静态内部类的方式，如下：

```Java
static class MyAsyncTask extends AsyncTask<Void, Void, Void> {
    private WeakReference<Context> weakReference;

    public MyAsyncTask(Context context) {
        weakReference = new WeakReference<>(context);
    }

    @Override
    protected Void doInBackground(Void... params) {
        SystemClock.sleep(10000);
        return null;
    }

    @Override
    protected void onPostExecute(Void aVoid) {
        super.onPostExecute(aVoid);
        MainActivity activity = (MainActivity) weakReference.get();
        if (activity != null) {
        //...
        }
    }
}
static class MyRunnable implements Runnable{
    @Override
    public void run() {
        SystemClock.sleep(10000);
    }
}
//——————
new Thread(new MyRunnable()).start();
new MyAsyncTask(this).execute();
```

这样就避免了 Activity 的内存资源泄漏，当然在 Activity 销毁时候也应该取消相应的任务 AsyncTask::cancel()，避免任务在后台执行浪费资源。

- 资源使用完未关闭

对于使用了 BraodcastReceiver，ContentObserver，File，Cursor，Stream，Bitmap 等资源的使用，应该在 Activity 销毁时及时关闭或者注销，否则这些资源将不会被回收，造成内存泄漏。

## 其他优化

- 常用数据结构优化
- 枚举
- View 复用
- 谨慎使用多进程
- 尽量使用系统资源

## Android Studio Monitor Memory

## Memory Analyzer Tool

## LeakCanary

## Allocation Traker

## ANR

## 参考资料

http://hukai.me/android-performance-oom/

Android 内存优化总结 & 实践
https://juejin.im/entry/58d4c7735c497d0057ead153

你的 Bitmap 究竟占多大内存？
https://mp.weixin.qq.com/s?__biz=MzA3NTYzODYzMg==&amp;mid=403263974&amp;idx=1&amp;sn=b0315addbc47f3c38e65d9c633a12cd6&amp;scene=21#wechat_redirect

使用新版Android Studio检测内存泄露和性能
http://www.jianshu.com/p/216b03c22bb8

基于Android Studio的内存泄漏检测与解决全攻略
http://wetest.qq.com/lab/view/?id=99

Android 应用内存泄漏的定位、分析与解决策略
https://www.diycode.cc/topics/475

