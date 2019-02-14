# Gradle 简介

![00](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/00.png)

## Gradle 是什么？

> Gradle is an open-source build automation tool focused on flexibility and performance. Gradle build scripts are written using a [Groovy](http://groovy-lang.org/) or [Kotlin](https://kotlinlang.org/) DSL. 
>
> Gradle是一款专注于灵活性和性能的开源构建自动化工具。Gradle构建脚本使用[Groovy](http://groovy-lang.org/)或[Kotlin](https://kotlinlang.org/) DSL 编写。
>
> DSL 的全称是 Domain Specific Language，即领域特定语言，或者直接翻译成”特定领域的语言”，算了，再直接点，其实就是这个语言不通用，只能用于特定的某个领域，俗称“小语言”。因此 DSL 也是语言。

- [官方介绍](https://docs.gradle.org/current/userguide/userguide.html#introduction)

说白了，Gradle 就是一个自动化构建项目的工具，用来帮助我们自动构建项目。就像我们在写 Java 项目的时候，如果没有构建工具，我们需要先执行 `javac` 命令先将 Java 源码编译成 class 文件，然后再执行 `jar` 命令再把 class 文件打成 jar 包。有了构建工具我们只需要点一个按钮就可以了。

Java 的构建，经历了从 `Ant` -> `Maven` -> `Gradle` 的过程，每一次的进步，都是为了解决之前的工具带来的问题:

- Ant：Ant 的功能虽然强大，但过于灵活，规范性不足，对目录结构及 build.xml 没有默认约定，且没有统一的项目依赖管理。
- Maven：Maven 解决了规范性的问题，也顺带解决了依赖项统一管理的问题，但由于规范性太强，灵活性不足，pom.xml 采用 xml 结构，项目一大，Xml 就显得冗长。
- Gradle：综合了 Ant 和 Maven 的优点，吸收了 Ant 中 task 的思想，然后把 Maven 的目录规范以及仓库思想也融合了进来，但允许用户自由的修改默认的规范（如：可随意修改源码目录），配置文件则采用 Groovy 语言来书写，Groovy 是一门可编程语言，配置文件本身就可以视为一份源代码，并最终交由 Gradle 来处理执行。

其实 Gradle 跟 Ant、Maven 等构建工具完成工作差不多，但 Gradle 更加强大，它不仅仅是一个构建工具，还是一个开发框架，这点我们将在后面的学习过程中具体体现。

在 Gradle 之前，Android 的项目构建工具是 Ant，用过 Eclipse 的同学应该都用过。 我们知道 Ant 是不支持自动去下载配置依赖 jar 的，这个坑就不提了。还有 Ant 的编译规则是基于 xml 的，用 xml 是很难描述类似这样不同条件的任务的：

```java
if(){
    //如果条件成立，编译某文件
}else{
	//如果条件不成立，编译某文件
}
```

然后我们都知道出现了 Gradle，首先 Gradle 是支持自动下载的依赖包的，Gradle 脚本不是像传统的 xml 文件那样，而是一种基于 Groovy 的动态 DSL，而 Groovy 语言是一种基于 jvm 的动态语言。 基于这种设计，Gradle 支持我们像写脚本一样的去写项目的构建规则也就是开发插件。

## 总结

1. Gradle 是一个构建工具，也是一个开发框架，基于 Groovy 语言。 我们可以通过 Groovy 语言去写自己的Gradle 插件，也可以去编写指定的脚本去改变构建规则。 
2. Android studio中 Gradle 之所以能够构建 Android 工程，是因为有基于 Android 的 Gradle 插件。

下面我们将从下面几个部分来学习：

- Groovy Language
- Gradle DSL
- Android Plugin DSL 
- 插件开发
- 插件发布

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！