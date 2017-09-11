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

图片显示：加载合适尺寸的图片，比如显示缩略图的地方不要加载大图。
图片回收：使用完 bitmap，及时使用 Bitmap.recycle() 回收。
> 问题：Android不是自身具备垃圾回收机制吗？此处为何要手动回收。
Bitmap对象不是new生成的，而是通过BitmapFactory生产的。而且通过源码可发现是通过调用JNI生成Bitmap对象（nativeDecodeStream()等方法）。所以，加载bitmap到内存里包括两部分，Dalvik内存和Linux kernel内存。前者会被虚拟机自动回收。而后者必须通过recycle()方法，内部调用nativeRecycle()让linux kernel回收。

捕获OOM异常：程序中设定如果发生OOM的应急处理方式。
图片缓存：内存缓存、硬盘缓存等
图片压缩：直接使用ImageView显示Bitmap时会占很多资源，尤其当图片较大时容易发生OOM。可以使用BitMapFactory.Options对图片进行压缩。
图片像素：android默认颜色模式为ARGB_8888，显示质量最高，占用内存最大。若要求不高时可采用RGB_565等模式。图片大小：图片长度*宽度*单位像素所占据字节数
ARGB_4444：每个像素占用2byte内存
ARGB_8888：每个像素占用4byte内存 （默认）
RGB_565：每个像素占用2byte内存



计算 Bitmap 内存大小

我们知道 ARGB 指的是一种色彩模式，里面 A 代表 Alpha，R 表示 Red，G 表示 Green，B 表示 Blue。 所有的可见色都是由红绿蓝组成的，所以红绿蓝又称为三原色，每个原色都存储着所表示颜色的信息值,下表中对四种颜色模式的详细描述，以及每种色彩模式占用的字节数。

| 模式		| 描述													| 占用字节 |
| :------	| :--------------------------------						| :------ |
| ALPHA		| Alpha 由 8 位组成										| 1B	  |
| ARGB_4444	| 4 个 4 位组成 16 位，每个色彩元素站 4 位					| 2B	  |
| ARGB_8888	| 4 个 8 为组成 32 位，每个色彩元素站 8 位					| 4B	  |
| RGB_565	| R 为 5 位，G 为 6 位，B 为 5 位共 16 位，没有Alpha		| 2B	  |



- 对象引用类型

强引用，软引用，弱引用，虚引用

- 强引用（Strong Reference）:JVM宁愿抛出OOM，也不会让GC回收的对象 
- 软引用（Soft Reference） ：只有内存不足时，才会被GC回收。 
- 弱引用（weak Reference）：在GC时，一旦发现弱引用，立即回收 
- 虚引用（Phantom Reference）：任何时候都可以被GC回收，当垃圾回收器准备回收一个对象时，如果发现它还有虚引用，就会在回收对象的内存之前，把这个虚引用加入到与之关联的引用队列中。程序可以通过判断引用队列中是否存在该对象的虚引用，来了解这个对象是否将要被回收。可以用来作为GC回收Object的标志。 


- 对象池

对象池：如果某个对象在创建时，需要较大的资源开销，那么可以将其放入对象池，即将对象保存起来，下次需要时直接取出使用，而不用再次创建对象。当然，维护对象池也需要一定开销，故要衡量。
线程池：与对象池差不多，将线程对象放在池中供反复使用，减少反复创建线程的开销。

- 缓存

## 内存泄露相关优化

Java 内存泄漏指的是进程中某些对象（垃圾对象）已经没有使用价值了，但是它们却可以直接或间接地引用到 gc roots 导致无法被 GC 回收。 Dalvik VM 具备的 GC 机制会在内存占用过多时自动回收，严重时会造成内存溢出 OOM。

- 单例
- 静态变量
- Handler
- 匿名内部类
- 资源使用完未关闭

## 其他优化

- 常用数据结构优化
- 枚举
- View 复用
- 谨慎使用多进程
- 尽量使用系统资源

## Android Studio Monitor Memory

## Memory Analyzer Tool

## LeakCanary

## Allocation Traker

## ANR

## 参考资料

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

