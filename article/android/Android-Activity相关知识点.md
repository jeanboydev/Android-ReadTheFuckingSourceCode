# Activity 相关知识点

## 什么是 Activity？

Activity 是 Android 的四大组件之一，是用户操作的可视化界面，它为用户提供了一个完成操作指令的窗口。

当我们创建完 Activity 之后，需要调用 `setContentView(view)` 方法来完成界面的显示，以此来为用户提供交互的入口。在 Android App 中只要能看见的几乎都要依托于 Activity，所以 Activity 是在开发中使用最频繁的一种组件。

## 生命周期

生命周期就是 Activity 从开始到结束所经历的各个状态，从一个状态到另一个状态的转变，从无到有再到无，这样一个过程中所经历的状态就叫做生命周期。

Acitivity 本质上有四种状态：

- 运行：如果一个活动被移到了前台（活动栈顶部）。
- 暂停：如果一个活动被另一个非全屏的活动所覆盖（比如一个 Dialog），那么该活动就失去了焦点，它将会暂停（但它仍然保留所有的状态和成员信息，并且仍然是依附在 WindowsManager 上），在系统内存积极缺乏的时候会将它杀死。
- 停止：如果一个活动被另一个全屏活动完全覆盖，那么该活动处于停止状态（状态和成员信息会保留，但是 Activity 已经不再依附于 WindowManager 了）。同时，在系统缺乏资源的时候会将它杀死（它会比暂停状态的活动先杀死）。
- 重启：如果一个活动在处于停止或者暂停的状态下，系统内存缺乏时会将其结束（finish）或者杀死（kill）。这种非正常情况下，系统在杀死或者结束之前会调用 `onSaveInstanceState()` 方法来保存信息，同时，当 Activity 被移动到前台时，重新启动该Activity并调用 `onRestoreInstanceState()` 方法加载保留的信息，以保持原有的状态。

在上面的四中常有的状态之间，还有着其他的生命周期来作为不同状态之间的过度，用于在不同的状态之间进行转换。

![Activity 生命周期](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity_intro/activity_lifecycle.png)

正常情况下的生命周期：

- onCreate()：与 onDestroy() 配对，表示 Activity 正在被创建，这是生命周期的第一个方法。

  在这个方法中可以做一些初始化的工作（加载布局资源、初始化 Activity 所需要的数据等），耗时的工作在异步线程上完成。

- onRestart()：表示 Activity 正在重新启动。

  一般情况下，在当前 Activity 从不可见重新变为可见的状态时 onRestart() 就会被调用。这种情形一般是由于用户的行为所导致的，比如用户按下 Home 键切换到桌面或者打开了一个新的 Activity（这时当前 Activity 会暂停，也就是 onPause() 和 onStop() 被执行），接着用户有回到了这个 Activity，就会出现这种情况。

- onStart()：与 onStop() 配对，表示 Activity 正在被启动，并且即将开始。

  但是这个时候要注意它与 onResume() 的区别。两者都表示 Activity 可见，但是 onStart() 时 Activity 还正在加载其他内容，正在向我们展示，用户还无法看到，即无法交互。

- onResume()：与 onPause() 配对，表示 Activity 已经创建完成，并且可以开始活动了，这个时候用户已经可以看到界面了，并且即将与用户交互（完成该周期之后便可以响应用户的交互事件了）。

- onPause()：与 onResume() 配对，表示 Activity 正在暂停，正常情况下，onStop() 接着就会被调用。

  在特殊情况下，如果这个时候用户快速地再回到当前的 Activity，那么 onResume() 会被调用（极端情况）。一般来说，在这个生命周期状态下，可以做一些存储数据、停止动画的工作，但是不能太耗时，如果是由于启动新的 Activity 而唤醒的该状态，那会影响到新 Activity 的显示，原因是 onPause() 必须执行完，新的 Activity的 onResume() 才会执行。

- onStop()：与 onStart() 配对，表示 Activity 即将停止，可以做一些稍微重量级的回收工作，同样也不能太耗时（可以比 onPause 稍微好一点）。

- onDestroy()：与 onCreate() 配对，表示 Activity 即将被销毁，这是 Activity 生命周期的最后一个回调，我们可以做一些回收工作和最终的资源释放（如 Service、BroadReceiver、Map 等）。

## 启动模式

Activity 的启动模式有4种，分别是 Standard、SingleTop、SingleTask、SingleInstance。可以在 `AndroidMainifest.xml` 文件中指定每一个 Activity 的启动模式。

一个 Android 应用一般都会有多个 Activity，系统会通过任务栈来管理这些 Activity，栈是一种后进先出的集合，当前的 Activity 就在栈顶，按返回键，栈顶 Activity 就会退出。Activity 启动模式不同，系统通过任务栈管理 Activity 的方式也会不同，以下将分别介绍。

- Standard

Standard 模式是 Android 的默认启动模式，你不在配置文件中做任何设置，那么这个 Activity 就是 Standard 模式。这种模式下，Activity 可以有多个实例，每次启动 Activity，无论任务栈中是否已经有这个 Activity 的实例，系统都会创建一个新的 Activity 实例。

- SingleTop

SingleTop 模式和 Standard 模式非常相似，主要区别就是当一个 SingleTop 模式的 Activity 已经位于任务栈的栈顶，再去启动它时，不会再创建新的实例。如果不位于栈顶，就会创建新的实例。

- SingleTask

SingleTask 模式的 Activity 在同一个 Task 内只有一个实例。如果 Activity 已经位于栈顶，系统不会创建新的 Activity 实例，和 SingleTop 模式一样。但 Activity 已经存在但不位于栈顶时，系统就会把该 Activity 移到栈顶，并把它上面的 Activity 出栈。

- SingleInstance

SingleInstance 模式也是单例的，但和 SingleTask 不同，SingleTask 只是任务栈内单例，系统里是可以有多个 SingleTask Activity 实例的，而 SingleInstance Activity 在整个系统里只有一个实例，启动一个SingleInstance 的 Activity 时，系统会创建一个新的任务栈，并且这个任务栈只有他一个 Activity。

SingleInstance 模式并不常用，如果我们把一个 Activity 设置为 SingleInstance 模式，你会发现它启动时会慢一些，切换效果不好，影响用户体验。它往往用于多个应用之间，例如一个电视 Launcher 里的 Activity，通过遥控器某个键在任何情况可以启动，这个 Activity 就可以设置为 SingleInstance 模式，当在某应用中按键启动这个 Activity，处理完后按返回键，就会回到之前启动它的应用，不影响用户体验。

## 任务与返回栈

一个应用程序当中通常会包含多个 Activity，每个 Activity 都应该设计成可以执行用户特定的操作，并且能够启动其他 Activity。比如，电子邮件应用可能有一个 Activity 显示新邮件列表。用户选择某个邮件时，会打开一个新的 Activity 来查看该邮件。

一个 Activity 甚至可以启动设备上其他应用中的 Activity。比如，如果当前应用想要发送电子邮件，就可以发送一个 Intent 添加一些数据（如邮箱和邮件内容等）。然后，系统将打开其他应用中已经声明可以处理该 Intent 的 Activity，如果有多个系统则让用户选择要使用的 Activity。即使这两个 Activity 可能来自不同的应用，但是 Android 仍会将 Activity 保留在相同的*任务*中，以维护这种无缝的用户体验。

任务是指在执行特定作业时与用户交互的一系列 Activity。 这些 Activity 按照各自的打开顺序排列在堆栈（即*返回栈*）中。

设备主屏幕是大多数任务的起点。当用户触摸应用启动器中的图标（或主屏幕上的快捷方式）时，该应用的任务将出现在前台。 如果应用不存在任务（应用最近未曾使用），则会创建一个新任务，并且该应用的“主” Activity 将作为堆栈中的根 Activity 打开。

当前 Activity 启动另一个 Activity 时，该新 Activity 会被推送到堆栈顶部，并获取焦点。前一个 Activity 仍保留在堆栈中，但是处于停止状态。Activity 停止时，系统会保持其用户界面的当前状态。 用户按「返回」按钮时，当前 Activity 会从堆栈顶部弹出（Activity 被销毁），而前一个 Activity 恢复执行（恢复其 UI 的前一状态）。

 堆栈中的 Activity 永远不会重新排列，仅推入和弹出堆栈：由当前 Activity 启动时推入堆栈；用户使用「返回」按钮退出时弹出堆栈。 因此，返回栈以「后进先出」对象结构运行。 如下图：

![Activity 返回栈](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity_intro/diagram_backstack.png)

如果用户继续按「返回」，堆栈中的相应 Activity 就会弹出，以显示前一个 Activity，直到用户返回主屏幕为止（或者，返回任务开始时正在运行的任意 Activity）。 当所有 Activity 均从堆栈中移除后，任务即不复存在。

任务是一个有机整体，当用户开始新任务或通过「主页」按钮转到主屏幕时，可以移动到「后台」。 尽管在后台时，该任务中的所有 Activity 全部停止，但是任务的返回栈仍旧不变，也就是说，当另一个任务发生时，该任务仅仅失去焦点而已，如下图所示。然后，任务可以返回到「前台」，用户就能够回到离开时的状态。

![Activity 多任务栈](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity_intro/diagram_multitasking.png)

例如，假设当前任务（任务 A）的堆栈中有三个 Activity，即当前 Activity 下方还有两个 Activity。 用户先按「主页」按钮，然后从应用启动器启动新应用。 显示主屏幕时，任务 A 进入后台。新应用启动时，系统会使用自己的 Activity 堆栈为该应用启动一个任务（任务 B）。与该应用交互之后，用户再次返回主屏幕并选择最初启动任务 A 的应用。现在，任务 A 出现在前台，其堆栈中的所有三个 Activity 保持不变，而位于堆栈顶部的 Activity 则会恢复执行。 此时，用户还可以通过转到主屏幕并选择启动该任务的应用图标（或者，通过从「屏幕预览」择该应用的任务）切换回任务 B。这就是 Android 系统中的多任务的场景。

无论 Activity 是在新任务中启动，还是在与启动 Activity 相同的任务中启动，用户按「返回」按钮始终会转到前一个 Activity。 但是，如果启动指定 `singleTask` 启动模式的 Activity，则当某后台任务中存在该 Activity 的实例时，整个任务都会转移到前台。此时，返回栈包括上移到堆栈顶部的任务中的所有 Activity，如下图：

![Activity SingleTask 任务栈](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity_intro/diagram_backstack_singletask_multiactivity.png)

## 保存与恢复

Activity 为我们提供了两个回调方法 onSaveInstanceState() 和 onRestoreInstanceState() 用于当 Activity 在不是用户主动意识关闭的情况下来进行页面数据的保存和恢复。

![Activity 保存与恢复](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_activity_intro/basic-lifecycle-savestate.png)

那么那些情况下 onSaveInstanceState() 会被调用呢？分别有以下几种情况：

- 当用户按下 Home 键 App 处于后台，此时会调用 onSaveInstanceState() 方法。
- 当用户按下电源键时，会调用 onSaveInstanceState() 方法。
- 当 Activity 进行横竖屏切换的时候也会调用 onSaveInstanceState() 方法。
- 从 AActivity 跳转到 BActivity 的时候 AActivity 也会调用 onSaveInstanceState() 方法。

虽然以上四种情况会执行 onSaveInstanceState() 方法 但是并不是都会执行 onRestoreInstanceState() 方法，只有第三种情况会调用 onRestoreInstanceState()，因为当 Activity 横竖屏切换的时候会重新走一遍生命周期，所以 Activity 会被销毁创建，由此会执行 onRestoreInstanceState() 方法。

也就是说 onSaveInstanceState 和 onRestoreInstanceState 并不是一定成双出现的，终于当 Activity 真正的被销毁的时候才会执行 onRestoreInstanceState()。

而其他情况 Activity 只是暂居后台，并没有被销毁，所以系统不会调用 onRestoreInstanceState()。

保存数据：

```java
@Override
public void onSaveInstanceState(Bundle savedInstanceState) {
    // 保存数据
    savedInstanceState.putString("data", "这是保存的数据");

    super.onSaveInstanceState(savedInstanceState);
}
```

恢复数据：

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    // 恢复数据
    if (savedInstanceState != null) {
        String data = savedInstanceState.getInt("data");
    }
}

@Override
public void onRestoreInstanceState(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    // 也可以在 onRestoreInstanceState() 方法中恢复数据
    if (savedInstanceState != null) {
        String data = savedInstanceState.getInt("data");
    }
}
```

## Intent

Intent 分两种，显式 Intent 和隐式 Intent。如果一个 Intent 明确指定了要启动的组件的完整类名，那么这个 Intent 就是显式 Intent，否则就是隐式 Intent。

当我们用一个显式 Intent 去启动组件时，Android 会根据 Intent 对象所提供的 component name 直接找到要启动的组件，当我们用一个隐式的 Intent 去启动组件时，Android 系统就无法直接知道要启动的组件名称了。

### 显式 Intent

```java
Intent intent = new Intent(this, xxx.class);
startActivity(intent);
```

### 隐式 Intent

使用隐式 Intent 之前需要在 AndroidManifest.xml 中对标签增加设置。

```xml
<activity android:name=".ui.activity.IntentActivity">
    <intent-filter>
        <action android:name="com.jeanboy.action.TEST" />
    </intent-filter>
</activity>
```

使用隐式 Intent 跳转 Activity。

```java
Intent intent = new Intent("com.jeanboy.action.TEST");
startActivity(intent);
```

### Intent Filter

如果 Intent 中的存在 category 那么所有的 category 都必须和 Activity 过滤规则中的 category 相同。才能和这个 Activity 匹配。Intent 中的 category 数量可能少于 Activity 中配置的 category 数量，但是 Intent 中的这 category 必须和 Activity 中配置的 category 相同才能匹配。

```xml
<activity android:name=".ui.activity.IntentActivity">
    <intent-filter>
        <action android:name="com.jeanboy.action.TEST" />
        <category android:name = "android.intent.category.DEFAULT" />
        <category android:name="aaa.bb.cc"/>
    </intent-filter>
</activity>
```

运行以下代码可以匹配到 IntentActivity：

```java
Intent intent = new Intent("com.jeanboy.action.TEST");
intent.addCategory("aaa.bb.cc");
startActivity(intent);
```

只通过 category 匹配是无法匹配到 IntentActivity 的，因为 category 属性是一个执行 Action 的附加信息。

### URL Scheme

Android 中的 Scheme 是一种页面内跳转协议，是一种非常好的实现机制。通过定义自己的 Scheme 协议，可以非常方便跳转 App 中的各个页面。

使用场景：

- 通过小程序，利用 Scheme 协议打开原生 App。
- H5 页面点击锚点，根据锚点具体跳转路径 App 端跳转具体的页面。
- App 端收到服务器端下发的 Push 通知栏消息，根据消息的点击跳转路径跳转相关页面。
- App 根据URL跳转到另外一个 App 指定页面。
- 通过短信息中的 URL 打开原生 App。

Scheme 路径的规则：

> \<scheme\> :// \<host\> : \<port\> [\<path\>|\<pathPrefix\>|\<pathPattern\>]

设置 Scheme

在 AndroidManifest.xml 中对标签增加设置 Scheme。

```xml
<activity
    android:name=".ui.activity.SchemeActivity"
    android:screenOrientation="portrait">
    <!--Android 接收外部跳转过滤器-->
    <!--要想在别的 App 上能成功调起 App，必须添加 intent 过滤器-->
    <intent-filter>
        <!--协议部分配置，注意需要跟 web 配置相同-->
        <!--协议部分，随便设置 aa://bb:1024/from?type=jeanboy-->
        <data android:scheme="aa"
            android:host="bb"
            android:port="1024"
            android:path="/from"/>
        <!--下面这几行也必须得设置-->
        <category android:name="android.intent.category.DEFAULT" />
        <!--表示 Activity 允许通过网络浏览器启动，以显示链接方式引用，如图像或电子邮件-->
        <category android:name="android.intent.category.BROWSABLE" />
        <action android:name="android.intent.action.VIEW" />
    </intent-filter>
</activity>
```

原生调用：

```java
Uri uri = Uri.parse("aa://bb:1024/from?type=jeanboy");
Intent intent = new Intent(Intent.ACTION_VIEW, uri);
startActivity(intent);
```

网页调用：

```html
<a href="aa://bb:1024/from?type=jeanboy">打开 App</a>
```

在 SchemeActivity 中可以处理 Scheme 跳转的参数：

```java
public class SchemeActivity extends AppCompatActivity {

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Uri uri = getIntent().getData();
        if (uri != null) {
            //获取指定参数值
            String type = uri.getQueryParameter("type");
            Log.e("SchemeActivity", "type:" + type);

            if(type.equals("jeanboy")){
                ActivityUtils.startActivity(XXXActivity.class);
            }else if(type.equals("main")){
                ActivityUtils.startActivity(MainActivity.class);
            }
        }
        finish();
    }
}
```

如何判断一个 Scheme 是否有效：

```java
PackageManager packageManager = getPackageManager();
Uri uri = Uri.parse("aa://bb:1024/from?type=jeanboy");
Intent intent = new Intent(Intent.ACTION_VIEW, uri);
List<ResolveInfo> activities = packageManager.queryIntentActivities(intent, 0);
boolean isValid = !activities.isEmpty();
if (isValid) {
    startActivity(intent);
}
```

## startActivityForResult()

如果想在 Activity 中得到新打开 Activity 关闭后返回的数据，需要使用系统提供的 `startActivityForResult()` 方法打开新的 Activity，新的 Activity 关闭后会向前面的 Activity 传回数据。

```java
@Override
public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    //...
    int resultCode = 1;
    startActivityForResult(new Intent(this, OtherActivity.class), resultCode);
}

/**
 * 接收 OtherActivity 返回的数据
 */
@Override
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    String result = data.getExtras().getString("result");
}
```

为了得到传回的数据，必须在前面的 Activity 中重写 `onActivityResult()` 方法。

```java
Intent intent = new Intent();
// 把返回数据存入 Intent
intent.putExtra("result", "我是返回数据");
// 设置返回数据
setResult(RESULT_OK, intent);
// 关闭当前 Activity
finish();
```

## 常见面试题

- 启动一个 Activity 的生命周期？

  例如：A 启动 B，生命周期如下

  ```json
  A: ==> onCreate()
  A: ==> onStart()
  A: ==> onResume()
  A: ==> onPause()
  
  B: ==> onCreate()
  B: ==> onStart()
  B: ==> onResume()
  
  A: ==> onStop()
  ```

- 下拉通知栏对生命周期的影响？

  没有影响！

- AlertDialog（对话框）对生命周期的影响？

  没有影响！

- Toast 对生命周期的影响？

  没有影响！

- 透明主题的 Activity 对生命周期的影响？

  ```json
  A: ==> onCreate()
  A: ==> onStart()
  A: ==> onResume()
  如果弹出透明 Activity
  A: ==> onPause()
  ```

- 屏幕旋转对生命周期的影响？

  没有配置 configChanges：

  ```json
  A: ==> onCreate()
  A: ==> onStart()
  A: ==> onResume()
  A: ==> onPause()
  A: ==> onSaveInstanceState()
  A: ==> onStop()
  A: ==> onDestroy()
  屏幕旋转后
  A: ==> onCreate()
  A: ==> onStart()
  A: ==> onRestoreInstanceState()
  A: ==> onResume()
  ```
  
  配置 configChanges 后：
  
  ```json
  A: ==> onCreate()
  A: ==> onStart()
  A: ==> onResume()
  A: ==> onConfigurationChanged()
  ```

## 参考资料

- [Android 官方文档 - Activity 生命周期](https://developer.android.com/guide/components/activities/activity-lifecycle?hl=zh-cn)
- [Android 官方文档 - 任务和返回栈](https://developer.android.com/guide/components/activities/tasks-and-back-stack?hl=zh-cn)

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！