# Android-反编译指南 #


## 反编译源码 ##
### 1. 使用 dex2jar ###

作用：将 apk 反编译成 java 源码（classes.dex 转化成 jar 文件）

dex2jar 下载：https://sourceforge.net/projects/dex2jar

下载最新的 dex2jar 并解压

### 2. 解压 apk 安装包，将 classes.dex 复制 dex2jar 目录下，执行下面命令 ###

```C
d2j-dex2jar classes.dex
```
Win10 最新 PowerShell 窗口尝试下面命令：

```C
.\d2j-dex2jar.bat .\classes.dex
```

### 3. 得到 classes-dex2jar.jar 使用 jd-gui.exe 打开 ###

作用：查看 APK 中 classes.dex 转化成出的 jar 文件，即源码文件

dex2jar 下载：http://jd.benow.ca/



## 反编译资源文件 ##
### 1. 使用 apktool ###
作用：资源文件获取，可以提取出图片文件和布局文件进行使用查看

apktool 下载：https://bitbucket.org/iBotPeaches/apktool/downloads/

下载最新的 apktool 并解压
### 2. 将 apk 安装包复制到 apktool 目录下，执行命令 ###

```C
java -jar apktool.jar d -f xxx.apk -o res
```

> 注意：apktool.bat 与 apktool.jar 文件名为 apktool