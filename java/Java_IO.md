# IO

## 基本概念

### 字节、字符

### 编码

### 字节流、字符流

### 协议

BIO（Blocking I/O）、NIO（New I/O）、AIO（Asynchronous I/O，NIO 2.0）

## 并发编程

### 多线程常见知识

- currentThread()：返回代码段正在被哪个线程调用的信息
- getId()：获取线程的唯一标识
- isAlive()：判断当前线程是否还处于活动状态
- sleep()：在指定的毫秒数内让当前“正在执行的线程”休眠（暂停执行）
- ~~stop()~~：【已废弃】停止线程
- interrupt()：中断线程
- ~~suspend()~~：【已废弃】暂停线程
- ~~resume()~~：【已废弃】恢复线程
- yield()：放弃当前 CPU 资源，将它让给其他任务去占用 CPU 执行时间
- setPriority()：设置线程优先级 1 - 10，优先级可以继承

### synchronized 关键字

- 方法锁

  ```java
  public synchronized void test() {
      //TODO: do something
  }
  ```

- 对象锁

  ```java
  synchronized (this) {
      //TODO: do something
  }
  
  synchronized (object) {
      //TODO: do something
  }
  ```

- 静态同步方法

  ```java
  public static synchronized void test() {
      //TODO: do something
  }
  //相当于
  synchronized (class) {
      //TODO: do something
  }
  ```

### volatile 关键字

主要作用是使变量在多个线程间可见。

线程主体 -> 工作内存 -> 主内存

### 线程间通讯

- 等待/通知机制

  - wait()：使调用该方法的线程释放共享资源的锁，然后从运行状态退出，进入等待队列，直到被再次唤醒。

  - notify()：随机唤醒等待队列中等待同一共享资源的一个线程，并使该线程退出等待队列，进入可运行状态。
  - notifyAll()：唤醒等待队列中所有正在等待的线程，并使全部线程退出等待队列，进入可运行状态。

- 生产者与消费者

- 管道

- join()：将一个线程加入到当前线程中，当前线程会等待加入的线程执行完才会结束。

- ThreadLocal：

### Lock

- ReentrantLock
- Condition

### Timer

### Sington



## 小标题

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/xxx/xxx.png" alt=""/>

## 参考资料

- [资料标题](http://www.baidu.com)


