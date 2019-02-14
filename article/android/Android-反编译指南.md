# Android - 反编译指南


## 反编译源码
### 1. 使用 dex2jar

作用：将 apk 反编译成 java 源码（classes.dex 转化成 jar 文件）

dex2jar 下载：https://sourceforge.net/projects/dex2jar

下载最新的 dex2jar 并解压

### 2. 解压 apk 安装包，将 classes.dex 复制 dex2jar 目录下，执行下面命令

```C
d2j-dex2jar classes.dex
```
Win10 最新 PowerShell 窗口尝试下面命令：

```C
.\d2j-dex2jar.bat .\classes.dex
```

### 3. 得到 classes-dex2jar.jar 使用 jd-gui.exe 打开

作用：查看 APK 中 classes.dex 转化成出的 jar 文件，即源码文件

dex2jar 下载：http://jd.benow.ca/



## 反编译资源文件
### 1. 使用 apktool
作用：资源文件获取，可以提取出图片文件和布局文件进行使用查看

apktool 下载：https://bitbucket.org/iBotPeaches/apktool/downloads/

下载最新的 apktool 并解压
### 2. 将 apk 安装包复制到 apktool 目录下，执行命令

```C
java -jar apktool.jar d -f xxx.apk -o res
```

> 注意：apktool.bat 与 apktool.jar 文件名为 apktool

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！

