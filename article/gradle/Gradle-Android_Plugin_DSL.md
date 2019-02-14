# Android Plugin DSL

Android Plugin DSL 就是 Google 为了开发 Android 应用定制了一个插件，具体的插件配置请查阅官方文档。

- [Android Plugin DSL Reference - 官方文档](http://google.github.io/android-gradle-dsl/current)

新建一个 Android 项目，可以看到 `project/app/build.gradle` 文件中的内容类似如下：

```groovy
// 使用 Android app 插件
apply plugin: 'com.android.application'
// app 插件中的配置
android {
    compileSdkVersion 27
    defaultConfig {
        applicationId "com.jeanboy.app.gradleplugintest"
        minSdkVersion 21
        // ...
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation fileTree(dir: 'libs', include: ['*.jar'])
    implementation 'com.android.support:appcompat-v7:27.1.1'
    // ...
}
```

所有的配置都可以在上面官方文档中找到。![03](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/03.png)

## 打包过程

我们来通过 Apk 打包的过程来看一下 Gradle 在 Android Studio 中都做了哪些工作。

下图是谷歌官网给出的一个典型的 Apk 构建的过程，主要包括两个过程。首先是编译过程，编译的内容包括本工程的文件以及依赖的各种库文件，编译的输出包括 dex 文件和编译后的资源文件。然后是打包过程，配合 Keystore 对第一步的输出进行签名对齐，生成最终的 Apk 文件。

![100](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/100.png)

下面这张图对上面的步骤以及每步用到的工具进行了细分，概括如下：

1. Java 编译器对工程本身的 Java 代码进行编译，这些 Java 代码有三个来源：App 的源代码，由资源文件生成的 R 文件(aapt 工具)，以及有 aidl 文件生成的 Java 接口文件(aidl 工具)。产出为 `.class` 文件。
2. `.class` 文件和依赖的三方库文件通过 dex 工具生成 Delvik 虚拟机可执行的 `.dex` 文件，可能有一个或多个，包含了所有的 class 信息，包括项目自身的 class 和依赖的 class。产出为 `.dex` 文件。
3. apkbuilder 工具将 `.dex` 文件和编译后的资源文件生成未经签名对齐的 Apk 文件。这里编译后的资源文件包括两部分，一是由 aapt 编译产生的编译后的资源文件，二是依赖的三方库里的资源文件。产出为未经签名的 `.apk` 文件。
4. 分别由 Jarsigner 和 zipalign 对 Apk 文件进行签名和对齐，生成最终的 Apk 文件。

![101](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/101.png)

## Gradle 目录结构

Android 工程通过 Gradle 文件管理各项配置，Gradle 文件利用 DSL（Domain Specific Language）语言描述配置，并使用 Groovy 语言处理编译逻辑。

![102](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/102.png)

在这里 Gradle 文件分布在几个不同的层级，Project 层级以及 Module 层级。

1. Project 层级的 `settings.gradle` 描述的是该 Project 包含哪些 Module。

   ```groovy
   include ':app', ':lib'
   ```

2. Project 层级的 `build.gradle` 描述的是作用于所有 Module 的配置，包括 Gradle 版本等。

   ```groovy
   buildscript {
       repositories {
           jcenter()
       }
       
       dependencies {
           classpath 'com.android.tools.build:gradle:3.0.1'
       }
   }
   
   allprojects {
       repositories {
           jcenter()
       }
   }
   
   task clean(type: Delete) {
       delete rootProject.buildDir
   }
   ```

3. Module 层级的 `build.gradle`。每个 Module 下都有一个作用于该 Module 的 `build.gradle` 文件，描述了该 Module 相关的配置。这些配置主要包括：BuildTypes，ProductFlavors，Dependency，SigningSettings 等。

   ```groovy
   apply plugin: 'com.android.application'
   
   android {
       compileSdkVersion 27
       defaultConfig {
           applicationId "com.jeanboy.app.gradleplugintest"
           minSdkVersion 21
           // ...
       }
       buildTypes {
           release {
               minifyEnabled false
               proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
           }
       }
   }
   
   dependencies {
       implementation fileTree(dir: 'libs', include: ['*.jar'])
       implementation 'com.android.support:appcompat-v7:27.1.1'
       // ...
   }
   ```
   
## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！




 

 

 

 

 