# Android-性能优化-UI优化

## 概述

Android 应用的卡顿，丢帧等，这些影响用户体验的因素绝大部分都与 16ms 这个值有关。 下面我们来讨论下 UI 渲染方面影响应用流畅性的因素。

## 16ms

- 12 fps（帧/秒）：由于人类眼睛的特殊生理结构，如果所看画面之帧率高于每秒约 10-12 fps 的时候，就会认为是连贯的。 早期的无声电影的帧率介于 16-24 fps 之间，虽然帧率足以让人感觉到运动，但往往被认为是在快放幻灯片。 在1920年代中后期，无声电影的帧率提高到 20-26 fps 之间。
- 24 fps：1926 年有声电影推出，人耳对音频的变化更敏感，反而削弱了人对电影帧率的关注。因为许多无声电影使用 20-26 fps 播放，所以选择了中间值 24 fps 作为有声电影的帧率。 之后 24 fps 成为35mm有声电影的标准。
- 30 fps：早期的高动态电子游戏，帧率少于每秒 30 fps 的话就会显得不连贯。这是因为没有动态模糊使流畅度降低。 （注:如果需要了解动态模糊技术相关知识，可以查阅 [这里](https://www.zhihu.com/question/21081976)）
- 60 fps：在实际体验中，60 fps 相对于30 fps 有着更好的体验。
- 85 fps：一般而言，大脑处理视频的极限。

所以，总体而言，帧率越高体验越好。 一般的电影拍摄及播放帧率均为每秒 24 帧，但是据称《霍比特人：意外旅程》是第一部以每秒 48 帧拍摄及播放的电影，观众认为其逼真度得到了显著的提示。

目前，大多数显示器根据其设定按 30Hz、 60Hz、 120Hz 或者 144Hz 的频率进行刷新。 而其中最常见的刷新频率是 60Hz。 这样做是为了继承以前电视机刷新频率为 60Hz 的设定。 而 60Hz 是美国交流电的频率，电视机如果匹配交流电的刷新频率就可以有效的预防屏幕中出现滚动条，即互调失真。

正如上面所述目前大多数显示器的刷新率是 60Hz，Android 设备的刷新率也是 60Hz。只有当画面达到 60fps 时 App 应用才不会让用户感觉到卡顿。那么 60fps 也就意味着 1000ms/60Hz = 16ms。也就是说 16ms 渲染一次画面才不会卡顿。

## V-Sync（垂直同步）

玩游戏的同学，尤其是大型 FPS 游戏应该都见过“垂直同步”这个选项。因为 GPU 的生成图像的频率与显示器的刷新频率是相互独立的，所以就涉及到了一个配合的问题。

最理想的情况是两者之间的频率是相同且协同进行工作的，在这样的理想条件下，达到了最优解。但实际中 GPU 的生成图像的频率是变化的，如果没有有效的技术手段进行保证，两者之间很容易出现这样的情况：当 GPU 还在渲染下一帧图像时，显示器却已经开始进行绘制，这样就会导致屏幕撕裂（Tear）。这会使得屏幕的一部分显示的是前一帧的内容，而另一部分却在显示下一帧的内容。如下图所示：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tearing_simulated.jpg" alt="撕裂的图像"/>


屏幕撕裂（Tear）的问题，早在 PC 游戏时代就被发现， 并不停的在尝试进行解决。 其中最知名可能也是最古老的解决方案就是 V-Sync 技术。

V-Sync 的原理简单而直观：产生屏幕撕裂的原因是 GPU 在屏幕刷新时进行了渲染，而 V-Sync 通过同步渲染/刷新时间的方式来解决这个问题。显示器的刷新频率为 60Hz，若此时开启 V-Sync，将控制 GPU 渲染速度在 60Hz 以内以匹配显示器刷新频率。这也意味着，在 V-Sync 的限制下，GPU 显示性能的极限就限制为 60Hz 以内。这样就能很好的避免图像撕裂的问题。

## Android 中的 GPU 渲染机制

大多数的 App 界面卡顿（Jank）现象都与 GPU 渲染有关，尤其是存在多层次布局嵌套，存在不必要的绘制，或者在 onDraw() 方法中执行了耗时操作，动画执行次数过多的情况下很容易出现界面卡顿。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_draw_per_16ms.png" alt="16ms"/>

如上图所示，Android 系统每隔 16ms 就会发出一个 V-Sync 信号，触发对 UI 的渲染，如果每次渲染都能成功，这样就能保证画面的流畅帧率 60fps。 如果出现 16ms 内无法渲染的情况就无法响应 V-Sync 信号，就会出现丢帧现象。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_vsync_over_draw.png" alt="vsync over draw"/>


如上图所示：如果某个操作耗时 24ms，系统就无法正常响应当前 V-Sync 信号，只能等待下次响应 V-Sync 信号，当前 V-Sync 信号就会丢失，也就是所谓丢帧。

## Overdraw 过度绘制

### 什么是过度绘制？

过度绘制就是屏幕上的某个像素在同一帧的时间内被绘制了多次。 在多层次的UI结构里面，如果不可见的 UI 也在做绘制的操作，这就会导致某些像素区域被绘制了多次。 这就浪费大量的 CPU 以及 GPU 资源。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_overdraw_1.jpg" alt="overdraw options draw"/>

### 如何发现过度绘制？

我们可以通过手机设置里面的 **开发者选项** ，打开 **显示过渡绘制区域（Show GPU Overdraw** 的选项，可以观察 UI 上的 Overdraw 情况。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_overdraw_options_view.png" alt="overdraw options draw"/>

蓝色，淡绿，淡红，深红代表了 4 种不同程度的 Overdraw 情况，我们的目标就是尽量减少红色 Overdraw，看到更多的蓝色区域。

- 蓝色： 意味着overdraw 1倍。像素绘制了两次。大片的蓝色还是可以接受的（若整个窗口是蓝色的，可以摆脱一层）。 
- 绿色： 意味着overdraw 2倍。像素绘制了三次。中等大小的绿色区域是可以接受的但你应该尝试优化、减少它们。 
- 淡红： 意味着overdraw 3倍。像素绘制了四次，小范围可以接受。 
- 深红： 意味着overdraw 4倍。像素绘制了五次或者更多。这是错误的，要修复它们。 

Overdraw 有时候是因为你的UI布局存在大量重叠的部分，还有的时候是因为非必须的重叠背景。

> 例如：某个 Activity 有一个背景，然后里面的 Layout 又有自己的背景，同时子 View 又分别有自己的背景。仅仅是通过移除非必须的背景图片，这就能够减少大量的红色 Overdraw 区域，增加蓝色区域的占比。这一措施能够显著提升程序性能。

## 使用 Hierarchy Viewer 分析 UI 性能

首先打开 Hierarchy Viewer，依次找到：Android Studio -> Tools -> Android -> Android Device Monitor

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_android_device_monitor.jpg" alt="Android Device Monitor"/>


启动 Android Device Monitor 成功之后，在新的窗口中点击切换视图图标，选择 Hierarchy View，如下图：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_hierarchy_view.jpg" alt="hierarchy view"/>

Hierarchy View 运行界面如下：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_hierarchy_view_2.jpg" alt="hierarchy view"/>

- 一个 Activity 的 View 树，通过这个树可以分析出 View 嵌套的冗余层级；
- 左下角可以输入 View 的 id 直接自动跳转到中间显示；
- Save as PNG 用来把左侧树保存为一张图片；
- Capture Layers 用来保存 psd 的 PhotoShop 分层素材；
- 右侧剧中显示选中 View 的当前属性状态；
- 右下角显示当前 View 在 Activity 中的位置等；
- Load View Hierarchy 用来手动刷新变化（不会自动刷新的）。

当我们选择一个 View 后会如下图所示：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_hierarchy_view_3.jpg" alt="hierarchy view"/>

类似上图可以很方便的查看到当前 View 的许多信息，上图最底那三个彩色原点代表了当前 View 的性能指标，从左到右依次代表测量、布局、绘制的渲染时间，红色和黄色的点代表速度渲染较慢的 View（当然了，有些时候较慢不代表有问题，比如 ViewGroup 子节点越多、结构越复杂，性能就越差）。

当然了，在自定义 View 的性能调试时，HierarchyViewer 上面的 invalidate Layout 和 requestLayout 按钮的功能更加强大，它可以帮助我们 debug 自定义 View 执行 invalidate() 和 requestLayout() 过程，我们只需要在代码的相关地方打上断点就行了，接下来通过它观察绘制即可。

可以发现，有了 Hierarchy View 调试工具，我们的 UI 性能分析变得十分容易，这个工具也是我们开发中调试 UI 的利器，在平时写代码时会时常伴随我们左右。

## 使用 GPU 呈现模式考核 UI 性能

在 Android 手机上开启这个功能：打开 **开发者选项** -> **GPU 呈现模式分析（Peofile GPU Rendering tool** -> **在屏幕上显示为条形图（On screen as bars**

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_gpu_16ms.jpg" alt="gpu 16ms"/>

在 Android 系统中是以 60fps 为满帧，绿色横线为 16ms 分界线，低于绿线即为流畅。

屏幕下方的柱状图每一根代表一帧，其高度表示“渲染这一帧耗时”，随着手机屏幕界面的变化，柱状图会持续刷新每帧用时的具体情况（通过高度表示）。那么，当柱状图高于绿线，是不是就说明我卡了呢？其实这不完全正确，这里就要开始分析组成每一根柱状图不同颜色所代表的含义了。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_gpu_16ms2.jpg" alt="gpu 16ms"/>

- **红色**，代表了“执行时间”，它指的是 Android 渲染引擎执行盒子中这些绘制命令的时间，假如当前界面的视图越多，那么红色便会“跳”得越高。实际使用中，比如我们平时刷淘宝 App 时遇到出现多张缩略图需要加载时，那么红色会突然跳很高，但是此时你的页面滑动其实是流畅的，虽然等了零点几秒图片才加载出来，但其实这可能并不意味着你卡住了。

- **黄色**，通常较短，它代表着 CPU 通知 GPU “你已经完成视图渲染了”，不过在这里 CPU 会等待 GPU 的回话，当 GPU 说“好的知道了”，才算完事儿。 假如橙色部分很高的话，说明当前 GPU 过于忙碌，有很多命令需要去处理，比如 Android 淘宝客户端，红色黄色通常会很高。

- **蓝色**，假如想通过玄学曲线来判断流畅度的话，其实蓝色的参考意义是较大的。蓝色代表了视图绘制所花费的时间，表示视图在界面发生变化（更新）的用时情况。当它越短时，即便是体验上更接近“丝滑”，当他越长时，说明当前视图较复杂或者无效需要重绘，即我们通常说的“卡了”。

理解了玄学曲线不同颜色代表的意义，看懂玄学曲线就不难了。 一般情况下，当蓝色低于绿线时都不会出现卡顿，但是想要追求真正的丝般顺滑那当然还是三色全部处于绿线以下最为理想。

## 使用 TraceView 从代码层面分析性能问题

生成 trace 文件有三种方法：

1. 使用代码
2. 使用 Android Studio
3. 使用 DDMS

## 1. 使用代码生成 trace 文件

```Java
Debug.startMethodTracing("test_trace");//开始 trace，保存文件到 "/sdcard/test_trace.trace"
// ...
Debug.stopMethodTracing();//结束
```

代码很简单，当你调用开始代码的时候，系统会生产 trace 文件，并且产生追踪数据，当你调用结束代码时，会将追踪数据写入到 trace 文件中。

下一步使用 adb 命令将 trace 文件导出到电脑：

```Java
adb pull /sdcard/test_trace.trace /tmp
```
使用代码生成 trace 方式的好处是容易控制追踪的开始和结束，缺点就是步骤稍微多了一点。

## 2. 使用 Android Studio 生成 trace 文件

Android Studio 内置的 Android Monitor 可以很方便的生成 trace 文件到电脑。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing.jpg" alt="android studio tracing"/>

在 CPU 监控的那栏会有一个闹钟似的的按钮，未启动应用时是灰色；
启动应用后，这个按钮会变亮，点击后开始追踪，相当于代码调用 startMethodTracing；

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing2.jpg" alt="android studio tracing"/>

当要结束追踪时再次点击这个按钮，就会生成 trace 文件了（文件可在 Caputures 中找到）。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing4.jpg" alt="android studio tracing"/>

生成 trace 后 Android Studio 自动加载的 traceview 图形如下：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing3.jpg" alt="android studio tracing"/>

从这个图可以大概了解一些方法的执行时间、次数以及调用关系，也可以搜索过滤特定的内容。

左上角可以切换不同的线程，这其实也是直接用 Android Studio 查看 trace 文件的缺点：无法直观地对比不同线程的执行时间。

鼠标悬浮到黄色的矩形上，会显示对应方法的开始、结束时间，以及自己占用和调用其他方法占用的时间比例：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing5.jpg" alt="android studio tracing"/>

## 3. 使用 DDMS 生成 trace 文件

DDMS 即 Dalvik Debug Monitor Server ，是 Android 调试监控工具，它为我们提供了截图，查看 log，查看视图层级，查看内存使用等功能，可以说是如今 Android Studio 中内置的 Android Monitor 的前身。

打开 Android Device Monitor，找到 Device 选中需要测试的 app，点击 Start Method Profiling 后开始追踪，相当于代码调用 startMethodTracing；

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing6.jpg" alt="android studio tracing"/>

当要结束追踪时再次点击这个按钮，就会生成 trace 文件；

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing7.jpg" alt="android studio tracing"/>

停止追踪后，DDMS 会启动 TraceView 加载 trace 文件：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing8.jpg" alt="android studio tracing"/>

上图介绍了 TraceView 的大致内容

面板列名含义如下:

| 名称				| 说明           															|
| :-----------		| :---------------------------------------------------------------------	|
| Incl Cpu Time 	| CPU 执行该方法该方法及其子方法所花费的时间										|
| Incl Cpu Time % 	| CPU 执行该方法该方法及其子方法所花费占 CPU 总执行时间的百分比					|
| Excl Cpu Time 	| CPU 执行该方法所花费的时间													|
| Excl Cpu Time % 	| CPU 执行该方法所花费的时间占Cpu总时间的百分比									|
| Incl Real Time 	| 该方法及其子方法执行所花费的实际时间，从执行该方法到结束一共花了多少时间			|
| Incl Real Time % 	| 上述时间占总的运行时间的百分比												|
| Excl Real Time 	| 该方法自身的实际允许时间														|
| Excl Real Time % 	| 上述时间占总的允许时间的百分比												|
| Calls+Recur 		| 调用次数+递归次数，只在方法中显示，在子展开后的父类和子类方法这一栏被下面的数据代替	|
| Calls/Total 		| 调用次数和总次数的占比														|
| Cpu Time/Call 	| CPU 执行时间和调用次数的百分比，代表该函数消耗 CPU 的平均时间					|
| Real Time/Call 	| 实际时间于调用次数的百分比，该表该函数平均执行时间								|



点击下面的任意一个方法，可以看到它的详细信息：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_tracing9.jpg" alt="android studio tracing"/>

- Parents：选中方法的调用处
- Children：选中方法调用的方法

## 使用 Systrace 检测 App 的性能

经过在上面的这些优化之后，如果你的界面还有卡顿，我们还有办法。 Systrace 工具也可以测量你 App 的性能。 甚至可以帮助你定位问题产生的位置。 这个工具是作为“Project Butter”一部分同 Jelly Bean 一同发布的，它能够从内核级检测你设备的运行状态。 Systrace 可配置的参数很多。我们这里重点关注 UI 是怎么渲染的，用 Systrace 检测卡顿问题。

Systrace 和之前的工具不同的是，它记录的是整个 Android 系统的状态，并不是针对某一个 App 的。所以最好是用运行 App 比较少的设备来做检测，这样就不会受到其他 App 的干扰了。 

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_systrace.jpg" alt="android studio systrace"/>

点击开始按钮会弹出窗口选择所需要的参数，这里主要研究屏幕的交互数据，主要收集 CPU，graphics 和 view 数据。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_systrace2.jpg" alt="android studio systrace"/>

trace 数据记录在一个 html 文件里，可以用浏览器打开。 点击OK之后，Systrace 会马上开始采集设备上的数据（最好马上开始操作）。 因为采集的数据非常之多，所以最好一次只针对一个问题。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_systrace3.jpg" alt="android studio systrace"/>

鼠标可以控制滑动，WASD 可以用来 zoom in/out（W，S）和左右滑动（A，D）。在刚跑的 trace 数据最上面，能看到 CPU 的详细数据， CPU 数据的下面是几个可折叠的区域，分别表示不同的活跃进程。每一个色条表示系统的一个行为，色条的长度表示该行为的耗时（放大可以看到更多细节）。

| 快捷键	| 作用								|
| :----	| :-----------------------			|
| w		| 放大								|
| s		| 缩小								|
| a		| 左移								|
| d		| 右移								|
| f		| 返回选中区域，且放大选中区域			|
| m		| 标记当前选定区域					|
| v		| 高亮 VSync							|
| g		| 切换是否显示 60hz 的网格线			|
| 0(零)	| 恢复trace到初始态					|
| h		| 切换是否显示详情					|
| /		| 搜索关键字							|
| enter | 显示搜索结果，可通过← →定位搜索结果	|
| `		| 显示/隐藏脚本控制台					|
| ?		| 显示帮助功能						|


Alerts 一栏标记了以下性能有问题的点，你可以点击该点查看详细信息,右边侧边栏还有一个 Alerts 框，点击可以查看每个类型的 Alerts 的数量。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_systrace5.jpg" alt="android studio systrace"/>

在每个包下都有 Frame 一栏，该栏中都有一个一个的 F 代表每一个 Frame，用颜色来代表性能的好坏，依次为绿-黄-红(性能越来越差),点击某一个 F,会显示该 Frame 绘制过程中的一些 Alerts 信息，如果你想查看Frame的耗时，可以点击某个 F 标志，然后按 m 键:。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_performance/ui_systrace4.jpg" alt="android studio systrace"/>


## 参考资料

[脑洞大开：为啥帧率达到 60 fps 就流畅？](http://www.jianshu.com/p/71cba1711de0)

[Android性能优化之渲染篇](http://hukai.me/android-performance-render/)

[Android性能专项测试-TraceView工具(Device Monitor)](https://www.kancloud.cn/digest/itfootballprefermanc/100911)

[Android性能专项测试-Systrace工具](https://www.kancloud.cn/digest/itfootballprefermanc/100913)

[Analyzing UI Performance with Systrace](https://developer.android.com/studio/profile/systrace.html)




