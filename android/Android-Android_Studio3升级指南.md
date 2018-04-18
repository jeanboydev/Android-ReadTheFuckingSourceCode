# Android Studio 3.0 升级指南

## Gradle 版本升级

- Gradle Plugin 升级到 3.0.0 及以上，修改 `project/build.gradle` 文件：

```Java
buildscript {
    repositories {
        ...
        google()//*增加
    }

    dependencies {
        classpath 'com.android.tools.build:gradle:3.1.1'//*修改
        ...
    }
}

allprojects {
    repositories {
        jcenter()
        google()//*增加
    }
}
```

- Gradle 升级到 4.1 及以上，修改 `project/gradle/gradle-wrapper.properties` 文件：

```Java
...
//*修改
distributionUrl=https\://services.gradle.org/distributions/gradle-4.4-all.zip
```

## 多渠道

> Error:All flavors must now belong to a named flavor dimension.
The flavor 'flavor_name' is not assigned to a flavor dimension.

3.0 后 Gradle 添加了 `flavorDimensions` 属性，用来控制多个版本的代码和资源，缺失就会报错。在项目 app 下 build.gradle 文件中，添加 flavorDimensions：

```Java
android {
   ...
   flavorDimensions "tier","minApi"
   productFlavors{
     fees{
        dimension "tier"
        ...
     }
     minApi23{
       dimension "minApi"
        ...
     }
   }
}
```

如果不需要多版本控制只需添加：flavorDimensions "code"：

```Java
android {
   ...
   defaultConfig {
       ...
      flavorDimensions "code"
   }
   ...
}
```


## Gradle 自定义 apk 名称

> Error:(88, 0) Cannot set the value of read-only property ‘outputFile’ for ApkVariantOutputImpl_Decorated{apkData=Main{type=MAIN, fullName=appDebug, filters=[]}} of type com.android.build.gradle.internal.api.ApkVariantOutputImpl.

之前改 Apk 名字的代码类似：

```Java
applicationVariants.all { variant ->
    variant.outputs.each { output ->
        def file = output.outputFile
        def apkName = 'xxx-xxx-xxx-signed.apk'
        output.outputFile = new File(file.parent, apkName)
    }
}
```

由于 outputFile 属性变为只读，需要进行如下修改，直接对 outputFileName 属性赋值即可：

```Java
applicationVariants.all { variant ->
    variant.outputs.all {//each 改为 each
        def apkName = 'xxx-xxx-xxx-signed.apk'
        outputFileName = apkName//output.outputFile 改为 outputFileName
    }
}
```

## 依赖关键字变化

- compile：

```Java
dependencies {
    ...
    //3.0 之前
    compile 'com.android.support:appcompat-v7:26.1.0'
    compile fileTree(include: ['*.jar'], dir: 'libs')
    compile files('libs/gson-2.3.1.jar')
    //3.0 之后
    implementation 'com.android.support:appcompat-v7:26.1.0'
    implementation fileTree(include: ['*.jar'], dir: 'libs')
    implementation files('libs/gson-2.3.1.jar')
}
```

- `api`: 对应之前的 `compile` 关键字，功能一模一样。会传递依赖，导致 gradle 编译的时候遍历整颗依赖树
- `implementation`: 对应之前的 `compile` ，与 api 类似，关键区别是不会有依赖传递
- `compileOnly`: 对应之前的 provided，依赖仅用于编译期不会打包进最终的 apk 中
- `runtimeOnly`: 对应之前的 `apk`，与上面的 compileOnly 相反

关于 implementation 与 api 的区别，主要在依赖是否会传递上。如：A 依赖 B，B 依赖 C，若使用api则 A 可以引用 C，而 implementation 则不能引用。

这里更推荐用 implementation，一是不会间接的暴露引用，清晰知道目前项目的依赖情况；二是可以提高编译时依赖树的查找速度，进而提升编译速度。

## Java 8 支持

Gradle 带来了新的 Java 8 兼容方案 desugar，启用方式十分简单，只要在 gradle android 层次之下加入如下代码即可：

```Java
android {
  ...
  compileOptions {
    sourceCompatibility JavaVersion.VERSION_1_8
    targetCompatibility JavaVersion.VERSION_1_8
  }
}
```

停用 desugar，在 gradle.properties 文件中加入以下代码：

```Java
android.enableDesugar=false
```

- [官方文档 - 使用 Java 8 语言功能](https://developer.android.com/studio/write/java8-support.html)

## AAPT2

AAPT2 将默认启用，如果遇到离奇的问题，可以尝试禁用，只要在 gradle.properties 中加入：

```Java
android.enableAapt2=false
```


## 参考资料

- [官方文档 - 迁移到 Android Plugin for Gradle 3.0.0](https://developer.android.com/studio/build/gradle-plugin-3-0-0-migration.html)

