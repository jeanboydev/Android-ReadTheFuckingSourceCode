# 渲染性能优化

一个 Android 应用是否流畅，或者说是否存在卡顿、丢帧现象，都与 60fps 和 16ms 有关。那么这两个值是怎么来的呢？为什么以这两个值为衡量标准呢？本文主要讨论下渲染性能方面决定 Android 应用流畅性的因素。

## 为什么是 60fps？

- 12fps（帧/秒）

由于人类眼睛的特殊生理结构，如果所看画面之帧率高于每秒约 10 - 12fps 的时候，就会认为是连贯的。 早期的无声电影的帧率介于 16 - 24fps 之间，虽然帧率足以让人感觉到运动，但往往被认为是在快放幻灯片。 在 1920 年代中后期，无声电影的帧率提高到 20 - 26fps 之间。

- 24fps

1926 年有声电影推出，人耳对音频的变化更敏感，反而削弱了人对电影帧率的关注。因为许多无声电影使用 20 - 26fps 播放，所以选择了中间值 24fps 作为有声电影的帧率。 之后 24fps 成为 35mm 有声电影的标准。

- 30fps

早期的高动态电子游戏，帧率少于每秒 30fps 的话就会显得不连贯。这是因为没有动态模糊使流畅度降低。 （注：如果需要了解动态模糊技术相关知识，可以查阅 [这里](https://www.zhihu.com/question/21081976)）

- 60fps

在实际体验中，60fps 相对于 30fps 有着更好的体验。

- 85fps

一般而言，大脑处理视频的极限。

所以，总体而言，帧率越高体验越好。 一般的电影拍摄及播放帧率均为每秒 24 帧，但是据称《霍比特人：意外旅程》是第一部以每秒 48 帧拍摄及播放的电影，观众认为其逼真度得到了显著的提示。

目前，大多数显示器根据其设定按 30Hz、 60Hz、 120Hz 或者 144Hz 的频率进行刷新。 而其中最常见的刷新频率是 60Hz。

这样做是为了继承以前电视机刷新频率为 60Hz 的设定。 而 60Hz 是美国交流电的频率，电视机如果匹配交流电的刷新频率就可以有效的预防屏幕中出现滚动条，即互调失真。

### 16 ms

正如上面所述目前大多数显示器的刷新率是 60Hz，Android 设备的刷新率也是 60Hz。只有当画面达到 60fps 时 App 应用才不会让用户感觉到卡顿。那么 60fps 也就意味着 1000ms/60Hz = 16ms。也就是说 16ms 渲染一次画面才不会卡顿。

## CPU vs GPU

渲染操作通常依赖于两个核心组件：CPU 与 GPU。CPU 负责包括 Measure、Layout、Record、Execute 的计算操作，GPU 负责 Rasterization （栅格化）操作。

CPU 通常存在的问题的原因是存在非必需的视图组件，它不仅仅会带来重复的计算操作，而且还会占用额外的 GPU 资源。

![CPU vs GPU](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/01.jpg)

## Android UI 与 GPU

了解 Android 是如何利用 GPU 进行画面渲染有助于我们更好的理解性能问题。

那么一个最实际的问题是：Activity 的画面是如何绘制到屏幕上的？那些复杂的 XML 布局文件又是如何能够被识别并绘制出来的？

![Resterization](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/02.png)

Resterization 栅格化是绘制那些 Button、Shape、Path、String、Bitmap 等组件最基础的操作。它把那些组件拆分到不同的像素上进行显示。

这是一个很费时的操作，GPU 的引入就是为了加快栅格化的操作。

CPU 负责把 UI 组件计算成 Polygons，Texture 纹理，然后交给 GPU 进行栅格化渲染。

![CPU 与 GPU 工作流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/03.png)

然而，每次从 CPU 转移到 GPU 是一件很麻烦的事情，所幸的是 OpenGL ES 可以把那些需要渲染的纹理缓存在 GPU Memory 里面，在下次需要渲染的时候可以直接使用。但是，如果你更新了 GPU 缓存的纹理内容，那么之前保存的状态就丢失了。

在 Android 里面那些由主题所提供的资源（例如：Bitmaps、Drawables）都是一起打包到统一的 Texture 纹理当中，然后再传递到GPU里面，这意味着每次你需要使用这些资源的时候，都是直接从纹理里面进行获取渲染的。

当然，随着 UI 组件的越来越丰富，有了更多演变的形态。例如，显示图片的时候，需要先经过 CPU 的计算加载到内存中，然后传递给 GPU 进行渲染。文字的显示更加复杂，需要先经过 CPU 换算成纹理，然后再交给 GPU 进行渲染，回到 CPU 绘制单个字符的时候，再重新引用经过 GPU 渲染的内容。动画则是一个更加复杂的操作流程。

为了能够使得 App 流畅，我们需要在每一帧 16ms 以内处理完所有的 CPU 与 GPU 计算，绘制，渲染等等操作。

### UI 组件的更新

通常来说，Android 需要把 XML 布局文件转换成 GPU 能够识别并绘制的对象。这个操作是在 DisplayList 的帮助下完成的。DisplayList 持有所有将要交给 GPU 绘制到屏幕上的数据信息。

在某个 View 第一次需要被渲染时，DisplayList 会因此而被创建。当这个 View 要显示到屏幕上时，我们会执行 GPU 的绘制指令来进行渲染。

如果你在后续有执行类似移动这个 View 的位置等操作而需要再次渲染这个 View 时，我们就仅仅需要额外操作一次渲染指令就够了。然而如果你修改了 View 中的某些可见组件，那么之前的 DisplayList 就无法继续使用了，我们需要回头重新创建一个 DisplayList 并且重新执行渲染指令并更新到屏幕上。

需要注意的是：任何时候 View 中的绘制内容发生变化时，都会重新执行创建 DisplayList，渲染 DisplayList，更新到屏幕上等一系列操作。这个流程的表现性能取决于你的 View 的复杂程度，View 的状态变化以及渲染管道的执行性能。

![UI 组件的更新](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/04.png)

举个例子，假设某个 Button 的大小需要增大到目前的两倍，在增大 Button 大小之前，需要通过父 View 重新计算并摆放其他子 View 的位置。修改 View 的大小会触发整个 HierarcyView 的重新计算大小的操作。如果是修改 View 的位置则会触发 HierarchView 重新计算其他 View 的位置。如果布局很复杂，这就会很容易导致严重的性能问题。

## 垂直同步

为了理解 App 是如何进行渲染的，我们必须了解手机硬件是如何工作，那么就必须理解什么是垂直同步（VSYNC）。

在讲解 VSYNC 之前，我们需要了解两个相关的概念：

### 刷新率

刷新率（Refresh Rate）代表了屏幕在一秒内刷新屏幕的次数，这取决于硬件的固定参数，例如 60Hz。

### 帧率

帧率（Frame Rate）代表了 GPU 在一秒内绘制操作的帧数，例如 30fps，60fps。

GPU 会获取图形数据进行渲染，然后硬件负责把渲染后的内容呈现到屏幕上，他们两者不停的进行协作。

![GPU 渲染](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/05.png)



玩游戏的同学，尤其是大型 FPS 游戏应该都见过「垂直同步」这个选项。因为 GPU 的生成图像的频率与显示器的刷新频率是相互独立的，所以就涉及到了一个配合的问题。

最理想的情况是两者之间的频率是相同且协同进行工作的，在这样的理想条件下，达到了最优解。

![GPU 帧率](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/06.png)

但实际中 GPU 的生成图像的频率是变化的，如果没有有效的技术手段进行保证，两者之间很容易出现这样的情况。

当 GPU 还在渲染下一帧图像时，显示器却已经开始进行绘制，这样就会导致屏幕撕裂（Tear）。这会使得屏幕的一部分显示的是前一帧的内容，而另一部分却在显示下一帧的内容。如下图所示：

![撕裂的图像](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/07.jpg)

屏幕撕裂（Tear）的问题，早在 PC 游戏时代就被发现， 并不停的在尝试进行解决。 其中最知名可能也是最古老的解决方案就是 VSYNC 技术。

VSYNC 的原理简单而直观：产生屏幕撕裂的原因是 GPU 在屏幕刷新时进行了渲染，而 VSYNC 通过同步渲染/刷新时间的方式来解决这个问题。

显示器的刷新频率为 60Hz，若此时开启 VSYNC，将控制 GPU 渲染速度在 60Hz 以内以匹配显示器刷新频率。这也意味着，在 VSYNC 的限制下，GPU 显示性能的极限就限制为 60Hz 以内。这样就能很好的避免图像撕裂的问题。

通常来说，帧率超过刷新频率只是一种理想的状况，在超过 60fps 的情况下，GPU 所产生的帧数据会因为等待 VSYNC 的刷新信息而被 Hold 住，这样能够保持每次刷新都有实际的新的数据可以显示。但是我们遇到更多的情况是帧率小于刷新频率。

![VSYNC](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/08.png)

在这种情况下，某些帧显示的画面内容就会与上一帧的画面相同。糟糕的事情是，帧率从超过 60fps 突然掉到 60fps 以下，这样就会发生 LAG、JANK、HITCHING 等卡顿掉帧的不顺滑的情况。这也是用户感受不好的原因所在。

## 渲染性能

大多数用户感知到的卡顿等性能问题的最主要根源都是因为渲染性能（Rendering Performance）。

从设计师的角度，他们希望 App 能够有更多的动画，图片等时尚元素来实现流畅的用户体验。但是 Android 系统很有可能无法及时完成那些复杂的界面渲染操作。

Android 系统每隔 16ms 发出 VSYNC 信号，触发对 UI 进行渲染，如果每次渲染都成功，这样就能够达到流畅的画面所需要的 60fps，为了能够实现 60fps，这意味着程序的大多数操作都必须在 16ms 内完成。

![VSYNC 信号](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/09.png)

如果你的某个操作花费时间是 24ms，系统在得到 VSYNC 信号的时候就无法进行正常渲染，这样就发生了丢帧现象。那么用户在 32ms 内看到的会是同一帧画面。

![丢帧](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/10.png)

用户容易在 UI 执行动画或者滑动 ListView 的时候感知到卡顿不流畅，是因为这里的操作相对复杂，容易发生丢帧的现象，从而感觉卡顿。

有很多原因可以导致丢帧，也许是因为你的 layout 太过复杂，无法在 16ms 内完成渲染，有可能是因为你的 UI 上有层叠太多的绘制单元，还有可能是因为动画执行的次数过多。这些都会导致 CPU 或者 GPU 负载过重。

## 过度重绘

过度重绘（Overdraw）描述的是屏幕上的某个像素在同一帧的时间内被绘制了多次。在多层次的UI结构里面，如果不可见的 UI 也在做绘制的操作，这就会导致某些像素区域被绘制了多次。这就浪费大量的 CPU 以及 GPU 资源。

![Overdraw](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/11.png)

当设计上追求更华丽的视觉效果的时候，我们就容易陷入采用越来越多的层叠组件来实现这种视觉效果的怪圈。这很容易导致大量的性能问题，为了获得最佳的性能，我们必须尽量减少 Overdraw 的情况发生。

## 如何找出过度重绘？

很荣幸 Android 系统的开发者模式中，提供了一些工具可以帮助我们找出过度重绘。

首先，打开手机里面的开发者选项（这个都找不到，那还开发什么 Android？），可以找到下面几个选项：

### 调试 GPU 过度重绘（Debug GPU overdraw）

我们可以通过手机设置里面的 `开发者选项` ，打开 `显示过渡绘制区域`（Show GPU Overdraw）的选项，可以观察 UI 上的 Overdraw 情况。

![Debug GPU overdraw](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/12.png)

蓝色，淡绿，淡红，深红代表了 4 种不同程度的 Overdraw 情况，我们的目标就是尽量减少红色 Overdraw，看到更多的蓝色区域。

- 真彩色：没有过度绘制
- 蓝色：过度重绘 1 次

像素绘制了 2 次。大片的蓝色还是可以接受的（若整个窗口是蓝色的，可以摆脱一层）。

- 绿色：过度重绘 2 次

像素绘制了 3 次。中等大小的绿色区域是可以接受的但你应该尝试优化、减少它们。

- 淡红： 过度重绘 3 次

像素绘制了 4 次，小范围可以接受。

- 深红： 过度重绘 4 次或更多

像素绘制了 5 次或者更多。这是错误的，要修复它们。

Overdraw 有时候是因为你的UI布局存在大量重叠的部分，还有的时候是因为非必须的重叠背景。

例如：某个 Activity 有一个背景，然后里面的 Layout 又有自己的背景，同时子 View 又分别有自己的背景。仅仅是通过移除非必须的背景图片，这就能够减少大量的红色 Overdraw 区域，增加蓝色区域的占比。这一措施能够显著提升程序性能。

![优化过度重绘](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/13.png)

### GPU 呈现模式分析（Profile GPU Rendering）

我们可以通过手机设置里面的 `开发者选项` 中找到 `GPU 呈现模式分析`（Peofile GPU Rendering tool） ，然后选择 `在屏幕上显示为条形图`（On screen as bars）。

![Profile GPU Rendering](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/14.png)

在 Android 系统中是以 60fps 为满帧，绿色横线为 16ms 分界线，低于绿线即为流畅。

屏幕下方的柱状图每一根代表一帧，其高度表示「渲染这一帧耗时」，随着手机屏幕界面的变化，柱状图会持续刷新每帧用时的具体情况（通过高度表示）。

那么，当柱状图高于绿线，是不是就说明我卡了呢？其实这不完全正确，这里就要开始分析组成每一根柱状图不同颜色所代表的含义了。

![gpu 16ms](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/15.jpg)

- 红色

代表了「执行时间」，它指的是 Android 渲染引擎执行盒子中这些绘制命令的时间。

假如当前界面的视图越多，那么红色便会「跳」得越高。实际使用中，比如我们平时刷淘宝 App 时遇到出现多张缩略图需要加载时，那么红色会突然跳很高，但是此时你的页面滑动其实是流畅的，虽然等了零点几秒图片才加载出来，但其实这可能并不意味着你卡住了。

- 黄色

通常较短，它代表着 CPU 通知 GPU 你已经完成视图渲染了，不过在这里 CPU 会等待 GPU 的回话，当 GPU 说「好的知道了」，才算完事儿。

假如橙色部分很高的话，说明当前 GPU 过于忙碌，有很多命令需要去处理，比如 Android 淘宝客户端，红色黄色通常会很高。

- 蓝色

假如想通过玄学曲线来判断流畅度的话，其实蓝色的参考意义是较大的。蓝色代表了视图绘制所花费的时间，表示视图在界面发生变化（更新）的用时情况。

当它越短时，即便是体验上更接近「丝滑」，当他越长时，说明当前视图较复杂或者无效需要重绘，即我们通常说的「卡了」。

理解了玄学曲线不同颜色代表的意义，看懂玄学曲线就不难了。 一般情况下，当蓝色低于绿线时都不会出现卡顿，但是想要追求真正的丝般顺滑那当然还是三色全部处于绿线以下最为理想。

### Hierarchy Viewer

Hierarchy Viewer 是  Android Device Monitor 中的一个工具，它可以帮助我们检测布局层次结构中每个视图的布局速度。

它的界面如下：

![Hierarchy Viewer](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/16.png)

有一定开发经验的小伙伴应该使用过它，不过现在已经被「弃用了」，Google 推荐我们使用 Layout Inspector 来检查应用程序的视图层次结构。

### Layout Inspector

Layout Inspector 集成在 Android Studio 中，点击 **Tools > Layout Inspector**，在出现的 **Choose Process** 对话框中，选择您想要检查的应用进程，然后点击 **OK**。

![Layout Inspector](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/17.png)

默认情况下，Choose Process 对话框仅会为 Android Studio 中当前打开的项目列出进程，并且该项目必须在设备上运行。

如果您想要检查设备上的其他应用，请点击 Show all processes。如果您正在使用已取得 root 权限的设备或者没有安装 Google Play 商店的模拟器，那么您会看到所有正在运行的应用。否则，您只能看到可以调试的运行中应用。

布局检查器会捕获快照，将它保存为 `.li` 文件并打开。 如图下图所示，布局检查器将显示以下内容：

![Layout Inspector](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/18.png)

## 优化布局

使用上面的工具找到了过度重绘的地方，就需要优化自己的代码，我们可以通过下面几个方式进行优化。

### include

include 标签常用于将布局中的公共部分提取出来供其他 layout 共用，以实现布局模块化。

### merge

merge 标签主要用于辅助 include 标签，在使用 include 后可能导致布局嵌套过多，多余的 layout 节点或导致解析变慢。

例如：根布局是 Linearlayout，那么我们又 include 一个 LinerLayout 布局就没意义了，反而会减慢 UI 加载速度。

### ViewStub

ViewStub 标签最大的优点是当你需要时才会加载，使用它并不会影响UI初始化时的性能。

例如：不常用的布局像进度条、显示错误消息等可以使用 ViewStub 标签，以减少内存使用量，加快渲染速度.。

ViewStub 是一个不可见的，实际上是把宽高设置为 0 的 View。效果有点类似普通的 view.setVisible()，但性能体验提高不少。

### ConstraintLayout

约束布局 ConstraintLayout 是一个 ViewGroup，可以在 API 9 以上的 Android 系统使用它，它的出现主要是为了解决布局嵌套过多的问题，以灵活的方式定位和调整小部件。从 Android Studio 2.3 起，官方的模板默认使用 ConstraintLayout。

更多使用细节详见：[Android 开发文档 - ConstraintLayout](https://developer.android.google.cn/reference/android/support/constraint/ConstraintLayout)、[ConstraintLayout，看完一篇真的就够了么？](https://blog.csdn.net/singwhatiwanna/article/details/96472681)。

## 优化自定义 View

### onDraw()

减少 onDraw() 耗时操作。

### clipRect() 与 quickReject()

我们可以通过 `canvas.clipRect()` 来帮助系统识别那些可见的区域。这个方法可以指定一块矩形区域，只有在这个区域内才会被绘制，其他的区域会被忽视。

这个API可以很好的帮助那些有多组重叠组件的自定义 View 来控制显示的区域。同时 clipRect 方法还可以帮助节约 CPU 与 GPU 资源，在 clipRect 区域之外的绘制指令都不会被执行，那些部分内容在矩形区域内的组件，仍然会得到绘制。

![clipRect](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/19.png)

除了 clipRect 方法之外，我们还可以使用 `canvas.quickReject()` 来判断是否没和某个矩形相交，从而跳过那些非矩形区域内的绘制操作。

![quickReject](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/01_render/20.png)

上面的示例图中显示了一个自定义的View，主要效果是呈现多张重叠的卡片。这个 View 的 onDraw 方法如下图所示：

```java
protected void onDraw(Canvas canvas) {
  super.onDraw(canvas);
  
  if (mDroids.length > 0 && mDroidCards.size() == mDroids.length) {
    // 过度重绘代码
    int i;
    for (i = 0; i < mDroidCards.size(); i++) {
      // 每张卡片都放在前一张卡片的右侧
      mCardLeft = i * mCardSpacing;
      drawDroidCard(canvas, mDroidCards.get(i), mCardLeft, 0);
    }
  }

  invalidate();
}
```

打开「开发者选项」中的「显示过度渲染」，可以看到我们这个自定义的 View 部分区域存在着过度绘制。

下面的代码显示了如何通过 clipRect 来解决自定义 View 的过度绘制，提高自定义 View 的绘制性能：

```java
protected void onDraw(Canvas canvas) {
  super.onDraw(canvas);

  if (mDroids.length > 0 && mDroidCards.size() == mDroids.length) {
    int i;
    for (i = 0; i < mDroidCards.size() - 1; i++) {
      // 每张卡片都放在前一张卡片的右侧
      mCardLeft = i * mCardSpacing;
      // 保存 canvas 的状态
      canvas.save();
      // 将绘图区域限制为可见的区域
      canvas.clipRect(mCardLeft, 0, mCardLeft + mCardSpacing, 
                      mDroidCards.get(i).getHeight());

      drawDroidCard(canvas, mDroidCards.get(i), mCardLeft, 0);
      // 将画布恢复到非剪切状态
      canvas.restore();
    }

    // 绘制最后没有剪裁的卡片
    drawDroidCard(canvas, mDroidCards.get(i), 
                  mCardLeft + mCardSpacing, 0);
  }

  invalidate();
}
```

### 避免使用不支持硬件加速的 API

Android 系统中图形绘制分为两种方式，纯软件绘制和使用硬件加速绘制。

大家可以查看 [美团技术团队 - Android 硬件加速原理与实现简介](https://tech.meituan.com/2017/01/19/hardware-accelerate.html) 这篇文章了解下硬件加速的实现原理。

简单来说在 Android 3.0（API 11）之前没有硬件加速，图形绘制是纯软件的方式，DisplayList 的生成和绘制都需要 CPU 来完成。之后加入的硬件加速（默认开启）将一部分图形相关的操作交给 GPU 来处理，这样大大减少了 CPU 的运算压力。

所以我们在开发过程中应尽量避免使用不支持硬件加速的 API，来提升 UI 的渲染性能。

## 参考资料

- [YouTube - 性能优化典范 第一季](https://www.youtube.com/watch?v=R5ON3iwx78M&list=PL8ktV16dN_6vKDQB-D7fAqA6zRFQOoKtI)
- [Android 开发文档 - 检查 GPU 渲染速度和绘制过度](https://developer.android.com/studio/profile/inspect-gpu-rendering?hl=zh-cn)
- [Android 开发文档 - 使用层次结构查看器优化布局](https://developer.android.com/studio/profile/hierarchy-viewer)
- [Android 开发文档 - 使用布局检查器调试您的布局](https://developer.android.com/studio/debug/layout-inspector.html)
- [Android 开发文档 - 图形](https://source.android.com/devices/graphics)
- [Android 开发文档 - 硬件加速](https://developer.android.com/guide/topics/graphics/hardware-accel.html)
- [胡凯 - Android 性能优化典范 - 第 1 季](http://hukai.me/android-performance-patterns/)
- [胡凯 - Android 性能优化之渲染篇](http://hukai.me/android-performance-render/)
- [Android 开发文档 - ConstraintLayout](https://developer.android.google.cn/reference/android/support/constraint/ConstraintLayout)
- [ConstraintLayout，看完一篇真的就够了么？](https://blog.csdn.net/singwhatiwanna/article/details/96472681)