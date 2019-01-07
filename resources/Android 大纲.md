# Android 基础

## 四大组件

### Activity

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

### Fragment

- LifeCycle（生命周期）
- 与 Activity 交互
- 与 ViewPager 结合

### Service

- 生命周期
- startService()
- bindService()
- startForeground()
- onStartCommand()、START_STICKY
- android:priority
- Service 与 IntentService
- aidl 的使用

### BroadcastReceiver

- 静态广播
- 动态广播
- 有序广播

### ContentProvider

- 增删改查
- 共享数据

## 屏幕适配

### drawable 与 mipmap

### layout

- RelativeLayout

- FragmentLayout

- LinerLayout（weight 机制）

### 点 9 图片

## 通知栏与状态栏

### RemotView

### 沉浸式状态栏

## 运行时权限

## ListView

### 图片加载错乱的原理和解决方案

### 常见优化

## RecylerView

### 基本使用

### 动画与分割线

### 自定义 LayoutManager

### 源码分析

## Material Design（材料设计）

### 介绍

### ToolBar、CardView、沉浸标题栏

### FloatingActionButton、Snackbar、SheetX3

### BottomNavigationBar、TabLayout

### AppBarLayout、CoordinatorLayout

### CollapsingToolbarLayout、Palette

### DrawerLayout、NavigationView、TextInputLayout

### Behavior

## 自定义 View

### 绘制原理

- measure
- layout
- draw
- invalidate() 与 postInvalidate()

### 事件传递机制

- dispatchTouchEvent()
- onInterceptTouchEvent()
- onTouchEvent()

### 动画处理

- Frame Animation（帧动画）
- Tweened Animation（补间动画）
- Property Animation（属性动画）
  1. ValueAnimator
  2. Interpolator（插值器）
  3. TypeEvaluator（估值器）

### 自定义属性

### 贝塞尔曲线、粒子效果

## 数据持久化

### SharedPreferences

- 实现原理
- 是否进程同步。如何做到同步

### 文件与文件目录操作

### SQLite 使用

### JSON 解析

## 多媒体

### 相机与相册

### 图片与 bitmap

### 音频与视频

## 第三方开源库

### OkHttp

### Retrofit

### Volley

### Glide

### ButterKnife

### EventBus

## 相关原理

### Application

### Context

### LRUCache

### Handler

- Thread
- Looper
- MessageQueue
- Handler
- Message
- AsyncTask

### ThreadLocal 原理

### SpareArray 原理

### Binder

- aidl

### 动画实现原理

### App 保活

### 编译打包

- AssertManager
- V1、V2 签名机制

### 虚拟机

- ClassLoader
  1. 类加载机制
  2. 双亲委派模型
- GC
  1. 内存模型
  2. 垃圾回收机制

- 热修复
- 插件化
- Hook

### 系统服务

- Binder
- ActivityManagerService
  1. Activity 启动流程
  2. Activity、View、Window 之间的关系
- WindowManagerService
- PackageManagerService
- PowerManagerService

## 相关优化

### 性能优化

- 布局优化
  1. ViewStub
  2. include
  3. merge
- 过渡渲染
- ANR
- 监控
  1. 埋点
  2. Crash 上报

### 内存优化

- OOM（内存溢出）
- Memory Leak（内存泄漏）
- 内存检测
- 内存分析
- Bitmap 优化

### 网络优化

- API 优化
- 流量优化
- 弱网优化

### 电量优化

- WakeLock

### 缩小 Apk 体积

## Gradle

### 构建流程

### 自动化构建

### 组件开发

## Kotlin

## 混合开发

### Flutter

### ReactNative

## NDK

### 如何加载 ndk 库？如何在 jni 中注册 native 函数，有几种注册方式?

## 架构能力

### 常见设计模式

1. OOD 原则

### 组件化

1. ARouter

### MVC、MVP、MVVM

### Jetpack