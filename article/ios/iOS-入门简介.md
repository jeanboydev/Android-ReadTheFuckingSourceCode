# iOS 入门简介

## 概述
iOS（原名 iPhone OS，自 iOS 4 后改名为 iOS）是苹果公司为移动设备所开发的专有移动操作系统，所支持的设备包括 iPhone、iPod touch 和 iPad。与 Android 不同，iOS 不支持任何非苹果的硬件设备。

iOS 是由苹果公司开发的移动操作系统。苹果公司最早于 2007 年 1 月 9 日的 Macworld 大会上公布这个系统，最初是设计给 iPhone 使用的，后来陆续套用到 iPod touch、iPad 以及 Apple TV 等产品上。iOS 与苹果的 Mac OS X 操作系统一样，属于类 Unix 的商业操作系统。最初苹果公司并没有给随 iPhone 发行的 iOS 一个独立的称谓，直到 2008 年才取名为 iPhone OS，并在 2010 年 6 月改名为 iOS。2012 年发布四英寸设备 iPhone 5，从此开启多屏幕适配的道路。WWDC 2013 中，苹果发布了 iOS 7，彻底更改了用户界面，将原本拟物的风格转变为平面化风格。

* 2007：第一个 iOS 版本，提出为它提供软件支持。iPhone 1 上市。
* 2008：操作系统系统取名为 iPhone OS，AppStore 出现。iPhone 3G 上市。
* 2009：iPhone OS 3 发布，增加复制粘贴，Spotlight 搜索和语音控制等，拟物化设计。iPhone 3GS 上市。
* 2010：iPhone OS 改名为 iOS，增加双击 Home 键跳转应用。iPhone 4 上市。
* 2011：iOS 5 发布，增加 iCloud，新的 iMessage 和通知中心。iPhone 4s 上市。
* 2012：iOS 6 发布，增加自己的地图服务。iPhone 5 上市。
* 2013：iOS 7 发布，扁平化设计，增加 Touch ID 允许通过指纹识别来解锁设备。iPhone 5c/5s 上市。
* 2014：iOS 8 发布，增加在 Mac 上也可以阅读和编辑 iMessages，或者接听电话。iPhone 6/6 plus 上市。
* 2015：iOS 9 发布。iPhone 6s/6s plus 上市。
* 2016：iOS 10 发布，增加家庭 App，通知可直接显示图片和视频。iPhone SE/7/7 plus 上市。
* 2017：iOS 11 发布，增加对 AR 的支持，提供 ARKit。iPhone X/8/8 plus 上市。
* ……

## 系统架构

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/ios_intro/ios_system_level.png" alt="ios_system_level"/>

iOS 系统分为可分为四级结构，由上至下分别为可触摸层（Cocoa Touch Layer）、媒体层（Media Layer）、核心服务层（Core Services Layer）、核心系统层（Core OS Layer），每个层级提供不同的服务。低层级结构提供基础服务如文件系统、内存管理、I/O 操作等。高层级结构建立在低层级结构之上提供具体服务如 UI 控件、文件访问等。

iOS 8.3 系统框架架构图

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/ios_intro/ios_8_system_level_desc.png" alt="ios_8_system_level_desc"/>

- 可触摸层（Cocoa Touch Layer）
    
大部分与用户界面有关，本质上来说它负责用户在 iOS 设备上的触摸交互操作。这一层基本都是基于 Objective-C 的接口。
    
可触摸层主要提供用户交互相关的服务如界面控件、事件管理、通知中心、地图，包含以下框架：

* UIKit（界面相关）
* EventKit（日历事件提醒等）
* Notification Center（通知中心）
* MapKit（地图显示）
* Address Book（联系人）
* iAd（广告）
* Message UI（邮件与 SMS 显示）
* PushKit（iOS8 新 push 机制）

- 媒体层（Media Layer）

通过它我们可以在应用程序中使用各种媒体文件，进行音频与视频的录制，图形的绘制，以及制作基础的动画效果。这一层既有基于 Objective-c 的接口也有基于 C 语言的接口。
    
媒体层主要提供图像引擎、音频引擎、视频引擎框架：

* 图像引擎（Core Graphics、Core Image、Core Animation、OpenGL ES）
* 音频引擎 （Core Audio、 AV Foundation、OpenAL）
* 视频引擎（AV Foundation、Core Media）

- 核心服务层（Core Services Layer）

可以通过它来访问 iOS 的一些服务。基本都是基于 C 语言的接口。
    
核心服务层为程序提供基础的系统服务例如网络访问、浏览器引擎、定位、文件访问、数据库访问等，主要包含以下框架：

* CFNetwork（网络访问）
* Core Data（数据存储）
* Core Location（定位功能）
* Core Motion（重力加速度，陀螺仪）
* Foundation（基础功能如 NSString）
* Webkit（浏览器引擎）
* JavaScript（JavaScript 引擎）

- 核心系统层（Core OS Layer）

它包括内存管理、文件系统、电源管理以及一些其他的操作系统任务。它可以直接和硬件设备进行交互。作为 App 开发者不需要与这一层打交道。基本都是基于 C 语言的接口。核心系统层提供为上层结构提供最基础的服务如操作系统内核服务、本地认证、安全、加速等。
    
操作系统内核服务（BSD sockets、I/O 访问、内存申请、文件系统、数学计算等）
本地认证（指纹识别验证等）
安全（提供管理证书、公钥、密钥等的接口）
加速 (执行数学、大数字以及 DSP 运算,这些接口 iOS 设备硬件相匹配）
    
在上面所有的框架中，最重要也最经常使用的就是 UIKit 和 Foundation 框架。
    
Foundation 框架提供许多基本的对象类和数据类型，使其成为应用程序开发的基础,为所有应用程序提供最基本的系统服务，和界面无关。
    
UIKit 框架提供的类是基础的UI类库，用于创建基于触摸的用户界面，所有 iOS 应用程序都是基于 UIKit，它提供应用程序的基础架构，用于构建用户界面，绘图、处理和用户交互事件，响应手势等等。UIKit 通过控制器对象管理屏幕上显示的内容，界面的跳转，来组织应用程序。没有 UIKit 框架就没有 iOS 应用程序。

## 开发准备

- 开发环境

    Mac OS

- 开发工具

    [Xcode](https://developer.apple.com/xcode/)

- 开发语言

    Objective-C，Swift(推荐)<br>
    [Swift 官方资料](https://swift.org/about/)<br>
    [Swift 中文资料](https://www.cnswift.org/)<br>
    [Swift 中文教程](http://wiki.jikexueyuan.com/project/swift/chapter2/chapter2.html)


## 参考资料
- https://developer.apple.com/library/content/documentation/Miscellaneous/Conceptual/iPhoneOSTechOverview/Introduction/Introduction.html
- http://www.jianshu.com/p/58bc11c800e4


