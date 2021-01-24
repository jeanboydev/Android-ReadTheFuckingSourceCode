# 启动性能优化

提高程序的启动速度意义重大，很显然，启动时间越短，用户才越有耐心等待打开这个 App 进行使用，反之启动时间越长，用户则越有可能来不及等到 App 打开就已经切换到其他 App 了。

程序启动过程中的那些复杂错误的操作很可能导致严重的性能问题。Android 系统会根据用户的操作行为调整程序的显示策略，用来提高程序的显示性能。

> 例如，一旦用户点击桌面图标，Android 系统会立即显示一个启动窗口，这个窗口会一直保持显示直到画面中的元素成功加载并绘制完第一帧。

这种行为常见于程序的冷启动，或者程序的热启动场景（程序从后台被唤起或者从其他 App 界面切换回来）。

那么关键的问题是，用户很可能会因为从启动窗口到显示画面的过程耗时过长而感到厌烦，从而导致用户没有来得及等程序启动完毕就切换到其他 App 了。更严重的是，如果启动时间过长，可能导致程序出现 ANR。我们应该避免出现这两种糟糕的情况。

## 启动方式

Android 应用的启动方式分为三种：冷启动、暖启动、热启动，不同的启动方式决定了应用 UI 对用户可见所需要花费的时间长短。

顾名思义，冷启动消耗的时间最长。基于冷启动方式的优化工作也是最考验产品用户体验的地方。谈及优化之前，下面我们来看看这三种启动方式的应用场景，以及启动过程中系统都做了些什么工作。

### 冷启动

在安卓系统中，系统为每个运行的应用至少分配一个进程 （多进程应用申请多个进程） 。从进程角度上讲，冷启动就是在启动应用前，系统中没有该应用的任何进程信息 (包括 Activity、Service 等) 。

所以，冷启动产生的场景就很容易理解了，比如设备开机后应用的第一次启动，系统杀掉应用进程 （如：系统内存吃紧引发的 kill 和用户主动产生的 kill）后的再次启动等。那么自然这种方式下，应用的启动时间最长，因为相比另外两种启动方式，系统和我们的应用要做的工作最多。

应用发生冷启动时，系统有三件任务要做：

- 开始加载并启动应用；
- 应用启动后，显示一个空白的启动窗口；
- 创建应用进程信息；

系统创建应用进程后，应用就要做下面这些事情：

- 初始化应用中的对象（比如 Application 中的工作）；
- 启动主线程（UI 线程）；
- 创建第一个 Activity；
- 加载内容视图（Inflating）；
- 计算视图在屏幕上的位置排版（Laying out）；
- 绘制视图（draw）。

只有当应用完成第一次绘制，系统当前展示的空白背景才会消失，才会被 Activity 的内容视图替换掉。也就是这个时候，用户才能和我们的应用开始交互。

下图展示了冷启动过程系统和应用的一个工作时间流：

![launch time](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/01.png)

这其中有两个 creation 工作，分别为 Application 和 Activity creation。从图中看出，他们均在 View 绘制展示之前。所以，在应用自定义的 Application 类和 第一个 Activity 类中，onCreate() 方法做的事情越多，冷启动消耗的时间越长。

### 暖启动

当应用中的 Activities 被销毁，但在内存中常驻时，应用的启动方式就会变为暖启动。

相比冷启动，暖启动过程减少了对象初始化、布局加载等工作，启动时间更短。但启动时，系统依然会展示一个空白背景，直到第一个 Activity 的内容呈现为止。

### 热启动

相比暖启动，热启动时应用做的工作更少，启动时间更短。热启动产生的场景很多，常见如：用户使用返回键退出应用，然后马上又重新启动应用。

## 启动时间

从技术角度来说，当用户点击桌面图标开始，系统会立即为这个 App 创建独立的专属进程，然后显示启动窗口，直到 App 在自己的进程里面完成了程序的创建以及主线程完成了 Activity 的初始化显示操作，再然后系统进程就会把启动窗口替换成 App 的显示窗口。

![start process](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/02.png)

上述流程里面的绝大多数步骤都是由系统控制的，一般来说不会出现什么问题，可是对于启动速度，我们能够控制并且需要特别关注的地方主要有三处：

- Application

Application 的 onCreate 流程，对于大型的 App 来说，通常会在这里做大量的通用组件的初始化操作。

- Activity

Activity 的 onCreate 流程，特别是 UI 的布局与渲染操作，如果布局过于复杂很可能导致严重的启动性能问题。

- 闪屏

目前有部分 APP 会提供自定义的启动窗口，这里可以做成品牌宣传界面或者是给用户提供一种程序已经启动的视觉效果。

### Display Time

在正式着手解决问题之前，我们需要掌握一套正确测量评估启动性能的方法。所幸的是，Android 系统有提供一些工具来帮助我们定位问题。

从 Android 4.4（API 19）开始，Logcat 自动帮我们打印出应用的启动时间。这个时间值从应用启动（创建进程）开始计算，到完成视图的第一次绘制（即 Activity 内容对用户可见）为止。如：

![display time](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/03.png)

### 统计启动时间

如果是本地调试的话，统计启动时间还是很简单的，通过命令行方式即可：

> $ adb shell am start -w <包名>/activity

输出的结果类似于：

```text
$ adb shell am start -W com.jeanboy.app.test/com.jeanboy.app.test.HomeActivity
Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.jeanboy.app.test/.HomeActivity }
Status: ok
Activity: com.jeanboy.app.test/.HomeActivity
ThisTime: 496
TotalTime: 496
WaitTime: 503
Complete
```

- WaitTime

返回从 startActivity 到应用第一帧完全显示这段时间。就是总的耗时，包括前一个应用 Activity pause 的时间和新应用启动的时间；

- ThisTime

表示一连串启动 Activity 的最后一个 Activity 的启动耗时；

- TotalTime

表示新应用启动的耗时，包括新进程的启动和 Activity 的启动，但不包括前一个应用 Activity pause 的耗时。

> 开发者一般只要关心 TotalTime 即可，这个时间才是自己应用真正启动的耗时。

当 App 发到线上之后，想要统计 App 在用户手机上的启动速度，就不能通过命令行的方式进行统计了，基本上都是通过打 `Log` 的方式将启动时间发送上来。

## 优化 Application

在 Application 初始化的地方做太多繁重的事情是可能导致严重启动性能问题的元凶之一。Application 里面的初始化操作不结束，其他任意的程序操作都无法进行。

有时候，我们会一股脑的把绝大多数全局组件的初始化操作都放在 Application 的 onCreate 里面，但其实很多组件是需要做区队对待的，有些可以做延迟加载，有些可以放到其他的地方做初始化操作，特别需要留意包含 Disk IO 操作，网络访问等严重耗时的任务，他们会严重阻塞程序的启动。

![application create](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/04.png)

优化这些问题的解决方案是做延迟加载，可以在 Application 里面做延迟加载，也可以把一些初始化的操作延迟到组件真正被调用到的时候再做加载。

## 优化 Activity

提升 Activity 的创建速度是优化 App 启动速度的首要关注目标。从桌面点击 App 图标启动应用开始，程序会显示一个启动窗口等待 Activity 的创建加载完毕再进行显示。

在 Activity 的创建加载过程中，会执行很多的操作，例如设置页面的主题，初始化页面的布局，加载图片，获取网络数据，读写 Preference 等等。

![activity create](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/05.png)

上述操作的任何一个环节出现性能问题都可能导致画面不能及时显示，影响了程序的启动速度。上一个段落我们介绍了使用Method Tracing来发现那些耗时占比相对较多的方法。假设我们发现某个方法执行时间过长，接下去就可以使用Systrace来帮忙定位到底是什么原因导致那个方法执行时间过长。

除了使用工具进行具体定位分析性能问题之外，以下两点经验可以帮助我们对 Activity 启动做性能优化：

- 优化布局耗时

一个布局层级越深，里面包含需要加载的元素越多，就会耗费更多的初始化时间。关于布局性能的优化，这里就不展开描述了！

- 异步延迟加载

一开始只初始化最需要的布局，异步加载图片，非立即需要的组件可以做延迟加载。

## 优化闪屏

启动闪屏不仅仅可以作为品牌宣传页，还能够减轻用户对启动耗时的感知，但是如果使用不恰当，将适得其反。

前面介绍过当点击桌面图标启动 App 的时候，程序会显示一个启动窗口，一直到页面的渲染加载完毕。如果程序的启动速度足够快，我们看的闪屏窗口停留显示的时间则会很短，但是当程序启动速度偏慢的时候，这个启动闪屏可以一定程度上减轻用户等待的焦虑感，避免用户过于轻易的关闭应用。

目前大多数开发者都会通过设置启动窗口主题的方式来替换系统默认的启动窗口，通过这种方式只是使用「障眼法」弱化了用户对启动时间的感知，但本质上并没有对启动速度做什么优化。

也有些 App 通过关闭启动窗口属性 `android:windowDisablePreview` 的方式来直接移除系统默认的启动窗口，但是这样的弊端是用户从点击桌面图标到真的看到实际页面的这段时间当中，画面没有任何变化，这样的用户体验是十分糟糕的！

![launch screen](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/06.png)

对于启动闪屏，正确的使用方法是自定义一张图片，把这张图片通过设置主题的方式显示为启动闪屏，代码执行到主页面的 onCreate 的时候设置为程序正常的主题。

![launch screen optimized](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/06_launch/07.png)

## 参考资料

- [YouTube - Android 性能优化典范第 6 季](https://www.youtube.com/watch?v=AkafJ6NdrhY&list=PLWz5rJ2EKKc-9gqRx5anfX0Ozp-qEI2CF)
- [胡凯 - Android 性能优化典范 - 第 6 季](http://hukai.me/android-performance-patterns-season-6/)
- [Android 开发文档 - App startup time](https://developer.android.com/topic/performance/vitals/launch-time)
- [Android 开发之 App 启动时间统计](https://www.jianshu.com/p/c967653a9468)
