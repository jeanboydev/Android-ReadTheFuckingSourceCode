# Android - Activity LaunchMode 启动模式 & IntentFilter 匹配规则

## 概述 ##
每个应用都会有多个 Activity，Android 中使用栈来管理 Activity。 Activity 的启动模式目前有四种：standard、singleTop、singleTask、singleIntance。


## Activity 启动模式
### 1. standard
![图1][1]

- 标准模式，也就是系统的默认模式。
- 每次启动都会重新创建一个实例，不管这个 Activity 在栈中是否已经存在。
- 谁启动了这个 Activity，那么 Activity 就运行在启动它的那个 Activity 所在的栈中。

	> 用 Application 去启动 Activity 时会报错，提示非 Activity 的 Context没有所谓的任务栈。
	> 解决办法是为需要启动的 Activity 指定 **FLAG_ACTIVITY_NEW_TASK** 标志位，这样就会为它创建一个新的任务栈。


### 2. singleTop
![图2][2]



- 栈顶复用模式，在这种模式下，如果新 Activity 位于任务栈的栈顶，那么此 Activity 不会被重新创建，同时回调 **onNewIntent** 方法。
- 如果新 Activity 已经存在但不是位于栈顶，那么新 Activity 仍然会被创建。


### 3. singleTask & singleIntance
![图3][3]


#### singleTask
- 栈内复用模式，这是一种单实例模式，在这种模式下，只要 Activity 在栈中存在，那么多次启动这个 Activity 都不会重新创建实例，同时也会回调 **onNewIntent** 方法。 同时会导致在 Activity 之上的栈内 Activity 出栈。
- 如果 Activity 不存在重新创建。

#### singleIntance
- 单实例模式，这是一种加强的 singleTask 模式。 具有 singleTask 模式的所有特性外，同时具有此模式的 Activity 只能单独的位于一个任务栈中。


### 4. 其他情况
![图4][4]
假设目前有2个任务栈，前台任务栈的情况为 AB，而后台任务栈的情况为 CD，这里假设 CD 的启动模式为 singleTask。 现在请求启动 D，那么整个后台的任务栈都会被切换到前台，这个时候整个后退列表变成了 ABCD。 当用户按 back 键的时候，列表中的 Activity 会一一出栈。


### 5. TaskAffinity 属性
TaskAffinity 参数标识了一个 Activity 所需要的任务栈的名字。 为字符串，且中间必须包含包名分隔符“.”。默认情况下，所有 Activity 所需的任务栈名字为应用包名。

TashAffinity 属性主要和 singleTask 启动模式或者 allowTaskReparenting 属性配对使用，其他情况下没有意义。

> 应用 A 启动了应用 B 的某个 Activity 后，如果 Activity 的 allowTaskReparenting 属性为 true 的话，那么当应用 B 被启动后，此 Activity 会直接从应用 A 的任务栈转移到应用 B 的任务栈中。

打个比方就是，应用 A 启动了应用 B 的 ActivityX，然后按 Home 回到桌面，单击应用 B 的图标，这时并不会启动 B 的主 Activity，而是重新显示已经被应用 A 启动的 ActivityX。 这是因为 ActivityX 的 TaskAffinity 值肯定不和应用 A 的任务栈相同（因为包名不同）。 所以当应用  B被启动以后，发现 ActivityX 原本所需的任务栈已经被创建了，所以把 ActivityX 从 A 的任务栈中转移过来了。


### 6. 设置启动模式
1. manifest中 设置下的 android:**launchMode** 属性。
2. 启动 Activity 的 **intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);** 。
3. 两种同时存在时，以第二种为准。 第一种方式无法直接为 Activity 添加 **FLAG_ACTIVITY_CLEAR_TOP** 标识，第二种方式无法指定 singleInstance 模式。
4. 可以通过命令行 adb shell dumpsys activity 命令查看栈中的 Activity 信息。

#### Activity 的 Flags
这些FLAG可以设定启动模式、可以影响Activity的运行状态。

- **FLAG_ACTIVITY_CLEAR_TOP** 
 具有此标记位的 Activity 启动时，同一个任务栈中位于它上面的 Activity 都要出栈，一般和 FLAG_ACTIVITY_NEW_TASK 配合使用。效果和 singleTask 一样。

- **FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS** 
 如果设置，新的 Activity 不会在最近启动的 Activity 的列表（就是安卓手机里显示最近打开的 Activity 那个系统级的UI）中保存。

<br><br>
## IntentFilter 匹配规则

启动Activity分为两种：<br>
1. 显示调用明确指定被启动对象的组件信息，包括包名和类名。<br>
2. 隐式调用不需要明确指定组件信息，需要 Intent 能够匹配目标组件中的 IntentFilter 中所设置的过滤信息。<br>
3. IntentFilter 中的过滤信息有 action、 category、 data。<br>
4. 只有一个 Intent 同时匹配 action类别、 category类别、 data类别才能成功启动目标 Activity。<br>
5. 一个 Activity 可以有多个 intent-filter ，一个 Intent 只要能匹配任何一组 intent-filter 即可成功启动对应的 Activity。

```Xml
<activity android:name="MainActivity">
    <!-- This activity is the main entry, should appear in app launcher -->
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>

<activity android:name="ShareActivity">
    <!-- This activity handles "SEND" actions with text data -->
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="text/plain"/>
    </intent-filter>
    <!-- This activity also handles "SEND" and "SEND_MULTIPLE" with media data -->
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <action android:name="android.intent.action.SEND_MULTIPLE"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="application/vnd.google.panorama360+jpg"/>
        <data android:mimeType="image/*"/>
        <data android:mimeType="video/*"/>
    </intent-filter>
</activity>
```

> 第一个 Activity MainActivity 是应用的主要入口点。当用户最初使用启动器图标启动应用时，该 Activity 将打开：
> - **ACTION_MAIN** 操作指示这是主要入口点，且不要求输入任何 Intent 数据。
> - **CATEGORY_LAUNCHER** 类别指示此 Activity 的图标应放入系统的应用启动器。 如果 <activity> 元素未使用 icon 指定图标，则系统将使用 <application> 元素中的图标。
> 
> 这两个元素必须配对使用，Activity 才会显示在应用启动器中。
> 
> 第二个 Activity ShareActivity 旨在便于共享文本和媒体内容。 尽管用户可以通过从 MainActivity 导航进入此 Activity，但也可以从发出隐式 Intent（与两个 Intent 过滤器之一匹配）的另一应用中直接进入 ShareActivity。

### 1. action
- action 是一个字符串。 系统预定义了一些，也可自己定义，区分大小写，例如 android.intent.action.SEND。
- 一个 intent-filter 可以有多个 aciton，只要 Intent 中的 action 能够和任何一个 action 相同即可成功匹配。匹配是指与 action 的字符串完全一样。
- Intent 中如果没有指定 action，那么匹配失败。


### 2. category
- category 是一个字符串。
- Intent 可以没有 category，但是如果你一旦有 category，不管有几个，每个都能够与 intent-filter 中的其中一个 category 相同。
- 系统在 startActivity 和 startActivityForResult 的时候，会默认为 Intent 加上 android.intent.category.DEFAULT 这个 category，所以为了我们的 activity能够接收隐式调用，就必须在intent-filter 中加上 android.intent.category.DEFAULT 这个 category。


### 3. data
- data 的匹配规则与 action一样，如果 intent-filter 中定义了 data，那么 Intent 中必须要定义可匹配的 data。
- intent-filter 中 data 的语法：

	```Xml
	  <data android:scheme="string"
		android:host="string"
		android:port="string"
		android:path="string"
		android:pathPattern="string"
		android:pathPrefix="string"
		android:mimeType="string"/>
	```
- Intent中 的 data 有两部分组成： mimeType 和 URI。 mimeType 是指媒体类型，比如 image/jpeg、audio/mpeg4-generic 和 video/* 等，可以表示图片、文本、视频等不同的媒体格式。

	- URI 的结构： ```Xml <scheme>://<host>:<port>/[<path>|<pathPrefix>|<pathPattern>] ```
		```Java
		//实际例子
		content://com.example.project:200/folder/subfolder/etc
		http://www.baidu.com:80/search/info
		```
		1. scheme：URI 的模式，比如 http、 file、 content 等，默认值是 file 。
		2.  host：URI 的主机名
		3.  port：URI 的端口号
		4.  path、 pathPattern 和 pathPrefix：这三个参数描述路径信息。
			- path、 pathPattern 可以表示完整的路径信息，其中 pathPattern 可以包含通配符 * ，表示0个或者多个任意字符。
			- pathPrefix 只表示路径的前缀信息。
	
	- Intent 指定 data 时，必须调用 setDataAndType 方法， setData 和 setType 会清除另一方的值。


### 4. 隐式调用需注意
1. 当通过隐式调用启动 Activity 时，没找到对应的 Activity 系统就会抛出 android.content.ActivityNotFoundException 异常，所以需要判断是否有 Activity 能够匹配我们的隐式 Intent。

	- 采用 PackageManager 的 resloveActivity 方法

		```Java
		public abstract List<ResolveInfo> queryIntentActivityies(Intent intent, int flags);
		public abstract ResolveInfo resloveActivity(Intent intent, int flags);
		```

		> 以上的第二个参数使用 MATCH_DEFAULT_ONLY ，这个标志位的含义是仅仅匹配那些在 intent-filter 中声明了 android.intent.category.DEFAULT 这个 category 的 Activity。 因为如果把不含这个 category 的 Activity 匹配出来了，由于不含 DEFAULT 这个 category 的 Activity 是无法接受隐式 Intent 的从而导致 startActivity 失败。

	- 采用 Intent 的 resloveActivity 方法

2. 下面的 action 和 category 用来表明这是一个入口 Activity 并且会出现在系统的应用列表中，二者缺一不可。
	```Xml
	<action android:name="android.intent.action.MAIN" />
	<category android:name="android.intent.category.LAUNCHER" />
	```
## 参考资料

[Google官方开发文档-任务和返回栈](https://developer.android.com/guide/components/tasks-and-back-stack.html?hl=zh-cn#TaskLaunchModes)<br>
[Google官方开发文档-Intent 和 Intent 过滤器](https://developer.android.com/guide/components/intents-filters.html)<br>
《Android 开发艺术探索》



[1]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_task_launch_modes/01.jpg
[2]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_task_launch_modes/02.jpg
[3]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_task_launch_modes/03.jpg
[4]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_task_launch_modes/04.jpg


## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！