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


#### 1.Looper源码分析 ####
Looper 源码最上面的注释里有如下使用示例，可以清晰的看出 Looper 的使用方法。


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

看一下 Looper 的完整源码，分析工作过程。

    public final class Looper {
   
	    private static final String TAG = "Looper";
	
	    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<Looper>();
		//每个线程都会有一个ThreadLocal 用来保存 Looper对象（里面包含了主线程和 MessageQueue）
	    private static Looper sMainLooper;  // 主线程的 Looper
	
	    final MessageQueue mQueue;//保存消息队列
	    final Thread mThread;//保存主线程
	
	    private Printer mLogging;
	    private long mTraceTag;
	
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
	
	        // Make sure the identity of this thread is that of the local process,
	        // and keep track of what that identity token actually is.
	        Binder.clearCallingIdentity();
	        final long ident = Binder.clearCallingIdentity();
	
	        for (;;) {//死循环
	            Message msg = queue.next(); // 不断的取出消息
	            if (msg == null) {
	                // No message indicates that the message queue is quitting.
	                return;
	            }
	
	            // This must be in a local variable, in case a UI event sets the logger
	            final Printer logging = me.mLogging;
	            if (logging != null) {
	                logging.println(">>>>> Dispatching to " + msg.target + " " +
	                        msg.callback + ": " + msg.what);
	            }
	
	            final long traceTag = me.mTraceTag;
	            if (traceTag != 0) {
	                Trace.traceBegin(traceTag, msg.target.getTraceName(msg));
	            }
	            try {
	                msg.target.dispatchMessage(msg);
					//取出消息的 target (也就是 Handler)，执行分发消息的操作
	            } finally {
	                if (traceTag != 0) {
	                    Trace.traceEnd(traceTag);
	                }
	            }
	
	            if (logging != null) {
	                logging.println("<<<<< Finished to " + msg.target + " " + msg.callback);
	            }
	
	            // Make sure that during the course of dispatching the
	            // identity of the thread wasn't corrupted.
	            final long newIdent = Binder.clearCallingIdentity();
	            if (ident != newIdent) {
	                Log.wtf(TAG, "Thread identity changed from 0x"
	                        + Long.toHexString(ident) + " to 0x"
	                        + Long.toHexString(newIdent) + " while dispatching to "
	                        + msg.target.getClass().getName() + " "
	                        + msg.callback + " what=" + msg.what);
	            }
	
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
	}


[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_handler/01.jpg