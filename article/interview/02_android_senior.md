# Android 高级学习指南

## 思维导图

![Android 基础](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/xmind/Android高级.png)

## 相关原理

### 常见 IPC 方式

- Binder 机制

- AIDL 的使用

### Handler 机制

- ThreadLocal 原理
- AsyncTask 原理

### ListView 工作原理

- 阅读源码
- 熟悉常见优化

### RecyclerView 工作原理

- 阅读源码
- 自定义 LayoutManager

### Animation 工作原理

### Activity 难点

- setResult() 和 finish() 的顺序关系？

- onSaveInstanceState() 和 onRestoreInstanceState()

- onNewIntent() 和 onConfigurationChanged()

### Service 难点

- startService 与 bindService 的区别？

- Service 中 onStartCommand 返回值的作用？

- bindService后，ServiceConnection 里面的回调方法运行在哪个线程？它们的调用时机分别是什么？

- Service 的 onCreate 运行在哪个线程？

### ContentProvider 难点

- ContentProvider 的生命周期

- ContentProvider 的 onCreate 和 CRUD 运行在哪个线程？它们是线程安全的吗？

- ContentProvider 的内部存储只能是 SQLite 吗？

### RemoteViews

- 熟悉 RemoteViews 的使用，并了解其运行原理

### Material Design（材料设计）

- 熟练使用材料设计的控件及布局

## 自定义 View

### View 的绘制流程

- onMeasure
- onLayout
- onDraw
- invalidate() 与 postInvalidate()

### 事件分发机制

- onDispatchTouchEvent
- onInterceptTouchEvent
- onTouchEvent
- 事件冲突处理

### 贝塞尔曲线、粒子效果

## 性能优化

- 布局优化：ViewStub、include、merge 的使用，它们的区别？

- 过度渲染的处理

- ANR 的处理

- 监控：埋点、Crash 上报

## 内存优化

- OOM 的处理

- 内存泄露的处理

- 内存检测

- 内存分析

- Bitmap 的优化：超大图的加载原理

## 网络优化

- API 优化

- 流量优化

- 弱网优化

## 电量优化

- WakeLock 机制

- JobScheduler 机制

## 第三方开源库

- OKHttp 原理

- Retrofit 原理

- RxJava 原理

- Glide 原理

- 加载原理
- 三级缓存
- LRU 算法

- Dagger2 原理

- ButterKnife 原理

- EventBus 原理

- RxJava 原理

## 混合开发

- WebView

- React Native

- Flutter

## NDK 开发

熟悉调用 JNI 方法的方式，熟悉如何回调 Java 方法。

## 安全

熟悉各种发编译，二次打包工具，了解 smali。

## 动态化

阅读 VirtualAPK、Tinker 的源码，熟悉常见的热修复和插件化原理。

## Gradle

### Groovy 语法

### Gradle 插件开发基础

## 设计模式与架构

- 熟悉 6 大基本原则

- MVC、MVP、MVVM

- 组件化

- Jetpack

## 其他问题

- Activity、Window，View 之间的关系？
- 子线程访问 UI 却不报错的原因？
- 主线程的消息循环是一个死循环，为何不会卡死？
- Binder、IBinder、IInterface 的关系？

## Java 知识

- String 常量池

- 类型转换原理

- ArrayList 实现原理

- HashMap 实现原理
- 常见锁（乐观锁、悲观锁），死锁解决方法
- synchronized 关键字
- volatile 关键字
- 常见 IO（AIO，BIO，NIO）
- 常见并发框架
- 了解类加载机制
- 了解垃圾回收机制

## 总结

以上就是 `Android 高级工程师` 需要掌握的知识点，高级工程师需要掌握的知识点还是比较多的。如果说初级工程师是打捞基础的过程，那么高级工程师就是一个沉淀技术进阶的过程。

高级工程师一般是指 3 - 5 年工作经验，如果学习能力比较强 3 工作经验足够进阶到高级工程师的。应聘高级工程师薪资一般在 15k - 25k 左右，这里的薪资范围一般会根据是否有亮点上下浮动。

高级工程师对 Android 的理解，不应该还停留在对 API 的使用。初级工程师可以说是对 API 熟悉的过程，高级工程师更应该注重的是 API 内部的原理，知其然而知其所以然。

这个阶段阅读源码是最好的进阶方式，当然阅读源码很容易陷入细节无法自拔。这里推荐看一下高质量的博客和一些进阶书籍，根据博客和书的思路有针对性的看源码是比较推荐的方式。

Android 方面推荐看下：

- 任玉刚的《Android 开发艺术探索》
- 刘望舒的《Android 进阶揭秘》
- 《Android 系统源代码情景分析》
- 《深入理解 Android》系列
- 《深入理解 Android 热修复技术原理》

由于 Android 与 Java 有很大的渊源，所以 Java 知识对高级工程师来说也是很重要的。这个阶段需要对 Java 有更深入的理解，还要对 Java 虚拟机有一定的研究。

Java 方面推荐看下：

- 《Java 并发编程的艺术》
- 《Java 并发编程实战》
- 《Java 多线程编程核心技术》
- 《深入理解 Java 虚拟机》

如果想让自己更加有亮点，推荐注重下面几个方面：

- 创建一个 GitHub 账号，多输出一些高质量的开源项目
- 拥有一个持续输出的技术博客
- 阅读源码

做技术开发的前 5 年是努力学习知识和技术沉淀的一个过程。有些人天赋比较好，进阶很快；有些人天赋虽然不好，但很勤奋，进阶也能很块。一定要让自己的工作经验与技术能力成正比，技术能力永远跟薪资成正比，能力越强薪资越高。

如果以上知识点对你来说仍然太简单了，那么请接受我称你为「大佬」。敬请期待下一期 `Android 资深/专家工程师` 的学习指南，视频和书籍对资深/专家级别的工程师来说帮助不大了，这里不做推荐了。