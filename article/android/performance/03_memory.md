# 内存性能优化

Android 为每个应用分配内存时，采用弹性的分配方式，即刚开始并不会给应用分配很多的内存，而是给每一个进程分配一个「够用」的内存大小，这个大小值是根据每一个设备的实际的物理内存大小来决定的。

随着应用的运行和使用，Android 会为应用分配一些额外的内存大小。但是分配的大小是有限度的，系统不可能为每一个应用分配无限大小的内存。

总之，Android 系统需要最大限度的让更多的进程存活在内存中，以保证用户再次打开应用时减少应用的启动时间，提高用户体验。

关于 Android 系统内存管理机制的相关细节，推荐大家阅读下这两篇文章：[谈谈 Android 的内存管理机制](https://zhuanlan.zhihu.com/p/27176914)、[Android 操作系统的内存回收机制](https://www.ibm.com/developerworks/cn/opensource/os-cn-android-mmry-rcycl/index.html)。

## 避免内存溢出

内存溢出（Out Of Memory 简称 OOM），简单地说内存溢出就是指程序运行过程中，申请的内存大于系统能够提供的内存，导致无法申请到足够的内存，于是就发生了内存溢出。

### 减小对象的内存占用

避免 OOM 的第一步就是要尽量减少新分配出来的对象占用内存的大小，尽量使用更加轻量的对象。

#### 使用更加轻量的数据结构

例如，我们可以考虑使用 ArrayMap/SparseArray 而不是 HashMap 等传统数据结构。

通常的 HashMap 的实现方式更加消耗内存，因为它需要一个额外的实例对象来记录 Mapping 操作。另外，SparseArray 更加高效在于他们避免了对 key 与 value 的 autobox 自动装箱，并且避免了装箱后的解箱。

关于更多ArrayMap/SparseArray的讨论，请参考上一篇 [性能优化 - 计算性能优化]() 的内容。

#### 正确的使用枚举类型

枚举类型（Enums），是 Java 语言中的一个特性。但 Android 官方强烈建议不要在 Android 应用里面使用到 Enums，是因为枚举类型在编译之后会生成很多内部类，在移动设备上内存比较珍贵显然会很占用内存。想了解枚举的实现细节可以查看 [Java 枚举类型的实现原理](https://blog.csdn.net/mhmyqn/article/details/48087247) 这篇文章。

所以了解了枚举类型的实现原理可以发现，在 Android 程序里不是不可以使用枚举类型，而是推荐使用。合理的使用枚举类型可以做到一些很优雅的操作，比如单例模式。

```java
public enum  EnumSingleton {
    INSTANCE;
}
```

我们把字节码反编译后可以看到：

```java
public final class EnumSingleton extends Enum<EnumSingleton> {
  public static final EnumSingleton INSTANCE;
  public static EnumSingleton[] values();
  public static EnumSingleton valueOf(String s);
  static {};
}
```

由反编译后的代码可知，**INSTANCE** 被声明为 **static** 的，在类加载过程中，虚拟机会保证一个类的*`<clinit>()`* 方法在多线程环境中被正确的加锁、同步。所以，枚举实现是在实例化时是线程安全。

Java 虚拟机规范中规定，每一个枚举类型极其定义的枚举变量在 JVM 中都是唯一的，因此在枚举类型的序列化和反序列化上，Java 做了特殊的规定。

在序列化的时候 Java 仅仅是将枚举对象的 name 属性输出到结果中，反序列化的时候则是通过 `java.lang.Enum` 的 valueOf 方法来根据名字查找枚举对象。同时，编译器是不允许任何对这种序列化机制的定制的，因此禁用了 writeObject、readObject、readObjectNoData、writeReplace 和 readResolve 等方法。

普通的 Java 类的反序列化过程中，会通过反射调用类的默认构造函数来初始化对象。所以，即使单例中构造函数是私有的，也会被反射给破坏掉。由于反序列化后的对象是重新 new 出来的，所以这就破坏了单例。

但是，枚举的反序列化并不是通过反射实现的。所以，也就不会发生由于反序列化导致的单例破坏问题。

感兴趣的可以参看 stackoverflow 上的回答 [What is an efficient way to implement a singleton pattern in Java? ](https://stackoverflow.com/questions/70689/what-is-an-efficient-way-to-implement-a-singleton-pattern-in-java)

#### 减小 Bitmap 对象的内存占用

Bitmap 是一个极容易消耗内存的大胖子，关于 Bitmap 内存占用大小详情请参阅 [Android 坑档案：你的 Bitmap 究竟占多大内存？](https://zhuanlan.zhihu.com/p/20732309)，所以减小创建出来的 Bitmap 的内存占用是很重要的，通常来说有下面 2 个措施：

- 缩放比例

在把图片载入内存之前，我们需要先计算出一个合适的缩放比例，避免不必要的大图载入。

- 解码格式

选择 ALPHA_8/ARGB_4444/ARGB_8888/RBG_565，存在很大差异。

| 模式      | 描述                                               | 占用字节 |
| --------- | -------------------------------------------------- | -------- |
| ALPHA_8   | Alpha 由 8 位组成                                  | 1B       |
| ARGB_4444 | 4 个 4 位组成 16 位，每个色彩元素站 4 位           | 2B       |
| ARGB_8888 | 4 个 8 为组成 32 位，每个色彩元素站 8 位（默认）   | 4B       |
| RGB_565   | R 为 5 位，G 为 6 位，B 为 5 位共 16 位，没有Alpha | 2B       |

#### 使用更小的图片

在设计给到资源图片的时候，我们需要特别留意这张图片是否存在可以压缩的空间，是否可以使用一张更小的图片。

尽量使用更小的图片不仅仅可以减少内存的使用，还可以避免出现大量的 InflationException。假设有一张很大的图片被 XML 文件直接引用，很有可能在初始化视图的时候就会因为内存不足而发生 InflationException，这个问题的根本原因其实是发生了 OOM。

- JPG vs PNG vs WebP

不了解这三种图片格式的建议看下 [JPG 和 PNG 有什么区别？](https://www.zhihu.com/question/29758228)、[WebP 原理和 Android 支持现状介绍](https://zhuanlan.zhihu.com/p/23648251) 这两篇文章。

- 图片压缩

图片压缩相关知识推荐看下腾讯音乐技术团队的 [Android 中图片压缩分析（上）](https://mp.weixin.qq.com/s/QZ-XTsO7WnNvpnbr3DWQmg)、 [Android 中图片压缩分析（下）](https://mp.weixin.qq.com/s/H9Tz1n4O2-Aawgu7p-XL5w) 两篇文章。

了解了图片压缩的相关知识，我们可以自己写算法来实现图片压缩，也可以使用优秀的开源库，比如：[鲁班](https://github.com/Curzibn/Luban)。

### 内存对象的重复利用

除了减小对象对内存的占用，合理的复用内存对象也是很好避免内存溢出的方式。

大多数对象的复用，最终实施的方案都是利用对象池技术，要么是在编写代码的时候显式的在程序里面去创建对象池，然后处理好复用的实现逻辑，要么就是利用系统框架既有的某些复用特性达到减少对象的重复创建，从而减少内存的分配与回收。

#### LruCache

在 Android 中最常用的一个缓存算法是 LRU（Least Recently Use），就是当超出缓存容量的时候，就优先淘汰链表中最近最少使用的那个数据。

```java
LruCache bitmapCache = new LruCache<String, Bitmap>();
// 根据内存空间设置缓存大小
ActivityManager am = (ActivityManager)getSystemService(Context.ACTIVITY_SERVICE);
int availMemInBytes = am.getMemoryClass() * 1024 *1024;
LruCache bitmapCache = new LruCache<String, Bitmap>(availMemInBytes/8);
```

使用 LruCache 可以缓存 Bitmap 对象，相同LruCache 只是对内存中对象有效，如果我们想把图片、视频等文件缓存在磁盘上可以使用 JakeWharton 大神开源的 [DiskLruCache](https://github.com/JakeWharton/DiskLruCache)。

#### 使用 Glide

Glide 是一个快速高效的 Android 图片加载库，注重于平滑的滚动。Glide 提供了易用的 API，高性能、可扩展的图片解码管道（decode pipeline），以及自动的资源池技术。

Glide 也是 Google 推荐过的开源项目，详见：[Glide](https://github.com/bumptech/glide)。

#### 复用系统自带的资源

Android 系统本身内置了很多的资源（例如：字符串、颜色、图片、动画、样式以、简单布局等等），这些资源都可以在应用程序中直接引用。

这样做不仅仅可以减少应用程序的自身负重，减小 APK 的大小，另外还可以一定程度上减少内存的开销，复用性更好。但是也有必要留意 Android 系统的版本差异性，对那些不同系统版本上表现存在很大差异，不符合需求的情况，还是需要应用程序自身内置进去。

#### 复用 ConvertView

在 ListView、GridView 等出现大量重复子组件的视图里面对 ConvertView 的复用。

### onLowMemory()

OnLowMemory 是 Android 提供的API，在系统内存不足，所有后台程序（优先级为 Background 的进程，不是指后台运行的进程）都被杀死时，系统会调用 OnLowMemory。

系统提供的回调有：Application、Activity、Fragementice、Service、ContentProvider。

### onTrimMemory()

OnTrimMemory 是 Android 4.0 之后提供的 API，系统会根据不同的内存状态来回调。

系统提供的回调有：Application、Activity、Fragementice、Service、ContentProvider。

OnTrimMemory的参数是一个 int 数值，代表不同的内存状态。

当 App 在前台运行时，该函数的 level （从低到高）有:

- TRIM_MEMORY_RUNNING_MODERATE

系统开始运行在低内存状态下 App 正在运行，不会被杀掉。

- TRIM_MEMORY_RUNNING_LOW

系统运行在更加低内存状态下，App 在运行，不会被杀掉 App 可以清理一些资源来保证系统的流畅。

- TRIM_MEMORY_RUNNING_CRITICAL

系统运行在相当低内存状态下，App 在运行，且系统不认为可以杀掉此 App，系统要开始杀掉后台进程。此时，App 应该去释放一些不重要的资源。

当 App 在后台运行时，level 状态有:

- TRIM_MEMORY_UI_HIDDEN：

App 的 UI 不可见，App 可以清理 UI 使用的较大的资源。

当 App 进入后台 LRU List 时：

- TRIM_MEMORY_BACKGROUND

系统运行在低内存下，App 进程在 LRU List 开始处附近，尽管 App 没有被杀掉的风险，但是系统也许已经正在杀后台进程。App 应该清理一些容易恢复的资源。

- TRIM_MEMORY_MODERATE

系统运行在低内存下，App 进程在 LRU List 中间处附件，App 此时有被杀的可能。

- TRIM_MEMORY_COMPLETE

系统运行在低内存下，App 是首先被杀的选择之一，App 应该及时清理掉恢复 App 到前台状态，不重要的所有资源。

另外，一个 App 占用内存越多，则系统清理后台 LRU List 时，越可能优先被清理。所以，内存使用我们要谨慎使用。

### 避免在 onDraw 方法里面执行对象的创建

类似 onDraw 等频繁调用的方法，一定需要注意避免在这里做创建对象的操作，因为他会迅速增加内存的使用，而且很容易引起频繁的 GC，甚至是内存抖动。

### 序列化

在 Android 中实现序列化一般用 Serializable 和 Parcelable 两种方式。

两者最大的区别在于 存储媒介的不同，Serializable 使用 I/O 读写存储在硬盘上，而 Parcelable 是直接 在内存中读写。很明显，内存的读写速度通常大于 IO 读写，所以在 Android 中传递数据优先选择 Parcelable。
Serializable 会使用反射，序列化和反序列化过程需要大量 I/O 操作， Parcelable 自已实现封送和解封（marshalled &unmarshalled）操作不需要用反射，数据也存放在 Native 内存中，效率要快很多。

Parcelable 的性能比 Serializable 好，在内存开销方面较小，所以在内存间数据传输时推荐使用 Parcelable（如 Activity 间传输数据）。

而 Serializable 可将数据持久化方便保存，所以在需要保存或网络传输数据时选择 Serializable，因为 Android 不同版本 Parcelable 可能不同，所以不推荐使用 Parcelable进行数据持久化.

### StringBuilder

在有些时候，代码中会需要使用到大量的字符串拼接的操作，这种时候有必要考虑使用 StringBuilder 来替代频繁的 `+`。

## 避免内存泄漏

内存泄漏（Memory Leak）指程序运行过程中分配内存给临时变量，用完之后却没有被 GC 回收，始终占用着内存，既不能被使用也不能分配给其他程序，于是就发生了内存泄漏。

内存泄露有时不严重且不易察觉，这样开发者就不知道存在内存泄露，但有时也会很严重，甚至会提示你 OOM。

### Context 的泄露

在 Android 开发中，最容易引发的内存泄漏问题的是 Context。比如 Activity 的 Context，就包含大量的内存引用，一旦泄漏了 Context，也意味泄漏它指向的所有对象。

造成 Activity 泄漏的常见原因：

#### 静态引用 Activity

在类中定义了静态 Activity 变量，把当前运行的 Activity 实例赋值于这个静态变量。如果这个静态变量在 Activity 生命周期结束后没有清空，就导致内存泄漏。

因为 static 变量是贯穿这个应用的生命周期的，所以被泄漏的 Activity 就会一直存在于应用的进程中，不会被垃圾回收器回收。

```java
static Activity activity; // 这种代码要避免
```

#### 单例中保存 Activity

在单例模式中，如果 Activity 经常被用到，那么在内存中保存一个 Activity 实例是很实用的。

但是由于单例的生命周期是应用程序的生命周期，这样会强制延长 Activity 的生命周期，这是相当危险而且不必要的，无论如何都不能在单例子中保存类似 Activity 的对象。

```java
public class Singleton {
  private static Singleton instance;
  private Context mContext;
  private Singleton(Context context){
    this.mContext = context;
  }

  public static Singleton getInstance(Context context){
    if (instance == null){
      synchronized (Singleton.class){
        if (instance == null){
          instance = new Singleton(context);
        }
      }
    }
    return instance;
  }
}
```

在调用 Singleton 的 getInstance() 方法时传入了 Activity。那么当 instance 没有释放时，这个 Activity 会一直存在，因此造成内存泄露。

#### 考虑使用 Application Context 而不是 Activity Context

对于大部分非必须使用 Activity Context 的情况（Dialog 的 Context 就必须是 Activity Context），我们都可以考虑使用 Application Context 而不是 Activity 的 Context，这样可以避免不经意的 Activity 泄露。

#### Inner Classes

内部类的优势可以提高可读性和封装性，而且可以访问外部类，不幸的是，导致内存泄漏的原因，就是内部类持有外部类实例的强引用（例如在内部类中持有 Activity 对象）。

解决方法：

- 将内部类变成静态内部类；
- 如果有强引用 Activity 中的属性，则将该属性的引用方式改为弱引用；
- 在业务允许的情况下，当 Activity 执行 onDestory 时，结束这些耗时任务。

#### 避免使用异步回调

异步回调被执行的时间不确定，很有可能发生在 Activity 已经被销毁之后，这不仅仅很容易引起 crash，还很容易发生内存泄露。

### 注意临时 Bitmap 对象的及时回收

虽然在大多数情况下，我们会对 Bitmap 增加缓存机制，但是在某些时候，部分 Bitmap 是需要及时回收的。

> 例如：临时创建的某个相对比较大的 Bitmap 对象，在经过变换得到新的 Bitmap 对象之后，应该尽快回收原始的 Bitmap，这样能够更快释放原始 Bitmap 所占用的空间。

需要特别留意的是 Bitmap 类里面提供的 createBitmap() 方法，这个函数返回的 Bitmap 有可能和 source bitmap 是同一个，在回收的时候，需要特别检查 source bitmap 与 return bitmap 的引用是否相同，只有在不等的情况下，才能够执行 source bitmap 的 recycle 方法。

### 注意监听器的注销

在 Android 程序里面存在很多需要 register 与 unregister 的监听器，我们需要确保在合适的时候及时 unregister 那些监听器。自己手动 add 的 listener，需要记得及时 remove 这个 listener。

### 注意 Cursor 对象是否及时关闭

在程序中我们经常会进行查询数据库的操作，但时常会存在不小心使用 Cursor 之后没有及时关闭的情况。这些 Cursor 的泄露，反复多次出现的话会对内存管理产生很大的负面影响，我们需要谨记对 Cursor 对象的及时关闭。

### 注意缓存容器中的对象泄漏

有时候，我们为了提高对象的复用性把某些对象放到缓存容器中，可是如果这些对象没有及时从容器中清除，也是有可能导致内存泄漏的。

> 例如：针对 2.3 的系统，如果把 drawable 添加到缓存容器，因为 drawable 与 View 的强应用，很容易导致 activity 发生泄漏。而从 4.0 开始，就不存在这个问题。解决这个问题，需要对 2.3 系统上的缓存 drawable 做特殊封装，处理引用解绑的问题，避免泄漏的情况。

### 注意 WebView 的泄漏

Android 中的 WebView 存在很大的兼容性问题，不仅仅是 Android 系统版本的不同对 WebView 产生很大的差异，另外不同的厂商出货的 ROM 里面 WebView 也存在着很大的差异。更严重的是标准的 WebView 存在内存泄露的问题，看这里 [WebView causes memory leak - leaks the parent Activity](https://code.google.com/p/android/issues/detail?id=5067)。

所以通常根治这个问题的办法是为 WebView 开启另外一个进程，通过 AIDL 与主进程进行通信， WebView 所在的进程可以根据业务的需要选择合适的时机进行销毁，从而达到内存的完整释放。

## Lint Tool

Lint 是Android Studio 提供的代码扫描分析工具，它可以帮助我们发现代码结构/质量问题，同时提供一些解决方案，而且这个过程不需要我们手写测试用例。

Lint 发现的每个问题都有描述信息和等级（和测试发现 bug 很相似），我们可以很方便地定位问题，同时按照严重程度进行解决。

点击 **Analyze > Inspect Code** 可打开 Lint 工具。

![Lint](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/03_memory/01.png)

详细使用介绍可查看 [Android 开发文档 - 使用 Lint 改进您的代码](https://developer.android.com/studio/write/lint?hl=zh-cn)、[Android 性能优化：使用 Lint 优化代码、去除多余资源](https://blog.csdn.net/u011240877/article/details/54141714) 这两篇文章，使用比较简单，网上介绍资源很多，这里不再详细介绍。

## adb dumpsys

dumpsys 是 Android 系统提供的一个工具，可以查看系统服务的相关信息，dumpsys 通过 adb 命令来调用。

查看指定进程包名的内存使用情况：

> $ adb shell dumpsys meminfo <包名>

输出内容如下：

![adb dumpsys](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/03_memory/02.png)

当然 dumpsys 的功能还有很多，可以查看 [Android  开发文档 - dumpsys](https://developer.android.com/studio/command-line/dumpsys)、[dumpsys 命令用法](http://gityuan.com/2016/05/14/dumpsys-command/) 这两篇文章了解更多用法。

## Heap Viewer

Heap Viewer 是 DDMS 中的一个工具，实时查看 App 分配的内存大小和空闲内存大小，可帮助查找内存泄露。Heap Viewer 支持 5.0 及以上的系统，现在已经弃用，官方推荐使用 Memory Profiler 来查看 App 内存分配情况。

## Memory Profiler

Memory Profiler 是 [Android Profiler](https://developer.android.com/studio/preview/features/android-profiler.html) 中的一个组件，可帮助开发者识别导致应用卡顿、OOM 和内存泄露。 它显示一个应用内存使用量的实时图表，可以捕获堆转储、强制执行垃圾回收以及跟踪内存分配。

可以在 **View > Tool Windows > Android Profiler** 中打开 Memory Profiler 界面。

![Memory Profiler](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/03_memory/03.png)

Memory Profile 的具体使用可查看 [Android 开发文档 - 使用 Memory Profiler 查看 Java 堆和内存分配](https://developer.android.com/studio/profile/memory-profiler)、[Android Studio 3.0 利用 Android Profiler 测量应用性能](https://juejin.im/post/5b7cbf6f518825430810bcc6#heading-7) 这两篇文章。

## MAT

MAT（Memory Analyzer Tool），一个基于 Eclipse 的内存分析工具，是一个快速、功能丰富的 Java Heap 分析工具，它可以帮助我们查找内存泄漏和减少内存消耗。

使用内存分析工具从众多的对象中进行分析，快速的计算出在内存中对象的占用大小，看看是谁阻止了垃圾收集器的回收工作，并可以通过报表直观的查看到可能造成这种结果的对象。

![Memory Analyzer](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/03_memory/04.png)

当然 MAT 也有独立的不依赖 Eclipse 的版本，只不过这个版本在调试 Android 内存的时候，需要将 Android Studio 生成的文件进行转换，才可以在独立版本的 MAT 上打开。.

一般情况下使用 Memory Profiler 就可以检测出内存泄露的大致位置，使用 MAT 可以更详细的分析内存的具体情况。

MAT 下载 [点击这里](https://www.eclipse.org/mat/)，使用教程可查看 [Eclipse Wiki - MemoryAnalyzer](https://wiki.eclipse.org/MemoryAnalyzer)，也可以参考 [Android 内存优化之一：MAT 使用入门](https://www.androidperformance.com/2015/04/11/AndroidMemory-Usage-Of-MAT/)、[Android内存优化之二：MAT使用进阶](https://www.androidperformance.com/2015/04/11/AndroidMemory-Usage-Of-MAT-Pro/) 这两篇文章。

## LeakCanary

[LeakCanary](https://github.com/square/leakcanary) 是一个用于检测 Android 内存泄漏的开源库，上面介绍的 Memory Profiler、MAT 使用起来比较复杂，LeakCanary 堪称傻瓜式的内存泄露检测工具。

使用方式详见 [https://square.github.io/leakcanary](https://square.github.io/leakcanary/)，也可参考 [LeakCanary 中文使用说明](https://www.liaohuqiu.net/cn/posts/leak-canary-read-me/) 这篇文章。

## 参考资料

- [YouTube - 性能优化典范 第一季](https://www.youtube.com/watch?v=R5ON3iwx78M&list=PL8ktV16dN_6vKDQB-D7fAqA6zRFQOoKtI)
- [YouTube - 性能优化典范 第三季](https://www.youtube.com/watch?v=ORgucLTtTDI&list=PLKbs_pHKyapmK84ah_AattCdso6gQyujx)
- [YouTube - 性能优化典范 第四季](https://www.youtube.com/watch?v=7lxVqqWwTb0&list=PL8cvstvtecscVxHNy2evUa9M5zOsI3unW)
- [Android 开发文档 - 管理你的应用内存](https://developer.android.com/topic/performance/memory)
- [谈谈 Android 的内存管理机制](https://zhuanlan.zhihu.com/p/27176914)
- [Android 操作系统的内存回收机制](https://www.ibm.com/developerworks/cn/opensource/os-cn-android-mmry-rcycl/index.html)
- [JPG 和 PNG 有什么区别？](https://www.zhihu.com/question/29758228)
- [WebP 原理和 Android 支持现状介绍](https://zhuanlan.zhihu.com/p/23648251)
- [Android 中图片压缩分析（上）](https://mp.weixin.qq.com/s/QZ-XTsO7WnNvpnbr3DWQmg)
- [Android 中图片压缩分析（下）](https://mp.weixin.qq.com/s/H9Tz1n4O2-Aawgu7p-XL5w)
- [Java 枚举类型的实现原理](https://blog.csdn.net/mhmyqn/article/details/48087247)
- [What is an efficient way to implement a singleton pattern in Java? ](https://stackoverflow.com/questions/70689/what-is-an-efficient-way-to-implement-a-singleton-pattern-in-java)
- [胡凯 - Android 内存优化之 OOM](http://hukai.me/android-performance-oom/)
- [Android 内存泄漏定位、分析、解决全方案](http://tryenough.com/android-momeryleak)
- [Android 开发文档 - 使用 Lint 改进您的代码](https://developer.android.com/studio/write/lint?hl=zh-cn)
- [Android  开发文档 - dumpsys](https://developer.android.com/studio/command-line/dumpsys)
- [dumpsys 命令用法](http://gityuan.com/2016/05/14/dumpsys-command/)
- [Android 开发文档 - 使用 Memory Profiler 查看 Java 堆和内存分配](https://developer.android.com/studio/profile/memory-profiler)
- [Android Studio 3.0 利用 Android Profiler 测量应用性能](https://juejin.im/post/5b7cbf6f518825430810bcc6#heading-7)
- [LeakCanary 中文使用说明](https://www.liaohuqiu.net/cn/posts/leak-canary-read-me/)

