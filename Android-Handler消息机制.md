# Android-Handler消息机制 #
<br>
## 概述 ##
Android 的消息机制主要是指 Handler 的运行机制以及 Handler 所附带的 MessageQueue 和 Looper 的工作过程。 Handler 的主要作用是将某个任务切换到 Handler 所在的线程中去执行。
## Handler机制 ##

Handler工作流程

![图1][1]

Looper
> **每个线程中最多只能有一个 Looper 对象**，由 Looper 来管理此线程里的 MessageQueue (消息队列)。
> 
> 可以通过 **Looper.myLooper()** 获取当前线程的 Looper 实例，通过 **Looper.getMainLooper()** 获取主（UI）线程的 Looper 实例。
> 
> Lopper 会以无限循环的形式去查找是否有新消息，如果有就处理消息，否则就一直等待着。


Handler
> 你可以构造 Handler 对象来与 Looper 沟通，通过 **push** 发送新消息到 MessageQueue 里；或者通过 **handleMessage** 接收 Looper 从 MessageQueue 取出来消息。

MessageQueue
> MessageQueue是一个消息队列，内部存储了一组消息，以队列的形式对外提供插入和
删除的工作，内部采用单链表的数据结构来存储消息列表。

ActivityThread
> 我们经常提到的主线程，也叫UI线程，它就是 ActivityThread，主线程启动会**默认初始化一个 Looper 并创建 Handler**。
> 
> **一个线程中只有一个 Looper 实例，一个 MessageQueue 实例，可以有多个 Handler 实例。**

ThreadLocal
> 一个线程内部的数据存储类，通过它可以在指定线程中存储数据，数据存储后，只有在指定线程中可以获取到存储的数据，对于其他线程来说无法获得数据。
> 
> 对于 Handler 来说，它需要获取当前线程的 Looper ,而 Looper 的作用于就是线程并且不同的线程具有不同的 Looper ，通过 ThreadLocal 可以轻松实现线程中的存取。
> 
> ThreadLocal原理：不同线程访问同一个ThreadLoacl的get方法，ThreadLocal的get方法会从各自的线程中取出一个数组，然后再从数组中根据当前ThreadLocal的索引去查找对应的Value值。

## 源码分析 ##
通过上面分析我们知道使用 Handler 之前必须先调用 **Looper.prepare();** 进行初始化，我们先看下 Looper 的源码。


#### 1. Looper 源码分析 ####
Looper 源码最上面的注释里有如下使用示例，可以清晰的看出 Looper 的使用方法。

```Java
class LooperThread extends Thread {
     public Handler mHandler;
     public void run() {
         Looper.prepare();//先初始化 Looper
         mHandler = new Handler() {//创建 Handler
             public void handleMessage(Message msg) {
                 // process incoming messages here
             }
         };
         Looper.loop();//启用 Looper 的 loop 方法开启消息轮询
     }
}
```

看一下 Looper 的完整源码，分析工作过程。

```Java
public final class Looper {

    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<Looper>();
	//每个线程都会有一个ThreadLocal 用来保存 Looper对象（里面包含了主线程和 MessageQueue）

    private static Looper sMainLooper;  // 主线程的 Looper

    final MessageQueue mQueue;//保存消息队列
    final Thread mThread;//保存主线程

    public static void prepare() {//为当前线程创建 Looper
        prepare(true);
    }

    private static void prepare(boolean quitAllowed) {
        if (sThreadLocal.get() != null) {
			//一个线程只能有一个 Looper， 否则抛出异常
            throw new RuntimeException("Only one Looper may be created per thread");
        }
        sThreadLocal.set(new Looper(quitAllowed));//将创建的 Looper 放入 ThreadLocal
    }
	
	//初始化主线程的 Looper
    public static void prepareMainLooper() {
        prepare(false);
        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException("The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }

    //获取主线程的 Looper
    public static Looper getMainLooper() {
        synchronized (Looper.class) {
            return sMainLooper;
        }
    }

    //在当前线程中开启轮询
    public static void loop() {
        final Looper me = myLooper();//从 ThreadLocal 中取出当前线程的 Looper 对象
        if (me == null) {
			//Looper 没有调用 Looper.prepare() 初始化，抛出异常
            throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
        }
        final MessageQueue queue = me.mQueue;//从 Looper 对象中取出消息队列

        for (;;) {//死循环
            Message msg = queue.next(); // 不断的取出消息
            if (msg == null) {
                // No message indicates that the message queue is quitting.
                return;
            }

			...				

            try {
                msg.target.dispatchMessage(msg);
				//取出消息的 target (也就是 Handler)，执行分发消息的操作
            } finally {
                if (traceTag != 0) {
                    Trace.traceEnd(traceTag);
                }
            }

			...	

            msg.recycleUnchecked();//消息已经分发，进行回收操作
        }
    }

    public static @Nullable Looper myLooper() {
        return sThreadLocal.get();//从 ThreadLocal 中取出当前线程的 Looper 对象
    }

    private Looper(boolean quitAllowed) {
        mQueue = new MessageQueue(quitAllowed);//创建消息队列
        mThread = Thread.currentThread();//保存当前线程
    }

    public void quit() {
        mQueue.quit(false);//直接退出消息循环，不管是否还有消息
    }

    public void quitSafely() {
        mQueue.quit(true);//执行完所有的消息，退出消息循环
    }

	...
}
```

#### 2. MessageQueue 源码分析 ####
在 Looper 中创建了 MessageQueue，我们接着看下 MessageQueue 是怎么工作的。

MessageQueue的构造方法。

```Java
MessageQueue(boolean quitAllowed) {
    mQuitAllowed = quitAllowed;
	//构造函数，quitAllowed 用来标识是否允许退出。
	//主线程是不允许退出的（不然会退出整个程序），子线程可以退出。
    mPtr = nativeInit();
}
```
然后我们再看一下 MessageQueue.enqueueMessage() 的源码是怎么添加消息的。

```Java
boolean enqueueMessage(Message msg, long when) {
    if (msg.target == null) {
        throw new IllegalArgumentException("Message must have a target.");
    }
    if (msg.isInUse()) {
        throw new IllegalStateException(msg + " This message is already in use.");
    }

    synchronized (this) {
        if (mQuitting) {
            IllegalStateException e = new IllegalStateException(
                    msg.target + " sending message to a Handler on a dead thread");
            Log.w(TAG, e.getMessage(), e);
            msg.recycle();
            return false;
        }

        msg.markInUse();
        msg.when = when;
        Message p = mMessages;
        boolean needWake;
        if (p == null || when == 0 || when < p.when) {
            // 如果消息队列里面没有消息，或者消息的执行时间比里面的消息早，就把这条消息设置成第一条消息。一般不会出现这种情况，因为系统一定会有很多消息。
            msg.next = p;
            mMessages = msg;
            needWake = mBlocked;
        } else {//如果消息队列里面有消息
            needWake = mBlocked && p.target == null && msg.isAsynchronous();
            Message prev;
            for (;;) {//找到消息队列里面的最后一条消息
                prev = p;
                p = p.next;
                if (p == null || when < p.when) {
                    break;
                }
                if (needWake && p.isAsynchronous()) {
                    needWake = false;
                }
            }
            msg.next = p; // invariant: p == prev.next
            prev.next = msg;//把消息添加到最后
        }

        // We can assume mPtr != 0 because mQuitting is false.
        if (needWake) {
            nativeWake(mPtr);
        }
    }
    return true;
}
```

知道了怎么添加消息，我们在看下 MessageQueue.next() 方法是怎么取出消息的，也就是 Looper.loop() 方法中不断取消息的方法。

```Java
Message next() {
    int pendingIdleHandlerCount = -1; // -1 only during first iteration
    int nextPollTimeoutMillis = 0;
    for (;;) {
        if (nextPollTimeoutMillis != 0) {
            Binder.flushPendingCommands();
        }

        nativePollOnce(ptr, nextPollTimeoutMillis);

        synchronized (this) {
            final long now = SystemClock.uptimeMillis();
            Message prevMsg = null;
            Message msg = mMessages;//拿到当前的消息队列
            if (msg != null && msg.target == null) {
                //处理异步的消息，暂不讨论
                do {
                    prevMsg = msg;
                    msg = msg.next;
                } while (msg != null && !msg.isAsynchronous());
            }
            if (msg != null) {
                if (now < msg.when) {
                    // Next message is not ready.  Set a timeout to wake up when it is ready.
                    nextPollTimeoutMillis = (int) Math.min(msg.when - now, Integer.MAX_VALUE);
                } else {
                    //取出一条消息，消息队列往后移动一个
                    mBlocked = false;
                    if (prevMsg != null) {
                        prevMsg.next = msg.next;
                    } else {
                        mMessages = msg.next;
                    }
                    msg.next = null;
                    if (DEBUG) Log.v(TAG, "Returning message: " + msg);
                    msg.markInUse();//标记为已使用
                    return msg;
                }
            } else {
                // No more messages.
                nextPollTimeoutMillis = -1;
            }

            ...
    }
}

```

我们知道 MessageQueue 是个链表结构，里面保存的是 Message，我们再看下 Message 是什么。

```Java
public final class Message implements Parcelable {
   
    public int what;//消息类型，标识消息的作用

    public int arg1;//整型参数1

    public int arg2;//整型参数2

    public Object obj;//复杂对象参数

    public Messenger replyTo;

    public int sendingUid = -1;

	/*package*/ static final int FLAG_IN_USE = 1 << 0;//标记消息已使用

    /** If set message is asynchronous */
    /*package*/ static final int FLAG_ASYNCHRONOUS = 1 << 1;//标记消息是否异步

    /** Flags to clear in the copyFrom method */
    /*package*/ static final int FLAGS_TO_CLEAR_ON_COPY_FROM = FLAG_IN_USE;

    /*package*/ int flags;//消息当前标记

    /*package*/ long when;//消息执行时间
    
    /*package*/ Bundle data;
    
    /*package*/ Handler target;//Handler 用于执行 handleMessage();
    
    /*package*/ Runnable callback;//消息是一个Runnable
    
    // sometimes we store linked lists of these things
    /*package*/ Message next;//下一个消息

    private static final Object sPoolSync = new Object();//控制并发访问
    private static Message sPool;//消息池
    private static int sPoolSize = 0;//消息池数量

    private static final int MAX_POOL_SIZE = 50;//消息最大数量

    ...

}
```

[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_handler/01.jpg