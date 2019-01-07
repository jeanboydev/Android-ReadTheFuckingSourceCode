# Android 基础

## 一、基础组件

### 1.1 Activity

- LifeCycle（生命周期）
  1. 通知栏对生命周期的影响
  2. Dialog（对话框）对生命周期的影响
  3. 屏幕旋转对生命周期的影响
- LaunchMode（启动模式）
  1. standard
  2. singleTop
  3. singleTask
  4. singleInstance
  5. onNewIntent()
  6. Intent Filter
- 状态保存与恢复
  1. onSaveInstanceState()
  2. onRestoreInstanceState()
- 转场动画

### 1.2 Fragment

- LifeCycle（生命周期）
- 与 Activity 交互
- 与 ViewPager 结合

### 1.3 Service

- 生命周期
- startService()
- bindService()
- startForeground()
- onStartCommand()、START_STICKY
- android:priority
- Service 与 IntentService
- aidl 的使用

### 1.4 BroadcastReceiver

- 静态广播
- 动态广播
- 有序广播

### 1.5 ContentProvider

- 增删改查
- 共享数据

### 1.6 RemotView

### 1.7 AppWidget

## 二、屏幕适配

### 2.1 使用限定符

### 2.2 layout

- RelativeLayout

- FragmentLayout

- LinerLayout（weight 机制）

### 2.3 drawable 与 mipmap

### 2.4 NinePatch(.9) 图片

## 三、运行时权限

## 四、ListView

### 4.1 图片加载错乱的原理和解决方案

### 4.2 常见优化

## 五、RecylerView

### 5.1 基本使用

### 5.2 动画与分割线

### 5.3 自定义 LayoutManager

### 5.4 源码分析

## 六、Material Design（材料设计）

### 6.1 ToolBar

### 6.2 CardView

### 6.3 FloatingActionButton

### 6.4 Snackbar

### 6.5 SheetX3

### 6.6 BottomNavigationBar

### 6.7 TabLayout

### 6.8 AppBarLayout

### 6.9 CoordinatorLayout

### 6.10 CollapsingToolbarLayout

### 6.11 Palette

### 6.12 DrawerLayout

### 6.13 NavigationView

### 6.14 TextInputLayout

### 6.15 Behavior

## 七、自定义 View

### 7.1 绘制原理

- measure
- layout
- draw
- invalidate() 与 postInvalidate()

### 7.2 事件传递机制

- dispatchTouchEvent()
- onInterceptTouchEvent()
- onTouchEvent()

### 7.3 动画处理

- Frame Animation（帧动画）
- Tweened Animation（补间动画）
- Property Animation（属性动画）
  1. ValueAnimator
  2. Interpolator（插值器）
  3. TypeEvaluator（估值器）

### 7.4 自定义属性

### 7.5 贝塞尔曲线、粒子效果

## 八、数据持久化

### 8.1 SharedPreferences

- 实现原理
- 是否进程同步，如何做到同步

### 8.2 文件与文件目录操作

### 8.3 SQLite 使用

### 8.4 JSON 解析

## 九、多媒体

### 9.1 相机与相册

### 9.2 图片与 bitmap

### 9.3 音频与视频

## 十、第三方开源库

### 10.1 OkHttp

### 10.2 Retrofit

### 10.3 Volley

### 10.4 Glide

### 10.5 ButterKnife

### 10.6 EventBus

## 十一、相关原理

### 11.1 Application

### 11.2 Context

### 11.3 LRUCache

### 11.4 Handler

- Thread
- Looper
- MessageQueue
- Handler
- Message
- AsyncTask

### 11.5 ThreadLocal 原理

### 11.6 SpareArray 原理

### 11.7 Binder

- aidl

### 11.8 动画实现原理

### 11.6 App 保活

### 11.8 编译打包

- AssertManager
- V1、V2 签名机制

### 11.9 虚拟机

- ClassLoader
  1. 类加载机制
  2. 双亲委派模型
- GC
  1. 内存模型
  2. 垃圾回收机制

- 热修复
- 插件化
- Hook

### 11.20 系统服务

- Binder
- ActivityManagerService
  1. Activity 启动流程
  2. Activity、View、Window 之间的关系
- WindowManagerService
- PackageManagerService
- PowerManagerService

## 十二、相关优化

### 12.1 性能优化

- 布局优化
  1. ViewStub
  2. include
  3. merge
- 过渡渲染
- ANR
- 监控
  1. 埋点
  2. Crash 上报

### 12.2 内存优化

- OOM（内存溢出）
- Memory Leak（内存泄漏）
- 内存检测
- 内存分析
- Bitmap 优化

### 12.3 网络优化

- API 优化
- 流量优化
- 弱网优化

### 12.4 电量优化

- WakeLock

### 12.5 缩小 Apk 体积

## 十三、Gradle

### 13.1 构建流程

### 13.2 自动化构建

### 13.3 组件开发

## 十四、Kotlin

## 十五、混合开发

### 15.1 Flutter

### 15.2 ReactNative

## 十六、NDK

### 16.1 加载 ndk 库

### 16.2 在 jni 中注册 native 函数

## 十七、架构能力

### 17.1 常见设计模式

- OOD 原则

### 17.2 组件化

- ARouter

### 17.3 MVC、MVP、MVVM

### 17.4 Jetpack