# Android-Handler消息机制 #
<br>
## 概述 ##
Android 的消息机制主要是指 Handler 的运行机制以及 Handler 所附带的 MessageQueue 和 Looper 的工作过程。 Handler 的主要作用是将某个任务切换到 Handler 所在的线程中去执行。
## Handler机制 ##
Looper
> **每个线程中最多只能有一个 Looper 对象**，由 Looper 来管理此线程里的 MessageQueue (消息队列)。
> 
> 可以通过 **Looper.myLooper()** 获取当前线程的 Looper 实例，通过 **Looper.getMainLooper()** 获取主（UI）线程的 Looper 实例。
> 
> Lopper会以无限循环的形式去查找是否有新消息，如果有就处理消息，否则就一直等待着。


Handler
> 你可以构造 Handler 对象来与 Looper 沟通，通过 **push** 发送新消息到 MessageQueue 里；或者通过 **handleMessage** 接收 Looper 从 MessageQueue 取出来消息。

MessageQueue
> MessageQueue是一个消息队列，内部存储了一组消息，以队列的形式对外提供插入和
删除的工作，内部采用单链表的数据结构来存储消息列表。

ActivityThread
> 我们经常提到的主线程，也叫UI线程，它就是ActivityThread，主线程启动会**默认初始化一个 Looper 并创建 Handler**。
> 
> **一个线程中只有一个 Looper 实例，一个 MessageQueue 实例，可以有多个 Handler 实例。**

ThreadLocal
> 一个线程内部的数据存储类，通过它可以在指定线程中存储数据，数据存储后，只有在指定线程中可以获取到存储的数据，对于其他线程来说无法获得数据。
> 
> 对于 Handler 来说，它需要获取当前线程的 Looper ,而 Looper 的作用于就是线程并且不同的线程具有不同的 Looper ，通过 ThreadLocal 可以轻松实现线程中的存取。

