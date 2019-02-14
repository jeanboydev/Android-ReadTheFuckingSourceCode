# Gradle DSL

Gradle 是一个编译打包工具，但实际上它也是一个编程框架。Gradle 有自己的 API 文档，对应链接如下：  

- [Gradle User Manual - 官方介绍文档](https://docs.gradle.org/current/userguide/userguide.html)
- [DSL Reference - API 文档](https://docs.gradle.org/current/dsl/)

由此可以看出，编写 Gradle 脚本时，我们实际上就是调用 Gradle 的 API 编程。

## 基本组件

- Project

  Gradle 中，每一个待编译的工程都是一个 Project。

  > 例如：用 AndroidStudio 构建项目时，每一个 module 都是 Gradle 定义的 Project。

- Task

  每一个 Project 在构建的时候都包含一系列的 Task。

  > 比如，一个 Android APK 的编译可能包含：Java 源码编译 Task、资源编译 Task、JNI 编译 Task、lint 检查 Task、打包生成 APK 的 Task、签名 Task 等。

  对于 Gradle 的编译打包流程而言，Task 就是最小的执行单元，其中将调用具体的函数来完成实际的工作。

- Plugin

  一个 Project 到底包含多少个 Task，在很大程度上依赖于编译脚本指定的插件。插件定义了一系列基本的 Task，并指定了这些 Task 的执行顺序。

  整体来看，Gradle 作为一个框架，负责定义通用的流程和规则；根据不同的需求，实际的编译工作则通过具体的插件来完成。 

  > 例如：编译 Java 项目时使用 Java 插件、编译 Groovy 项目时使用 Groovy 插件、编译 Android App 有 Android App 插件，编译 Android Library 有 Android Library 插件。

  举个例子来说，我们在 Android APK 对应的 build.gradle 中经常可以看到如下代码：

  ```groovy
  apply plugin: 'com.android.application'
  ```

  这就是使用编译 APK 的插件。

  同样，在编译 Android Library 时可以看到如下代码，用于指定使用编译 Library 的插件：

  ```groovy
  apply plugin: 'com.android.library'
  ```

  到现在为止，我们知道每一个 Library 和每一个 App 都是单独的 Project。根据 Gradle 的要求，每一个 Project 在其根目录下都需要有一个 `build.gradle`。`build.gradle` 文件就是该 Project 的编译脚本，类似于 Makefile。

## 构建过程

新建一个 Android 项目，目录结构如下：

```json
ProjectName
	|-app
		|-build
		|-lib
		|-src
		|-build.gradle	//后面讨论
	|-library-test
		|-build.gradle	//后面讨论
	|-gradle
		|-wrapper
	|-build.gradle	//*
	|-settings.gradle	//*
```

通过目录结构可以看出来，每一个 Project 中都有一个 `build.gradle` 文件，里面的内容后面再介绍。

在上面项目中有 `app` 和 `library-test` 两个 Project，如果编译某个 Project 则需要 cd 到某个 Project 目录中。比如，`cd xxx/app` 然后执行 `gradle xxx` xxx 是 task 的名字。

这很麻烦啊，有 10 个独立 Project，就得重复执行 10 次这样的命令。更有甚者，所谓的独立 Project 其实有依赖关系的。那么，我想在项目目录下，直接执行 `gradle xxx` 是否能够把所有的 Project 都编译出来呢？

答案是可以的。 在Gradle中，这叫Multi-Projects Build。需要在根目录下放一个 `build.gradle` 和一个 `settings.gradle` 。

可以看到 `project/build.gradle` 文件中的内容类似如下：

```groovy
buildscript {
    //为当前项目配置仓库
    repositories {
        //jcenter 是一个函数，表示编译过程中依赖的库，
        //所需的插件可以在 jcenter 仓库中下载
        jcenter()
    }
    //定义编译脚本依赖的库
    dependencies {
         //表示我们编译的时候，依赖 Android 开发的 gradle 插件
        classpath 'com.android.tools.build:gradle:3.0.1'
    }
}
//为所有的子项目配置
allprojects {
    repositories {
        jcenter()
    }
}
// 项目 clean task
task clean(type: Delete) {
    delete rootProject.buildDir
}
```

这个 `build.gradle` 主要作用是配置其他子 Project 。比如，为子 Project 添加一些属性。这个 `build.gradle` 有没有都无所属。

`project/settings.gradle` 则主要定义了根目录下具体有多少个 Gradle Project ，其内容类似于：

```groovy
include ':app', ':library-test'
```

这个文件很重要，名字必须是 `settings.gradle`。它里边用来告诉 Gradle，这个 Multi-Projects 包含多少个子 Project。

## 生命周期

当我们执行 Gradle 的时候，Gradle 首先是按顺序解析各个 Gradle 文件。这里边就有所所谓的生命周期的问题，即先解析谁，后解析谁。

- [Build Lifecycle - 官方文档](https://docs.gradle.org/current/userguide/build_lifecycle.html)

Gradle 构建系统有自己的生命周期，初始化、配置和运行三个阶段。

![img](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/02.png)

- 初始化阶段

  读取项目根目录中 `setting.gradle` 中的 include 信息，决定有哪几个工程加入构建，并为每个项目创建一个 Project 对象实例，比如下面有两个工程：

  ```groovy
  include ':app', ':library-test'
  ```

  所以 Gradle 将会为它们两个分别创建一个 Project 对象实例。

- 配置阶段

  执行所有 Project 中的 `build.gradle` 脚本，配置 Project 对象，一个对象由多个任务组成，此阶段也会去创建、配置 task 及相关信息。

- 运行阶段

  根据 Gradle 命令传递过来的 task 名称，执行相关依赖任务。task 的执行阶段。首先执行 `doFirst {}` 闭包中的内容，最后执行 `doLast {}` 闭包中的内容。

Gradle 基于 Groovy，Groovy 又基于 Java。所以，Gradle 执行的时候和 Groovy 一样，会把脚本转换成 Java 对象。Gradle 主要有三种对象，这三种对象和三种不同的脚本文件对应，在 Gradle 执行的时候，会将脚本转换成对应的对端：

- Gradle 对象

  当我们执行 `gradle xxx` 或者什么的时候，gradle 会从默认的配置脚本中构造出一个 Gradle 对象。在整个执行过程中，只有这么一个对象。Gradle 对象的数据类型就是 Gradle。我们一般很少去定制这个默认的配置脚本。

- Project 对象

  每一个 `build.gradle` 会转换成一个 Project 对象。

- Settings 对象

  显然，每一个 `settings.gradle` 都会转换成一个 Settings 对象。

> 对于其他 gradle 文件，除非定义了 class，否则会转换成一个实现了 Script 接口的对象。

## Task

Task 是 Gradle 中的一种数据类型，它代表了一些要执行或者要干的工作。不同的插件可以添加不同的 Task。每一个 Task 都需要和一个 Project 关联。

Task 的 API 文档位于：https://docs.gradle.org/current/dsl/org.gradle.api.Task.html。

- 任务创建

  ```groovy
  task hello {
      doLast {//doLast 可用 << 代替，不推荐此写法
          println "hello"//在 gradle 的运行阶段打印出来
      }
  }
  
  task hello {
      println "hello"//在 gradle 的配置阶段打印出来
  }
  ```

  task 中有一个 action list，task 运行时会顺序执行 action list 中的 action，doLast 或者 doFirst 后面跟的闭包就是一个 action，doLast 是把 action 插入到 list 的最后面，而 doFirst 是把 action 插入到 list 的最前面。

- 任务依赖

  当我们在 Android 工程中执行 `./gradlew build` 的时候，会有很多任务运行，因为 build 任务依赖了很多任务，要先执行依赖任务才能运行当前任务。

  任务依赖主要使用 `dependsOn` 方法，如下所示：

  ```groovy
  task A << {println 'Hello from A'}
  task B << {println 'Hello from B'}
  task C << {println 'Hello from C'}
  B.dependsOn A	//执行 B 之前会先执行 A
  C.dependsOn B	//执行 C 之前会先执行 B
  ```

  另外，你也可以在 Task 的配置区中来声明它的依赖：

  ```groovy
  task A << {println 'Hello from A'}
  task B {
      dependsOn A
      doLast {
          println 'Hello from B'  
      }
  }
  ```

  mustRunAfter：

  例如下面的场景，A 依赖 B，A 又同时依赖 C。但执行的结果可能是 B -> C -> A，我们想 C 在 B 之前执行，可以使用 mustRunAfter。

  ```groovy
  task A << {println 'Hello from A'}
  task B << {println 'Hello from B'}
  task C << {println 'Hello from C'}
  A.dependsOn B
  A.dependsOn C
  B.mustRunAfter C	//B 必须在 C 之后执行
  ```

  finalizedBy：在 Task 执行完之后要执行的 Task。

- 增量构建

  你在执行 Gradle 命令的时候，是不是经常看到有些任务后面跟着 [UP-TO-DATE]，这是怎么回事？

  在 Gradle 中，每一个 Task 都有 inputs 和 outputs，如果在执行一个 Task时，如果它的输入和输出与前一次执行时没有发生变化，那么 Gradle 便会认为该 Task 是最新的，因此 Gradle 将不予执行，这就是增量构建的概念。

  一个 Task 的 inputs 和 outputs 可以是一个或多个文件，可以是文件夹，还可以是 project 的某个 property，甚至可以是某个闭包所定义的条件。自定义 Task 默认每次执行，但通过指定 inputs 和 outputs，可以达到增量构建的效果。

- 依赖传递

  Gradle 默认支持传递性依赖，比如当前工程依赖包A，包 A 依赖包 B，那么当前工程会自动依赖包 B。同时，Gradle 支持排除和关闭依赖性传递。

  之前引入远程 AAR，一般会这样写：

  ```groovy
  compile 'com.somepackage:LIBRARY_NAME:1.0.0@aar'
  ```

  上面的写法会关闭依赖性传递，所以有时候可能就会出问题，为什么呢？

  本来以为 @aar 是指定下载的格式，但其实不然，远程仓库文件下载格式应该是由 pom 文件中 packaging 属性决定的，@ 符号的真正作用是 Artifact only notation，也就是只下载文件本身，不下载依赖，相当于变相的关闭了依赖传递。

## 常用命令

> $ gradle tasks	// 查看根目录包含的 task
>
> $ gradle tasks -all		// 查看根目录包含的所有 task
>
> $ gradle app:tasks	//查看具体 Project 中的 task
>
> $ gradle projects	//查看项目下所有的子 Project
>
> $ gradle build	//构建项目

Android Studio 的 Terminal 中：

> $ ./gradlew tasks	// 查看根目录包含的 task
>
> $ ./gradlew tasks -all		// 查看根目录包含的所有 task
>
> $ ./gradlew app:tasks	//查看具体 Project 中的 task
>
> $ ./gradlew projects	//查看项目下所有的子 Project
>
> $ ./gradlew build	//构建项目

## 环境变量

Mac 中使用 Gradle 命令会出现 `bash gradle command not found` 原因是没有配置环境变量。

- 找到 Gradle 所在的路径

  在 Finder 应用程序中 -> Android Studio 右键 -> 显示包内容，打开之后按照 Contents -> gradle -> gradle-xxx -> bin -> gradle。

  找到 gradle 文件后，右键 -> 显示简介，复制路径，类似：

  > /Applications/Android\ Studio.app/Contents/gradle/gradle-4.4

- 设置环境变量

  > $ cd ~	//返回 Home 目录
  >
  > $ touch .base_profile	//创建 base_profile 文件
  >
  > $ open -e .base_profile	//使用文本编辑器打开 base_profile 文件

  输入以下内容：

  ```js
  export GRADLE_HOME=/Applications/Android\ Studio.app/Contents/gradle/gradle-4.4
  export PATH=${PATH}:${GRADLE_HOME}/bin
  ```

  > $ source .bash_profile		//使修改生效
  >
  > $ gradle -v	//显示 gradle 版本

  ```js
  WARNING: An illegal reflective access operation has occurred
  WARNING: Illegal reflective access by org.codehaus.groovy.reflection.CachedClass (file:/Applications/Android%20Studio.app/Contents/gradle/gradle-4.4/lib/groovy-all-2.4.12.jar) to method java.lang.Object.finalize()
  WARNING: Please consider reporting this to the maintainers of org.codehaus.groovy.reflection.CachedClass
  WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
  WARNING: All illegal access operations will be denied in a future release
  
  ------------------------------------------------------------
  Gradle 4.4
  ------------------------------------------------------------
  
  Build time:   2017-12-06 09:05:06 UTC
  Revision:     cf7821a6f79f8e2a598df21780e3ff7ce8db2b82
  
  Groovy:       2.4.12
  Ant:          Apache Ant(TM) version 1.9.9 compiled on February 2 2017
  JVM:          9.0.1 (Oracle Corporation 9.0.1+11)
  OS:           Mac OS X 10.13.3 x86_64
  ```

  如果显示如下问题，需要修改权限：

  ```js
  -bash: /Applications/Android Studio.app/Contents/gradle/gradle-4.4/bin/gradle: Permission denied
  ```

- 修改权限

  > //进入 gradle 中 bin 目录
  >
  > $ cd /Applications/Android\ Studio.app/Contents/gradle/gradle-4.4/bin
  >
  > $ ls -l	//查看权限

  ```js
  total 24
  -rw-r--r--  1 jeanboy  admin  5286  4 16 17:49 gradle
  -rw-r--r--  1 jeanboy  admin  2250  4 16 17:49 gradle.bat
  ```

  > $ chmod +x gradle	//增加权限
  > $ chmod +x gradle.bat	//增加权限

  ```js
  total 24
  -rwxr-xr-x  1 jeanboy  admin  5286  4 16 17:49 gradle
  -rwxr-xr-x  1 jeanboy  admin  2250  4 16 17:49 gradle.bat
  ```

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！