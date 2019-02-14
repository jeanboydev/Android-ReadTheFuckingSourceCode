# 插件开发

## 新建 Module

首先新建一个项目，在项目中新建一个 Module 选择 Android Library，并修改目录结构删除不需要的文件如图：

![05](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/04.png)

目录结构：

```json
ProjectName
	|-src
		|-main
			|-groovy
				|-//插件具体实现逻辑
			|-resources
				|-META-INF
					|-gradle-plugins
						|-<插件 group id>.properties
	|-build.gradle//插件构建配置
```

## 配置项目

首先在 `src/main/groovy` 下创建包名 `com.jeanboy.plugin.test` ，并创建 `PluginImpl.groovy` 文件：

```groovy
com.jeanboy.plugin.test

import org.gradle.api.Plugin
import org.gradle.api.Project

class TestPlugin implements Plugin<Project> {

    @Override
    void apply(Project project) {
        project.task('testTask') << {
            println("========================")
            println("hello gradle plugin!")
            println("========================")
        }
    }
}
```

这时候 `PluginImpl.groovy` 文件应该是编译不通过的，我们修改下 `build.gradle` 文件，清空里面所有内容填入下面内容：

```groovy
apply plugin: 'groovy'//使用 groovy 插件构建项目
apply plugin: 'maven'//用于发布本地 maven 仓库中

dependencies {
    compile gradleApi()//gradle sdk
    compile localGroovy()//groovy sdk
}

repositories {
    jcenter()
    mavenCentral()
}

def groupName = 'com.jeanboy.plugin.test'//组名
def artifactName = 'TestPlugin'//项目名
def versionName = '1.0.1'//版本号

//上传至本地仓库
uploadArchives {
    repositories {
        mavenDeployer {
            pom.groupId = "${groupName}"
            pom.artifactId = "${artifactName}"
            pom.version = "${versionName}"
            repository(url: uri('../PluginRepository'))
        }
    }
}
```

最后修改 `src/main/resources/META-INF/gradle-plugins` 下的 properties 文件：

```json
implementation-class=com.jeanboy.plugin.test.PluginImpl
//implementation-class=<这里根据自己的插件自定义配置>
```

>  注意：该文件的文件名就是插件的名字。

例如：`com.jeanboy.plugin.test.properties`

最终使用插件时为：

```groovy
apply plugin: 'com.jeanboy.plugin.test'
```

## 发布到本地仓库

首先找到 `uploadArchives` ，然后双击执行这个 Task：

![06](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/05.png)

执行结果如下表示创建插件成功：

![07](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/06.png)

然后在项目根目录的 `PluginRepository` 中可以找到我们创建的插件：

![08](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/07.png)

## 本地仓库测试

接下来我们进行插件测试，首先需要到 `app` 目录下配置一下 `build.gradle` 引入我们的插件：

```groovy
//在 build.gradle 中最下面添加下面配置
apply plugin: 'com.jeanboy.plugin.test'//使用自定义的插件

//测试本地仓库中的插件
buildscript {
    repositories {
        maven {
            url uri('../PluginRepository')
        }
    }
    dependencies {
        classpath 'com.jeanboy.plugin.test:testPlugin:1.0.1'
    }
}

```

然后刷新一下 gradle，我们就可以找到刚才创建的 Task：

![081](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/08.png)

双击执行结果如下：

![09](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/09.png)

## 项目源码

https://github.com/jeanboydev/Android-GradlePluginTest

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！