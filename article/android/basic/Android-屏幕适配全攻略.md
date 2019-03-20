# Android - 屏幕适配全攻略

## 一、Android 屏幕碎片化
由于 Android 系统的开发性，任何用户、开发者、OEM厂商、运营商都可以对 Android 进行定制，修改成他们想要的样子。各大厂商、开发者的标准不统一，所以就造成了 Android 系统碎片化。

但是这种“碎片化”到底到达什么程度呢？

下面这张图片所显示的内容足以充分说明当今 Android 系统碎片化问题的严重性，因为该图片中的每一个矩形都代表着一种 Android 设备。

![图08][8]

而随着支持 Android 系统的设备(手机、平板、电视、手表)的增多，设备碎片化、品牌碎片化、系统碎片化、传感器碎片化和屏幕碎片化的程度也在不断地加深。而我们今天要探讨的，则是对我们开发影响比较大的——屏幕的碎片化。

下面这张图是 Android 屏幕尺寸的示意图，在这张图里面，蓝色矩形的大小代表不同尺寸，颜色深浅则代表所占百分比的大小。

![图06][6]

而与之相对应的，则是下面这张图。这张图显示了 IOS 设备所需要进行适配的屏幕尺寸和占比。

![图07][7]

当然，这张图片只是 4, 4s, 5, 5c, 5s 和平板的尺寸，现在还应该加上新推出的 iphone6 和 plus，但是和 Android 的屏幕碎片化程度相比而言，还是差的太远。

> Android屏幕的碎片化如此严重，所以我们不得不进行屏幕的适配，如何面对如此多的屏幕进行适配？下面结合Google官方开发文档讨论下最优的解决方案。

## 二、术语和概念
#### 1. 什么是屏幕尺寸、屏幕分辨率、屏幕像素密度？
屏幕尺寸
> **按屏幕对角测量的实际物理尺寸。**单位是英寸(inch)，1英寸 = 2.54厘米。

屏幕分辨率
> **屏幕上物理像素的总数。**单位是 px，1px = 1像素点，一般是纵向像素×横向像素，如1280×720。

每英寸点数
> 是指每英寸多少点。单位是 dpi，即 “dot per inch” 的缩写，是打印机、鼠标等设备分辨率的单位。

屏幕像素密度
> **所表示的是每英寸所拥有的像素数量。**单位是ppi，即 “Pixel per inch“ 的缩写，每英寸像素点数。**针对显示器的设计时，dpi = ppi。**

![图01][1]

> 例如：计算Nexus5的屏幕像素密度：屏幕尺寸：4.95 inch、分辨率：1920×1080，屏幕像素密度(ppi)：445

![图02][2]

#### 2. 什么是 dp、dip、dpi、sp、px？之间的关系是什么？
dip/dp
> 在定义 UI 布局时应使用的虚拟像素单位，用于以密度无关方式表示布局维度或位置。
> 
> Density Independent Pixels(密度无关像素)的缩写。
以160dpi为基准，1dp = 1px。单位转换： px = dp * (dpi / 160)。

dpi
> 屏幕像素密度的单位，“dot per inch” 的缩写

px
> 像素，物理上的绝对单位

sp
> Scale-Independent Pixels 的缩写，可以根据文字大小首选项自动进行缩放。
> 
> Google 推荐我们使用 12s p以上的大小，通常可以使用 12sp，14sp，18sp，22sp，最好不要使用**奇数**和**小数**。

#### 3. 什么是 mdpi、hdpi、xdpi、xxdpi、xxxdpi？如何计算和区分？

| 名称				| 像素密度范围	| 图片大小  	|
| :------------- 	| :-----------	| :-----	|
| mdpi(中)      		| 120dp~160dp	| 48×48px 	|
| hdpi(高)      		| 160dp~240dp	| 72×72px 	|
| xhdpi(超高) 		| 240dp~320dp	| 96×96px 	|
| xxhdpi(超超高) 	| 320dp~480dp	| 144×144px |
| xxxhdpi(超超超高) 	| 480dp~640dp	| 192×192px |

![图03][3]

>在Google官方开发文档中，说明了 mdpi：hdpi：xhdpi：xxhdpi：xxxhdpi = 2：3：4：6：8 的尺寸比例进行缩放。例如，一个图标的大小为 48×48dp，表示在mdpi上，实际大小为 48×48px，在 hdpi 像素密度上，实际尺寸为 mdpi 上的1.5倍，即 72×72px，以此类推。

#### 4. 支持的屏幕范围
四种通用尺寸：小、正常、 大 和超大。

六种通用的密度：

-  ldpi（低）~120dpi<br>
-  mdpi（中）~160dpi<br>
-  hdpi（高）~240dpi<br>
-  xhdpi（超高）~320dpi<br>
-  xxhdpi（超超高）~480dpi<br>
-  xxxhdpi（超超超高）~640dpi

屏幕尺寸与屏幕密度对比：

![图04][4]<br>
- 超大屏幕至少为 960dp x 720dp<br>
- 大屏幕至少为 640dp x 480dp<br>
- 正常屏幕至少为 470dp x 320dp<br>
- 小屏幕至少为 426dp x 320dp

##	三、解决方案 - 支持各种屏幕尺寸
#### 1.  使用配置限定符
![图05][5]

> 这里只是展示了常用的一些配置限定符，具体用法和详情请参阅：[Google官方开发文档-使用配置限定符](https://developer.android.com/guide/practices/screens_support.html?hl=zh-cn#qualifiers)

#### 2. 使用 NinePatch(.9) 图片
什么是.9图？
> NinePatch 是一种 PNG 图像，在其中可定义当视图中的内容超出正常图像边界时 Android 缩放的可拉伸区域。 后缀以 **.9.png** 结尾，命名格式为：xxx.9.png。<br>
> 如：普通图：ic_launcher**.png** <br>
> .9图 为：ic_launcher**.9.png** <br>
> 文件位置： res/drawable/filename.9.png 文件名用作资源 ID。

怎么制作.9图？
> 使用 Photoshop（不推荐）<br>
> 使用 Android SDK 自带工具，在 ...\Android\SDK\tools\ 下名字为 draw9patch 的文件。<br>
> 使用 Android Studio 同上。


draw9patch如图 ：

![图09][9]<br>
![图10][10]<br>

拉伸区域

![图11][11]<br>

> **红色框区域**：表示纵向拉伸的区域，也就是说，当图片需要纵向拉伸的时候它会只指定拉伸红色区域，其他区域在纵向是不会拉伸的。
> 
> **绿色框区域**：表示横向拉伸的区域，也就是说，当图片需要横向拉伸的时候它会只指定拉伸绿色区域，其他区域在横向是不会拉伸的。
> 
> 显然红色和绿色相交的部分是既会进行横向拉伸也会进行纵向拉伸的。

前景的显示区域

![图12][12]<br>

> **蓝色区域**：表示前景能显示的纵向范围。即前景的最上面可以显示到什么地方，最下面可以显示的什么地方。
> 
> **黄色区域**：表示前景能显示的横向范围。即前景的最左边可以显示到什么地方，最右边可以显示的什么地方。
> 
> 蓝色和黄色相交部分：表示整个前景能显示的区域。一个区域是矩形的，蓝色规定了上下边界，黄色规定了左右边界，两者共同当然也就规定了一个矩形区域。

#### 3.可绘制的资源文件 Drawable
> 请参考：[Google官方开发文档-可绘制对象资源](https://developer.android.com/guide/topics/resources/drawable-resource.html)

#### 4. 最佳做法
1.	在 XML 布局文件中指定尺寸时使用 wrap_content、 match_parent 或 dp 单位 。
2.	不要在应用代码中使用硬编码的像素值 。
3.	不要使用 AbsoluteLayout（已弃用） 。
4.	为不同屏幕密度提供替代位图可绘制对象 。

#### 5. 总结

![图13][13]<br>

> 表格里面列出了目前主流的 Android 手机设备分辨率对应的 dpi 缩放级别。<br>
> 一般设计师会以 **1920 x 1080** 来设计效果图，那么**只需要将效果图测量出来的 px值 填入 第6行-px列** 中即可自动计算出所需的 **dp/sp 的值**。<br>
> 通常情况下以 **1280 x 720** 的效果图来写布局是比较好的方式，因为**测量出来的 px值是 dp/sp 的两倍**，方便计算。<br>
>表格下载：[Android屏幕适配单位转换.xls](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/Android%E5%B1%8F%E5%B9%95%E9%80%82%E9%85%8D%E5%8D%95%E4%BD%8D%E8%BD%AC%E6%8D%A2.xls)


## 参考资料
- [https://developer.android.com/guide/practices/screens_support.html?hl=zh-cn#DeclaringTabletLayouts](https://developer.android.com/guide/practices/screens_support.html?hl=zh-cn#DeclaringTabletLayouts)
- [http://blog.jeswang.org/blog/2013/08/07/ppi-vs-dpi-you-shi-yao-qu-bie/](http://blog.jeswang.org/blog/2013/08/07/ppi-vs-dpi-you-shi-yao-qu-bie/)
- [http://blog.csdn.net/zhaokaiqiang1992/article/details/45419023](http://blog.csdn.net/zhaokaiqiang1992/article/details/45419023)
- [http://www.cnblogs.com/vanezkw/archive/2012/07/19/2599092.html](http://www.cnblogs.com/vanezkw/archive/2012/07/19/2599092.html)


[1]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/01.png
[2]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/02.png
[3]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/03.png
[4]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/04.png
[5]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/05.jpg
[6]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/06.png
[7]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/07.png
[8]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/08.png
[9]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/09.png
[10]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/10.png
[11]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/11.png
[12]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/12.png
[13]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_screens_support/13.png

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！