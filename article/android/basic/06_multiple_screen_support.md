# 屏幕适配最佳实践

## 基本概念

### 屏幕尺寸

手机屏幕对角线的物理尺寸。单位英寸（inch），一英寸大约 2.54cm。常见的手机屏幕尺寸有 4.7 英寸、5.0英寸、5.5 英寸、6.0 英寸等。

![屏幕尺寸示例图](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/01.png)

### 像素（px）

像素（英语：Picture  Element），Pixel 的缩写。液晶屏显示图像，放大来看是一个个小点组成的，这些小点就是像素点。

![像素点](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/02.png)

### 分辨率

分辨率（英语：Image resolution），又称解析度、解像度，可以从显示分辨率与图像分辨率两个方向来分类。

在 Android 设备中指的是显示分辨率，即屏幕分辨率。也就是屏幕所能显示的像素有多少，比如：手机分辨率 1920 x 1080。

在图片中指是图像分辨率，则是单位英寸中所包含的像素点数。比如：图片分辨率 600 x 400。

![不同分辨率的图像的差别](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/03.png)

### 每英寸点数（DPI）

每英寸点数（英语：**D**ots **P**er **I**nch，缩写：**DPI**）是一个量度单位，用于点阵数码影像，指每一英寸长度中，取样、可显示或输出点的数目。

一般用于打印机、鼠标等设备分辨率的度量单位。

比如：打印机输出可达 600 DPI 的分辨率，表示打印机可以在每一平方英寸的面积中可以输出 600 x 600 ＝ 360000 个输出点。

鼠标的 DPI 参数，指的是鼠标在桌面上移动一英寸的距离的同时，鼠标光标能够在屏幕上移动多少「点」。

### 每英寸像素（PPI）

每英寸像素（英语：**P**ixels **P**er **I**nch，缩写：**PPI**），又被称为像素密度。

一般用来计量计算机显示器，电视机和手持电子设备屏幕的精细程度。通常情况下，每英寸像素值越高，屏幕能显示的图像也越精细。

### 分辨率、DPI、PPI 之间的关系

当我们把相同分辨率的图片，放在具有相同像素显示的屏幕上显示时。每一个像素，屏幕上对应一个点显示，此时 DPI = PPI。
比如：我们把分辨率为 `m x n` 的图片，放在最大支持 `m x n` 像素的屏幕上时，DPI = PPI。

但是，实际上，我们所需要显示图片的分辨率，跟屏幕参数匹配的概率还是很小的。我们来分析下，不匹配时的情况：

当我们把 `1280 x 720` 的图片，放在 `800 x 480` 的 4 英寸的屏幕与 `1920 x 1080` 的 5.5 英寸的屏幕上显示时的结果为：

![分辨率、DPI 与 PPI](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/04.png)

PPI 是屏幕的显示性能，所以与显示的图片没有关系，是固定的值，但是 DPI 与显示的图片是有关系的。

- 分辨率为 `1280 x 720` 的图片放在 `800 x 480` 的 4 英寸的屏幕上显示

虽然图片一行有 720 个像素，但是屏幕一行最多只能显示 480 个点，所以 `DPI = PPI = 233`，已经达到屏幕的最大显示能力。

- 分辨率为 `1280 x 720` 的图片放在 `1920 x 1080` 的 5.5 英寸的屏幕上显示

虽然屏幕一行有 1080 个点，但是图片一行最多只能显示 720 个像素，所以 `DPI = 267 < PPI`，并未达到屏幕的最大显示能力，未达到屏幕的最佳显示效果。

通过上面分析可以得到：

- 分辨率：只能用来描述图片的像素信息，不能描述图片清晰度。
- PPI：只能用来描述屏幕的显示密度，也不能描述图片的清晰度
- DPI：才能用来描述图片显示的清晰度，表示图片在屏幕上的显示效果。

一句话总结下就是 DPI 表示印刷品点的密度，PPI 表示显示设备点的密度。

![PPI(左)和 DPI(右)的比较](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/05.png)

#### PPI 计算公式

由于显示器的 DPI 是固定的，不像打印机那样可以调整，所以针对显示器的设计时 DPI = PPI。

计算显示器的每英寸像素值，需要确定屏幕的尺寸和分辨率。

![PPI 计算公式](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/11.png)

其中：

- W（Width）：为屏幕横向分辨率。
- H（Height）：为屏幕纵向分辨率。
- inch：为屏幕对角线的长度（单位为英寸）。

#### 基于 PPI 屏幕分级

根据屏幕每英寸像素值的不同，Android 中将平板电脑和手机的屏幕分为下面几类：

|        密度名称         |  每英寸像素值   |   图标尺寸   |
| :---------------------: | :-------------: | :----------: |
|     低密度（LDPI）      |     ~120dpi     |  36 x 36 px  |
|     中密度（MDPI）      | 120dpi ~ 160dpi |  48 x 48 px  |
|     高密度（HDPI）      | 160dpi ~ 240dpi |  72 x 72 px  |
|    超高密度（XHDPI）    | 240dpi ~ 320dpi |  96 x 96 px  |
|  超超高密度（XXHDPI）   | 320dpi ~ 480dpi | 144 x 144 px |
| 超超超高密度（XXXHDPI） | 480dpi ~ 640dpi | 192 x 192 px |

### 密度无关像素（DP）

DP 或者 DIP，是 Android 开发用的单位。1dp 表示在屏幕点密度为 160ppi 时 1px 长度。

由于 Android 设备屏幕众多，不可能为每个屏幕单独开发，所以用下面公式计算在不同屏幕上的像素数。

![PX 计算公式](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/12.png)

同一图标在分辨率不同的设备上显示时，会出现如下效果：

![同一图标不同设备显示效果](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/06.png)

可以看到上图第 1 和第 2 个设备两个屏幕尺寸相同，由于它们分辨率的不同，同一个图标在两个设备上显示的尺寸相差很大。

那么，图片显示大小是由什么决定的呢，屏幕尺寸吗？上图第 1 和第 2 个设备屏幕都是 4.3 英寸。

还是因为分辨率呢？上图第 2 和第 3 个设备屏幕都是 720 x 1280 的分辨率。

最后我们找到了像素密度（density），也就是像素数和屏幕尺寸的比值。density 是每单位长度容纳的像素数量，一般用像素/英寸，也就是 Pixel per inch（PPI）。

对比上图可以知道，PPI 越低图片显示的越大，PPI 越高图片显示的越小。

要让不同屏幕显示图片的大小相同，就需要对图片进行缩放，给高 PPI 屏提供更大的图片。

![兼容高 PPI 屏幕](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/07.png)

高 PPI 屏幕需要更大的图片才能得到同样的显示效果，反之亦然。

PPI 和图片 px 的关系，如下：

![PPI 与 PX 计算公式](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/13.png)

选定一个 PPI 值作为基础绘制图片，用 PPI 的比值计算出图片缩放比例，就可以适配各种屏幕。

![公式换算 1](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/14.png)

Android 选定的这个基础值就是 `160ppi`。

![公式换算 2](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/15.png)

我们已经解决了图片放大缩小的问题，还需要一个单位用来描述长度。

因为 px 不固定，inch 不方便，所以 Android 创造了一个新的单位 dp，中文名密度无关像素。并且规定在 160ppi 的屏幕上 1dp = 1px。

设计师只需要针对 160ppi 的显示屏设计并制图，安卓会根据当前手机屏幕的 PPI 值来放大缩小图片，在不同的屏幕上得到相近的显示效果。

![公式换算 3](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/16.png)


### 独立比例像素（SP） 

Android 设备的文字单位是 SP，简单理解和 DP 是相同的。另外 SP 会随着系统的字体大小改变，而 DP 则不会。

Google 推荐我们使用 12sp 以上的大小，通常可以使用 12sp、14sp、18sp、22sp。最好不要使用「奇数」和「小数」。

## 适配不同屏幕尺寸

### 布局适配

#### wrap_content

设置视图的宽高为 wrap_content 时，视图大小会根据内容自动增加。

#### match_parent

设置视图宽高位 match_parent 时，视图大小始终与父级一样大。

#### LinerLayout

LinerLayout 是一个视图组，用于使所有子视图在单个方向（垂直或水平）保持对齐。 可以使用 `android:orientation` 属性指定布局方向。

- weight

使用线性布局时，将某一个或者多个子视图的宽或者高设置为 `0dp`，设置 weight 值为 `1`。

weight 值为 1 的子视图将会充满父视图剩余的空间，如果设置多个子视图的 weight 都为 1，那么这些子视图将平分并充满父视图剩余的空间。

#### RelativeLayout

RelativeLayout 是一个视图组，显示相对位置的子视图。使用 RelativeLayout 可以将子视图定位在任意位置。

### 限定符适配

#### 尺寸限定符

- small：提供给小屏幕设备的资源
- normal：提供给中等屏幕设备的资源
- large：提供给大屏幕设备的资源
- xlarge：提供给超大屏幕的资源

使用方式如下：

```json
|- layout // 无限定符，默认布局
	|- main.xml
|- layout-small // 小屏幕设备
	|- main.xml
|- layout-normal // 中等屏幕设备
	|- main.xml
|- layout-large // 大屏幕设备
	|- main.xml
|- layout-xlarge // 超大屏幕设备
	|- main.xml
```

#### 最小宽度限定符

最小宽度限定符就是设置设备屏幕大于或等于最小宽度时加载的视图。

例如，7 英寸平板电脑最小宽度为 600dp，如果希望的 UI 在这些屏幕上显示两列，但在较小屏幕上显示单列，就可以使用最小宽度限定符。

```json
|- layout // 无限定符，默认布局显示单列
	|- main.xml
|- layout-sw600dp // 设备宽度为 600dp 以上时显示两列
	|- main.xml
```

#### 布局别名

如果适配的屏幕设备比较多，为了方便视图文件的管理，我们可以使用布局别名。

```json
|- layout
	|- main.xml // 单列布局
	|- main_twopanes.xml // 双列布局
|- values-large
	|- layout.xml
|- values-sw600dp
	|- layout.xml
```

- `res/values-large/layout.xml`：

```xml
<resources>
    <item name="main" type="layout">@layout/main_twopanes</item>
</resources>
```

- `res/values-sw600p/layout.xml`：

```xml
<resources>
    <item name="main" type="layout">@layout/main_twopanes</item>
</resources>
```

后两个文件内容完全相同，但它们实际上并未定义布局， 而只是将 `main` 设置为 `main_twopanes` 的别名。由于这些文件具有 `large` 和 `sw600dp` 选择器，因此它们适用于任何 Android 版本的平板电脑和电视（低于 3.2 版本的平板电脑和电视匹配 `large`，高于 3.2 版本者将匹配 `sw600dp`）。

#### 屏幕方向限定符

- land：提供给横屏设备的资源
- port：提供给竖屏设备的资源

```json
|- layout
	|- main.xml // 单列布局
	|- main_twopanes.xml // 双列布局
|- values-large-land // 大屏幕横向
	|- layout.xml
|- values-sw600dp-port // 最小宽度 600dp 横向
	|- layout.xml
```

### 图片适配

#### 位图

- Logo 图标

官方建议的图标尺寸：

|    密度名称    |  每英寸像素值   |   图标尺寸   |     图片资源目录      |
| :------------: | :-------------: | :----------: | :-------------------: |
|      LDPI      |     ~120dpi     |  36 x 36 px  |      mipmap-ldpi      |
|  MDPI（基准）  | 120dpi ~ 160dpi |  48 x 48 px  | mipmap 或 mipmap-mdpi |
| HDPI（1.5倍）  | 160dpi ~ 240dpi |  72 x 72 px  |      mipmap-hdpi      |
|  XHDPI（2倍）  | 240dpi ~ 320dpi |  96 x 96 px  |     mipmap-xhdpi      |
| XXHDPI（3倍）  | 320dpi ~ 480dpi | 144 x 144 px |     mipmap-xxhdpi     |
| XXXHDPI（4倍） | 480dpi ~ 640dpi | 192 x 192 px |    mipmap-xxxhdpi     |

- 普通位图和图标

按照官方密度类型进行切图即可，一般情况下只需要根据主流设备选择所需要的资源文件即可。

目前已知主流设备屏幕：

| 屏幕分辨率  | 屏幕尺寸 | PPI  |    对应密度    |  图片资源文件夹  |
| :---------: | :------: | :--: | :------------: | :--------------: |
|  240 x 320  |   2.5    | 160  |  MDPI（基准）  |  drawable-mdpi   |
|  400 x 800  |   4.0    | 224  | HDPI（1.5倍）  |  drawable-hdpi   |
| 720 x 1280  |   4.7    | 313  |  XHDPI（2倍）  |  drawable-xhdpi  |
| 1080 x 1920 |   5.5    | 401  | XXHDPI（3倍）  | drawable-xxhdpi  |
| 1440 x 2560 |   6.0    | 490  | XXXHDPI（4倍） | drawable-xxxhdpi |

#### 九宫格位图

- 拉伸区域

![拉伸区域](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/08.png)

**红色框区域**：表示纵向拉伸的区域，当图片需要纵向拉伸的时候它会只指定拉伸红色区域，其他区域在纵向是不会拉伸。

**绿色框区域**：表示横向拉伸的区域，当图片需要横向拉伸的时候它会只指定拉伸绿色区域，其他区域在横向是不会拉伸的。

显然红色和绿色相交的部分是既会进行横向拉伸也会进行纵向拉伸。

- 显示区域

![显示区域](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/09.png)

**黄色区域**：表示前景能显示的横向范围。即前景的最左边可以显示到什么地方，最右边可以显示的什么地方。

**蓝色区域**：表示前景能显示的纵向范围。即前景的最上面可以显示到什么地方，最下面可以显示的什么地方。

蓝色和黄色相交部分：表示整个前景能显示的区域。一个区域是矩形的，蓝色规定了上下边界，黄色规定了左右边界，两者共同当然也就规定了一个矩形区域。

#### 矢量图

矢量图是根据几何特性来绘制图形，矢量可以是一个点或一条线，矢量图只能靠软件生成，文件占用内在空间较小，因为这种类型的图像文件包含独立的分离图像，可以自由无限制的重新组合。

它的特点是放大后图像不会失真，和分辨率无关，适用于图形设计、文字设计和一些标志设计、版式设计等。

- SVG

SVG 指可伸缩矢量图形 (Scalable Vector Graphics)。用来定义用于网络的基于矢量的图形，SVG 使用 XML 格式定义图形，图像在放大或改变尺寸的情况下其图形质量不会有所损失。

Android 中对矢量图的支持就是对 SVG 的支持。使用方式比较简单，这里不再赘述。

#### ScaleType

ImageView 是 Android 中最常用的控件之一，而在使用 ImageView 时，必不可少的会使用到它的 scaleType 属性。该属性指定了你想让 ImageView 如何显示图片，包括是否进行缩放、等比缩放、缩放后展示位置等。

Android 提供了八种 scaleType的 属性值，每种都对应了一种展示方式。

- center：保持原图的大小，显示在 ImageView 的中心。当原图的尺寸大于 ImageView 的尺寸时，多出来的部分被裁切掉。
- center_inside：以原图正常显示为目的，如果原图大小大于 ImageView 的尺寸，就按照比例缩小原图的宽高，居中显示在 ImageView 中。如果原图尺寸小于 ImageView 的 size，则不做处理居中显示图片。
- center_crop：以原图填满 ImageView 为目的，如果原图尺寸大于 ImageView 的尺寸，则与 center_inside 一样，按比例缩小，居中显示在 ImageView 上。如果原图尺寸小于 ImageView 的尺寸，则按比例拉伸原图的宽和高，填充 ImageView 居中显示。
- matrix：不改变原图的大小，从 ImageView 的左上角开始绘制，超出部分做剪切处理。
- fit_xy：把图片按照指定的大小在 ImageView 中显示，拉伸显示图片，不保持原比例，填满ImageView。
- fit_start：把原图按照比例放大缩小到 ImageView的 高度，显示在 ImageView 的 center（前部/上部）。
- fit_center：把原图按照比例放大缩小到 ImageView 的高度，显示在 ImageView 的 center（中部/居中显示）。
- fit_end： 把原图按照比例放大缩小到 ImageView 的高度，显示在 ImageVIew 的 end（后部/尾部/底部）

![scaleType](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/06_multiple_screen_support/10.png)

#### 接口适配

本地加载图片时，根据设备屏幕分辨率或像素密度，向服务器请求对应级别的图片资源。

### 支持刘海屏幕

Android P 提供提供的刘海屏适配方案，详见：[Android 开发文档 - 支持显示切口](https://developer.android.com/guide/topics/display-cutout)

- 对于有状态栏的页面，不会受到刘海屏特性的影响，因为刘海屏包含在状态栏中了；
- 全屏显示的页面，系统刘海屏方案会对应用界面做下移处理，避开刘海区显示，这时会看到刘海区域变成一条黑边，完全看不到刘海了；
- 已经适配 Android P 应用的全屏页面可以通过谷歌提供的适配方案使用刘海区，真正做到全屏显示。

刘海屏适配思路：

- Android P 以后的设备：如果有状态栏不需要适配，因为刘海区域会包含在状态栏中了（设置 `LAYOUT_IN_DISPLAY_CUTOUT_MODE_NEVER` 可将刘海区域变成一条黑色边）。如果全屏显示，获取到危险区域（刘海区域），让操作区域避开危险区域即可。
- Android P 之前的设备：根据主流厂商 华为、vivo、OPPO、小米等所提供的方案进行适配。

### 增加不支持的屏幕

Google 建议我们支持更多的设备，但是根据需求可能需要不支持某些设备。比如，仅支持手机不支持平板电脑。我们就可以增加不支持的屏幕设备。

如果应用仅支持小屏幕尺寸和标准屏幕尺寸，可以这么做：

```xml
<manifest ... >
  <compatible-screens>
    <!-- 所有的小尺寸屏幕 -->
    <screen android:screenSize="small" android:screenDensity="ldpi" />
    <screen android:screenSize="small" android:screenDensity="mdpi" />
    <screen android:screenSize="small" android:screenDensity="hdpi" />
    <screen android:screenSize="small" android:screenDensity="xhdpi" />
    <!-- 所有的标准尺寸屏幕 -->
    <screen android:screenSize="normal" android:screenDensity="ldpi" />
    <screen android:screenSize="normal" android:screenDensity="mdpi" />
    <screen android:screenSize="normal" android:screenDensity="hdpi" />
    <screen android:screenSize="normal" android:screenDensity="xhdpi" />
  </compatible-screens>
  ...
  <application ... >
    ...
  <application>
</manifest>
```

如果应用仅支持平板电脑或电视，可以这么做：

```xml
<manifest ... >
  <supports-screens android:smallScreens="false"
                    android:normalScreens="false"
                    android:largeScreens="true"
                    android:xlargeScreens="true"/>
  ...
</manifest>
```

## 今日头条适配方案

2018 年 5 月，字节跳动技术团队提出了一种低成本的屏幕适配方式，强烈推荐大家看一下：[一种极低成本的 Android 屏幕适配方式](https://mp.weixin.qq.com/s/d9QCoBP6kV9VSWvVldVVwA)

## 参考资料

- [Android 开发文档 - 屏幕兼容性概览](https://developer.android.com/guide/practices/screens_support?hl=zh-CN)
- [DPI、PPI、DP、PX 的详细计算方法及算法来源是什么？](https://www.zhihu.com/question/21220154)
- [分辨率 PPI DPI概念定义详解](https://blog.csdn.net/csdn66_2016/article/details/70331919)
- [Android 屏幕适配方案](https://juejin.im/post/5ae32bac518825671a638405)
- [Android ImageView 的scaleType 属性图解](https://www.jianshu.com/p/32e335d5b842)