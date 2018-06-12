# 插件开发

## 新建 Module

首先新建一个项目，在项目中新建一个 Module 选择 Android Library，并修改目录结构删除不需要的文件如图：

![05](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/gradle/04.png)

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

![06](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/gradle/05.png)

执行结果如下表示创建插件成功：

![07](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/gradle/06.png)

然后在项目根目录的 `PluginRepository` 中可以找到我们创建的插件：

![08](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/gradle/07.png)

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

![081](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/gradle/08.png)

双击执行结果如下：

![09](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/gradle/09.png)