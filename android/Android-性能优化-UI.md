# Android-性能优化-UI优化 #

## 概述 ##

Android 应用的卡顿，丢帧等，这些影响用户体验的因素绝大部分都与 16ms 这个值有关。 下面我们来讨论下 UI 渲染方面影响应用流畅性的因素。

### 16ms

- 12 fps（帧/秒）：由于人类眼睛的特殊生理结构，如果所看画面之帧率高于每秒约 10-12 fps 的时候，就会认为是连贯的。 早期的无声电影的帧率介于 16-24 fps 之间，虽然帧率足以让人感觉到运动，但往往被认为是在快放幻灯片。 在1920年代中后期，无声电影的帧率提高到 20-26 fps 之间。
- 24 fps：1926 年有声电影推出，人耳对音频的变化更敏感，反而削弱了人对电影帧率的关注。因为许多无声电影使用 20-26 fps 播放，所以选择了中间值 24 fps 作为有声电影的帧率。 之后 24 fps 成为35mm有声电影的标准。
- 30 fps：早期的高动态电子游戏，帧率少于每秒 30 fps 的话就会显得不连贯。这是因为没有动态模糊使流畅度降低。 （注:如果需要了解动态模糊技术相关知识，可以查阅[这里](https://www.zhihu.com/question/21081976)）
- 60 fps：在实际体验中，60帧相对于30帧有着更好的体验。
- 85 fps：一般而言，大脑处理视频的极限。

所以，总体而言，帧率越高体验越好。 一般的电影拍摄及播放帧率均为每秒 24 帧，但是据称《霍比特人：意外旅程》是第一部以每秒 48 帧拍摄及播放的电影，观众认为其逼真度得到了显著的提示。

目前，大多数显示器根据其设定按 30Hz、 60Hz、 120Hz 或者 144Hz 的频率进行刷新。 而其中最常见的刷新频率是 60Hz。 这样做是为了继承以前电视机刷新频率为 60Hz 的设定。 而 60Hz 是美国交流电的频率，电视机如果匹配交流电的刷新频率就可以有效的预防屏幕中出现滚动条，即互调失真。

正如上面所述目前大多数显示器的刷新率是 60Hz，Android 设备的刷新率也是 60Hz。只有当画面达到 60fps 时 App 应用才不会让用户感觉到卡顿。那么 60fps 也就意味着 1000ms/60Hz = 16ms。也就是说 16ms 渲染一次画面才不会卡顿。

### V-Sync（垂直同步）

玩游戏的同学，尤其是大型 FPS 游戏应该都见过“垂直同步”这个选项。因为 GPU 的生成图像的频率与显示器的刷新频率是相互独立的，所以就涉及到了一个配合的问题。

最理想的情况是两者之间的频率是相同且协同进行工作的，在这样的理想条件下，达到了最优解。但实际中 GPU 的生成图像的频率是变化的，如果没有有效的技术手段进行保证，两者之间很容易出现这样的情况：当 GPU 还在渲染下一帧图像时，显示器却已经开始进行绘制，这样就会导致屏幕撕裂（Tear）。这会使得屏幕的一部分显示的是前一帧的内容，而另一部分却在显示下一帧的内容。如下图所示：

撕裂的图像：https://zh.wikipedia.org/wiki/File:Tearing_(simulated).jpg

屏幕撕裂（Tear）的问题，早在 PC 游戏时代就被发现， 并不停的在尝试进行解决。 其中最知名可能也是最古老的解决方案就是 V-Sync 技术。

V-Sync 的原理简单而直观：产生屏幕撕裂的原因是 GPU 在屏幕刷新时进行了渲染，而 V-Sync 通过同步渲染/刷新时间的方式来解决这个问题。显示器的刷新频率为 60Hz，若此时开启 V-Sync，将控制 GPU 渲染速度在 60Hz 以内以匹配显示器刷新频率。这也意味着，在 V-Sync 的限制下，GPU 显示性能的极限就限制为 60Hz 以内。这样就能很好的避免图像撕裂的问题。

### Android 中的 GPU 渲染机制

大多数的 App 界面卡顿（Jank）现象都与 GPU 渲染有关，尤其是存在多层次布局嵌套，存在不必要的绘制，或者在 onDraw() 方法中执行了耗时操作，动画执行次数过多的情况下很容易出现界面卡顿。

图片16ms：http://hukai.me/images/draw_per_16ms.png

如上图所示，Android 系统每隔 16ms 就会发出一个 V-Sync 信号，触发对 UI 的渲染，如果每次渲染都能成功，这样就能保证画面的流畅帧率 60fps。 如果出现 16ms 内无法渲染的情况就无法响应 V-Sync 信号，就会出现丢帧现象。

图片16ms time out：http://hukai.me/images/vsync_over_draw.png

如上图所示：如果某个操作耗时 24ms，系统就无法正常响应当前 V-Sync 信号，只能等待下次响应 V-Sync 信号，当前 V-Sync 信号就会丢失，也就是所谓丢帧。

### Overdraw 过度绘制

- 什么是过度绘制？

过度绘制就是屏幕上的某个像素在同一帧的时间内被绘制了多次。 在多层次的UI结构里面，如果不可见的 UI 也在做绘制的操作，这就会导致某些像素区域被绘制了多次。这就浪费大量的 CPU 以及 GPU 资源。

- 如何发现过度绘制？

我们可以通过手机设置里面的开发者选项，打开 Show GPU Overdraw 的选项，可以观察 UI 上的 Overdraw 情况。

图片 过度绘制：http://hukai.me/images/overdraw_options_view.png

蓝色，淡绿，淡红，深红代表了 4 种不同程度的 Overdraw 情况，我们的目标就是尽量减少红色 Overdraw，看到更多的蓝色区域。

> 蓝色： 意味着overdraw 1倍。像素绘制了两次。大片的蓝色还是可以接受的（若整个窗口是蓝色的，可以摆脱一层）。 
> 绿色： 意味着overdraw 2倍。像素绘制了三次。中等大小的绿色区域是可以接受的但你应该尝试优化、减少它们。 
> 淡红： 意味着overdraw 3倍。像素绘制了四次，小范围可以接受。 
> 深红： 意味着overdraw 4倍。像素绘制了五次或者更多。这是错误的，要修复它们。 

Overdraw 有时候是因为你的UI布局存在大量重叠的部分，还有的时候是因为非必须的重叠背景。

> 例如：某个 Activity 有一个背景，然后里面的 Layout 又有自己的背景，同时子 View 又分别有自己的背景。仅仅是通过移除非必须的背景图片，这就能够减少大量的红色 Overdraw 区域，增加蓝色区域的占比。这一措施能够显著提升程序性能。

### 使用 Hierarchy Viewer 分析 UI 性能

http://www.jianshu.com/p/e9e05ce5b0c9
- 打开 Hierarchy Viewer

依次找到：Android Studio -> Tools -> Android -> Android Device Monitor

http://upload-images.jianshu.io/upload_images/1897639-9c9f672b014fbb82.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240

启动 Android Device Monitor 成功之后，在新的的窗口中点击切换视图图标，选择 Hierarchy View，如下图：

http://upload-images.jianshu.io/upload_images/1897639-c0631c3809290179.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240

Hierarchy View 运行界面如下：

图片：hierarchy_view.jpg

一个 Activity 的 View 树，通过这个树可以分析出 View 嵌套的冗余层级；
左下角可以输入 View 的 id 直接自动跳转到中间显示；
Save as PNG 用来把左侧树保存为一张图片；
Capture Layers 用来保存 psd 的 PhotoShop 分层素材；
右侧剧中显示选中 View 的当前属性状态；
右下角显示当前 View 在 Activity 中的位置等；
Load View Hierarchy 用来手动刷新变化（不会自动刷新的）。

当我们选择一个View后会如下图所示：

http://img.blog.csdn.net/20151005213558095

类似上图可以很方便的查看到当前 View 的许多信息；
上图最底那三个彩色原点代表了当前 View 的性能指标，从左到右依次代表测量、布局、绘制的渲染时间，红色和黄色的点代表速度渲染较慢的 View（当然了，有些时候较慢不代表有问题，比如 ViewGroup 子节点越多、结构越复杂，性能就越差）。

当然了，在自定义 View 的性能调试时，HierarchyViewer 上面的 invalidate Layout 和 requestLayout 按钮的功能更加强大，它可以帮助我们 debug 自定义 View 执行 invalidate() 和 requestLayout() 过程，我们只需要在代码的相关地方打上断点就行了，接下来通过它观察绘制即可。

可以发现，有了 Hierarchy View 调试工具，我们的 UI 性能分析变得十分容易，这个工具也是我们开发中调试 UI 的利器，在平时写代码时会时常伴随我们左右。

### 使用 GPU 呈现模式考核 UI 性能

http://blog.csdn.net/gjy211/article/details/52624788

在 Android 手机上开启这个功能：打开 开发者选项 -> GPU 呈现模式分析（Peofile GPU Rendering tool） -> 在屏幕上显示为条形图（On screen as bars）

图 绿色水平线

在 Android 系统中是以 60fps 为满帧，绿色横线为 16ms 分界线，低于绿线即为流畅。

屏幕下方的柱状图每一根代表一帧，其高度表示“渲染这一帧耗时”，随着手机屏幕界面的变化，柱状图会持续刷新每帧用时的具体情况（通过高度表示）。那么，当柱状图高于绿线，是不是就说明我卡了呢？其实这不完全正确，这里就要开始分析组成每一根柱状图不同颜色所代表的含义了。

- 红色，代表了“执行时间”，它指的是 Android 渲染引擎执行盒子中这些绘制命令的时间，假如当前界面的视图越多，那么红色便会“跳”得越高。实际使用中，比如我们平时刷淘宝 App 时遇到出现多张缩略图需要加载时，那么红色会突然跳很高，但是此时你的页面滑动其实是流畅的，虽然等了零点几秒图片才加载出来，但其实这可能并不意味着你卡住了。
- 黄色，通常较短，它代表着 CPU 通知 GPU “你已经完成视图渲染了”，不过在这里 CPU 会等待 GPU 的回话，当 GPU 说“好的知道了”，才算完事儿。 假如橙色部分很高的话，说明当前 GPU 过于忙碌，有很多命令需要去处理，比如 Android 淘宝客户端，红色黄色通常会很高。
- 蓝色，假如想通过玄学曲线来判断流畅度的话，其实蓝色的参考意义是较大的。蓝色代表了视图绘制所花费的时间，表示视图在界面发生变化（更新）的用时情况。当它越短时，即便是体验上更接近“丝滑”，当他越长时，说明当前视图较复杂或者无效需要重绘，即我们通常说的“卡了”。

理解了玄学曲线不同颜色代表的意义，看懂玄学曲线就不难了。 一般情况下，当蓝色低于绿线时都不会出现卡顿，但是想要追求真正的丝般顺滑那当然还是三色全部处于绿线以下最为理想。

### TraceView

生成 trace 文件有三种方法：

http://blog.csdn.net/u011240877/article/details/54347396

1. 使用代码
2. 使用 Android Studio
3. 使用 DDMS

- 使用代码生成 trace 文件

```Java
Debug.startMethodTracing("shixintrace");//开始 trace，保存文件到 "/sdcard/shixintrace.trace"
// ...
Debug.stopMethodTracing();//结束
```

代码很简单，当你调用开始代码的时候，系统会生产 trace 文件，并且产生追踪数据，当你调用结束代码时，会将追踪数据写入到 trace 文件中。

下一步使用 adb 命令将 trace 文件导出到电脑：

```Java
adb pull /sdcard/shixintrace.trace /tmp
```
使用代码生成 trace 方式的好处是容易控制追踪的开始和结束，缺点就是步骤稍微多了一点。

- 使用 Android Studio 生成 trace 文件
- 使用 DDMS 生成 trace 文件

### Systrace

## 参考资料

[脑洞大开：为啥帧率达到 60 fps 就流畅？](http://www.jianshu.com/p/71cba1711de0)
[Android性能优化之渲染篇](http://hukai.me/android-performance-render/)

