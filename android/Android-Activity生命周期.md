# Android - Activity 生命周期

## 概述
作为四大组件中我们使用最频繁的 Activity，它的生命周期大家都了解。 然而面试中经常问到可见它的重要性。下面从两个方面来分析一下 Activity 的生命周期和一些需要注意的细节。

Activity 生命周期图

![图1][1]


## 典型情况下生命周期分析
1. 一般情况下，当当前 Activity 从**不可见**重新变为**可见**状态时，**onRestart** 方法就会被调用。

2. 当用户打开**新的 Activity** 或者**切换到桌面**的时候，回调如下：**onPause** -> **onStop**，但是如果新 Activity 采用了**透明主题**，那么 **onStop** 方法不会被回调。
当用户**再次回到原来的 Activity** 时，回调如下：**onRestart** -> **onStart** -> **onResume**。

3. **onStart** 和 **onStop** 对应，它们是从 **Activity 是否可见**这个角度来回调的；<br>**onPause** 和 **onResume** 方法对应，它们是从 **Activity 是否位于前台**这个角度来回调的。

4. 从 Activity A 进入到 Activity B ，回调顺序是 onPause(A) -> onCreate(B) -> onStart(B) -> onResume(B) -> onStop(A)，所以不能在 onPause 方法中做重量级的操作。

## 异常情况下生命周期分析
1. **onSaveInstanceState** 方法只会出现在 **Activity 被异常终止**的情况下，它的调用时机是在 onStop 之前，它和 onPause 方法没有既定的时序关系，可能在它之前，也可能在它之后。 当 Activity 被重新创建的时候，**onRestoreInstanceState** 会被回调，它的调用时机是 onStart 之后。<br>
系统只会在 Activity 即将被销毁并且有机会重新显示的情况下才会去调用 onSaveInstanceState 方法。 <br>当 Activity 在异常情况下需要重新创建时，系统会默认为我们保存当前 Activity 的视图结构，并且在 Activity 重启后为我们恢复这些数据。 
> 比如：文本框中用户输入的数据、 listview 滚动的位置等，这些 view 相关的状态系统都会默认为我们恢复。 

 具体针对某一个 view 系统能为我们恢复哪些数据可以查看 view 的源码中的 onSaveInstanceState 和 onRestoreInstanceState 方法。

2. Activity按优先级的分类

	前台 Activity > 可见但非前台 Activity > 后台 Activity

3. android:configChanges="xxx" 属性，常用的主要有下面三个选项：
	> local：设备的本地位置发生了变化，一般指切换了系统语言；
	> 
	> keyboardHidden：键盘的可访问性发生了变化，比如用户调出了键盘；
	> 
	> orientation：屏幕方向发生了变化，比如旋转了手机屏幕。
	
	配置了 android:**configChanges**="xxx" 属性之后，Activity就不会在对应变化发生时重新创建，而是调用 Activity 的 **onConfigurationChanged** 方法。

## 参考资料
[Google官方开发文档-Activity](https://developer.android.com/guide/components/activities.html?hl=zh-cn#Lifecycle)<br>
《Android 开发艺术探索》

## 扫一扫关注我的公众账号

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/wechat/qrcode_for_gh_26eef6f9e7c1_258.jpg?raw=true" width=256 height=256 />

[1]:https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_activity_life_cycle/Android-Activity%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F.png?raw=true

