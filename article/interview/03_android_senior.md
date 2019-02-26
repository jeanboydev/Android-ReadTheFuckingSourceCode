# Android 资深（专家）学习指南

## 思维导图

![Android 资深(专家) 思维导图](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/xmind/Android%E8%B5%84%E6%B7%B1.png)

## 系统启动过程

这一部分是 Android 系统从按下电源键开始，然后到展示开机界面，再到展示桌面之前的一个过程。了解下面相关进程的工作流程，会对 Android 系统有一个整体的概念，是一个从 0 到 1 的过程，对深入研究 Android 系统内部机制有很大帮助。

- init 进程

  了解 init 进程创建与启动的流程。

- Zygote 进程

  了解 Zygote 进程创建的流程，以及 fork 的过程。

- system_server 进程

  了解 system_server 进程启动流程，工作流程。

- ServiceManager

  了解 ServiceManager 的启动流程，以及 ServiceManager 在系统中的作用。

## 内核技术

这一部分是计算机操作系统相关的原理，也是计算机相关专业的一门必修课程，推荐学习下相关知识。

- CPU 调度
- 进程管理
- 文件系统
- 内存管理

## 通信方式

- Binder

  Binder 是 Android 系统中特有的一种 IPC 通信方式，建议阅读 Binder 相关的源码，与深入越好，理解 Binder 工作的原理，了解服务的注册、获取、死亡通知的流程。

- Handler

  Handler 是 Android 系统中线程间通信的方式，已经在 Android 高级工程师部分说过了。这里一定要阅读下源码了解内部的运行机制。

- Socket

  Socket 是系统中常见的一种 IPC 通信方式，Socket 的应用范围很广，在进程间通信、网络通信都会用到，建议深入了解下。

- Pipe

  Pipe（管道）是 Linux 系统中常见的一种 IPC 通信方式，建议深入了解下工作原理。

- signal 

  signal（信号量）是系统中常见的一种 IPC 通信方式，建议深入了解下工作原理。

## 核心服务

- Activity、Service、Broadcast、ContentProvider

  了解四大组件启动流程，理解生命周期回调过程，了解工作原理。

- ActivityManagerService（AMS）

  理解 ActivityManagerService 工作流程，以及与 Activity 工作的流程。

- WindowManagerService（WMS）

  理解 WindowManagerService 工作流程，以及与 ActivityManagerService 和 Activity 工作的过程。

- View、Window、Surface

  理解 Activity、Window、View 之间的关系，了解 View 渲染机制。

- Surface、SurfaceFlinger

  理解 View 与 Surface 之间的关系，了解 SurfaceFlinger 工作流程，理解 View 渲染的过程。

- PackageManagerService（PKMS）

  理解 PackageManagerService 工作流程，了解 Apk 安装与卸载过程。

- PowerManagerService（PMS）

  理解 PackageManagerService 工作流程，了解屏幕唤醒、灭屏的过程，并理解 WeakLock 机制。

- InputManagerService（IMS）

  理解 InputManagerService 工作流程，理解事件的创建流程、事件分发机制，ANR 触发原理。

- AudioFlinger

  理解 AudioFlinger 工作流程。

- AssertManager

  理解 Apk 安装包中资源管理的过程。

## 异常处理

可以从源码的角度分析异常产生的原因，定位异常，以及处理。

- Watchdog
- ANR
- Java Crash
- Native Crash
- 卡顿

## Java 虚拟机

- 内存模型

  了解 JVM 内存模型，包括堆、栈、方法区、运行时常量池等。

- 类加载机制

  了解类加载时机，类加载的过程，理解类加载器双亲委派模型。

- 垃圾回收机制

  了解垃圾回收的原因，理解对象生命周期，了解垃圾回收算法。

## 动态化

- Android Gradle Plugin

  通过阅读 Android Gradle Plugin 源码，理解 Gradle 构建项目的过程，了解插件开发过程。

-  VirtualAPK、Tinker

  通过阅读 VirtualAPK 源码，理解热修复、插件化的原理。

- Hook 技术

## 设计模式与架构

- 熟悉六大 OOD 设计原则
- 熟悉常见的设计模式，可以熟练的运用在项目中
- 理解 MVC、MVP、MVVM 的思想以及区别
- 项目架构设计与重构
- 项目组件化设计与开发

## 软技能

- 拓展技术广度，其他领域的技术学习
- 团队管理和指导新人

## 总结

以上就是 `Android 资深（专家）工程师` 的基本知识点，如果在高级工程师部分基础很牢，进阶到资深（专家）是很容易的。这个级别的知识点不仅仅需要对 API 熟练应用，更重要的是对内部的运行机制的深入理解。

我们可以发现很多的知识点都是对 Android 系统源码的阅读来获取的，阅读源码是一个很痛苦的过程，也是必须经历的一个过程。

在阅读源码的时候建议多注重对整体流程的把握，而不是深入细节不能自拔。毕竟我们主要工作还是开发 App，阅读源码是为了更好的理解内部运行机制。

专家除了具有扎实的技术深度以外，还有一定的技术广度，以及不错的架构设计能力。除了技术，软技能也是很重要的部分。比如如何管理团队，带带新人，写写 PPT，吹 NB 啥的。

已经达到了资深（专家）的开发者，以后的学习路线跟自己的职业规划有很大关系。这个级别技术也不再那么重要，毕竟都是专家了，大家都很 NB，怎么还能让人手把手教呢？！

以下方面大家可以参考下：

- 维护一个公众号，增加业内影响力
- 考虑出一本书，增加业内知名度
- 开源一个 NB 的项目，为开源贡献一份力量
- 转型做产品或者管理
- 换一个领域继续深入研究

一般达到资深（专家）的开发者需要 3 - 5 年左右，本科毕业的学生年龄一般在 22 周岁左右，那么达到资深（专家）最快也得 25 周岁了。这里我们会遇到一个职业上的危机 —— 30 岁危机。

随着年龄的越来越大是继续做技术？还是转型做管理呢？Android 也没啥可研究的了，还是换其他领域呢？这是一个值得思考的问题，我还没有这个经历（岁数还没到）不敢妄下定论，哈哈。

这里分享下网上的一份关于各大厂 Android 级别的薪资参考图（如有侵权，请联系我删除）。

![大厂薪资参考，如有侵权立删！](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/interview/01.jpeg)

我看到网上很多消息都说今年互联网寒冬什么什么的，其实每年都会说寒冬。互联网总共也就发展了十几年，从 2000 年初的诺基亚到现在的智能手机时代，也就十几年的时间。谁有会预料的下一个十年之后会是什么样的呢？

由于前几年大量培训出来的开发者（这里只是说下客观事实，没有贬低的意思），整个市场涌入大量的初级、中级开发者，所以对于新人来说的确不好找工作了，因为竞争的人多了。

> 自己没能力就说没能力，怎么你到哪儿，哪都大环境不好，你是破坏大环境的人啊？—— 赵本山

作为开发者我们最好的准备就是知识的储备，如果我们努力学习达到了高级甚至更高，目前需求量还是很大的。目前我了解到的 Android 领域专家级别的工程师也没有多少，大家可以留意统计一下。

关于 Android 进阶的学习指南就已经完结了，欢迎大家继续关注，其他方面的技术分享，及个人感悟。