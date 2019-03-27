# 图解 Android 系列（一）揭秘 Android 系统启动过程

当我们按下手机开机按键后，手机就会启动了。然后会看到 Logo，开机动画，最后会进入到手机桌面（Launcher），手机也就启动完成了。

我一直搞不明白，这个过程到底做了什么？为什么按一个按键，手机就启动了呢？

随着对 Android 的了解越来越多，直到阅读了源码，才逐渐解答了我的疑惑。如果你也有相同疑惑，请继续往下看，我将从源码的角度分析下 Android 系统启动的整个流程。

## 计算机是如何启动的？

智能手机相当于是精简版的计算机，我们先看看计算机是如何启动的？

首先熟悉一些概念，我们知道计算机的硬件包括：CPU、内存、硬盘、显卡、显示器、键盘、鼠标等其他输入输出设备。所有的软件（比如：操作系统）都是存放在硬盘上的，程序执行时需要将程序从硬盘上读取到内存中，然后加载到 CPU 中来运行的。

当我们按下开机键时，此时内存中什么都没有，因此需要借助某种方式，将操作系统加载到内存中，而完成这项任务的就是 BIOS。

## BIOS

> BIOS: Basic Input/Output System（基本输入输出系统），在 IBM PC 兼容系统上，是一种业界标准的固件接口（来自维基百科）。

BIOS 一般是主板芯片上的一个程序，计算机通电后，第一件事就是读取它。BIOS 程序启动后，首先会检查计算机硬件能否满足运行的基本条件，这个过程叫做「硬件自检」（Power-On Self-Test），缩写为 POST。

自检过程中如果硬件出现问题，主板会发出不同含义的[蜂鸣](https://en.wikipedia.org/wiki/Power-on_self-test#Original_IBM_POST_beep_codes)，启动将中止。 如果没有问题，屏幕就会显示出 CPU，内存，硬盘等信息。也就是我们按下开机按键后经常看到的，屏幕上快速滚动各种提示。

![硬件自检图](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/01.jpg)

硬件自检完成后，BIOS 会把控制权转交给下一阶段的启动程序。

这时 BIOS 需要知道，下一阶段的启动程序到底存放在哪一个设备当中。也就是说 BIOS 需要有一个外部存储设备的排序，排在前面的设备就是优先转交控制权的设备。 这种排序叫做启动排序，也就是我们平时进入 BIOS 界面（比如：按 F9/F10 等等，这里装过系统的小伙伴应该比较熟悉）时能看到的 Boot Sequence。

![启动顺序图](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/02.jpg)

如果我们没有进行特殊操作的话，那么 BIOS 就会按照这个启动顺序将控制权交给下一个存储设备。 我们在使用 U 盘或者光盘之类的安装系统时就是在这里将启动顺序改变了，将本来要移交给硬盘的控制权交给了 U 盘或者光盘。

## 主引导记录

BIOS 按照启动顺序，把控制权转交给排在第一位的储存设备。第一存储设备被激活后，计算机读取该设备的第一个扇区，也就是读取最前面的 512 个字节。 

> 这最前面的 512 个字节，就叫做[主引导记录](http://en.wikipedia.org/wiki/Master_boot_record)（Master boot record，缩写为 MBR）。

主引导记录 MBR 是位于磁盘最前边的一段引导代码。它负责磁盘操作系统对磁盘进行读写时分区合法性的判别、分区引导信息的定位，它由磁盘操作系统在对硬盘进行初始化时产生的。

硬盘的主引导记录 MBR 是不属于任何一个操作系统的，它先于所有的操作系统而被调入内存，并发挥作用，然后才将控制权交给主分区内的操作系统，并用主分区信息表来管理硬盘。

MBR 只有512个字节，放不了太多东西。 它的主要作用是，告诉计算机到硬盘的哪一个位置去找操作系统。 

主引导记录由三个部分组成：

- 第 1 - 446 字节：调用操作系统的机器码。
- 第 447 - 510 字节：分区表（Partition table）。
- 第 511 - 512 字节：主引导记录签名（0x55 和 0xAA）。

其中，第二部分「分区表」的作用，就是将硬盘分成若干个区。硬盘分区有很多好处，考虑到每个区可以安装不同的操作系统，「主引导记录」因此必须知道将控制权转交给哪个区。

分区表的长度只有 64 个字节，里面又分成四项，每项 16 个字节。所以，一个硬盘最多只能分四个一级分区，又叫做「主分区」。

四个主分区里面，只有一个是激活的。计算机会读取激活分区的第一个扇区，叫做[卷引导记录](http://en.wikipedia.org/wiki/Volume_Boot_Record)（Volume boot record，缩写为 VBR ）。卷引导记录的主要作用是，告诉计算机，操作系统在这个分区里的位置。

如果这 512 个字节的最后两个字节是 0x55 和 0xAA ，表明这个设备可以用于启动；如果不是，表明设备不能用于启动，控制权于是被转交给启动顺序中的下一个设备。

当计算机加载 MBR 后，计算机会从 MBR 中知道当前硬盘的文件格式、硬盘分区情况、系统盘存放位置等信息，然后控制权将被移交给了系统盘所在的分区。

如果硬盘上装有多个系统的话，在找到可用的 MBR 后，计算机从 MBR 中读取前面 446 字节的机器码之后，不再把控制权转交给某一个分区，而是运行事先安装的[启动管理器](http://en.wikipedia.org/wiki/Boot_loader#Modern_boot_loaders)（boot loader），由用户选择启动哪一个操作系统。

Windows 中是 Boot Manager。

![Windows Boot Manager](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/03.jpg)

Linux 环境中，目前最流行的启动管理器是 Grub。

![Linux Grub](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/04.jpg)

## 加载内核阶段

选择完操作系统后，控制权转交给操作系统，操作系统的内核首先被载入内存。

以 Linux 系统为例，先载入 `/boot` 目录下面的 kernel。 内核加载成功后，第一个运行的程序是 `/sbin/init`。 它根据配置文件（Debian 系统是 /etc/initab ）产生 init 进程。 这是 Linux 启动后的第一个用户进程，pid 进程编号为 1，其他进程都是它的后代。

然后，init 进程加载系统的各个模块，比如：窗口程序和网络程序，直至执行 `/bin/login` 程序，跳出登录界面，等待用户输入用户名和密码。

至此，计算机全部启动过程完成。

## Android 系统启动过程

了解了计算机的启动流程，我们再来看一下 Android 系统的启动过程。Android 系统是基于 Linux 内核的，所以启动过程与 Linux 系统有很多相似的地方。

由于 Android 属于嵌入式设备，并没有像计算机上那样的 BIOS 程序， 取而代之的是 Bootloader —— 系统启动加载器。 它类似于 BIOS，在系统加载前，用以初始化硬件设备，建立内存空间的映像图，为最终调用系统内核准备好环境。 

![Android Bootloader](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/05.jpg)

在 Android 里没有硬盘，而是 ROM，它类似于硬盘存放操作系统，用户程序等。 ROM 跟硬盘一样也会划分为不同的区域，用于放置不同的程序，在 Android 中主要划分为一下几个分区：

- /boot：存放引导程序，包括内核和内存操作程序。
- /system：相当于电脑 C 盘，存放 Android 系统及系统应用。
- /recovery：恢复分区，可以进入该分区进行系统恢复。
- /data：用户数据区，包含了用户的数据：联系人、短信、设置、用户安装的程序。
- /cache：安卓系统缓存区，保存系统最常访问的数据和应用程序。
- /misc：包含一些杂项内容，如系统设置和系统功能启用禁用设置。
- /sdcard：用户自己的存储区，可以存放照片，音乐，视频等文件。

## Bootloader

那么 Bootloader 是如何被加载的呢？

与计算机启动过程类似，当按下电源按键后，引导芯片代码开始从预定义的地方（固化在 ROM 中的预设代码）开始执行，芯片上的 ROM 会寻找 Bootloader 代码，并加载到内存（RAM）中。

接着 Bootloader 开始执行，Bootloader 会读取 ROM 找到操作系统并将 Linux 内核加载到 RAM 中。

当 Linux 内核启动后会初始化各种软硬件环境，加载驱动程序，挂载根文件系统，Linux 内核加载的最后阶段会启动并执行第一个用户空间进程 init 进程。


## Linux 内核

Android 系统本质上就是一个基于 Linux 内核的操作系统，与 Ubuntu Linux、Fedora Linux 类似，我们要了解 Android 系统，必定先要了解一些 Linux 内核的知识。

Linux 内核的东西特别多，本文也不可能全部讲完，本文主要介绍 Android 系统启动流程，所以这里主要介绍一些内核启动相关的知识。

Linux 内核启动过程主要涉及 3 个特殊的进程，swapper 进程（又称为 idle 进程，PID = 0）， init 进程（PID = 1）和 kthreadd 进程（PID = 2），这三个进程是内核的基础。

- idle 进程是 Linux 系统第一个进程，是 init 进程和 kthreadd 进程的父进程。
- init 进程是 Linux 系统第一个用户进程，是 Android 系统应用程序的始祖，我们的 app 都是直接或间接以它为父进程。
- kthreadd 进程是 Linux 系统内核管家，所有的内核线程都是直接或间接以它为父进程。

![进程关系图](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/06.png)

## idle 进程

很多文章讲 Android 都从 init 进程讲起，它的进程号是 1，既然进程号是 1，那么有没有进程号是 0 的进程呢？其实是有的。

这个进程名字叫 `init_task`，后期会退化为「idle」，它是 Linux 系统的第一个进程（init 进程是第一个用户进程），也是唯一一个没有通过 fork 或者 kernel_thread 产生的进程，它在完成初始化操作后，主要负责进程调度、交换。

idle 进程是 Linux 系统的第一个进程，进程号是 0，在完成系统环境初始化工作之后，开启了两个重要的进程，init 进程和 kthreadd 进程，执行完创建工作之后，开启一个无限循环，负责进程的调度。

## kthreadd 进程

kthreadd 进程由 idle 通过 kernel_thread 创建，并始终运行在内核空间, 负责所有内核线程的调度和管理，所有的内核线程都是直接或者间接的以 kthreadd为 父进程。

## init 进程

init 进程启动分为前后两部分，前一部分是在内核启动的，主要是完成创建和内核初始化工作，内容都是跟 Linux 内核相关的；后一部分是在用户空间启动的，主要完成 Android 系统的初始化工作。

Android 系统一般会在根目录下放一个 init 的可执行文件，也就是说 Linux 系统的 init 进程在内核初始化完成后，就直接执行 init 这个文件，这个文件的源代码在 `/system/core/init/init.cpp`。

介绍到这里，我们来看下目前 Android 系统做了哪些工作，如下图：

![init 进程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/framework/01_system_start/07.png)

## 总结

本文介绍的内容相对比较简单，主要是想带大家了解了一下计算机启动的流程，了解一下 Android 系统从按下电源键到 init 进程开始启动的过程，为以后的章节做下准备。

接下来的章节会涉及到 Android 系统源码，建议大家准备一下系统源码，对着源码学习会更加印象深刻，事半功倍。

> 源码基于：Android Oreo（8.0）

### 关于源码下载

可以参考下面方式下载 Android 源码：

- [Windows 环境下载 Android 源码](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/android/framework/Android-Windows%E7%8E%AF%E5%A2%83%E4%B8%8B%E8%BD%BD%E6%BA%90%E7%A0%81.md)
- [官方文档（需要梯子） - macOS、Linux 环境下载 Android 源码](https://source.android.com/source/initializing.html)

也可以在线查看源码：

- [Android XRef](http://androidxref.com)
- [Android OS](https://www.androidos.net.cn/sourcecode)

### 源码查看工具

源码查看工具推荐使用 [Visual Studio Code](https://code.visualstudio.com) 我用的就是这个，也可以使用 [Source Insight](https://www.sourceinsight.com) 不过是要付费的，并且只有 Windows 平台，大家根据个人喜好自行选择就好。


## 参考资料

- [计算机是如何启动的？](http://www.ruanyifeng.com/blog/2013/02/booting.html)
- [按下电源键之后，电脑又默默干了很多事](http://daily.zhihu.com/story/8803295)
- [Android系统启动-概述](http://gityuan.com/2016/02/01/android-booting)

