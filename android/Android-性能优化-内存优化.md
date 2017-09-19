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

1. 图片显示：加载合适尺寸的图片，比如显示缩略图的地方不要加载大图。
2. 图片回收：使用完 bitmap，及时使用 Bitmap.recycle() 回收。

> 问题：Android 不是自身具备垃圾回收机制吗？此处为何要手动回收？
> 
> Bitmap 对象不是 new 生成的，而是通过 BitmapFactory 生产的。 而且通过源码可发现是通过调用 JNI 生成 Bitma p对象（nativeDecodeStream()等方法）。 所以，加载 bitmap 到内存里包括两部分，Dalvik 内存和 Linux kernel 内存。 前者会被虚拟机自动回收。 而后者必须通过 recycle() 方法，内部调用 nativeRecycle() 让 linux kernel 回收。

3. 捕获 OOM 异常：程序中设定如果发生 OOM 的应急处理方式。
4. 图片缓存：内存缓存、硬盘缓存等
5. 图片压缩：直接使用 ImageView 显示 Bitmap 时会占很多资源，尤其当图片较大时容易发 生OOM。 可以使用 BitMapFactory.Options 对图片进行压缩。
6. 图片像素：android 默认颜色模式为 ARGB_8888，显示质量最高，占用内存最大。 若要求不高时可采用 RGB_565 等模式。 
7. 图片大小：图片 长度×宽度×单位像素 所占据字节数。

我们知道 ARGB 指的是一种色彩模式，里面 A 代表 Alpha，R 表示 Red，G 表示 Green，B 表示 Blue。 所有的可见色都是由红绿蓝组成的，所以红绿蓝又称为三原色，每个原色都存储着所表示颜色的信息值,下表中对四种颜色模式的详细描述，以及每种色彩模式占用的字节数。

| 模式		| 描述													| 占用字节 |
| :------	| :--------------------------------						| :------ |
| ALPHA		| Alpha 由 8 位组成										| 1B	  |
| ARGB_4444	| 4 个 4 位组成 16 位，每个色彩元素站 4 位					| 2B	  |
| ARGB_8888	| 4 个 8 为组成 32 位，每个色彩元素站 8 位（默认）			| 4B	  |
| RGB_565	| R 为 5 位，G 为 6 位，B 为 5 位共 16 位，没有Alpha		| 2B	  |


- 对象引用类型

强引用，软引用，弱引用，虚引用

- 强引用（Strong Reference）:JVM宁愿抛出OOM，也不会让GC回收的对象 
- 软引用（Soft Reference） ：只有内存不足时，才会被GC回收。 
- 弱引用（weak Reference）：在GC时，一旦发现弱引用，立即回收 
- 虚引用（Phantom Reference）：任何时候都可以被 GC 回收，当垃圾回收器准备回收一个对象时，如果发现它还有虚引用，就会在回收对象的内存之前，把这个虚引用加入到与之关联的引用队列中。 程序可以通过判断引用队列中是否存在该对象的虚引用，来了解这个对象是否将要被回收。 可以用来作为 GC 回收 Object 的标志。 


- 缓存池

对象池：如果某个对象在创建时，需要较大的资源开销，那么可以将其放入对象池，即将对象保存起来，下次需要时直接取出使用，而不用再次创建对象。当然，维护对象池也需要一定开销，故要衡量。
线程池：与对象池差不多，将线程对象放在池中供反复使用，减少反复创建线程的开销。

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

BraodcastReceiver，ContentObserver，FileObserver，Cursor，Callback等在 Activity onDestroy 或者某类生命周期结束之后一定要 unregister 或者 close 掉，否则这个 Activity 类会被 system 强引用，不会被内存回收。

不要直接对 Activity 进行直接引用作为成员变量，如果不得不这么做，请用 private WeakReference mActivity 来做，相同的，对于Service 等其他有自己声明周期的对象来说，直接引用都需要谨慎考虑是否会存在内存泄露的可能。

## 其他优化

- 常用数据结构优化

1. ArrayMap 及 SparseArray 是 android 的系统API，是专门为移动设备而定制的。 用于在一定情况下取代 HashMap 而达到节省内存的目的。 对于 key 为 int 的 HashMap 尽量使用 SparceArray 替代，大概可以省 30% 的内存，而对于其他类型，ArrayMap 对内存的节省实际并不明显，10% 左右，但是数据量在 1000 以上时，查找速度可能会变慢。
2. 避免在 Android 里面使用 Enum。
3. 在有些时候，代码中会需要使用到大量的字符串拼接的操作，这种时候有必要考虑使用 StringBuilder 来替代频繁的 “+”。

- 枚举

Android 平台上枚举是比较争议的，在较早的 Android 版本，使用枚举会导致包过大，使用枚举甚至比直接使用 int 包的 size 大了 10 多倍。 在 stackoverflow 上也有很多的讨论, 大致意思是随着虚拟机的优化，目前枚举变量在 Android 平台性能问题已经不大，而目前 Android 官方建议，使用枚举变量还是需要谨慎，因为枚举变量可能比直接用 int 多使用 2 倍的内存。

- View 复用

1. 使用 ListView 时 getView 里尽量复用 conertView，同时因为 getView 会频繁调用，要避免频繁地生成对象。 优先考虑使用 RecyclerView 代替 ListView。
2. 重复的布局优先使用 <include>，使用 <merge> 减少 view 的层级，对于可以延迟初始化的页面，使用 <ViewStub>。

- 谨慎使用多进程

现在很多 App 都不是单进程，为了保活，或者提高稳定性都会进行一些进程拆分，而实际上即使是空进程也会占用内存(1M 左右)，对于使用完的进程，服务都要及时进行回收。

- 系统资源

尽量使用系统组件，图片甚至控件的 id。 例如：@android:color/xxx，@android:style/xxx。

## 使用工具检查内存泄漏

即使在编码时将上述情况都考虑了，往往会有疏忽的地方，更何况通常情况下是团队开发。 所以不仅仅要在编码时考虑内存优化的情况，当出现内存泄漏时，更有效更准确的定位问题才是最重要的方式。 内存泄漏不像 bug，排查起来相对复杂一些，下面介绍下常用的检查方式。

## 使用 Lint 代码静态检查

Lint 是 Android Studio 自带的工具，使用很简单找到 **Analyze** -> **Inspect Code** 然后选择想要扫面的区域即可。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_lint1.jpg" alt="memory_lint1"/>

选择 Lint 扫描区域。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_lint2.jpg" alt="memory_lint2"/>

对可能引起性能问题的代码，Lint 都会进行提示。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_lint3.jpg" alt="memory_lint3"/>

## 使用 Android Studio 自带的 Monitor Memory 检查

一般在 Android Studio 的底部可以找到 Android Monitor。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_ast_1.jpg" alt="Monitor Memory 1"/>

可以看到当前 App的内存变动比较大，很有可能出现了内存泄漏。 点击 Dump Java Heap，等一段时间会自动生成 Heap Snapshot 文件。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_ast_2.jpg" alt="Monitor Memory 2"/>

在 Captures 中可以找到 hprof 文件。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_ast_3.jpg" alt="Monitor Memory 3"/>

在右侧找到 Analyzer Tasks 并打开，点击图中 Perform Analysis 按钮开始分析。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_ast_4.jpg" alt="Monitor Memory 4"/>

通过分析结果可以看到 TestActivity 泄漏了，从左侧 Reference Tree 中可以看到是 TestActivity 中的 context 泄露了。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_ast_5.jpg" alt="Monitor Memory 5"/>

我们来看下代码：

```Java
public class TestActivity extends AppCompatActivity {

    private static Context context;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);

        context = this;

    }
}
```

代码中 context 为静态的引用了当前 Activity 造成了当前 Activity 无法释放。

一般的通过 使用 Android Studio 自带的 Monitor Memory 可以定位到内存泄漏所在的类，更详细的信息需要借助 Memory Analyzer Tool（MAT）工具。


## 使用 Memory Analyzer Tool 检查

首先下载 Memory Analyzer Tool [下载地址](http://www.eclipse.org/mat/downloads.php)

在 Android Studio 中先将 hprof 文件导出为 MAT 可以识别的 hprof 文件。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat1.jpg" alt="MAT1"/>

打开刚才导出的文件。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat2.jpg" alt="MAT2"/>

经过分析后会显示如下，Leak Suspectss 是一个关于内存泄露猜想的饼图，Problem Suspect 1 是泄露猜想的描述。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat3.jpg" alt="MAT3"/>

Overview 是一个概况图，把内存的消耗以饼状图形式显示出来，鼠标在每个饼块区域划过或者点击，就会在 Inspector 栏目显示这块区域的相关信息。 MAT 从多角度提供了内存分析，其中包括 Histogram、 Dominator Tree、 Leak Suspects 和 Top consumers 等。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat4.jpg" alt="MAT4"/>

这里我们使用 Histogram 进行分析，切换到 Histogram 页面。 这个页面主要有 4 个列，Class Name、 Objects、 Shallow Heap 和 Retained Heap。 其中 Class Name 是全类名，Objects 是这个类的对象实例个数。 Shallow Heap 是对象本身占用内存大小，非数组的常规对象，本身内存占用很小，所以这个对泄露分析作用不大。 Retained Heap 指当前对象大小和当前对象能直接或间接引用的对象大小的总和，这个栏目是分析重点。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat5.jpg" alt="MAT5"/>

内存分析是分析的整个系统的内存泄露，而我们只要查找我们 App 的内存泄露情况。 这无疑增加了很多工作，不过幸亏 Histogram 支持正则表达式查找，在 Regex 中输入我们的包名进行过滤，直奔和我们 App 有关的内存泄露。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat6.jpg" alt="MAT6"/>

过滤后就显示了我们 App 相关内存信息，按 Retained Heap 大小排列下，发现 MainActivity 和 TestActivity 这两个类问题比较大。 TestActivity 的问题更突出些，所以先从 TestActivity 下手。

首先看下是哪里的引用导致了 TestActivity 不能被 GC 回收。 右键使用 **Merge Shortest Paths to GC Roots** 显示距 GC Root 最短路径，当然选择过程中要排除软引用和弱引用，因为这些标记的一般都是可以被回收的。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat7.jpg" alt="MAT7"/>

进入结果页查看。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_mat8.jpg" alt="MAT8"/>

可以看到 TestActivity 不能被 GC 回收是因为 context 没有释放的原因。 我们再来看下代码：

```Java
public class TestActivity extends AppCompatActivity {

    private static Context context;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);

        context = this;

    }
}
```

## 使用 LeakCanary 检查

项目地址：https://github.com/square/leakcanary

使用方式很简单，参考项目里面的介绍即可。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/memory_leak_test.jpg" alt="LeakCanary"/>

## Allocation Traker

## ANR

## 参考资料

[Android Bitmap的内存大小是如何计算的？](https://ivonhoe.github.io/2017/03/22/Bitmap&Memory/)

[Android性能优化之常见的内存泄漏](http://hanhailong.com/2015/12/27/Android性能优化之常见的内存泄漏/)

[使用新版Android Studio检测内存泄露和性能](http://www.jianshu.com/p/216b03c22bb8)

[Android 应用内存泄漏的定位、分析与解决策略](https://www.diycode.cc/topics/475)


#####

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

