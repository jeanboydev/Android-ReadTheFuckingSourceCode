# 最通俗易懂的 Handler 源码解析

## 简介

在 Android 中 UI 线程是不安全的，如果在子线程中尝试进行更新 UI 操作，程序就有可能会崩溃；当然如果在 UI 线程中做耗时的操作，系统就会弹出 ANR 弹窗提示该程序无响应，十分影响用户体验。

Android 系统中提供了 Handler，这样我们就可以使用 Handler 在子线程中发送消息来更新 UI；也可以将耗时操作交给子线程处理，等子线程处理完后再使用 Handler 发送消息来回到主线程。

可以看到 Handler 的主要作用是进行线程间通信的，本文将从源码的角度分析下 Handler，以便更好的理解 Handler 的工作流程。

我们先来回顾下 Handler 常用的方式：

```java
// 在主线程中创建 Handler 来处理子线程发送的消息
private Handler handler = new Handler() {
  @Override
  public void handleMessage(Message msg) {
    super.handleMessage(msg);
    switch (msg.what) {
      case 0:
        //TODO: 处理消息
        break;
    }
  }
};

// 使用方式一：在子线程中发送消息
new Thread(new Runnable() {
  @Override
  public void run() {
    Message message = new Message();
    message.what = 0;
    message.obj = "测试消息";
    // 子线程中发送消息
    handler.sendMessage(message);
  }
}).start();

// 使用方式二：handler.post()
handler.post(new Runnable() {
  @Override
  public void run() {
    // 运行在子线程中...
  }
});
```

## Handler

```java
private Handler handler = new Handler();
```

通过上面示例代码可以看到，在使用 Handler 时首先需要创建 Handler 对象，我们先来看下 Handler 的构造方法。

```java
//frameworks/base/core/java/android/os/Handler.java

/* 构造方法一 */
public Handler() {
  this(null, false);
}
/* 构造方法二 */
public Handler(Callback callback) {
  this(callback, false);
}
/* 构造方法三 */
public Handler(Looper looper) {
  this(looper, null, false);
}
/* 构造方法四 */
public Handler(Looper looper, Callback callback) {
  this(looper, callback, false);
}
/* 构造方法五 */
public Handler(boolean async) {
  this(null, async);
}
/* 构造方法六 */
public Handler(Callback callback, boolean async) {
  // ...
  mLooper = Looper.myLooper();
  if (mLooper == null) {
    throw new RuntimeException(
      "Can't create handler inside thread that has not called Looper.prepare()");
  }
  mQueue = mLooper.mQueue;
  mCallback = callback;
  mAsynchronous = async;
}
/* 构造方法七 */
public Handler(Looper looper, Callback callback, boolean async) {
  mLooper = looper;
  mQueue = looper.mQueue;
  mCallback = callback;
  mAsynchronous = async;
}
```

可以看到 Handler 有很多构造方法，我们一般常用的是「构造方法一」和「构造方法三」。

我们在「构造方法六」中可以看到：

```java
//frameworks/base/core/java/android/os/Handler.java

/* 构造方法六 */
public Handler(Callback callback, boolean async) {
  // ...
  mLooper = Looper.myLooper();
  if (mLooper == null) {
    throw new RuntimeException(
      "Can't create handler inside thread that has not called Looper.prepare()");
  }
  mQueue = mLooper.mQueue;
  mCallback = callback;
  mAsynchronous = async;
}
```

这里调用了 `Looper.myLooper()` 方法，当 mLooper 为空时会抛出异常，提示我们需要先调用 `Looper.prepare()` 方法，我接下来看下 Looper 中的这两个方法。

## Looper

```java
//frameworks/base/core/java/android/os/Looper.java

static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<Looper>();
private static Looper sMainLooper;

final MessageQueue mQueue;
final Thread mThread;
```

从上面源码中可以看到 Looper 有 4 个成员变量：

- sThreadLocal：保存的是当前线程的 Looper。
- sMainLooper：Application 中主线程中的 Looper。
- mQueue：当前线程中的 MessageQueue。
- mThread：创建 Looper 的线程。

### myLoop()

```java
//frameworks/base/core/java/android/os/Looper.java

/* Handler 构造方法六中调用的方法 */
public static Looper myLooper() {
  // 返回当前线程中的 looper
  return sThreadLocal.get();
}
```

可以看到 `myLooper()` 逻辑很简单，调用了 ThreadLocal 的 get() 方法。ThreadLocal 我们稍后再分析。

### prepare()

在 Handler 构造方法六中可以看到，如果 myLoop() 的结果为空会直接抛出异常，提示需要先调用  `prepare()` 方法，接下来分析下 `prepare()` 方法。

```java
//frameworks/base/core/java/android/os/Looper.java

/* Handler 构造方法六中调用的方法 */
public static void prepare() {
  prepare(true);
}
/* 带参数的 prepare 方法 */
private static void prepare(boolean quitAllowed) {
  if (sThreadLocal.get() != null) {
    throw new RuntimeException("Only one Looper may be created per thread");
  }
  sThreadLocal.set(new Looper(quitAllowed));
}
/* Looper 构造方法 */
private Looper(boolean quitAllowed) {
  mQueue = new MessageQueue(quitAllowed);
  mThread = Thread.currentThread();
}
```

`prepare()` 方法中调用了 `prepare(quitAllowed)` 方法，这里判断了 Looper 是否为空。

如果当前线程已经创建了 Looper 直接抛出异常，也就是说一个线程中只能创建一个 Looper，经常使用 Handler 的小伙伴应该对这个异常很熟悉。

如果当前线程没有创建 Looper 会直接调用 `Looper(quitAllowed)` 的构造方法，创建一个 Looper 并创建一个 MessageQueue，然后保存一下当前线程的信息。

## MessageQueue

接下来我们分析下 MessageQueue 的具体实现。

```java
//frameworks/base/core/java/android/os/Looper.java

final MessageQueue mQueue;

/* Looper 构造方法 */
private Looper(boolean quitAllowed) {
  mQueue = new MessageQueue(quitAllowed);
  mThread = Thread.currentThread();
}
```

我们看下 MessageQueue 的构造方法：

```java
//frameworks/base/core/java/android/os/MessageQueue.java

private native static long nativeInit();

MessageQueue(boolean quitAllowed) {
  mQuitAllowed = quitAllowed;
  mPtr = nativeInit();
}
```

MessageQueue 的构造方法逻辑还是很简单的。这里调用了一个 native 方法 `nativeInit()` 在 native 层进行了初始化，感兴趣的可以去查看 native 源码，文件如下：

```c++
//frameworks/base/core/jni/android_os_MessageQueue.cpp

static jlong android_os_MessageQueue_nativeInit(JNIEnv* env, jclass clazz) {
  NativeMessageQueue* nativeMessageQueue = new NativeMessageQueue();
  if (!nativeMessageQueue) {
    jniThrowRuntimeException(env, "Unable to allocate native queue");
    return 0;
  }

  nativeMessageQueue->incStrong(env);
  return reinterpret_cast<jlong>(nativeMessageQueue);
}
```

分析到这里 Handler 的创建流程已经分析完了，目前可以看到 Handler 创建时创建了如下内容：

![Handler 创建过程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/01.png)

如图所示，在创建 Handler 之前需要先调用 Looper.prepare()，该方法会初始化 Looper，创建 MessageQueue 和 ThreadLocal。

第二步当我们创建 Handler 时会调用 Looper 中的 myLoop() 方法获取到 Looper 和 MessageQueue 保存到 Handler 中。

## ThreadLocal

我们现在来分析下 ThreadLocal 的作用。

```java
ThreadLocal<Looper> sThreadLocal = new ThreadLocal<Looper>();
sThreadLocal.set(new Looper(quitAllowed)); // 设置变量信息
sThreadLocal.get(); // 读取变量信息
```

ThreadLocal 提供了线程本地变量，它可以保证访问到的变量属于当前线程，每个线程都保存有一个变量副本，每个线程的变量都不同，而同一个线程在任何时候访问这个本地变量的结果都是一致的。

ThreadLocal 相当于提供了一种线程隔离，将变量与线程相绑定。而当线程结束生命周期时，所有的线程本地实例都会被 GC 回收掉。通常 ThreadLocal 定义为 private static 类型。

### nextHashCode()

接下来分析下 ThreadLocal 的具体实现。

```java
//java/lang/ThreadLocal.java

private final int threadLocalHashCode = nextHashCode();

private static AtomicInteger nextHashCode =
    new AtomicInteger();

private static final int HASH_INCREMENT = 0x61c88647;

private static int nextHashCode() {
    return nextHashCode.getAndAdd(HASH_INCREMENT);
}
```

ThreadLocal 通过 threadLocalHashCode 来标识每一个 ThreadLocal 的唯一性。threadLocalHashCode 通过 CAS 操作进行更新，每次 hash 操作的增量为 0x61c88647。

### set()

我们来看看 ThreadLocal 的 set() 方法。

```java
//java/lang/ThreadLocal.java

public void set(T value) {
    Thread t = Thread.currentThread();
    ThreadLocalMap map = getMap(t);
    if (map != null)
        map.set(this, value);
    else
        createMap(t, value);
}

ThreadLocalMap getMap(Thread t) {
    return t.threadLocals;
}

void createMap(Thread t, T firstValue) {
    t.threadLocals = new ThreadLocalMap(this, firstValue);
}
```

可以看到通过 `Thread.currentThread()` 方法获取了当前的线程引用，并传给了 `getMap(Thread)` 方法获取一个 ThreadLocalMap 的实例。

在 `getMap(Thread)` 方法中直接返回 Thread 实例的成员变量 threadLocals。它的定义在 Thread 内部，访问级别为 package 级别：

```java
//java/lang/Thread.java

ThreadLocal.ThreadLocalMap threadLocals = null;
```

到了这里，可以看出，每个 Thread 里面都有一个 `ThreadLocal.ThreadLocalMap` 成员变量，也就是说每个线程通过 `ThreadLocal.ThreadLocalMap` 与 `ThreadLocal` 相绑定，这样可以确保每个线程访问到的 ThreadLocal 变量都是本线程的。

我们往下继续分析。获取了 ThreadLocalMap 实例以后，如果它不为空则调用 ThreadLocalMap.ThreadLocalMap.set() 方法设值；若为空则调用 ThreadLocal.createMap() 方法 new 一个 ThreadLocalMap 实例并赋给 Thread.threadLocals。

### ThreadLocalMap

下面我们分析一下 ThreadLocalMap 的实现，可以看到 ThreadLocalMap 有一个常量和三个成员变量：

```java
//java/lang/ThreadLocal.ThreadLocalMap

private static final int INITIAL_CAPACITY = 16;

private Entry[] table;

private int size = 0;

private int threshold; // Default to 0
```

其中 INITIAL_CAPACITY 代表这个 Map 的初始容量；table 是一个 Entry 类型的数组，用于存储数据；size 代表表中的存储数目； threshold 代表需要扩容时对应 size 的阈值。

Entry 类是 ThreadLocalMap 的静态内部类，用于存储数据。它的源码如下：

```java
//java/lang/ThreadLocal.ThreadLocalMap

static class Entry extends WeakReference<ThreadLocal<?>> {
    /** The value associated with this ThreadLocal. */
    Object value;

    Entry(ThreadLocal<?> k, Object v) {
        super(k);
        value = v;
    }
}
```

Entry 类继承了 WeakReference<ThreadLocal<?>>，即每个 Entry 对象都有一个 ThreadLocal 的弱引用（作为 key），这是为了防止内存泄露。一旦线程结束，key 变为一个不可达的对象，这个 Entry 就可以被 GC 回收了。

ThreadLocalMap 类有两个构造函数，其中常用的是 ThreadLocalMap(ThreadLocal<?> firstKey, Object firstValue)：

```java
//java/lang/ThreadLocal.ThreadLocalMap

ThreadLocalMap(ThreadLocal<?> firstKey, Object firstValue) {
    table = new Entry[INITIAL_CAPACITY];
    int i = firstKey.threadLocalHashCode & (INITIAL_CAPACITY - 1);
    table[i] = new Entry(firstKey, firstValue);
    size = 1;
    setThreshold(INITIAL_CAPACITY);
}
```

构造函数的第一个参数就是本 ThreadLocal 实例（this），第二个参数就是要保存的线程本地变量。构造函数首先创建一个长度为 16 的 Entry 数组，然后计算出 firstKey 对应的哈希值，然后存储到 table 中，并设置 size 和 threshold。

注意一个细节，计算 hash 的时候里面采用了 `hashCode & (size - 1)` 的算法，这相当于取模运算 `hashCode % size` 的一个更高效的实现（与 HashMap 中的思路相同）。正是因为这种算法，我们要求 size 必须是 2 的指数，因为这可以使得 hash 发生冲突的次数减小。

- set()

接下来我们来看 ThreadLocalMap.set() 方法的实现：

```java
//java/lang/ThreadLocal.ThreadLocalMap

private void set(ThreadLocal<?> key, Object value) {

    Entry[] tab = table;
    int len = tab.length;
    int i = key.threadLocalHashCode & (len-1);

    for (Entry e = tab[i];
            e != null;
            e = tab[i = nextIndex(i, len)]) {
        ThreadLocal<?> k = e.get();

        if (k == key) {
            e.value = value;
            return;
        }

        if (k == null) {
            replaceStaleEntry(key, value, i);
            return;
        }
    }

    tab[i] = new Entry(key, value);
    int sz = ++size;
    if (!cleanSomeSlots(i, sz) && sz >= threshold)
        rehash();
}
```

如果冲突了，就会通过 nextIndex 方法再次计算哈希值：


```java
//java/lang/ThreadLocal.ThreadLocalMap

private static int nextIndex(int i, int len) {
    return ((i + 1 < len) ? i + 1 : 0);
}
```

到这里，我们看到 ThreadLocalMap 解决冲突的方法是 线性探测法（不断加 1），而不是 HashMap 的 链地址法，这一点也能从 Entry 的结构上推断出来。

- getEntry()

我们继续看 ThreadLocalMap.getEntry() 的源码：

```java
//java/lang/ThreadLocal.ThreadLocalMap

private Entry getEntry(ThreadLocal<?> key) {
    int i = key.threadLocalHashCode & (table.length - 1);
    Entry e = table[i];
    if (e != null && e.get() == key)
        return e;
    else
        return getEntryAfterMiss(key, i, e);
}

private Entry getEntryAfterMiss(ThreadLocal<?> key, int i, Entry e) {
    Entry[] tab = table;
    int len = tab.length;

    while (e != null) {
        ThreadLocal<?> k = e.get();
        if (k == key)
            return e;
        if (k == null)
            expungeStaleEntry(i);
        else
            i = nextIndex(i, len);
        e = tab[i];
    }
    return null;
}
```

逻辑很简单，hash 以后如果是 ThreadLocal 对应的 Entry 就返回，否则调用 getEntryAfterMiss 方法，根据线性探测法继续查找，直到找到或对应 entry 为 null，并返回。

由于篇幅有限，更多细节不是本文讨论的重点，感兴趣的小伙伴可以去查看源码。

通过上面分析可以看到 ThreadLocal 的工作原理如下：

![ThreadLocal 工作原理](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/02.png)

如图所示，ThreadLocal 中有一个 ThreadLocalMap 其中以 ThreadLocal 作为 Key，以需要保存的值作为 Value。这样不同的线程访问同一个 ThreadLocal 时，获取到的值也就是各个线程存储时对应的值了。

## ActivityThread

我们已经分析了 Handler 的创建流程，也就下面代码执行的过程：

```java
private Handler handler = new Handler();
```

在 Handler 的构造方法中可以看到：

```java
//frameworks/base/core/java/android/os/Handler.java

/* 构造方法六 */
public Handler(Callback callback, boolean async) {
  // ...
  mLooper = Looper.myLooper();
  if (mLooper == null) {
    throw new RuntimeException(
      "Can't create handler inside thread that has not called Looper.prepare()");
  }
  mQueue = mLooper.mQueue;
  mCallback = callback;
  mAsynchronous = async;
}
```

如果 `Looper.myLooper()` 获取到的 Looper 为空就直接抛出异常了，但是我们在 Activity 中创建 Handler 时并不会抛出异常。

这是因为 Activity 在创建过程中已经调用了 `Looper.prepareMainLooper()` 源码如下：

```java
//frameworks/base/core/java/android/app/ActivityThread.java

public static void main(String[] args) {
  SamplingProfilerIntegration.start();
  CloseGuard.setEnabled(false);
  Environment.initForCurrentUser();

  final File configDir = 
    Environment.getUserConfigDirectory(UserHandle.myUserId());
  TrustedCertificateStore.setDefaultUserDirectory(configDir);
  
  // 这里调用了 prepareMainLooper() 方法
  Looper.prepareMainLooper();

  ActivityThread thread = new ActivityThread();
  thread.attach(false);

  if (sMainThreadHandler == null) {
    sMainThreadHandler = thread.getHandler();
  }
  
  // 然后调用了 loop() 方法
  Looper.loop();

  throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

我们来看下 `Looper.prepareMainLooper()` 方法的具体实现。

### Looper.prepareMainLooper()

在 Looper 类中还可以看到一个 `prepareMainLooper()` 方法。

```java
//frameworks/base/core/java/android/os/Looper.java

/* 初始化一个 main looper */
public static void prepareMainLooper() {
  prepare(false);
  synchronized (Looper.class) {
    if (sMainLooper != null) {
      throw new IllegalStateException("The main Looper has already been prepared.");
    }
    sMainLooper = myLooper();
  }
}
/* 返回 main looper */
public static Looper getMainLooper() {
  synchronized (Looper.class) {
    return sMainLooper;
  }
}
```

可以看到 `prepareMainLooper()` 方法中首先调用了 `prepare(false)` 创建了一个不可以退出的 Looper，然后检查 MainLooper 是否已经创建，最后保存了一下 MainLooper 的引用。原来 `prepareMainLooper()` 中已经调用了 `prepare()` 方法。

### Looper.loop()

继续分析 `Looper.loop()` 方法。

```java
//frameworks/base/core/java/android/os/Looper.java

public static void loop() {
  // 从 ThreadLocal 中取出当前线程的 Looper 对象
  final Looper me = myLooper();
  if (me == null) {
    // Looper 没有调用 Looper.prepare() 进行初始化，抛出异常
    throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
  }
  // 从 Looper 对象中取出消息队列
  final MessageQueue queue = me.mQueue;
  // ...
  for (;;) { // 死循环
    // 不断的取出消息
    Message msg = queue.next();
    if (msg == null) { // 没有消息直接返回
      return;
    }
    // ...
    try {
      // 取到消息，回调到 Handler 中的 dispatchMessage()
      msg.target.dispatchMessage(msg);
    } finally {
      // ...
    }
    // ...
    // 消息已经分发，进行回收操作
    msg.recycleUnchecked();
  }
}
```

可以看到 `Looper.loop()` 就是不断的从 `MessageQueue` 中取出消息，然后回调到 `Handler.dispatchMessage()` 来处理消息。

```java
//frameworks/base/core/java/android/os/Handler.java

public void dispatchMessage(Message msg) {
  if (msg.callback != null) {
    handleCallback(msg); // 处理 post 消息，稍后再分析
  } else {
    if (mCallback != null) {
      // 回调到 Handler.handleMessage() 方法
      if (mCallback.handleMessage(msg)) {
        return;
      }
    }
    handleMessage(msg);
  }
}
```

可以看到，最后回调到我们最开始创建的 Handler 中了。

```java
private Handler handler = new Handler() {
  @Override
  public void handleMessage(Message msg) {
    super.handleMessage(msg);
    switch (msg.what) {
      case 0:
        //TODO: 处理消息
        break;
    }
  }
};
```

分析到这里可以看到 Handler 的大概工作原理如下：

![Handler 基本流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/03.png)

如图所示，可以看到我们之前创建 Handler 之前其实已经做了两步，第一步调用 Looper.prepare() 方法，创建 Looper 同时创建 MessageQueue 和 ThreadLocal。第二步调用 Looper.loop() 方法，不断地读取 MessageQueue 中的消息。第三步创建 Handler，Handler 的作用就是向 MessageQueue 中放入消息。

## Handler.sendMessage()

我们常用的发消息的方法如下：

```java
//frameworks/base/core/java/android/os/Handler.java

public final boolean sendMessage(Message msg) {
  return sendMessageDelayed(msg, 0);
}

public final boolean sendEmptyMessage(int what) {
  return sendEmptyMessageDelayed(what, 0);
}

public final boolean sendEmptyMessageDelayed(int what, long delayMillis) {
  Message msg = Message.obtain();
  msg.what = what;
  return sendMessageDelayed(msg, delayMillis);
}
```

可以看到上面不管哪种发消息的方式，最后都调用了 `sendMessageDelayed()` 方法。

```java
//frameworks/base/core/java/android/os/Handler.java

public final boolean sendMessageDelayed(Message msg, long delayMillis) {
  if (delayMillis < 0) {
    delayMillis = 0;
  }
  return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
}

public boolean sendMessageAtTime(Message msg, long uptimeMillis) {
  MessageQueue queue = mQueue;
  if (queue == null) {
    RuntimeException e = new RuntimeException(
      this + " sendMessageAtTime() called with no mQueue");
    Log.w("Looper", e.getMessage(), e);
    return false;
  }
  return enqueueMessage(queue, msg, uptimeMillis);
}

private boolean enqueueMessage(MessageQueue queue, Message msg, long uptimeMillis) {
  msg.target = this;
  if (mAsynchronous) {
    msg.setAsynchronous(true);
  }
  return queue.enqueueMessage(msg, uptimeMillis);
}
```

`sendMessageDelayed()` 方法最后调用了 `MessageQueue.enqueueMessage()` 。

## MessageQueue.enqueueMessage()

我们接着来看 `enqueueMessage()` 方法的实现：

```java
//frameworks/base/core/java/android/os/MessageQueue.java

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
      // 如果消息队列里面没有消息，或者消息的执行时间比里面的消息早，
      // 就把这条消息设置成第一条消息；
			// 一般不会出现这种情况，因为系统一定会有很多消息。
      msg.next = p;
      mMessages = msg;
      needWake = mBlocked;
    } else {
      // 如果消息队列里面有消息
      needWake = mBlocked && p.target == null && msg.isAsynchronous();
      Message prev;
      for (;;) { // 循环找到消息队列里面的最后一条消息
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
      prev.next = msg; // 把消息添加到最后
    }

    if (needWake) {
      nativeWake(mPtr);
    }
  }
  return true;
}
```

分析到这里可以看到，我们通过调用 `Handler.sendMessage()` 最后将 Message 添加到了 MessageQueue 的消息队列中。

在前面 `Looper.loop()` 方法中分析过，`loop()` 方法中有一个死循环一直在读取消息，当读取到刚才添加的消息后会回调到 `Handler.dispatchMessage()` 方法。

到这里 Handler 的工作流程大家应该已经很清楚了，如下图所示：

![Handler 工作流程](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/04.png)

假设在 Thread 1 中创建了 Handler，那么 Thread 2 向 Thread 1 发送消息的过程如上图所示。Handler 机制就像是一个传送机器，Looper 就是传送轮一直在不停的旋转，MessageQueue 就是传送带跟着Looper 旋转来运输 Message，Handler 就是机械手在 Thread 2 中将 Message 放到传送带 MessageQueue 上，传送到 Thread 1 后再将 Message 拿下来通知 Thread 1 进行处理。 

## Handler.post()

了解了 Handler 工作流程，我们继续来分析下另一种使用方式 `Handler.post()`。

```java
//frameworks/base/core/java/android/os/Handler.java

public final boolean post(Runnable r) {
  return  sendMessageDelayed(getPostMessage(r), 0);
}
```

可以看到 `post()` 也是调用了 `sendMessageDelayed()` 方法，上面已经分析过了，这里不再赘述。我们来看下 `getPostMessage(r)` 方法的实现。

```java
//frameworks/base/core/java/android/os/Handler.java

private static Message getPostMessage(Runnable r) {
  Message m = Message.obtain();
  m.callback = r;
  return m;
}
```

原来这里创建了一个 Message，将 Runnable 放入了 Message 的 callback 上。

那 Message 最后怎么处理的呢？

在分析中 `Looper.loop()` 方法中有这么一句 `msg.target.dispatchMessage(msg);`。

```java
//frameworks/base/core/java/android/os/Handler.java

public void dispatchMessage(Message msg) {
  if (msg.callback != null) {
    handleCallback(msg); // 处理 post 消息，稍后再分析
  } else {
    if (mCallback != null) {
      // 回调到 Handler.handleMessage() 方法
      if (mCallback.handleMessage(msg)) {
        return;
      }
    }
    handleMessage(msg);
  }
}
```

`handleCallback()` 就是处理 `Handler.post()` 发送的消息的。我们接着看，见证奇迹的时刻。

```java
//frameworks/base/core/java/android/os/Handler.java

private static void handleCallback(Message message) {
  message.callback.run();
}
```

如此简单，就是拿到 Runnable 调用了 `run()` 方法。

## Looper 中死循环为什么不会导致应用卡死？

这个问题涉及到线程，先来说下进程与线程相关知识。

### 进程

首先每个 App 都是运行在进程中的，进程由 Zygote 进程 fork 出来，进程承载了 App 上运行的个各种组件，如：Activity、Service 等。进程对于上层应用是完全透明的，大多数情况下一个 App 运行在一个进程中，其他情况暂不讨论。

### 线程

线程在应用中十分常见，比如下面代码：

```java
new Thread(new Runnable() {
  
  @Override
  public void run() {
  
  }
}).start();
```

每次执行上面代码都会创建一个线程。线程与当前 App 进程之间共享资源，从 Linux 系统角度来说进程与线程除了是否共享资源外，并没有本质的区别，都是一个 task_struct 结构体，在CPU看来进程或线程无非就是一段可执行的代码。

CPU 采用 CFS 调度算法，保证每个 task 都尽可能公平的享有 CPU 时间片。

### 死循环

对于线程来说，既然是一段可执行的代码，当可执行的代码执行完后，线程的生命周期就该终止了，线程也就退出。

而对于主线程，我们是绝不希望运行一段时间自己就退出的。

那么如何保证能一直存活呢？简单的做法就是让可执行的代码一直执行下去，死循环就可以保证不被退出。例如：loop() 方法中就是采用 `for(;;)` 死循环的方式。当然这里并非简单的死循环，无消息时会休眠。

真正卡死的主线程的操作，是在生命周期回调方法 onCreate()、onStart()、onResume() 等中操作时间过长，会导致 UI 渲染掉帧，甚至 ANR。

### loop()

如果仅仅使用死循环会一直占用 CPU，导致 CPU 一直处于工作状态。即使不会造成应用卡死，也会十分耗电。而事实上 loop() 中的死循环在没有消息的情况下是处于休眠状态的，并没有一直在运行。

```java
//frameworks/base/core/java/android/os/Looper.java

public static void loop() {
  // ...
  for (;;) { // 死循环
    // 不断的取出消息
    Message msg = queue.next();
    // ...
  }
}
```

在 loop() 方法中调用了 `MessageQueue.next()` 方法，我们来看下这个方法的具体实现：

```java
//frameworks/base/core/java/android/os/MessageQueue.java

Message next() {
  // ...
  for (;;) {
    // ...
    nativePollOnce(ptr, nextPollTimeoutMillis);
    // ...
  }
}
```

 `MessageQueue.next()` 方法调用了 native 方法 `nativePollOnce()`，此时主线程会释放 CPU 资源进入休眠状态，直到下个消息到达或者有事务发生时唤醒主线程。

原来这里采用的是 epoll 机制，消息到达时通过往 pipe 管道写端写入数据来唤醒主线程工作。

### 任务切换

在介绍 epoll 机制之前先来了解下任务切换，操作系统为了支持多任务，实现了进程调度的功能，会把进程分为「运行」和「等待」等几种状态。

运行状态是进程获得 CPU 使用权，正在执行代码的状态；等待状态是阻塞状态，进程会释放 CPU 使用权，程序会从运行状态变为等待状态，等接收到数据后变回运行状态重新获得 CPU 使用权。

操作系统会分时执行各个运行状态的进程，由于速度很快，看上去就像是同时执行多个任务。

![任务切换](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/05.png)

如上图，系统内核空间有两个队列，一个是运行队列，一个是等待队列。运行队列存放的是正在执行的进程，等待队列存放的是正在阻塞的进程。当接收到数据时，系统内核会唤醒等待队列中需要执行的进程，将该进程移到运行队列中；同理，当运行中的进程阻塞时，系统内核也会将进程移到等待队列中。

从历史发展角度看，必然会先出现一种不太高效的方法，人们再加以改进，最后留下来的才是最优的方法。只有先理解了不太高效的方法，才能够理解 epoll 的本质。

### select 机制

select 机制的设计思路很简单，假设进程 A 中同时监听 socket 1 和 socket 2，那么在调用 select 之后，操作系统会把进程 A 分别加入这两个 socket 的等待队列中。

![select 机制](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/06.png)

当任何一个 socket 收到数据后，中断程序将唤醒进程 A。将进程 A 从等待队列中移除，加入到工作队列中。当进程 A 被唤醒后，它知道至少有一个 socket 接收了数据。只需要遍历一遍 socket 列表，就可以得到就绪的 socket。

select 机制的缺点就是，每次唤醒进程都需要遍历一遍等待队列才能找到需要唤醒的进程，找到唤醒的进程后还需要遍历一遍 socket 列表才能找到就绪的 socket。为了 性能的考虑 Linux 中将 select 最大的监听数量限制为 1024 个，也就是 fd_set 列表的数量 fd_size 最大为 1024。

### poll 机制

由于 select 机制的监听数量最大为 1024，poll 机制进行了升级使用 pollfd 替换 fd_set，pollfd 是链表结构这样就没有了数量限制，但是在数量过大后性能还是会下降。

![poll 机制](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/07.png)

### epoll 机制

epoll 是在 2.6 内核中提出的，是之前的 select 和 poll 的增强版本。相对于 select 和 poll 来说，epoll 更加灵活，没有描述符限制。

![epoll 机制](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/07_handler/08.png)

如图所示，在使用 epoll 后内核中会创建一个 eventpoll 对象，eventpoll 对象中有 rdlist（就绪列表） 和 wq（等待队列）。

假设内核中运行着进程 A 与进程 B，当进程 A 使用 epoll 机制时，会将进程 A 加入到 eventpoll 对象的 wq 等待队列中。当 rdlist 为空时阻塞等待队列中进程 A，当 rdlist 不为空时唤醒等待队列中进程 A。因为有 rdlist 就序列表，进程 A 被唤醒后也可以知道哪些 socket 发生了变化。

## 参考资料

- [Android 异步消息处理机制 让你深入理解 Looper、Handler、Message三者关系](https://blog.csdn.net/lmj623565791/article/details/38377229/)
- [并发编程 | ThreadLocal 源码深入分析](https://www.sczyh30.com/posts/Java/java-concurrent-threadlocal/)
- [Android中为什么主线程不会因为Looper.loop()里的死循环卡死？](https://www.zhihu.com/question/34652589/answer/90344494)
- [Epoll 本质](https://bbs.gameres.com/thread_842984_1_1.html)
- [Linux IO模式及 select、poll、epoll详解](https://segmentfault.com/a/1190000003063859)