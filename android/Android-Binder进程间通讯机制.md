# Android-Binder进程间通讯机制 #

## 概述 ##
最近在学习Binder机制，在网上查阅了大量的资料，也看了老罗的Binder系列的博客和阿拉神农的深入理解Binder系列的博客，都是从底层开始讲的，全是C代码，虽然之前学过C和C++，然而各种函数之间花式跳转，看的我都怀疑人生。毫不夸张的讲每看一边都是新的内容，跟没看过一样。后来又看到了Gityuan的博客看到了一些图解仿佛发现了新大陆。 

下面就以图解的方式介绍下Binder机制，相信你看这篇文章，一定有所收获。


## 什么是Binder？ ##

Binder是Android系统中进程间通讯（IPC）的一种方式，也是Android系统中最重要的特性之一。Android中的四大组件Activity，Service，Broadcast，ContentProvider，不同的App等都运行在不同的进程中，它是这些进程间通讯的桥梁。正如其名“粘合剂”一样，它把系统中各个组件粘合到了一起，是各个组件的桥梁。

理解Binder对于理解整个Android系统有着非常重要的作用，如果对Binder不了解，就很难对Android系统机制有更深入的理解。


## 1. Binder架构 ##

![图1][1]

- Binder 通信采用 C/S 架构，从组件视角来说，包含 Client、 Server、 ServiceManager 以及 Binder 驱动，其中 ServiceManager 用于管理系统中的各种服务。
- Binder 在 framework 层进行了封装，通过JNI技术调用 Native（C/C++）层的 Binder 架构。 
- Binder 在 Native 层以 ioctl 的方式与 Binder 驱动通讯。

## 2. Binder驱动 ##

![图2][2]

### 用户空间/内核空间 ###
详细解释可以参考 [Kernel Space Definition](http://www.linfo.org/kernel_space.html)； 简单理解如下：

Kernel space 是 Linux 内核的运行空间，User space 是用户程序的运行空间。 为了安全，它们是隔离的，即使用户的程序崩溃了，内核也不受影响。

Kernel space 可以执行任意命令，调用系统的一切资源； User space 只能执行简单的运算，不能直接调用系统资源，必须通过系统接口（又称 system call），才能向内核发出指令。

### 系统调用/内核态/用户态 ###
虽然从逻辑上抽离出用户空间和内核空间；但是不可避免的的是，总有那么一些用户空间需要访问内核的资源；比如应用程序访问文件，网络是很常见的事情，怎么办呢？

> Kernel space can be accessed by user processes only through the use of system calls.

用户空间访问内核空间的唯一方式就是系统调用；通过这个统一入口接口，所有的资源访问都是在内核的控制下执行，以免导致对用户程序对系统资源的越权访问，从而保障了系统的安全和稳定。用户软件良莠不齐，要是它们乱搞把系统玩坏了怎么办？因此对于某些特权操作必须交给安全可靠的内核来执行。

当一个任务（进程）执行系统调用而陷入内核代码中执行时，我们就称进程处于内核运行态（或简称为内核态）此时处理器处于特权级最高的（0级）内核代码中执行。当进程在执行用户自己的代码时，则称其处于用户运行态（用户态）。即此时处理器在特权级最低的（3级）用户代码中运行。处理器在特权等级高的时候才能执行那些特权CPU指令。

### 内核模块/驱动 ###
通过系统调用，用户空间可以访问内核空间，那么如果一个用户空间想与另外一个用户空间进行通信怎么办呢？很自然想到的是让操作系统内核添加支持；传统的Linux通信机制，比如Socket，管道等都是内核支持的；但是Binder并不是Linux内核的一部分，它是怎么做到访问内核空间的呢？Linux的动态可加载内核模块（Loadable Kernel Module，LKM）机制解决了这个问题；模块是具有独立功能的程序，它可以被单独编译，但不能独立运行。它在运行时被链接到内核作为内核的一部分在内核空间运行。这样，Android系统可以通过添加一个内核模块运行在内核空间，用户进程之间的通过这个模块作为桥梁，就可以完成通信了。

在Android系统中，这个运行在内核空间的，负责各个用户进程通过Binder通信的内核模块叫做Binder驱动;

> 驱动程序一般指的是设备驱动程序（Device Driver），是一种可以使计算机和设备通信的特殊程序。相当于硬件的接口，操作系统只有通过这个接口，才能控制硬件设备的工作；

驱动就是操作硬件的接口，为了支持Binder通信过程，Binder使用了一种“硬件”，因此这个模块被称之为驱动。


熟悉了上面这些概念，我们再来看下上面的图，用户空间中binder_open(), binder_mmap(), binder_ioctl()这些方法通过 system call 来调用内核空间 Binder 驱动中的方法。内核空间与用户空间共享内存通过 copy_from_user(), copy_to_user() 内核方法来完成用户空间与内核空间内存的数据传输。 Binder驱动中有一个 binder_procs 链表保存了服务端的进程信息。

## 3. Binder进程与线程 ##

![图3][3]

对于底层Binder驱动，通过binder_procs链表记录所有创建的binder_proc结构体，binder驱动层的每一个binder_proc结构体都与用户空间的一个用于binder通信的进程一一对应，且每个进程有且只有一个ProcessState对象，这是通过单例模式来保证的。在每个进程中可以有很多个线程，每个线程对应一个IPCThreadState对象，IPCThreadState对象也是单例模式，即一个线程对应一个IPCThreadState对象，在Binder驱动层也有与之相对应的结构，那就是Binder_thread结构体。在binder_proc结构体中通过成员变量rb_root threads，来记录当前进程内所有的binder_thread。

Binder线程池：每个Server进程在启动时会创建一个binder线程池，并向其中注册一个Binder线程；之后Server进程也可以向binder线程池注册新的线程，或者Binder驱动在探测到没有空闲binder线程时会主动向Server进程注册新的的binder线程。对于一个Server进程有一个最大Binder线程数限制，默认为16个binder线程，例如Android的system_server进程就存在16个线程。对于所有Client端进程的binder请求都是交由Server端进程的binder线程来处理的。


## 总结 ##


[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/binder_main.jpg
[2]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/binder_device.jpg
[3]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/process_thread.jpg
[4]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/service_manager_start.jpg
[5]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/service_manager_add.jpg
[6]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/service_manager_get.jpg
[7]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_binder/binder_one_main.jpg