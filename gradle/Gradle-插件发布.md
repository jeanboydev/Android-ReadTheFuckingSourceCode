# 插件发布

## 注册 bintray 账户

- [bintray 官网](https://bintray.com)

首先注册选择右边开源账户注册，这个是免费的；右边只是免费试用30天。

![10](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/10.png)

推荐使用关联 github 账号的方式注册。

![11](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/11.png)

创建你的 Maven 仓库，如果没有创建这个库，后面上传会出现不存在 maven 路径的错误。

![12](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/12.png)

## 引入 bintray release

在项目根目录的 `build.gradle` 配置：

```groovy
buildscript {

    repositories {
        google()
        jcenter()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:3.1.2'
        //引入上传 jcenter 的插件库
        classpath 'com.novoda:bintray-release:0.8.1'

        // NOTE: Do not place your application dependencies here; they belong
        // in the individual module build.gradle files
    }
}

allprojects {
    repositories {
        google()
        jcenter()
    }

    //添加 utf-8 的支持，避免中文注释生成 Javadoc 文件出现编码错误
    tasks.withType(Javadoc){
        options{
            encoding "UTF-8"
            charSet 'UTF-8'
            links "http://docs.oracle.com/javase/7/docs/api"
        }
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
```

在插件 Module 中的 `build.gradle` 添加配置：

```groovy
//使用 bintray-release 插件
apply plugin: 'com.novoda.bintray-release'

publish {
    groupId = "${groupName}"
    artifactId = "${artifactName}"
    publishVersion = "${versionName}"

    //项目描述
    desc = 'Task timer'
    //项目网址，建议github开源库网址
    website = 'https://github.com/jeanboy/Android-GradlePluginTest'
    //bintray 的用户名
    bintrayUser = 'jeanboydev'
    //bintray 用户名
    userOrg = 'jeanboydev'
    //API Key
    bintrayKey = "**********"
    dryRun = false
}
```

API Key 在个人设置中：

![13](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/13.png)

## 发布

直接使用 Android Studio 中的 Terminal 控制台使用命令：

> $ ./gradlew bintrayUpload

显示 BUILD SUCCESSFUL 表示上传成功：

![15](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/14.png)

在刚才创建的 Maven 仓库中可以看到刚刚上传的项目。

## 测试

在项目根目录的 `build.gradle` 引入配置：

```groovy
buildscript {

    repositories {
        google()
        jcenter()
        maven {//使用远程 maven 仓库
            //对应自己创建的仓库路径
            url 'https://dl.bintray.com/jeanboydev/maven'
        }
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:3.1.2'
        //引入上传 jcenter 的插件库
        classpath 'com.novoda:bintray-release:0.8.1'
    }
}

//...
```

在 app 目录下添加就可以测试了。

```groovy
  apply plugin: 'com.jeanboy.plugin.timer'
```

直接使用 Android Studio 中的 Terminal 控制台使用命令：

> $ ./gradlew build

![131](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/15.png)

##  Add to Jcenter

如果没有添加到 Jcenter 可以点击这里。![16](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/gradle/16.png)

## 项目源码

https://github.com/jeanboydev/Android-GradlePluginTest

# 参考资料

- [深入理解Android之Gradle](https://blog.csdn.net/innost/article/details/48228651)

- [如何使用Android Studio开发Gradle插件](https://blog.csdn.net/sbsujjbcy/article/details/50782830)
- [使用bintray_release插件轻松上传库到Jcenter](https://blog.csdn.net/KevinsCSDN/article/details/71655428)