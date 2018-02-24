# Android - SurfaceFlinger 图形系统

## 概述

- [Android 系统启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-系统启动过程.md)
- [Activity 创建过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity启动过程.md)
- [Activity 与 Window 与 View 之间的关系](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Activity与Window与View之间的关系.md)

通过前面的知识我们知道了，Android 系统从按下开机键到桌面，从桌面点击 App 图标到 Activity 显示的过程。但是 Activity 是怎么显示在屏幕上的呢？下面我们就来讨论下这一过程。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/android-bootloader.png" alt=""/>

## SurfaceFlinger 启动过程

SurfaceFlinger 进程是由 init 进程创建的，运行在独立的 SurfaceFlinger 进程中。init 进程读取 init.rc 文件启动 SurfaceFlinger。

```C
service surfaceflinger /system/bin/surfaceflinger
    class core
    user system
    group graphics drmrpc
    onrestart restart zygote
    writepid /dev/cpuset/system-background/tasks
```

## Surface 创建过程

## Surface 显示过程

## 参考资料

- [资料标题](http://www.baidu.com)


