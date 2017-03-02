# Android-Activity启动模式 #
<br>
## 概述 ##
每个应用都会有多个 Activity，Android 中使用栈来管理 Activity。 Activity 的启动模式目前有四种：standard、singleTop、singleTask、singleIntance。


## 1. standard ##
![图1][1]

- 标准模式，也就是系统的默认模式。
- 每次启动都会重新创建一个实例，不管这个 Activity 在栈中是否已经存在。
- 谁启动了这个Activity，那么 Activity 就运行在启动它的那个 Activity 所在的栈中。

> 用Application去启动Activity时会报错，提示非Activity的Context没有所谓的任务栈。
> 解决办法是为待启动Activity制定FLAG_ACTIVITY_NEW_TASH标志位，这样就会为它创建一个新的任务栈。

2 singleTop
如果新Activity位于任务栈的栈顶，那么此Activity不会被重新创建，同时回
调 onNewIntent 方法。
如果新Activity已经存在但不是位于栈顶，那么新Activity仍然会被创建。
3 singleTask
这是一种单实例模式
只要Activity在栈中存在，那么多次启动这个Activity都不会重新创建实例，同时也会回
调 onNewIntent 方法。
同时会导致在Activity之上的栈内Activity出栈。
4 singleIntance
具有singleTask模式的所有特性，同时具有此模式的Activity只能单独的位于一个任务栈中
TaskAffinity属性
TaskAffinity参数标识了一个Activity所需要的任务栈的名字。为字符串，且中间必须包含包名
分隔符“.”。默认情况下，所有Activity所需的任务栈名字为应用包名。TashAffinity属性主要和
singleTask启动模式或者 allowTaskReparenting 属性配对使用，其他情况下没有意义。 应用A
启动了应用B的某个Activity后，如果Activity的allowTaskReparenting属性为true的话，那么当
应用B被启动后，此Activity会直接从应用A的任务栈转移到应用B的任务栈中。 打个比方就
是，应用A启动了应用B的ActivityX，然后按Home回到桌面，单击应用B的图标，这时并不会
启动B的主Activity，而是重新显示已经被应用A启动的ActivityX。这是因为ActivityX的
TaskAffinity值肯定不和应用A的任务栈相同（因为包名不同）。所以当应用B被启动以后，发
现ActivityX原本所需的任务栈已经被创建了，所以把ActivityX从A的任务栈中转移过来了。
设置启动模式
1. manifest中 设置下的 android:launchMode 属性。
2. 启动Activity的 intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); 。
3. 两种同时存在时，以第二种为准。第一种方式无法直接为Activity添加
FLAG_ACTIVITY_CLEAR_TOP标识，第二种方式无法指定singleInstance模式。
4. 可以通过命令行 adb shell dumpsys activity 命令查看栈中的Activity信息。
Activity的生命周期和启动模式
6
1.2.2 Activity的Flags
这些FLAG可以设定启动模式、可以影响Activity的运行状态。
FLAG_ACTIVITY_CLEAR_TOP 具有此标记位的Activity启动时，同一个任务栈中位于它
上面的Activity都要出栈，一般和FLAG_ACTIVITY_NEW_TASK配合使用。效果和
singleTask一样。
FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS 如果设置，新的Activity不会在最近启
动的Activity的列表(就是安卓手机里显示最近打开的Activity那个系统级的UI)中保存。




[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/01.jpg
[2]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/02.jpg
[3]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/03.jpg
[4]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_task_launch_modes/04.jpg