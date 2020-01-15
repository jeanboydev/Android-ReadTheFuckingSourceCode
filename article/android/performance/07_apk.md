# APK 体积优化

减少应用程序安装包的大小，不仅仅减少了用户的网络数据流量还减少了下载等待的时间。毋庸置疑，尽量减少程序安装包的大小是十分有必要的。

通常来说，减少程序安装包的大小有两条规律：要么减少程序资源的大小，要么就是减少程序的代码量。

## APK 构成

在开始讲瘦身技巧之前，先来讲一下 APK 的构成。可以用 Android Studio 中的 APK Analyzer 打开 APK 查看。

![APK 构成](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/07_apk/01.png)

可以看到 APK 由以下主要部分组成：

| 文件/目录           | 描述                                                         |
| :------------------ | :----------------------------------------------------------- |
| lib/                | 存放 so 文件，可能会有 armeabi、armeabi-v7a、arm64-v8a、x86、x86_64、mips，大多数情况下只需要支持 armabi 与 x86 的架构即可，如果非必需，可以考虑拿掉 x86 的部分 |
| res/                | 存放编译后的资源文件，例如：drawable、layout 等等            |
| assets/             | 应用程序的资源，应用程序可以使用 AssetManager 来检索该资源   |
| META-INF/           | 该文件夹一般存放于已经签名的 APK 中，它包含了 APK 中所有文件的签名摘要等信息 |
| classes(n).dex      | classes 文件是 Java Class，被 DEX 编译后可供 Dalvik/ART 虚拟机所理解的文件格式 |
| resources.arsc      | 编译后的二进制资源文件                                       |
| AndroidManifest.xml | Android 的清单文件，格式为 AXML，用于描述应用程序的名称、版本、所需权限、注册的四大组件 |

当然还会有一些其它的文件，例如上图中的 `org/`、`src/`、`push_version` 等文件或文件夹。这些资源是 Java Resources，感兴趣的可以结合编译工作流中的 [流程图](http://tools.android.com/tech-docs/new-build-system/build-workflow) 以及 [MergeJavaResourcesTransform的源码 ](https://android.googlesource.com/platform/tools/base/+/gradle_2.0.0/build-system/gradle-core/src/main/groovy/com/android/build/gradle/internal/transforms/MergeJavaResourcesTransform.java)看看被打入 APK 包中的资源都有哪些，这里不做过多介绍。

在充分了解了 APK 各个组成部分以及它们的作用后，我们针对自身特点进行了分析和优化。下面将从 Zip 文件格式、classes.dex、资源文件、resources.arsc 等方面来介绍下优化技巧。

## 优化代码

### 压缩代码

可以通过开启 ProGuard 来实现代码压缩，可以在 build.gradle 文件相应的构建类型中添加 `minifyEnabled true`。

打开这些编译属性之后，程序在打包的时候就不会把没有引用到的代码编译进来，以此达到减少安装包大小的目的。

```java
android {
  buildTypes {
    release {
      minifyEnabled true
      proguardFiles getDefaultProguardFile(‘proguard-android.txt'),
                    'proguard-rules.pro'
    }
  }
}
```

除了 `minifyEnabled` 属性外，还有用于定义 ProGuard 规则的 proguardFiles 属性：

- `getDefaultProguardFile(‘proguard-android.txt')` 是从Android SDK `tools/proguard/` 文件夹获取默认 ProGuard 设置。
- `proguard-rules.pro` 文件用于添加自定义 ProGuard 规则。默认情况下，该文件位于模块根目录（build.gradle 文件旁）。

### 减少 ENUM 的使用

详情可以参考：[Remove Enumerations](https://developer.android.com/topic/performance/reduce-apk-size.html#reduce-code)，每减少一个 ENUM 可以减少大约 1.0 到 1.4 KB 的大小。

### 精简类库

部分引入到工程中的 jar 类库可能并不是专门针对移动端 App 而设计的，他们最开始可能是运用在 PC 或者 Server 上的。使用这些类库不仅仅额外增加了包的大小，还增加了编译时间。

单纯依靠 Proguard 可能无法完全移除那些使用不到的方法，最佳的方式是使用一些更加轻量化，专门为Android App 设计的 jar 类库。

### 精简 so 资源

Android系 统目前支持以下七种不同的 CPU 架构：ARMv5、ARMv7（从 2010 年起）、x86（从 2011 年起）、MIPS（从 2012 年起）、ARMv8、MIPS64 和 x86_64（从 2014 年起）。

每一个 CPU 架构对应一个 ABI：armeabi、armeabi_v7a、x86、mips、arm64_v8a、mips64、x86_64。

所有的 x86、x86_64、armeabi_v7a、arm64_v8a 设备都支持 armeabi 架构的 so 文件，x86 设备能够很好的运行 ARM 类型函数库，但并不保证 100% 不发生 Crash，特别是对旧设备。

64 位设备（arm64-v8a、 x86_64、mips64）能够运行 32 位的函数库，但是以 32 位模式运行，在 64 位平台上运行 32 位版本的 ART 和 Android 组件，将丢失专为 64 位优化过的性能（ART、webview、media 等等）。

所以一般的应用完全可以根据自己业务需求选择使用 armeabi 或者 armeabi_v7a 一种支持就行。

> 比如：微信、微博、QQ 只保留了 armeabi，Facebook、Twitter、Instagram 只保留了 armeabi_v7a。

假设只支持了 armeabi，如果有特殊要求（比如视频应用）需要用到部分 armeabi_v7a 的 so，可以通过改名放到 armeabi 文件夹中，根据手机实际情况选择加载。

- 动态下发

比较大的 so 可以选择动态下发的形式延迟加载，代码上需要加一些判断逻辑。

### 精简语言资源

大部分应用其实并不需要支持几十种语言的国际化支持。还好强大的gradle支持语言的配置，比如国内应用只支持中文：

```java
android {
    defaultConfig {
        resConfigs "zh"
    }
}
```

### 安装包拆分

设想一下，一个 low dpi，API<14 的用户手机下载安装的 APK 里面却包含了大量 xxhdpi 的资源文件，对于这个用户来说，这个 APK 是存在很大的资源浪费的。

幸好 Android 平台为我们提供了拆分 APK 的方法，它能够根据 API Level，屏幕大小以及 GPU 版本的不同进行拆分，使得对应平台的用户下载到最合适自己手机的安装包。

更多关于安装包拆分的信息，请查看 [Configure APK Splits](https://developer.android.com/studio/build/configure-apk-splits.html) 与 [Maintaining Multiple APKs](https://developer.android.com/training/multiple-apks/index.html)。

> 由于国内应用分发市场的现状，这一条几乎没有办法执行。

### 支持插件化

插件化技术雨后春笋一样的都冒了出来，这些技术支持动态的加载代码和动态的加载资源，把 APP 的一部分分离出来了，对于业务庞大的项目来说非常有用，极大的分解了 APK 大小。

因为插件化技术需要一定的技术保障和服务端系统支持，有一定的风险，如无必要（比如一些小型项目，也没什么扩展业务）就不需要了，建议酌情选择。

### 精简功能业务

从统计数据分析砍掉一些没用的功能是完全有可能的，甚至干脆去掉一些花哨的功能出个轻聊版、极速版也不是不可以的。

> 比如：今日头条极速版、QQ 轻聊版等等。

## 优化资源文件

### 移除未使用资源

确保在 build.gradle 文件中开启了  `shrinkResources` 的属性，这个属性可以帮助移除那些在程序中使用不到的资源文件，帮助减少 App 的安装包大小。

```java
android {
  buildTypes {
    release {
      shrinkResources true
    }
  }
}
```

有选择性的提供对应分辨率的图片资源，系统会自动匹配最合适分辨率的图片并执行拉伸或者压缩的处理。

### 有损压缩图片

Android 打包本身会对 PNG 进行无损压缩，所以使用像 [Tinypng](http://tinypng.com) 这样的有损压缩是有必要的。

重点是 Tinypng 使用智能有损压缩技术，以尽量少的失真换来图片大小的锐减，效果非常好，强烈推荐。

### 使用更小的图片

如果对于非透明的大图，JPG 将会比 PNG 的大小有显著的优势，虽然不是绝对的，但是通常会减小到一半都不止。在启动页，活动页等之类的大图展示区采用 JPG 将是非常明智的选择。

[WebP](https://developers.google.com/speed/webp/docs/precompiled) 支持透明度，压缩比比 JPG 更高但显示效果却不输于 JPG，官方评测 quality 参数等于 75 均衡最佳。
相对于 JPG、PNG，WebP 作为一种新的图片格式，限于 Android 的支持情况暂时还没用在手机端广泛应用起来。从 Android 4.0+ 开始原生支持，但是不支持包含透明度，直到 Android 4.2.1+ 才支持显示含透明度的 WebP，使用的时候要特别注意。

### 使用 VectorDrawable

在符合条件的情况下，使用 Vertor Drawable 替代传统的 PNG/JPEG 图片，能够极大的减少图片资源的大小。

传统模式下，针对不同 DPI 的手机都需要提供一套 PNG/JPEG 的图片，而如果使用 Vector Drawable 的话，只需要一个 XML 文件即可。

![android_perf_6_smaller_apks_vector](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/performance/07_apk/02.png)

尽量复用已经存在的资源图片，使用代码的方式对已有的资源进行复用。

## APK Analyzer

Android Studio 2.2 包含了 APK Analyzer，通过它我们能够直观地看到 APK 的组成。使用 APK Analyzer 不仅能够减少你花在 debug 上的时间，而且还能减少你的 APK 大小。

使用 APK Analyzer，你能够实现：

- 查看 APK 中文件的绝对大小和相对大小。
- 理解 dex 文件的组成。
- 快速查看 APK 中文件的最终版本（比如AndroidManifest.xml）。
- 对比两个 APK。

这里有 3 种方法访问 APK Analyzer：

- 拖拽 APK 到 Android Studio 的编辑窗口。
- 切换到 Project 视图，并且双击 APK 文件。
- 在菜单栏中选择 **Build > Analyzer APK**，并且选择 APK。

 更多关于 的内容可以查看 [Android 开发文档 - Analyze your build with APK Analyzer](https://developer.android.com/studio/build/apk-analyzer)、[使用 APK Analyzer 分析你的 APK](https://zhuanlan.zhihu.com/p/26714024) 这两篇文章。

## 参考资料

- [YouTube - Android 性能优化典范第 6 季](https://www.youtube.com/watch?v=AkafJ6NdrhY&list=PLWz5rJ2EKKc-9gqRx5anfX0Ozp-qEI2CF)
- [胡凯 - Android 性能优化典范 - 第 6 季](http://hukai.me/android-performance-patterns-season-6/)
-  [Android 开发文档 - Configure APK Splits](https://developer.android.com/studio/build/configure-apk-splits.html)
- [Android 开发文档 - Maintaining Multiple APKs](https://developer.android.com/training/multiple-apks/index.html)
- [美团技术团队 - Android App包瘦身优化实践](https://tech.meituan.com/2017/04/07/android-shrink-overall-solution.html)
- [Android APP 终极瘦身指南](https://jayfeng.com/2016/03/01/Android-APP终极瘦身指南/)
- [头条 APK 瘦身之路](https://techblog.toutiao.com/2017/05/16/apk/)
- [Android 开发文档 - Analyze your build with APK Analyzer](https://developer.android.com/studio/build/apk-analyzer)
- [使用 APK Analyzer 分析你的 APK](https://zhuanlan.zhihu.com/p/26714024) 