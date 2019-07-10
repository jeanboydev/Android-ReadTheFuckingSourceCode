# Activity 的 Task 亲和关系

## launchMode

```xml
<activity
		android:name=".ui.activity.TaskAffinityActivity"
		android:launchMode="singleTask" />
```

- standard
- singleTop
- singleTask
- singleInstance

默认模式是 `standard`，这些模式分为两大类，`standard` 和 `singleTop` Activity 为一类，`singleTask` 和 `singleInstance` 为另一类。

使用 `standard` 或 `singleTop` 启动模式的 Activity 可多次实例化。 实例可归属任何 Task（任务栈），并且可以位于 Activity 堆栈中的任何位置。它们通常启动到名为 `startActivity()` 的 Task（任务栈）之中（除非 Intent 对象包含 `FLAG_ACTIVITY_NEW_TASK` 指令）。

相比之下，`singleTask` 和 `singleInstance` Activity 只能启动 Task（任务栈）。 它们始终位于 Activity 堆栈的根位置。此外，设备一次只能保留一个 Activity 实例，只允许有一个此类 Task（任务栈）。

`singleTask` Activity 允许其他 Activity 成为其 Task（任务栈）的组成部分。 它始终位于其任务的根位置，但其他 Activity（必然是 `standard` 和 `singleTop` Activity）可以启动到该 Task（任务栈）中。 

相反， `singleInstance` Activity 则不允许其他 Activity 成为其 Task（任务栈）的组成部分。它是 Task（任务栈）中唯一的 Activity。 如果它启动另一个 Activity，系统会将该 Activity 分配给其他 Task（任务栈），就好像 Intent 中包含 `FLAG_ACTIVITY_NEW_TASK` 一样。

## taskAffinity

```xml
<activity
		android:name=".ui.activity.TaskAffinityActivity"
		android:launchMode="singleTask"
		android:taskAffinity="com.jeanboy.task.test" />
```

除了 launchMode 可以用来调配 Task（任务栈），Activity 的另一属性 taskAffinity，也是常常被使用。

taskAffinity 是一种物以类聚的思想，它倾向于将 taskAffinity 属性相同的 Activity，扔进同一个 Task 中。不过，它的约束力比 launchMode 弱了许多。只有将 allowTaskReparenting 属性设置为 true，或者调用方将 Intent 的 flag 添加 FLAG_ACTIVITY_NEW_TASK 属性时才会生效。

每个 Activity 都有 taskAffinity 属性，这个属性表示了该 Activity 希望进入的 Task（任务栈）。

默认情况下，同一个应用中的所有 Activity 都具有相同的 taskAffinity（亲和关系）。我们可以设置该属性来以不同方式组合它们，甚至可以将不同应用中的 Activity 组合到同一个 Task（任务栈）内。 如果要指定 Activity 与任何 Task（任务栈）均无 taskAffinity（亲和关系），设置为空字符串即可。

如果一个 Activity 没有显式的指明该 Activity 的 taskAffinity 值，那么它的这个属性就等于 Application 指明的 taskAffinity。如果 Application 也没有指明，那么该 taskAffinity 的值就等于包名。

而 Task（任务栈）也有自己的 taskAffinity 属性，它的值默认等于它的根 Activity 的 taskAffinity 值。

### 示例验证

首先我们创建一个应用 Task2。Task2 有 MainActivity、SingleTaskActivity 两个 Activity，其中 SingleTaskActivity 配置如下：

```xml
<activity android:name=".SingleTaskActivity"
          android:launchMode="singleTask"
          android:taskAffinity="com.jeanboy.app.task.other2"/>
```

首先我们在 MainActivity 启动 SingleTaskActivity。

然后在控制台使用下面命令来查看 Task（任务栈）的状态信息，通过观察 Task 的信息来验证上面的理论。

> adb shell dumpsys activity

通过命令可以看到如下信息（这里删减了不重要的信息）：

```java
ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)
Display #0 (activities from top to bottom):
  Stack #1:
    Task id #222
      TaskRecord{2dd0b176 #222 A=com.jeanboy.app.task.other2 U=0 sz=1}
        Hist #0: ActivityRecord{35b3fc43 u0 com.jeanboy.app.task2/.SingleTaskActivity t222}
    Task id #221
      TaskRecord{f31b377 #221 A=com.jeanboy.app.task2 U=0 sz=1}
        Hist #0: ActivityRecord{37c25eb6 u0 com.jeanboy.app.task2/.MainActivity t221}
```

可以清楚的看到两个任务栈，Task（任务栈）#222，栈名为 `com.jeanboy.app.task.other2`；Task（任务栈）#222，栈名为 `com.jeanboy.app.task2`。

到此我们也明白了，我们确实可以通过 `singleTask` 与 `android:taskAffinity` 属性相结合的方式来指定我们 Activity 所需要的栈名称，使相应的 Activity 存在于不同的栈中。

## allowTaskReparenting

```xml
<activity
		android:name=".ui.activity.TaskAffinityActivity"
		android:launchMode="standard"
		android:taskAffinity="com.jeanboy.task.test"
		android:allowTaskReparenting="true" />
```

allowTaskReparenting 表示当某个拥有相同 taskAffinity（亲和关系） 的 Task（任务栈）即将返回前台时，Activity 是否能从启动时的 Task（任务栈）转移至此 Task（任务栈）中去。`true` 表示可以移动，`false` 表示它必须留在启动时的 Task（任务栈）中。

正常情况下，当 Activity 启动时，会与启动它的 Task（任务栈）关联，并在其整个生命周期中一直留在该 Task（任务栈）中。我们可以使用该属性强制将 Activity 在当前 Task（任务栈）不显示时，归属到另一个与它  taskAffinity（亲和关系） 相同的 Task（任务栈）。该属性通常用于让一个应用程序的 Activity 转移到另一个应用程序关联的主 Task（任务栈）中去。

Activity 的亲和关系由 taskAffinity 属性定义。 Task（任务栈）的亲和关系由根 Activity 的 taskAffinity 确定。 然而，根据规定，根 Activity 总是位于 taskAffinity 同名的任务中。 因为以 `singleTask` 和 `singleInstance` 模式启动的 Activity 只能位于任务的根部， 所以 Activity 的 `allowTaskReparenting` 仅限于 `standard` 和 `singleTop` 启动模式中使用。

> 例如，如果电子邮件包含网页链接，则点击链接会调出可显示网页的 Activity。 该 Activity 由浏览器应用定义，但作为电子邮件任务的一部分启动。
>
>  如果将它归属到浏览器 Task（任务栈），那么它会在浏览器下一次转至前台时显示，当电子邮件 Task（任务栈）再次转至前台时则会消失。

![allowTaskReparenting](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/08_task_affinity/01.jpg)

### 示例验证

首先我们创建两个应用 Task1、Task2，Task1 中有 MainActivity，Task2 有 AllowActivity 默认启动模式，并设置 `allowTaskReparenting="true"`。

首先我们在 Task1 中 启动 Task2 的 AllowActivity。

我们在控制台使用下面命令来查看 Task（任务栈）的状态信息，通过观察 Task 的信息来验证上面的理论。

> adb shell dumpsys activity

通过命令可以看到如下信息（这里删减了不重要的信息）：

```java
ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)
Display #0 (activities from top to bottom):
  Stack #1:
    Task id #219
      TaskRecord{21746940 #219 A=com.jeanboy.app.task1 U=0 sz=2}
        Hist #1: ActivityRecord{31f54e4e u0 com.jeanboy.app.task2/.AllowActivity t219}
        Hist #0: ActivityRecord{37ed66dd u0 com.jeanboy.app.task1/.MainActivity t219}
```

可以看到 Task（任务栈）#219 中有 MainActivity、AllowActivity 两个 Activity，然后我们点击 Home 后，再打开 Task2。

打开 Task2 后可以看到直接打开了 AllowActivity，通过命令可以看下信息：

```java
ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)
Display #0 (activities from top to bottom):
  Stack #1:
    Task id #220
      TaskRecord{12b34f0b #220 A=com.jeanboy.app.task2 U=0 sz=2}
        Hist #1: ActivityRecord{31f54e4e u0 com.jeanboy.app.task2/.AllowActivity t220}
        Hist #0: ActivityRecord{2dbef71e u0 com.jeanboy.app.task2/.MainActivity t220}
    Task id #219
      TaskRecord{21746940 #219 A=com.jeanboy.app.task1 U=0 sz=1}
        Hist #0: ActivityRecord{37ed66dd u0 com.jeanboy.app.task1/.MainActivity t219}
```

可以看到 AllowActivity 被转移到了  Task（任务栈）#220 中，也就是 Task2 应用所在的任务栈中，也就验证了上面的理论。 

## FLAG_ACTIVITY_NEW_TASK

```java
Intent intent = new Intent(this, TaskAffinityActivity.class);
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
startActivity(intent);
```

如果设置了 `FLAG_ACTIVITY_NEW_TASK` 标识，意思是把将要启动的 Activity 放在一个新 Task（任务）中。

设置 `FLAG_ACTIVITY_NEW_TASK` 标识后，首先会查找是否存在和被启动的 Activity 具有相同的  taskAffinity（亲和关系）的 Task（任务栈）（注意同一个应用程序中的 Activity 的 taskAffinity 一样）。如果有，则直接把这个 Task（任务栈）整体移动到前台，并保持栈中的状态不变，即 Task（任务栈）中的 Activity 顺序不变；如果没有，则新建一个 Task（任务栈）来存放被启动的 Activity。

## 参考资料

- [官方文档](https://developer.android.com/guide/topics/manifest/activity-element.html)
- [Android 的 taskAffinity 对四种 launchMode 的影响](https://www.cnblogs.com/yyz666/p/4674173.html)
- [Android 之Activity启动模式(二)之 Intent的Flag属性](https://wangkuiwu.github.io/2014/06/26/IntentFlag/)
- [singleTask 与 taskAffinity 缠绵的那些事](https://blog.csdn.net/dfqin/article/details/7481683)
- [基础总结篇之二：Activity的四种launchMode](https://blog.csdn.net/liuhe688/article/details/6754323)
- [Activity 启动模式与任务栈 (Task) 全面图文深入记录](https://juejin.im/entry/57ac05858ac247005fec2ca1)