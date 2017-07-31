# 深入理解 Java 虚拟机 #


## 1.对象回收问题 ##

### 引用计数算法 ###
很难解决对象之间互相循环引用的问题

### 可达性分析 ###
通过树结构，判断是否可达

1.2 引入 
强引用（Strong Reference）	Object obj=new Object()
软引用（Soft Reference）		SoftReference类
弱引用（Weak Reference）		WeakReference类
虚引用（Phantom Reference）	PhantomReference类


## 2.理解 GC 日志 ##

## 3.对象内存分配 ##
按年代分配
对象年龄

由于 Class 文件中方法、字段等都需要引用 CONSTANT_Utf8_info 型常量来描述名称，所以 CONSTANT_Utf8_info 型常量的最大长度也就是 Java 中方法、字段名的最大长度。而这里的最大长度是 length 的最大值，即 u2 类型能表达的最大值 65535.

Address		0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00000000	ca fe ba be 00 00 00 34 00 1d 0a 00 06 00 0f 09    
			[---魔数---][Hex  版本号][1~29][10]
									[常量池容量][参见常量池项目类型表]
											   [0a=10,CONSTANT_Methodref_info]
00000010	00 10 00 11 08 00 12 0a 00 13 00 14 07 00 15 07  
...
000000d0	73 74 65 6d 01 20 03 6f 75 74 01 20 15 4c 6a 61 
000000e0	76 61 2f 69 6f 2f 50 72 69 6e 74 53 74 72 65 61 
000000f0	6d 3b 01 20 13 6a 61 76 61 2f 69 6f 2f 50 72 69 
00000100	6e 74 53 74 72 65 61 6d 01 20 07 70 72 69 6e 74  

使用 javap 命令输出常量表
-> javap -verbose TestClass


volatile 修改对所有线程可见
synchronized
lock unlock