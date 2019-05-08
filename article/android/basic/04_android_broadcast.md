# 分享一些 Broadcast 使用技巧

## 简介

Broadcast（广播） 是 Android 的四大组件之一，用于进程/线程间通信。

广播最大的特点就是发送方并不关心接收方是否接到数据，也不关心接收方是如何处理数据的，它只负责「说」而不管你「听不听」。

广播可以来之系统，例如，Android 系统在发生各种系统事件时发送广播（系统启动或者设备开始充电时）。

也可以来自于其他应用程序，例如，应用程序也可以发送自定义广播，来通知其他应用程序接受他们可能感兴趣的内容（更新数据）。

## 广播的分类

### 按发送方式分类

- 标准广播

是一种「完全异步执行」的广播，没有任何先后顺序，所有的广播接收器几乎同一时刻接收到这条广播消息，效率高，无法被截断。

- 有序广播

是一种「同步执行」的广播，有先后顺序，同一时刻只有一个接收器可以接收这个广播消息，优先级高的广播接收器可以先收到广播消息，并且前面的广播接收器还可以截断正在传递的广播，这样后面的广播接收器就无法接收广播消息了。

### 按注册方式分类

- 静态广播

不管应用程序是否处于活动状态，都会进行监听。每次触发都会建立新的 Receiver 对象。

- 动态广播

在代码中进行注册，注意动态注册的广播一定要取消注册才行，通常是在 `onDestroy()` 方法中调用 `unregisterReceiver()` 方法来实现。

  从开始创建直到其被解除注册会使用同一个 Receiver，无论这个广播被触发几次。

### 按定义方式分类

- 系统广播

Android 系统中内置了多个系统广播，每个系统广播都具有特定的 IntentFilter，其中主要包括具体的 Action，系统广播发出后，将被相应的 BroadcastReceiver 接收。系统广播在系统内部当特定事件发生时，由系统自动发出。

- 自定义广播

由应用程序开发者自己定义的广播。

### 按范围方式分类

- 全局广播

发出的广播可以被其他任意的应用程序接收，或者可以接收来自其他任意应用程序的广播。

- 本地广播

只能在应用程序的内部进行传递的广播，广播接收器也只能接收内部的广播，不能接受其他应用程序的广播。

## 广播的使用

### 创建广播接收器

使用广播我们需要先创建 BroadcastReceiver（广播接收器） ，直接继承 BroadcastReceiver 创建子类并实现父类的 `onReceive()` 方法即可，如下示例代码。

```java
public class MyReceiver extends BroadcastReceiver {
  // 自定义 action
  private static final String ACTION = "com.jeanboy.broadcast.MyReceiverFilter";
  
  @Override
  public void onReceive(Context context, Intent intent) {
    //TODO: 接收到广播进行处理
  }
}
```

### 静态广播

在使用广播时还需要在 AndroidMainfest 文件中定义，也就是注册静态广播。

```xml
<receiver android:name=".ui.broadcast.MyReceiver"
          android:enabled="true"
          android:exported="true">
    <intent-filter>
        <!-- 例如：接收系统开机广播 -->
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <!-- 例如：接收自定义的广播 -->
        <action android:name="com.jeanboy.broadcast.MyReceiverFilter" />
    </intent-filter>
</receiver>
```

上面的 enabled 设置为 true 意味着能够接受到广播信息。exported 为 true 意味着能够接收到外部 APK 发送的广播信息。

### 动态广播

使用动态广播不需要在 AndroidMainfest 文件中定义，只需在代码中注册即可。

```java
// 创建广播
MyReceiver myReceiver = new MyReceiver();
// 创建 IntentFilter
IntentFilter intentFilter = new IntentFilter();
// 例如：添加系统广播 action 接受网络变化
intentFilter.addAction(ConnectivityManager.CONNECTIVITY_ACTION);
// 例如：添加自定义的 action
intentFilter.addAction(MyReceiver.ACTION);
// 注册广播
registerReceiver(myReceiver, intentFilter);
// 注销广播
unregisterReceiver(myReceiver);
```

### 发送广播

发送广播比较简单，无论静态广播还是动态广播，都是如下方式（系统广播 Android 系统会自动发送，不在本文讨论范围）。

```java
// 创建 Intent
Intent intent = new Intent();
// 例如：添加自定义的 action
intent.setAction(MyReceiver.ACTION);
// 发送广播
sendBroadcast(intent);
```

### Android  8.0 中的静态广播

由于 Android 8.0 废除大部分静态广播，对于代码需要修改某些部分。

发送广播部分需要设置 `ComponetName`。

```java
Intent intent = new Intent(MyReceiver.ACTION);
// ComponetName("自定义广播的包名", "自定义广播的路径")
ComponentName component = new ComponentName("com.jeanboy.app.broadcast", "com.jeanboy.app.broadcast.MyReceiver");
intent.setComponent(component);
sendBroadcast(intent);
```

### 带权限的广播

使用广播可能引发的安全问题：

- 如果别的应用程序监听我们的广播，那么会造成我们应用程序的数据泄露；
- 如果别的应用程序冒充我们的应用发送广播，那么就会频繁的启动我们的广播接收程序，造成我们应用的混乱，甚至崩溃。 

为了避免以上安全问题，Android 为我们提供了权限机制。

首先在注册静态广播时可以在 AndroidMainfest 文件中添加权限。

```xml
<manifest ...>
  <!-- 自定义一个自己的权限 -->
  <permission android:name="com.jeanboy.permissions.MY_BROADCAST"/>
  <!-- 使用自定义的权限 -->
  <uses-permission android:name="com.jeanboy.permissions.MY_BROADCAST"/>

  <application ...>
    <!-- 添加权限 -->
    <receiver android:name=".ui.broadcast.MyReceiver"
              android:permission="com.jeanboy.broadcast.MY_BROADCAST"
              android:enabled="true"
              android:exported="true">
      <intent-filter>
        <!-- 例如：接收自定义的广播 -->
        <action android:name="com.jeanboy.broadcast.MyReceiverFilter" />
      </intent-filter>
    </receiver>
  </application>
</manifest>
```

然后在我们发送广播时，可以为它指定一个权限，只有具有该权限的应用才能接收到广播，如下所示：

```java
// 创建 Intent
Intent intent = new Intent();
// 例如：添加自定义的 action
intent.setAction(MyReceiver.ACTION);
// 发送广播，添加权限
sendBroadcast(intent, "com.jeanboy.permissions.MY_BROADCAST");
```

### 本地广播

上面介绍的 BroadcastReceiver 用于应用之间的传递消息，本质上它是跨进程的，还有可能被其他应用拦截。

而 LocalBroadcast（本地广播）用于应用内部传递消息，比 BroadcastReceiver 更加高效，它只在应用内部有效，不需要考虑安全问题。

本地广播的创建仍然是继承 BroadcastReceiver 创建子类，并实现父类的 `onReceive()` 方法。在注册、发送、注销广播时使用 LocalBroadcastManager 来进行相关操作。

```java
// 创建广播
MyReceiver myReceiver = new MyReceiver();
// 创建 IntentFilter
IntentFilter intentFilter = new IntentFilter();
// 例如：添加自定义的 action
intentFilter.addAction(MyReceiver.ACTION);
// 注册本地广播
LocalBroadcastManager.getInstance(this)
                .registerReceiver(myReceiver, intentFilter);

// 发送广播
Intent intent = new Intent(MyReceiver.ACTION));
LocalBroadcastManager.getInstance(this).sendBroadcast(intent);

// 注销本地广播
LocalBroadcastManager.getInstance(this).unregisterReceiver(myReceiver);
```

## 参考资料

- [Android 官方文档 - 广播](https://developer.android.com/guide/components/broadcasts)
- [Android开发 - Broadcast的使用](https://blog.csdn.net/lllllyt/article/details/83187683)
- [Android 之 超详细 Broadcast](https://blog.csdn.net/weixin_39460667/article/details/82413819)