# Android-内存优化 #

## 概述 ##
管理应用的内存
https://developer.android.com/topic/performance/memory.html
调查 RAM 使用情况
https://developer.android.com/studio/profile/investigate-ram.html

https://developer.android.com/studio/profile/allocation-tracker-walkthru.html
Android 性能优化典范
https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE

http://blog.csdn.net/qq_23191031/article/details/61920222
http://blog.csdn.net/qq_23191031/article/details/63685756


- 渲染
	GPU渲染原理，16ms，VSYNC（垂直同步），开发者模式工具使用，Overdraw（过渡绘制）优化，布局优化，Hierarchy Viewer使用
- 运算
	float数值大小执行时间是int数值的4倍左右，TraceView查看与使用，算法优化，SparseArray与HashMap
- 内存
	内存回收原理，内存泄漏检测
- 电量
	电量消耗，如何优化