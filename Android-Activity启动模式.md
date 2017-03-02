# Android-Activity启动模式 #
<br>
## 概述 ##
每个应用都会有多个 Activity，Android 中使用栈来管理 Activity。 Activity 的启动模式目前有四种：standard、singleTop、singleTask、singleIntance。


## 1. standard ##
![图1][1]

- 标准模式，也就是系统的默认模式。
- 每次启动都会重新创建一个实例，不管这个 Activity 在栈中是否已经存在。
- 谁启动了这个Activity，那么 Activity 就运行在启动它的那个 Activity 所在的栈中。

	> 用 Application 去启动 Activity 时会报错，提示非 Activity 的 Context没有所谓的任务栈。
	> 解决办法是为待启动 Activity 指定 **FLAG_ACTIVITY_NEW_TASK** 标志位，这样就会为它创建一个新的任务栈。

## 2. singleTop ##
![图2][2]



- 栈顶复用模式，在这种模式下，如果新 Activity 位于任务栈的栈顶，那么此 Activity 不会被重新创建，同时回调 **onNewIntent** 方法。
- 如果新 Activity 已经存在但不是位于栈顶，那么新 Activity 仍然会被创建。

## 3. singleTask & singleIntance ##
![图3][3]


#### singleTask ####
- 栈内复用模式，这是一种单实例模式，在这种模式下，只要 Activity 在栈中存在，那么多次启动这个 Activity 都不会重新创建实例，同时也会回调 **onNewIntent** 方法。 同时会导致在 Activity 之上的栈内 Activity 出栈。
- 如果 Activity 不存在重新创建。

#### singleIntance ####
- 单实例模式，这是一种加强的 singleTask 模式。 具有 singleTask 模式的所有特性外，同时具有此模式的 Activity 只能单独的位于一个任务栈中。

## 4. 其他情况 ##
![图4][4]
假设目前有2个任务栈，前台任务栈的情况为 AB，而后台任务栈的情况为 CD，这里假设 CD 的启动模式为 singleTask。 现在请求启动 D，那么整个后台的任务栈都会被切换到前台，这个时候整个后退列表变成了 ABCD。 当用户按 back 键的时候，列表中的 Activity 会一一出栈。
## 5. TaskAffinity属性 ##
TaskAffinity 参数标识了一个 Activity 所需要的任务栈的名字。 为字符串，且中间必须包含包名分隔符“.”。默认情况下，所有 Activity 所需的任务栈名字为应用包名。

TashAffinity 属性主要和 singleTask 启动模式或者 allowTaskReparenting 属性配对使用，其他情况下没有意义。

> 应用 A 启动了应用 B 的某个 Activity 后，如果 Activity 的 allowTaskReparenting 属性为 true 的话，那么当应用 B 被启动后，此 Activity 会直接从应用 A 的任务栈转移到应用 B 的任务栈中。

打个比方就是，应用 A 启动了应用 B 的 ActivityX，然后按 Home 回到桌面，单击应用 B 的图标，这时并不会启动 B 的主 Activity，而是重新显示已经被应用 A 启动的 ActivityX。 这是因为 ActivityX 的 TaskAffinity 值肯定不和应用 A 的任务栈相同（因为包名不同）。 所以当应用  B被启动以后，发现 ActivityX 原本所需的任务栈已经被创建了，所以把 ActivityX 从 A 的任务栈中转移过来了。


## 6. 设置启动模式 ##
1. manifest中 设置下的 android:**launchMode** 属性。
2. 启动 Activity 的 **intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);** 。
3. 两种同时存在时，以第二种为准。 第一种方式无法直接为 Activity 添加 **FLAG_ACTIVITY_CLEAR_TOP** 标识，第二种方式无法指定 singleInstance 模式。
4. 可以通过命令行 adb shell dumpsys activity 命令查看栈中的 Activity 信息。

#### Activity的Flags ####
这些FLAG可以设定启动模式、可以影响Activity的运行状态。

- **FLAG_ACTIVITY_CLEAR_TOP** 具有此标记位的 Activity 启动时，同一个任务栈中位于它
上面的 Activity 都要出栈，一般和 FLAG_ACTIVITY_NEW_TASK 配合使用。效果和 singleTask 一样。

- **FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS** 如果设置，新的 Activity 不会在最近启动的 Activity 的列表（就是安卓手机里显示最近打开的 Activity 那个系统级的UI）中保存。




[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/01.jpg
[2]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/02.jpg
[3]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/03.jpg
[4]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/04.jpg