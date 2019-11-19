# 计算性能优化

上一篇文章 [渲染性能优化](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/android/performance/01_render.md) 中，我们分析了 UI 可能引起卡顿原因。卡顿的因素有很多，UI 只是其中一个因素。应用是否流畅往往也与 CPU 的计算性能有关，接下来我们从代码上来分析下引起性能问题的因素。

## ArrayMap 与 HashMap

ArrayMap 是 Android 提供的工具类，在 `android.util.ArrayMap` 中，ArrayMap 的使用方式与 HashMap 几乎没有差别。

```java
ArrayMap<String, String> arrayMap = new ArrayMap<>();
arrayMap.put("test","haha");
arrayMap.get("test");
arrayMap.remove("test");
```

我们知道 HasnMap  使用 `链表` + `红黑树` 的方式实现，对 HashMap 不熟悉的小伙伴可以看下我之前写过的 [HashMap 源码分析](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/java/basic/01_hashmap.md) 这篇文章。

ArrayMap 使用数组的方式实现，想了解更多细节内容可以看下这篇文章 [深入剖析 Android 中的  ArrayMap](https://droidyue.com/blog/2017/02/12/dive-into-arraymap-in-android/)。

ArrayMap 相比 HasnMap 占用内存更小，遍历效率更快。但是，ArrayMap 在数据量过多（> 1000）时性能并不比 HashMap 好。所以 ArrayMap 更适合数据量比较少，数据结构类型为 Map 类型的情况。

## 自动装箱

自动装箱就是 Java 自动将原始类型值转换成对应的对象，比如将 int 的变量转换成 Integer 对象，这个过程叫做装箱，反之将 Integer 对象转换成 int 类型值，这个过程叫做拆箱。

因为这里的装箱和拆箱是自动进行的非人为转换，所以就称作为自动装箱和拆箱。

原始类型 byte、short、char、int、long、float、double 和 boolean 对应的封装类为Byte、Short、Character、Integer、Long、Float、Double、Boolean。

```java
ArrayList<Integer> intList = new ArrayList<Integer>();
intList.add(1); // 自动装箱
int number = intList.get(1); // 自动拆箱
```

### 自动装箱的弊端

自动装箱有一个问题，那就是在一个循环中进行自动装箱操作的情况，如下面的例子就会创建多余的对象，影响程序的性能。

```java
Integer sum = 0;
 for(int i=1000; i<5000; i++){
   sum += i;
}
```

上面的代码 `sum += i` 可以看成 `sum = sum + i`，但是 + 这个操作符不适用于 Integer 对象。首先 sum 进行自动拆箱操作，进行数值相加操作，最后发生自动装箱操作转换成 Integer 对象。其内部变化如下

```java
int result = sum.intValue() + i;
Integer sum = new Integer(result);
```

由于我们这里声明的 sum 为 Integer 类型，在上面的循环中会创建将近 5000 个无用的 Integer 对象，在这样庞大的循环中，会降低程序的性能并且加重了垃圾回收的工作量。因此在我们编程时，需要注意到这一点，正确地声明变量类型，避免因为自动装箱引起的性能问题。

## SparseArray

为了避免上面示例代码中的自动装箱行为，Android 系统提供了 SparseArray、SparseBoolArray、SparseIntArray、SparseLongArray、LongSparseArray 等容器。

SparseArray 用法如下：

```java
SparseArray sparseArray = new SparseArray();
sparseArray.append(1,"aaaa");
sparseArray.get(1);
sparseArray.remove(1);
```

SparseArray 与 ArrayMap 的实现原理相似，不同的是 SparseArray 的 key 只能为 int 类型。所以 SparseArray 适合数据量比较少，数据结构 key 为 Integer 的 Map 类型的情况。

SparseBoolArray、SparseIntArray、SparseLongArray、LongSparseArray 与 SparseArray 相似，只不过 value 值为对应名称中限定的值类型，例如 SparseBoolArray 的 value 必须为 bool 类型，比较简单这里不再赘述。


## 线程

在程序开发的实践当中，为了让程序表现得更加流畅，我们肯定会需要使用到多线程来提升程序的并发执行性能。

但是编写多线程并发的代码一直以来都是一个相对棘手的问题，所以想要获得更佳的程序性能，我们非常有必要掌握多线程并发编程的基础技能。

### UI 线程与主线程

当程序启动的时候 Android 会自动创建一个进程和一个线程，这个线程负责界面更新，收集系统事件和用户的操作事件等并分配给对应的组件，所以这个线程非常重要 被称为主线程（Main Thread）。

因为所的和 UI 有关的操作都是在这个线程当中进行的所以也被称作 UI 线程（UI Thread）。所以说默认情况下主线程和 UI 线程指的是同一个线程。

众所周知，Android 程序的大多数代码操作都必须执行在主线程，例如系统事件（设备屏幕发生旋转)，输入事件（用户点击滑动等），程序回调服务，UI 绘制以及闹钟事件等等。那么我们在上述事件或者方法中插入的代码也将执行在主线程。

![MainThread](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/01.png)

一旦我们在主线程里面添加了操作复杂的代码，这些代码就很可能阻碍主线程去响应点击/滑动事件，阻碍主线程的 UI 绘制等等。

我们知道，为了让屏幕的刷新帧率达到 60fps，我们需要确保 16ms 内完成单次刷新的操作。

一旦我们在主线程里面执行的任务过于繁重，就可能导致接收到刷新信号的时候因为资源被占用而无法完成这次刷新操作，这样就会产生掉帧的现象，刷新帧率自然也就跟着下降了（一旦刷新帧率降到 20fps 左右，用户就可以明显感知到卡顿不流畅了）。

![掉帧](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/02.png)

为了避免上面提到的掉帧问题，我们需要使用多线程的技术方案，把那些操作复杂的任务移动到其他线程当中执行，这样就不容易阻塞主线程的操作，也就减小了出现掉帧的可能性。

![减少掉帧](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/03.png)

那么问题来了，为主线程减轻负的多线程方案有哪些呢？这些方案分别适合在什么场景下使用？Android 系统为我们提供了若干组工具类来帮助解决这个问题。

### AsyncTask

为 UI 线程与工作线程之间进行快速的切换提供一种简单便捷的机制。适用于当下立即需要启动，但是异步执行的生命周期短暂的使用场景。

AsyncTask 作为 Android 的基础之一，怎么使用就不多介绍了，网上到处都是教程，建议查看 Android 官方文档 [Android 开发文档 - AsyncTask](https://developer.android.google.cn/reference/android/os/AsyncTask.html)。

AsyncTask 使用起来比较繁琐，使用不当很容易造成内存泄漏，通常情况下使用 Handler 也可以达到相同的效果。

### HandlerThread

为某些回调方法或者等待某些任务的执行设置一个专属的线程，并提供线程任务的调度机制。

HandlerThread 本质就是一个带有 Looper 的线程，如果你对 Handler 机制比较熟悉看一眼 HandlerThread 源码就明白了。不熟悉 Handler 机制的小伙伴可以看下我之前写的文章 [最通俗易懂的 Handler 源码解析](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/android/basic/07_handler.md)。

### ThreadPool

Android 中线程池一般是使用 Java 中提供的 Executor 来实现。Executor 位于 `java.util.concurrent` 包下，具体实现为 ThreadPoolExecutor 和 ScheduledThreadPoolExecutor。

Executor 预定义了一些线程池：

- FixedThreadPool

创建一个定长线程池，可控制线程最大并发数，超出的线程会在队列中等待。

- CachedThreadPool

创建一个可缓存线程池，如果线程池长度超过处理需要，可灵活回收空闲线程，若无可回收，则新建线程。

- SingleThreadExecutor

创建一个单线程化的线程池，它只会用唯一的工作线程来执行任务，保证所有任务按照指定顺序（FIFO/ LIFO 优先级）执行。

- ScheduledThreadPool

创建一个定长线程池，支持定时及周期性任务执行。

关于线程池的使用这里不做过多介绍，网上也有很多文章。想要了解线程池的具体实现细节推荐阅读下《Java 并发编程的艺术》。

### IntentService

适合于执行由 UI 触发的后台 Service 任务，并可以把后台任务执行的情况通过一定的机制反馈给 UI。

IntentService 使用方式如下：

```java
public class TestIntentService extends IntentService {

  public TestIntentService(String name) {
    super(name);
  }

  @Override
  protected void onHandleIntent(@Nullable Intent intent) {
    //TODO: 耗时操作
    Log.e(TestIntentService.class.getSimpleName(), 
          "======== currentThread:" + Thread.currentThread().getName());
    Log.e(TestIntentService.class.getSimpleName(), 
          "======== 耗时操作开始:" + System.currentTimeMillis());
    try {
      Thread.sleep(5000);
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
    Log.e(TestIntentService.class.getSimpleName(),
          "======== 耗时操作结束:" + System.currentTimeMillis());
  }
}
```

查看的源码可以发现 IntentService 是 Service + HandlerThread 的方式实现的，这就很好理解 IntentService 为什么能处理异步任务了。

## 避免 ANR

ANR（Application Not responding），是指应用程序未响应，Android 系统对于一些事件需要在一定的时间范围内完成，如果超过预定时间能未能得到有效响应或者响应时间过长，都会造成 ANR。

一般地，这时往往会弹出一个提示框，告知用户「当前 xxx 未响应」，用户可选择继续等待或者 Force Close。

那么哪些场景会造成 ANR 呢？

- Service Timeout：比如前台服务在 20s 内未执行完成；
- BroadcastQueue Timeout：比如前台广播在 10s 内未执行完成；
- ContentProvider Timeout：内容提供者,在 publish 过超时 10s；
- InputDispatching Timeout：输入事件分发超时 5s，包括按键和触摸事件。

### 如何避免

基本的思路就是将耗时操作在子线程来处理，减少其他耗时操作和错误操作。

- 使用 [AsyncTask](http://droidyue.com/blog/2014/11/08/bad-smell-of-asynctask-in-android/) 处理耗时 IO 操作。
- 使用T hread 或者 HandlerThread 时，调用 Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND) 设置优先级，否则仍然会降低程序响应，因为默认 Thread 的优先级和主线程相同。
- 使用 [Handler](http://droidyue.com/blog/2014/12/28/in-android-handler-classes-should-be-static-or-leaks-might-occur/) 处理工作线程结果，而不是使用 Thread.wait() 或者 Thread.sleep() 来阻塞主线程。
- Activity 的 onCreate 和 onResume 回调中尽量避免耗时的代码
- BroadcastReceive 中 onReceive 代码也要尽量减少耗时，建议使用 IntentService 处理。

### 如何定位

如果开发机器上出现问题，我们可以通过查看 `/data/anr/traces.txt` 即可，最新的 ANR 信息在最开始部分。

可以通过 ADB 命令将其导出到本地：

> $ adb pull data/anr/traces.txt

`traces.txt` 默认会被导出到 **Android SDK/platform-tools** 目录。一般来说 `traces.txt` 文件记录的东西会比较多，分析的时候需要有针对性地去找相关记录。

关于 traces.txt 日志的分析可参考 [说说 Android 中的 ANR](https://droidyue.com/blog/2015/07/18/anr-in-android/)、[Android ANR：原理分析及解决办法](https://www.jianshu.com/p/388166988cef) 这两篇文章。

## Traceview

TraceView 是 Android SDK 中内置的一个工具，它可以加载 trace 文件，用图形的形式展示代码的执行时间、次数及调用栈，便于我们分析。

TraceView 在最新的 SDK 中已经找不到，[Android 开发文档 ](https://developer.android.com/studio/profile/traceview?hl=zh-cn) 上也注明了已弃用，感兴趣的可以看下这篇文章：[Android 性能优化：使用 TraceView 找到卡顿的元凶](https://blog.csdn.net/u011240877/article/details/54347396)。

## CPU Profiler

最新的 Android Studio 提供了 CPU Profiler 来代替 TraceView，它是 Android Profiler 中的一个工具，可以在 **View > Tool Windows > Android Profiler** 中打开 CPU Profiler 界面。

![CPU Profiler](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/04.png)

CPU Profiler 的使用在 [Android 开发文档 - 使用 CPU Profiler 检查 CPU Activity 和函数跟踪](https://developer.android.com/studio/profile/cpu-profiler?hl=zh-cn) 中介绍的很详细，国内也有很多类似的文章比如 [Android Studio 3.0 利用 Android Profiler 测量应用性能](https://juejin.im/post/5b7cbf6f518825430810bcc6#heading-3)，大家搜一下看看就好，这里就不做过多介绍。

## Systrace

Systrace 是 Android 4.1 版本之后推出的，一个对系统性能分析的工具。

Systrace 的功能包括跟踪系统的 I/O 操作、内核工作队列、CPU 负载以及 Android 各个子系统的运行状况等。

在 Android 平台中，它主要由 3 部分组成：

- 内核部分

Systrace 利用了 Linux Kernel 中的 ftrace 功能。所以，如果要使用 Systrace 的话，必须开启 Krnel 中和 ftrace 相关的模块。

- 数据采集部分

Android 定义了一个 Trace 类。应用程序可利用该类把统计信息输出给 ftrace。同时，Android 还有一个 atrace 程序，它可以从 ftrace 中读取统计信息然后交给数据分析工具来处理。

- 数据分析工具

Android SDK 提供一个 systrace.py（python 脚本文件，位于 Android SDK 目录 `/sdk/platform-tools/systrace` 中，其内部将调用 atrace 程序）用来配置数据采集的方式（如采集数据的标签、输出文件名等）和收集 ftrace统 计数据并生成一个结果网页文件供用户查看。

简单来说，当机器以60帧/秒显示（也就是 16.6 ms），用户会感觉机器会流畅。如果出现显示时出现丢帧的情况，就需要知道系统在做什么？

Systrace 是用来收集系统和应用的数据信息和一些中间生成数据的细节，在 Android 4.1 系统和 4.1之 后的系统。Systrace 在一些分析显示的问题上特别有用，如应用画图慢，显示动作或动画时变形。

### 安装 Python

Systrace 是一个 python 脚本，因此需要安装 Python 环境才能运行，不同操作系统环境配置不太一样，大家根据自己的操作系统安装就好。

### 连接手机

使用 USB 连接要测试的手机，并打开 USB 调试开关。

### 抓取 Systrace 信息

首先，进入 `Android/Sdk/platform-tools/systrace` 目录。

Systrace 运行的命令格式如下：

> $ python systrace.py [options] [category1 [category2 ...]]

options 表示选项，category 表示需要抓取的 trace 类别，默认抓取所有的类别，也可以进行指定。

常用 options 有：

| options                                       | 描述                                                     |
| --------------------------------------------- | -------------------------------------------------------- |
| -o \<FILE\>                                   | 输出的目标文件                                           |
| -t N, –time=N                                 | 执行时间，默认 5s                                        |
| -b N, –buf-size=N                             | buffer 大小（单位 kB)，用于限制 trace 总大小，默认无上限 |
| -k \<KFUNCS\>，–ktrace=\<KFUNCS\>             | 追踪 Kernel 函数，用逗号分隔                             |
| -a \<APP_NAME\>,–app=\<APP_NAME\>             | 追踪应用包名，用逗号分隔                                 |
| –from-file=\<FROM_FILE\>                      | 从文件中创建互动的 systrace                              |
| -e \<DEVICE_SERIA\>,–serial=\<DEVICE_SERIAL\> | 指定设备                                                 |
| -l, –list-categories                          | 列举可用的 tags                                          |

例如下面命令：

> $ python systrace.py -b 8000 -t 5 -o systrace.html

通过以上的这些命令，最终将会获得 html 类型的报告结果。Chrome 浏览器可以打开 systrace.html，如果打不开，可以浏览器输入 `chrome://tracing/`，然后选择 load systrace。

### 查看报告

通过 Chrome 浏览器打开 html 报告，将会出现类似如下图的结果：

![systrace 报告](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/05.jpg)

左侧这一栏表示各个进程中 trace 的 TraceName，中间则是各个 Trace 对应的时间轴，可以看到由各种颜色标记。其中 `绿色` 表示正常，其他颜色如 `红色`、`黄色` 则表示需要优化。

鼠标可以控制滑动，WASD 可以用来 zoom in/out（W，S）和左右滑动（A，D）。在刚跑的 trace 数据最上面，能看到 CPU 的详细数据， CPU 数据的下面是几个可折叠的区域，分别表示不同的活跃进程。每一个色条表示系统的一个行为，色条的长度表示该行为的耗时（放大可以看到更多细节）。

| 快捷键 | 作用                                |
| ------ | ----------------------------------- |
| w      | 放大                                |
| s      | 缩小                                |
| a      | 左移                                |
| d      | 右移                                |
| f      | 返回选中区域，且放大选中区域        |
| m      | 标记当前选定区域                    |
| v      | 高亮 VSync                          |
| g      | 切换是否显示 60hz 的网格线          |
| 0(零)  | 恢复trace到初始态                   |
| h      | 切换是否显示详情                    |
| /      | 搜索关键字                          |
| enter  | 显示搜索结果，可通过← →定位搜索结果 |
| `      | 显示/隐藏脚本控制台                 |
| ?      | 显示帮助功能                        |

### 调查 UI 性能

正常情况下，大约以每秒 60 帧，一帧约 16.6ms 的速率渲染，如果超过这个时间，F 圆圈就会变成红色或者黄色。这时可以点击 F 圆圈，会给出详细信息，以及可能的解决方案，如下图所示：

![调查 UI 性能](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/06.png)

对于 Android 5.0（API level 21）或者更高的设备，渲染帧的工作在 UI Thread 和 Render Thread 这两个线程当中。对于更早的版本，则所有工作在 UI Thread上 进行。

### Alerts

Alerts 一栏标记了以下性能有问题的点，你可以点击该点查看详细信息，右边侧边栏还有一个 Alerts 框，点击可以查看每个类型的 Alerts 的数量。

![ALerts](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/07.jpg)

在每个包下都有 Frame 一栏，该栏中都有一个一个的 F 代表每一个 Frame，用颜色来代表性能的好坏，依次为绿-黄-红（性能越来越差），点击某一个  F，会显示该 Frame 绘制过程中的一些 Alerts 信息，如果你想查看 Frame 的耗时，可以点击某个 F 标志，然后按 m 键。

![Frame](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/02_compute/08.jpg)

## 参考资料

- [YouTube - 性能优化典范 第三季](https://www.youtube.com/watch?v=ORgucLTtTDI&list=PLKbs_pHKyapmK84ah_AattCdso6gQyujx)
- [YouTube - 性能优化典范 第四季](https://www.youtube.com/watch?v=7lxVqqWwTb0&list=PL8cvstvtecscVxHNy2evUa9M5zOsI3unW)
- [YouTube - 性能优化典范 第五季](https://www.youtube.com/watch?v=0Z5MZ0jL2BM&list=PL8ktV16dN_6tCnhgyduLgJBqT6asYYBWU)
- [深入剖析 Android中的 ArrayMap](https://droidyue.com/blog/2017/02/12/dive-into-arraymap-in-android/)
- [Android 开发文档 - SparseArray](https://developer.android.com/reference/android/util/SparseArray.html)
- [Android 开发文档 - AsyncTask](https://developer.android.google.cn/reference/android/os/AsyncTask.html)
- [Android 开发文档 - Background](https://developer.android.com/guide/background/)
- [Android 开发文档 - 使应用能迅速响应](https://developer.android.com/training/articles/perf-anr.html#anr)
- [说说 Android 中的 ANR](https://droidyue.com/blog/2015/07/18/anr-in-android/)
- [Android ANR：原理分析及解决办法](https://www.jianshu.com/p/388166988cef)
- [Android 开发文档 - 使用 Traceview 检查跟踪日志](https://developer.android.com/studio/profile/traceview?hl=zh-cn)
- [Android 性能优化：使用 TraceView 找到卡顿的元凶](https://blog.csdn.net/u011240877/article/details/54347396)
- [Android 开发文档 - 使用 CPU Profiler 检查 CPU Activity 和函数跟踪](https://developer.android.com/studio/profile/cpu-profiler?hl=zh-cn)
- [Android Studio 3.0 利用 Android Profiler 测量应用性能](https://juejin.im/post/5b7cbf6f518825430810bcc6#heading-3)
- [Android 开发文档 - Systrace 概述](https://developer.android.com/studio/profile/systrace)
- [Android 性能工具 Systrace 的使用](https://blog.csdn.net/FightFightFight/article/details/83385177)
- [Android 性能分析工具 systrace 使用](https://www.cnblogs.com/1996swg/p/10007602.html)
- [胡凯 - Android 性能优化典范 - 第 5 季](http://hukai.me/android-performance-patterns-season-5/)