#Android-IPC多进程 #

## 概述 ##
IPC 即 Inter-Process Communication，含义为进程间通信或者跨进程通信，是指两个进程之间进行数据交换的过程。

线程是 CPU 调度的最小单元，是一种有限的系统资源。进程一般指一个执行单元，在PC和移动设备上是指一个程序或者应用。进程与线程是包含与被包含的关系。一个进程可以包含多个线程。最简单的情况下一个进程只有一个线程，即主线程（例如 Android 的 UI 线程）。

任何操作系统都需要有相应的IPC机制。在Android中，IPC的使用场景大概有以下：

1. 有些模块由于特殊原因需要运行在单独的进程中。
2. 通过多进程来获取多份内存空间。
3. 当前应用需要向其他应用获取数据。

## 1. 开启多进程模式 ##

给四大组件在Manifest中指定 android:process 属性。这个属性的值就是进程名。
```Java
<service
    android:name=".service.RemoteService"
    android:process=":remote">
</service>
```

> tips：使用 adb shell ps 或 adb shell ps|grep 包名 查看当前所存在的进程信息。

## 2. 多线程模式的运行机制 ##

Android 为每个进程都分配了一个独立的虚拟机，不同虚拟机在内存分配上有不同的地址空间，导致不同的虚拟机访问同一个类的对象会产生多份副本。例如不同进程的 Activity 对静态变量的修改，对其他进程不会造成任何影响。所有运行在不同进程的四大组件，只要它们之间需要通过内存在共享数据，都会共享失败。四大组件之间不可能不通过中间层来共享数据。

多进程会带来以下问题：
1. 静态成员和单例模式完全失效。
2. 线程同步锁机制完全失效。这两点都是因为不同进程不在同一个内存空间下，锁的对象也不是同一个对象。
3. SharedPreferences的可靠性下降。SharedPreferences底层是 通过读/写XML文件实现的，并发读/写会导致一定几率的数据丢失。
4. Application会多次创建。


由于系统创建新的进程的同时分配独立虚拟机，其实这就是启动一个应用的过程。在多进程模式中，不同进程的组件拥有独立的虚拟机、Application以及内存空间。实现跨进程的方式有很多：
1. Intent传递数据。
2. 共享文件和SharedPreferences。
3. 基于Binder的Messenger和AIDL。
4. Socket。


## 3. Binder ##
Android 中进程间通讯的核心就是 Binder 机制，强烈建议了解一下 Binder 机制。

[Android Binder 进程间通讯](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Binder进程间通讯.md)

## 4. Android 中的 IPC 方式 ##

主要有以下方式：
1. Intent 中附加 extras 来传递消息
2. 共享文件
3. Binder 方式
4. 四大组件之一的 ContentProvider
5. Socket


### 1. 使用Bundle ###

四大组件中的三大组件（Activity、Service、Receiver）都支持在Intent中传递 Bundle 数据。Bundle实现了Parcelable接口，**当我们在一个进程中启动了另一个进程的Activity、Service、Receiver，可以再Bundle中附加我们需要传输给远程进程的消息并通过Intent发送出去。被传输的数据必须能够被序列化。

### 2. 使用文件共享 ###
一些概念：
1. 两个进程通过读写同一个文件来交换数据。还可以通过 ObjectOutputStream / ObjectInputStream 序列化一个对象到文件中，或者在另一个进程从文件中反序列这个对象。

	> 注意：反序列化得到的对象只是内容上和序列化之前的对象一样，本质是两个对象。
2. 文件并发读写会导致读出的对象可能不是最新的，并发写的话那就更严重了。所以文件共享方式适合对数据同步要求不高的进程之间进行通信，并且要妥善处理并发读写问题。
3. SharedPreferences 底层实现采用XML文件来存储键值对。系统对它的读/写有一定的缓存策略，即在内存中会有一份 SharedPreferences 文件的缓存，因此在多进程模式下，系统对它的读/写变得不可靠，面对高并发读/写时 SharedPreferences 有很大几率丢失数据，因此不建议在IPC中使用 SharedPreferences 。

### 3. 使用Messenger ###

Messenger可以在不同进程间传递Message对象。是一种轻量级的IPC方案，底层实现是AIDL。

具体使用时，分为服务端和客户端：

1. 服务端：创建一个Service来处理客户端请求，同时创建一个Handler并通过它来创建一个Messenger，然后再Service的onBind中返回Messenger对象底层的Binder即可。
	```Java
	private final Messenger mMessenger = new Messenger (new xxxHandler());
	```

2. 客户端：绑定服务端的Sevice，利用服务端返回的IBinder对象来创建一个Messenger，通过这个Messenger就可以向服务端发送消息了，消息类型是 Message 。如果需要服务端响应，则需要创建一个Handler并通过它来创建一个Messenger（和服务端一样），并通过 Message 的 replyTo 参数传递给服务端。服务端通过Message的 replyTo 参数就可以回应客户端了。
3. 总而言之，就是客户端和服务端 拿到对方的Messenger来发送 Message 。只不过客户端通过 bindService 而服务端通过 message.replyTo 来获得对方的Messenger。
4. Messenger中有一个 Hanlder 以串行的方式处理队列中的消息。不存在并发执行，因此我们不用考虑线程同步的问题。

### 4. 使用AIDL ###

如果有大量的并发请求，使用Messenger就不太适合，同时如果需要跨进程调用服务端的方法，Messenger就无法做到了。这时我们可以使用AIDL。

流程如下：

1. 服务端需要创建Service来监听客户端请求，然后创建一个AIDL文件，将暴露给客户端的接口在AIDL文件中声明，最后在Service中实现这个AIDL接口即可。
2. 客户端首先绑定服务端的Service，绑定成功后，将服务端返回的Binder对象转成AIDL接口所属的类型，接着就可以调用AIDL中的方法了。

注意事项：
1. AIDL支持的数据类型：
- 基本数据类型、String、CharSequence
- List：只支持ArrayList，里面的每个元素必须被AIDL支持
- Map：只支持HashMap，里面的每个元素必须被AIDL支持
- Parcelable
- 所有的AIDL接口本身也可以在AIDL文件中使用
2. 自定义的Parcelable对象和AIDL对象，不管它们与当前的AIDL文件是否位于同一个包，都必须显式import进来。
3. 如果AIDL文件中使用了自定义的Parcelable对象，就必须新建一个和它同名的AIDL文件，并在其中声明它为Parcelable类型。
	```Java
	package com.ryg.chapter_2.aidl;
	parcelable Book;
	```
4. AIDL接口中的参数除了基本类型以外都必须表明方向in/out。AIDL接口文件中只支持方法，不支持声明静态常量。建议把所有和AIDL相关的类和文件放在同一个包中，方便管理。
	```Java
	void addBook(in Book book);
	```
5. AIDL方法是在服务端的Binder线程池中执行的，因此当多个客户端同时连接时，管理数据的集合直接采用 CopyOnWriteArrayList 来进行自动线程同步。类似的还有 ConcurrentHashMap 。
6. 因为客户端的 listener 和服务端的 listener 不是同一个对象，所以 RecmoteCallbackList 是系统专门提供用于删除跨进程 listener 的接口，支持管理任意的 AIDL 接口，因为所有 AIDL 接口都继承自 IInterface 接口。
	```Java
	public class RemoteCallbackList<E extends IInterface>
	```
它内部通过一个Map接口来保存所有的 AIDL 回调，这个Map的key是 IBinder 类型，value是 Callback 类型。当客户端解除注册时，遍历服务端所有listener，找到和客户端 listener 具有相同 Binder 对象的服务端 listenr 并把它删掉。
7. 客户端 RPC 的时候线程会被挂起，由于被调用的方法运行在服务端的 Binder 线程池中，可能很耗时，不能在主线程中去调用服务端的方法。


### 5. 使用ContentProvider ###

1. ContentProvider 是四大组件之一，其底层实现和 Messenger 一样是 Binder。ContentProvider 天生就是用来进程间通信，只需要实现一个自定义或者系统预设置的 ContentProvider，通过 ContentResolver 的 query、update、insert 和 delete 方法即可。
2. 创建 ContentProvider，只需继承 ContentProvider 实现 onCreate 、 query 、 update 、 insert 、 getType 六个抽象方法即可。除了 onCreate 由系统回调并运行在主线程，其他五个方法都由外界调用并运行在Binder线程池中。

### 6. 使用Socket ###
Socket可以实现计算机网络中的两个进程间的通信，当然也可以在本地实现进程间的通信。服务端 Service 监听本地端口，客户端连接指定的端口，建立连接成功后，拿到 Socket 对象就可以向服务端发送消息或者接受服务端发送的消息。

## 5. 具体实现 ##
参考代码：

[https://github.com/jeanboydev/Android-AIDLTest](https://github.com/jeanboydev/Android-AIDLTest)