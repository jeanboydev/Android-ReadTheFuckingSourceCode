# Android屏幕适配 #
<br>
## 一、术语和概念 ##
####1.什么是屏幕尺寸、屏幕分辨率、屏幕像素密度？####
屏幕尺寸
> 按屏幕对角测量的实际物理尺寸。单位是英寸(inch)，1英寸=2.54厘米。

屏幕分辨率
> 屏幕上物理像素的总数。单位是px，1px=1像素点，一般是纵向像素×横向像素，如1280×720。

每英寸点数
> 是指每英寸多少点。单位是dpi，即“dot per inch”的缩写，是打印机、鼠标等设备分辨率的单位。

屏幕像素密度
> 所表示的是每英寸所拥有的像素数量。单位是ppi，即“Pixel per inch“的缩写，每英寸像素点数。针对显示器的设计时，dpi=ppi。

![图01][1]<br>
> 例如：计算Nexus5的屏幕像素密度：屏幕尺寸：4.95inch、分辨率：1920×1080，屏幕像素密度(ppi)：445

![图02][2]<br>

####2.什么是dp、dip、dpi、sp、px？之间的关系是什么？####
dip/dp
> 在定义 UI 布局时应使用的虚拟像素单位，用于以密度无关方式表示布局维度或位置。<br>
> Density Independent Pixels(密度无关像素)的缩写。
以160dpi为基准，1dp=1px。单位转换： px = dp * (dpi / 160)。

dpi
> 屏幕像素密度的单位，“dot per inch”的缩写

px
> 像素，物理上的绝对单位

sp
> Scale-Independent Pixels的缩写，可以根据文字大小首选项自动进行缩放。<br>
> Google推荐我们使用12sp以上的大小，通常可以使用12sp，14sp，18sp，22sp，最好不要使用奇数和小数。

####3.什么是mdpi、hdpi、xdpi、xxdpi、xxxdpi？如何计算和区分？####

| 名称				| 像素密度范围	| 图片大小  	|
| :------------- 	| :-----------	| :-----	|
| mdpi(中)      		| 120dp~160dp	| 48×48px 	|
| hdpi(高)      		| 160dp~240dp	| 72×72px 	|
| xhdpi(超高) 		| 240dp~320dp	| 96×96px 	|
| xxhdpi(超超高) 	| 320dp~480dp	| 144×144px |
| xxxhdpi(超超超高) 	| 480dp~640dp	| 192×192px |
![图03][3]<br>
>在Google官方开发文档中，说明了 mdpi：hdpi：xhdpi：xxhdpi：xxxhdpi=2：3：4：6：8 的尺寸比例进行缩放。例如，一个图标的大小为48×48dp，表示在mdpi上，实际大小为48×48px，在hdpi像素密度上，实际尺寸为mdpi上的1.5倍，即72×72px，以此类推。<br>

####4.支持的屏幕范围####
四种通用尺寸：小、正常、 大 和超大。<br><br>
六种通用的密度：<br>
-  ldpi（低）~120dpi<br>
-  mdpi（中）~160dpi<br>
-  hdpi（高）~240dpi<br>
-  xhdpi（超高）~320dpi<br>
-  xxhdpi（超超高）~480dpi<br>
-  xxxhdpi（超超超高）~640dpi<br><br>
屏幕尺寸与屏幕密度对比：<br>
![图04][4]<br>
- 超大屏幕至少为 960dp x 720dp<br>
- 大屏幕至少为 640dp x 480dp<br>
- 正常屏幕至少为 470dp x 320dp<br>
- 小屏幕至少为 426dp x 320dp<br>
##二、解决方案-支持各种屏幕尺寸##
####1. 使用配置限定符####
![图05][5]<br>

####2.最佳做法####
1.	在 XML 布局文件中指定尺寸时使用 wrap_content、match_parent 或 dp 单位 。
2.	不要在应用代码中使用硬编码的像素值
3.	不要使用 AbsoluteLayout（已弃用）
4.	为不同屏幕密度提供替代位图可绘制对象



[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/01.png
[2]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/02.png
[3]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/03.png
[4]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/04.png
[5]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/05.jpg
[6]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/06.png
[7]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_screens_support/07.png