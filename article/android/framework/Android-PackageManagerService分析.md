# Android - PackageMangerService 分析

## 概述

PackageManagerService（简称 PKMS），是 Android 系统中核心服务之一，管理着所有跟 package 相关的工作，常见的比如安装、卸载应用。

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_boot_loader/android-bootloader.png" alt=""/>

PackageManagerService 是在 SystemServer 进程中启动的。如不了解 Android 是如何从开机到 Launcher 启动的过程，请先阅读：[Android - 系统启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-系统启动过程.md)。


## PackageManagerService 启动

SystemServer 启动过程中涉及到的 PKMS 如下：

```Java
private void startBootstrapServices() {
    //启动installer服务
    Installer installer = mSystemServiceManager.startService(Installer.class);
    ...

    //处于加密状态则仅仅解析核心应用
    String cryptState = SystemProperties.get("vold.decrypt");
    if (ENCRYPTING_STATE.equals(cryptState)) {
        mOnlyCore = true; // ENCRYPTING_STATE = "trigger_restart_min_framework"
    } else if (ENCRYPTED_STATE.equals(cryptState)) {
        mOnlyCore = true; // ENCRYPTED_STATE = "1"
    }

    //创建 PKMS 对象【1】
    mPackageManagerService = PackageManagerService.main(mSystemContext, installer,
                mFactoryTestMode != FactoryTest.FACTORY_TEST_OFF, mOnlyCore);
    //PKMS是否首次启动
    mFirstBoot = mPackageManagerService.isFirstBoot();

    //【2】
    mPackageManager = mSystemContext.getPackageManager();
    //...
}

private void startOtherServices() {
    //...
    //启动 MountService，后续 PackageManager 会需要使用
    mSystemServiceManager.startService(MOUNT_SERVICE_CLASS);
    //【3】做 dex 优化。dex 是 Android 上针对 Java 字节码的一种优化技术，可提高运行效率
    mPackageManagerService.performBootDexOpt();
    /...  

    // phase 500
    mSystemServiceManager.startBootPhase(SystemService.PHASE_SYSTEM_SERVICES_READY);
    //...

    //【4】
    mPackageManagerService.systemReady();
    //...
}
```

整个 system_server 进程启动过程，涉及 PKMS 服务的主要几个动作如下，接下来分别讲解每个过程：

- PKMS.main()
- PKMS.performBootDexOpt()
- PKMS.systemReady()

### PKMS.main()

```Java
public static PackageManagerService main(Context context, Installer installer, 
	boolean factoryTest, boolean onlyCore) {
    //初始化 PKMS 对象
    PackageManagerService m = new PackageManagerService(context, installer,
            factoryTest, onlyCore);
    //将 package 服务注册到 ServiceManager，这是 binder 服务的常规注册流程
    ServiceManager.addService("package", m);
    return m;
}
```
该方法的主要功能创建 PKMS 对象，并将其注册到 `ServiceManager` 中，内部是一个 HashMap 的集合，存储了很多相关的 `binder` 服务，缓存起来，我们在使用的时候， 会通过 `getService(key)` 的方式去 `map`中获取，ServiceManger 工作流程详见：[Android - Binder 机制](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-Binder%E8%BF%9B%E7%A8%8B%E9%97%B4%E9%80%9A%E8%AE%AF.md)。

关于 PKMS 对象的构造方法很长，分为以下几个阶段，每个阶段会输出相应的 EventLog。

```Java
public PackageManagerService(Context context, Installer installer, 
	boolean factoryTest, boolean onlyCore) {

    //PackageManagerService 启动开始
    EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_START, SystemClock.uptimeMillis());
    //SDK 版本检查
    if (mSdkVersion <= 0) {
        Slog.w(TAG, "**** ro.build.version.sdk not set!");
    }

    //读取开机启动模式
    String mode = SystemProperties.get("ro.bootmode", "mode");
    engModeEnable = "engtest".equals(mode) ? true : false;
    Slog.i(TAG, "engModeEnable: " + engModeEnable + " ,mode:" + mode);
    mContext = context;
    mFactoryTest = factoryTest;//开机模式
    mOnlyCore = onlyCore;//是否对包做 dex 优化
    //如果编译版本为 eng，则不需要 dex 优化
    mNoDexOpt = "eng".equals(SystemProperties.get("ro.build.type"));
    //创建显示尺寸信息
    mMetrics = new DisplayMetrics();
    //存储系统运行过程中的设置信息
    mSettings = new Settings();//【1】
    /*创建 SharedUserSetting 对象并添加到 Settings 的成员变量 mSharedUsers 中，
        在 Android 系统中，多个 package 通过设置 sharedUserId 属性可以运行在同一个进程，共享同一个 UID */
    mSettings.addSharedUserLPw("android.uid.system", Process.SYSTEM_UID, ApplicationInfo.FLAG_SYSTEM);
    mSettings.addSharedUserLPw("android.uid.phone", RADIO_UID, ApplicationInfo.FLAG_SYSTEM);
    mSettings.addSharedUserLPw("android.uid.log", LOG_UID, ApplicationInfo.FLAG_SYSTEM);
    mSettings.addSharedUserLPw("android.uid.nfc", NFC_UID, ApplicationInfo.FLAG_SYSTEM);
    String separateProcesses = SystemProperties.get("debug.separate_processes");
    if (separateProcesses != null && separateProcesses.length() > 0) {
        if ("*".equals(separateProcesses)) {
            mDefParseFlags = PackageParser.PARSE_IGNORE_PROCESSES;
            mSeparateProcesses = null;
            Slog.w(TAG, "Running with debug.separate_processes: * (ALL)");
        } else {
            mDefParseFlags = 0;
            mSeparateProcesses = separateProcesses.split(",");
            Slog.w(TAG, "Running with debug.separate_processes: "
                   + separateProcesses);
        }
    } else {
        mDefParseFlags = 0;
        mSeparateProcesses = null;
    }

    mPreInstallDir = new File("/system/preloadapp");
    //创建应用安装器
    mInstaller = new Installer();

    //获取屏幕尺寸大小
    WindowManager wm = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
    Display d = wm.getDefaultDisplay();
    d.getMetrics(mMetrics);
    synchronized (mInstallLock) {
        // writer
        synchronized (mPackages) {
            //启动消息处理线程
            mHandlerThread.start();
            //为消息处理线程创建一个消息分发handler
            mHandler = new PackageHandler(mHandlerThread.getLooper());
            // dataDir =/data/
            File dataDir = Environment.getDataDirectory();
            // mAppDataDir = /data/data
            mAppDataDir = new File(dataDir, "data");
            // mAsecInternalPath = /data/app-asec
            mAsecInternalPath = new File(dataDir, "app-asec").getPath();
            // mUserAppDataDir = /data/user
            mUserAppDataDir = new File(dataDir, "user");
            // mDrmAppPrivateInstallDir = /data/app-private
            mDrmAppPrivateInstallDir = new File(dataDir, "app-private");
            sUserManager = new UserManager(mInstaller, mUserAppDataDir);
            //读取并解析/etc/permissions下的XML文件
            readPermissions();
            mRestoredSettings = mSettings.readLPw();
           	long startTime = SystemClock.uptimeMillis();//【2】
        }
    }

    Runtime.getRuntime().gc();
    //暴露私有服务，用于系统组件的使用
    LocalServices.addService(PackageManagerInternal.class, 
		new PackageManagerInternalImpl());
}
```
刚进入构造函数，就会遇到第一个较为复杂的数据结构 `Settings` 及它的 `addSharedUserLPw()` 函数。Settings 的作用是管理 Android 系统运行过程中的一些设置信息。到底是哪些信息呢？来看下面的分析。

### Settings

先分析 addSharedUserLPw 函数。如下所示：

```java
mSettings.addSharedUserLPw("android.uid.system",//字符串
    Process.SYSTEM_UID, //系统进程使用的用户id，值为1000
    ApplicationInfo.FLAG_SYSTEM//标志系统 Package
);
```

在进入对addSharedUserLPw 函数的分析前，先介绍一下 SYSTEM_UID 及相关知识。

Android 系统中 UID/GID 介绍：

UID 为用户 ID 的缩写，GID 为用户组 ID 的缩写，这两个概念均与 Linux 系统中进程的权限管理有关。一般说来，每一个进程都会有一个对应的 UID（即表示该进程属于哪个 user，不同 user 有不同权限）。一个进程也可分属不同的用户组（每个用户组都有对应的权限）。

> 提示 Linux 的 UID/GID 还可细分为几种类型，此处我们仅考虑普适意义的 UID/GID。

下面分析 addSharedUserLPw 函数，代码如下：

```java
SharedUserSetting addSharedUserLPw(String name, int uid, int pkgFlags) {
    /*
        注意这里的参数：name 为字符串”android.uid.system”，uid 为 1000，pkgFlags 为
        ApplicationInfo.FLAG_SYSETM (以后简写为FLAG_SYSTEM)
      */
    //mSharedUsers 是一个 HashMap，key 为字符串，值为 SharedUserSetting 对象
    SharedUserSetting s = mSharedUsers.get(name);
    if (s != null) {
        if (s.userId == uid) {
            return s;
        }
        //...
        return null;
    }

    //创建一个新的 SharedUserSettings 对象，并设置的 userId 为 uid
    s = new SharedUserSetting(name, pkgFlags);
    s.userId = uid;
    if (addUserIdLPw(uid, s, name)) {
        mSharedUsers.put(name, s);//将name与s键值对添加到mSharedUsers中保存
        return s;
    }
    return null;
}
```

从以上代码可知，Settings 中有一个 mSharedUsers 成员，该成员存储的是字符串与 SharedUserSetting 键值对，也就是说以字符串为 key 得到对应的 SharedUserSetting 对象。

那么 SharedUserSettings 是什么？它的目的是什么？来看一个例子。

该例子来源于 SystemUI 的 AndroidManifest.xml，如下所示：

```xml
<manifestxmlns:android="http://schemas.android.com/apk/res/android"
       package="com.android.systemui"
       coreApp="true"
       android:sharedUserId="android.uid.system"
       android:process="system">
...
```

在 xml 中，声明了一个名为 `android:sharedUserId` 的属性，其值为 `android.uid.system`。 sharedUserId 看起来和 UID 有关，确实如此，它有两个作用：

- 两个或多个声明了同一种 sharedUserIds 的 APK 可共享彼此的数据，并且可运行在同一进程中。
- 更重要的是，通过声明特定的 sharedUserId，该 APK 所在进程将被赋予指定的 UID。例如，本例中的 SystemUI 声明了 system 的 uid，运行 SystemUI 的进程就可享有 system 用户所对应的权限（实际上就是将该进程的 uid 设置为 system 的 uid）了。

> 提示：除了在 AndroidManifest.xml 中声明 sharedUserId 外，Apk 在编译时还必须使用对应的证书进行签名。例如，本例的 SystemUI，在其 Android.mk 中需要额外声明 LOCAL_CERTIFICATE := platform，如此，才可获得指定的 UID。

通过以上介绍，我们能了解到如何组织一种数据结构来包括上面的内容。此处有三个关键点需注意：

- XML 中 sharedUserId 属性指定了一个字符串，它是 UID 的字符串描述，故对应数据结构中也应该有这样一个字符串，这样就把代码和 XML 中的属性联系起来了。
- 在 Linux 系统中，真正的 UID 是一个整数，所以该数据结构中必然有一个整型变量。
- 多个 Package 可声明同一个 sharedUserId，因此该数据结构必然会保存那些声明了相同 sharedUserId的 Package 的某些信息。

了解了上面三个关键点，再来看 Android 是如何设计相应数据结构的，如图所示。

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/01.png" alt=""/>

由上图可知：

- Settings 类定义了一个 mSharedUsers 成员，它是一个 HashMap，以字符串（如“android.uid.system”）为Key，对应的 Value 是一个 SharedUserSettings 对象。
- SharedUserSetting 派生自 GrantedPermissions 类，从 GrantedPermissions 类的命名可知，它和权限有关。SharedUserSetting 定义了一个成员变量 packages，类型为 HashSet，用于保存声明了相同 sharedUserId 的 Package 的权限设置信息。
- 每个 Package 有自己的权限设置。权限的概念由 PackageSetting 类表达。该类继承自 PackagesettingBase，而 PackageSettingBase 又继承自 GrantedPermissions。
- Settings 中还有两个成员，一个是 mUserIds，另一个是 mOtherUserIds，这两位成员的类型分别是 ArrayList 和 SparseArray。其目的是以 UID 为索引，得到对应的 SharedUserSettings 对象。在一般情况下，以索引获取数组元素的速度，比以 key 获取 HashMap 中元素的速度要快很多。

> 提示：根据以上对 mUserIds 和 mOtherUserIds 的描述，可知这是典型的以空间换时间的做法。

下边来分析 addUserIdLPw 函数，它的功能就是将 SharedUserSettings 对象保存到对应的数组中，代码如下：

```java
private boolean addUserIdLPw(int uid, Object obj, Objectname) {
    //uid 不能超出限制。Android 对 UID 进行了分类，应用 APK 所在进程的 UID 从 10000 开始，
    //而系统 APK 所在进程小于 10000
    if (uid >= PackageManagerService.FIRST_APPLICATION_UID + PackageManagerService.MAX_APPLICATION_UIDS) {
        return false;
    }

    if (uid >= PackageManagerService.FIRST_APPLICATION_UID) {
        int N = mUserIds.size();
        //计算索引，其值是 uid 和 FIRST_APPLICATION_UID 的差
        final int index = uid - PackageManagerService.FIRST_APPLICATION_UID;
        while (index >= N) {
            mUserIds.add(null);
            N++;
        }
        //...
        //判断该索引位置的内容是否为空，为空才保存
        mUserIds.set(index, obj);//mUserIds 保存应用 Package 的 UID
    } else {
        //...
        mOtherUserIds.put(uid, obj);//系统 Package 的 UID 由 mOtherUserIds 保存
    }
    return true;
}
```

### readPermissions()

先来分析 readPermissions 函数，从其函数名可猜测到它和权限有关，代码如下：

```java
void readPermissions() {
    // 指向 /system/etc/permission 目录，该目录中存储了和设备相关的一些权限信息
    FilelibraryDir = new File(Environment.getRootDirectory(), "etc/permissions");
    //...
    for (File f : libraryDir.listFiles()) {
        //先处理该目录下的非platform.xml文件
        if (f.getPath().endsWith("etc/permissions/platform.xml")) {
            continue;
        }
        //...
        // 调用 readPermissionFromXml 解析此 XML 文件
        readPermissionsFromXml(f);
    }

    finalFile permFile = new File(Environment.getRootDirectory(), "etc/permissions/platform.xml");

    //解析 platform.xml 文件，看来该文件优先级最高
    readPermissionsFromXml(permFile);
}
```

在 `etc/permissions` 目录下保存了一下配置文件：

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/02.png" alt=""/>

函数 readPermissionsFromXml 使用 PULL 方式解析这些 XML 文件：

```java
private void readPermissionsFromXml(File permFile) {
    FileReader permReader = null;
    try {
        permReader = new FileReader(permFile);
    }
    //...
    try {
        XmlPullParser parser = Xml.newPullParser();
        parser.setInput(permReader);
        XmlUtils.beginDocument(parser, "permissions");
        while (true) {
            //...
            String name = parser.getName();
            //解析 group 标签，前面介绍的 XML 文件中没有单独使用该标签的地方
            if ("group".equals(name)) {
                String gidStr = parser.getAttributeValue(null, "gid");
                if (gidStr != null) {
                    int gid = Integer.parseInt(gidStr);
                    //转换 XML 中的 gi d字符串为整型，并保存到 mGlobalGids 中
                    mGlobalGids = appendInt(mGlobalGids, gid);
                }
                //...
            } else if ("permission".equals(name)) {//解析 permission 标签
                String perm = parser.getAttributeValue(null, "name");
                //...
                perm = perm.intern();
                //调用 readPermission 处理
                readPermission(parser, perm);
            } else if ("assign-permission".equals(name)) {//下面解析的是assign-permission标签
                String perm = parser.getAttributeValue(null, "name");
                //...
                String uidStr = parser.getAttributeValue(null, "uid");
                //...
                //如果是 assign-permission，则取出 uid 字符串，然后获得 Linux 平台上
                //的整型 uid 值
                int uid = Process.getUidForName(uidStr);
                //...
                perm = perm.intern();
                //和 assign 相关的信息保存在 mSystemPermissions 中
                HashSet<String> perms = mSystemPermissions.get(uid);
                if (perms == null) {
                    perms = newHashSet < String > ();
                    mSystemPermissions.put(uid, perms);
                }
                perms.add(perm);
                //...
            } else if ("library".equals(name)) {//解析 library 标签
                String lname = parser.getAttributeValue(null, "name");
                String lfile = parser.getAttributeValue(null, "file");
                if (lname == null) {
                    //...
                } else if (lfile == null) {
                    //...
                } else {
                    //将 XML 中的 name 和 library 属性值存储到 mSharedLibraries 中
                    mSharedLibraries.put(lname, lfile);
                }
                //...
            } else if ("feature".equals(name)) {//解析 feature 标签
                String fname = parser.getAttributeValue(null, "name");
                //...
                {
                    //在 XML 中定义的 feature 由 FeatureInfo 表达
                    FeatureInfo fi = newFeatureInfo();
                    fi.name = fname;
                    //存储 feature 名和对应的 FeatureInfo 到 mAvailableFeatures 中
                    mAvailableFeatures.put(fname, fi);
                }//...
            } //...
        } //...
    }
}
```

readPermissions 函数就是将 XML 中的标签转换成对应的数据结构。

### readLPw()

readLPw 函数的功能也是解析文件，不过这些文件的内容却是在 PKMS 正常启动后生成的。

```java
Settings() {
    FiledataDir = Environment.getDataDirectory();
    FilesystemDir = new File(dataDir, "system");//指向/data/system目录
    systemDir.mkdirs();//创建该目录
    //...
    /*
        一共有 5 个文件，packages.xml 和 packages-backup.xml 为一组，用于描述系统中
        所安装的 Package 的信息，其中 backup 是临时文件。PKMS 先把数据写到 backup 中，
        信息都写成功后再改名成非 backup 的文件。其目的是防止在写文件过程中出错，导致信息丢失。

        packages-stopped.xml 和 packages-stopped-backup.xml 为一组，用于描述系统中
        强制停止运行的 pakcage 的信息，backup 也是临时文件。如果此处存在该临时文件，表明
        此前系统因为某种原因中断了正常流程 packages.list 列出当前系统中应用级（即UID大于10000）Package 的信息
        */
    mSettingsFilename = new File(systemDir, "packages.xml");
    mBackupSettingsFilename = new File(systemDir, "packages-backup.xml");
    mPackageListFilename = new File(systemDir, "packages.list");
    mStoppedPackagesFilename = new File(systemDir, "packages-stopped.xml");
    mBackupStoppedPackagesFilename = new File(systemDir, "packages-stopped-backup.xml");
}
```

上面 5 个文件共分为三组，这里简单介绍一下这些文件的来历（不考虑临时的 backup 文件）。

-  packages.xml： PKMS 扫描完目标文件夹后会创建该文件。当系统进行程序安装、卸载和更新等操作时，均会更新该文件。该文件保存了系统中与 package 相关的一些信息。
- packages.list：描述系统中存在的所有非系统自带的 APK 的信息。当这些程序有变动时，PKMS 就会更新该文件。
- packages-stopped.xml：从系统自带的设置程序中进入应用程序页面，然后在选择强制停止（ForceStop）某个应用时，系统会将该应用的相关信息记录到此文件中。也就是该文件保存系统中被用户强制停止的 Package 的信息。

readLPw 的函数功能就是解析其中的 XML 文件的内容，然后建立并更新对应的数据结构。例如，停止的 package 重启之后依然是 stopped 状态。

### 第一阶段总结

PKMS 构造函数在第一阶段的工作，主要是扫描并解析 XML 文件，将其中的信息保存到特定的数据结构中。

第一阶段扫描的 XML 文件与权限及上一次扫描得到的 Package 信息有关，它为 PKMS 下一阶段的工作提供了重要的参考信息。

### 扫描 Package

PKMS 构造函数第二阶段的工作就是扫描系统中的 APK 了。由于需要逐个扫描文件，因此手机上装的程序越多，PKMS 的工作量越大，系统启动速度也就越慢。

```java
//...
mRestoredSettings = mSettings.readLPw();//接第一段的结尾
longstartTime = SystemClock.uptimeMillis();//记录扫描开始的时间
//定义扫描参数
intscanMode = SCAN_MONITOR | SCAN_NO_PATHS | SCAN_DEFER_DEX;
if (mNoDexOpt) {
    scanMode |= SCAN_NO_DEX; //在控制扫描过程中是否对 APK 文件进行 dex 优化
}
finalHashSet<String> libFiles = new HashSet<String>();
// mFrameworkDir指向/system/frameworks目录
mFrameworkDir = newFile(Environment.getRootDirectory(), "framework");
// mDalvikCacheDir指向/data/dalvik-cache目录
mDalvikCacheDir = new File(dataDir, "dalvik-cache");
booleandidDexOpt = false;
/*
  获取 Java 启动类库的路径，在 init.rc 文件中通过 BOOTCLASSPATH 环境变量输出，该值如下
  /system/framework/core.jar:/system/frameworks/core-junit.jar:
  /system/frameworks/bouncycastle.jar:/system/frameworks/ext.jar:
  /system/frameworks/framework.jar:/system/frameworks/android.policy.jar:
  /system/frameworks/services.jar:/system/frameworks/apache-xml.jar:
  /system/frameworks/filterfw.jar
  该变量指明了 framework 所有核心库及文件位置
 */
StringbootClassPath = System.getProperty("java.boot.class.path");
if (bootClassPath != null) {
    String[] paths = splitString(bootClassPath, ':');
    for (int i = 0; i < paths.length; i++) {
        try {  //判断该 jar 包是否需要重新做 dex 优化
            if (dalvik.system.DexFile.isDexOptNeeded(paths[i])) {
              /*
               将该 jar 包文件路径保存到 libFiles 中，然后通过 mInstall 对象发送
               命令给 installd，让其对该 jar 包进行 dex 优化
              */
                libFiles.add(paths[i]);
                mInstaller.dexopt(paths[i], Process.SYSTEM_UID, true);
                didDexOpt = true;
            }
        }
        //...
    }
}
//...
/*
还记得 mSharedLibrarires 的作用吗？它保存的是 platform.xml 中声明的系统库的信息。
这里也要判断系统库是否需要做 dex 优化。处理方式同上
*/
if (mSharedLibraries.size() > 0) {
    //...
}
//将 framework-res.apk 添加到 libFiles 中。framework-res.apk 定义了系统常用的
//资源，还有几个重要的 Activity，如长按 Power 键后弹出的选择框
libFiles.add(mFrameworkDir.getPath() + "/framework-res.apk");
//列举 /system/frameworks 目录中的文件
String[] frameworkFiles = mFrameworkDir.list();
if (frameworkFiles != null) {
    //...
    // 判断该目录下的 apk 或 jar 文件是否需要做 dex 优化。处理方式同上
}
/*
上面代码对系统库（BOOTCLASSPATH 指定，或 platform.xml 定义，或
/system/frameworks目录下的 jar 包与 apk 文件）进行一次仔细检查，该优化的一定要优化。
如果发现期间对任何一个文件进行了优化，则设置 didDexOpt 为 true
*/
if (didDexOpt) {
    String[] files = mDalvikCacheDir.list();
    if (files != null) {
        /*
        如果前面对任意一个系统库重新做过 dex 优化，就需要删除 cache 文件。原因和
        dalvik 虚拟机的运行机制有关。暂不探讨 dex 及 cache 文件的作用。
        从删除 cache 文件这个操作来看，这些 cache 文件应该使用了 dex 优化后的系统库
        所以当系统库重新做 dex 优化后，就需要删除旧的 cache 文件。可简单理解为缓存失效
        */
        for (int i = 0; i < files.length; i++) {
            String fn = files[i];
            if (fn.startsWith("data@app@") || fn.startsWith("data@app-private@")) {
                (newFile(mDalvikCacheDir, fn)).delete();
                //...
            }
        }
    }
}
```

清空 cache 文件后，PKMS 终于进入重点段了。接下来看 PKMS 第二阶段工作的核心内容，即扫描 Package。

```java
//创建文件夹监控对象，监视 /system/frameworks 目录。利用了 Linux 平台的 notify 机制
mFrameworkInstallObserver = new AppDirObserver(mFrameworkDir.getPath(), OBSERVER_EVENTS, true);
mFrameworkInstallObserver.startWatching();

/*
 调用 scanDirLI 函数扫描 /system/frameworks 目录，这个函数很重要，稍后会再分析。
 注意，在第三个参数中设置了SCAN_NO_DEX标志，因为该目录下的package在前面的流程
 中已经过判断并根据需要做过dex优化了
 */
scanDirLI(mFrameworkDir, PackageParser.PARSE_IS_SYSTEM
                | PackageParser.PARSE_IS_SYSTEM_DIR, scanMode | SCAN_NO_DEX, 0);
//创建文件夹监控对象，监视 /system/app 目录
mSystemAppDir = new File(Environment.getRootDirectory(), "app");
mSystemInstallObserver = new AppDirObserver(mSystemAppDir.getPath(), OBSERVER_EVENTS, true);
mSystemInstallObserver.startWatching();

//扫描 /system/app 下的 package
scanDirLI(mSystemAppDir, PackageParser.PARSE_IS_SYSTEM | PackageParser.PARSE_IS_SYSTEM_DIR, scanMode, 0);

//监视并扫描 /vendor/app 目录
mVendorAppDir = new File("/vendor/app");
mVendorInstallObserver = new AppDirObserver(mVendorAppDir.getPath(), OBSERVER_EVENTS, true);
mVendorInstallObserver.startWatching();

//扫描 /vendor/app 下的 package
scanDirLI(mVendorAppDir, PackageParser.PARSE_IS_SYSTEM | PackageParser.PARSE_IS_SYSTEM_DIR, scanMode, 0);

//和 installd 交互。以后单独分析 installd
mInstaller.moveFiles();
```

由以上代码可知，PKMS 将扫描以下几个目录。

- /system/frameworks：该目录中的文件都是系统库，例如：framework.jar、services.jar、framework-res.apk。不过 scanDirLI 只扫描APK文件，所以 framework-res.apk 是该目录中唯一“受宠”的文件。
- /system/app：该目录下全是默认的系统应用，例如：Browser.apk、SettingsProvider.apk 等。
- /vendor/app：该目录中的文件由厂商提供，即厂商特定的 APK 文件，不过目前市面上的厂商都把自己的应用放在 /system/app 目录下。

PKMS 调用 scanDirLI 函数进行扫描，下面来分析此函数。

```java
private void scanDirLI(File dir, int flags, int scanMode, long currentTime) {
    String[] files = dir.list();//列举该目录下的文件
    //...
    int i;
    for (i = 0; i < files.length; i++) {
        File file = new File(dir, files[i]);
        if (!isPackageFilename(files[i])) {
            continue; //根据文件名后缀，判断是否为APK 文件。这里只扫描APK 文件
        }

        /*
            调用scanPackageLI函数扫描一个特定的文件，返回值是PackageParser的内部类
            Package，该类的实例代表一个APK文件，所以它就是和APK文件对应的数据结构
            */
        PackageParser.Package pkg = scanPackageLI(file,
                                                  flags | PackageParser.PARSE_MUST_BE_APK, scanMode, currentTime);
        if (pkg == null && (flags & PackageParser.PARSE_IS_SYSTEM) == 0 &&
            mLastScanError == PackageManager.INSTALL_FAILED_INVALID_APK) {
            //注意此处flags的作用，只有非系统Package扫描失败，才会删除该文件
            file.delete();
        }
    }
}
```

接着来分析 scanPackageLI 函数。PKMS 中有两个同名的 scanPackageLI 函数，后面会一一见到。先来看第一个也是最先碰到的 scanPackageLI 函数。

### scanPackageLI()

首次相遇的 scanPackageLI 函数的代码如下：

```java
private PackageParser.Package scanPackageLI(FilescanFile, int parseFlags,
                                                int scanMode, long currentTime) {
    mLastScanError = PackageManager.INSTALL_SUCCEEDED;
    StringscanPath = scanFile.getPath();
    parseFlags |= mDefParseFlags;//默认的扫描标志，正常情况下为0

    //创建一个 PackageParser 对象
    PackageParser pp = new PackageParser(scanPath);
    pp.setSeparateProcesses(mSeparateProcesses);// mSeparateProcesses 为空
    pp.setOnlyCoreApps(mOnlyCore);// mOnlyCore 为 false

    /*
           调用 PackageParser 的 parsePackage 函数解析APK文件。注意，这里把代表屏幕
           信息的 mMetrics 对象也传了进去
        */
    finalPackageParser.Package pkg = pp.parsePackage(scanFile,
                                                     scanPath, mMetrics, parseFlags);
    //...
    PackageSetting ps = null;
    PackageSetting updatedPkg;
    //...

    /*
            这里略去一大段代码，主要是关于 Package 升级方面的工作。
        */
    //收集签名信息，这部分内容涉及 signature。
    if (!collectCertificatesLI(pp, ps, pkg, scanFile, parseFlags))
        return null;

    //判断是否需要设置 PARSE_FORWARD_LOCK 标志，这个标志针对资源文件和 Class 文件
    //不在同一个目录的情况。目前只有 /vendor/app 目录下的扫描会使用该标志。这里不讨论
    //这种情况。
    if (ps != null && !ps.codePath.equals(ps.resourcePath))
        parseFlags |= PackageParser.PARSE_FORWARD_LOCK;

    String codePath = null;
    String resPath = null;
    if ((parseFlags & PackageParser.PARSE_FORWARD_LOCK) != 0) {
        //...//这里不考虑 PARSE_FORWARD_LOCK的情况。
    } else {
        resPath = pkg.mScanPath;
    }

    codePath = pkg.mScanPath;//mScanPath 指向该 APK 文件所在位置
    //设置文件路径信息，codePath 和 resPath 都指向 APK 文件所在位置
    setApplicationInfoPaths(pkg, codePath, resPath);

    //调用第二个 scanPackageLI 函数
    return scanPackageLI(pkg, parseFlags, scanMode | SCAN_UPDATE_SIGNATURE,
                         currentTime);
}
```

scanPackageLI 函数首先调用 PackageParser 对 APK 文件进行解析。根据前面的介绍可知，PackageParser 完成了从物理文件到对应数据结构的转换。下面来分析这个 PackageParser。

### PackageParser

PackageParser 主要负责 APK 文件的解析，即解析 APK 文件中的 AndroidManifest.xml 代码如下：

```java
public Package parsePackage(File sourceFile, String destCodePath,
                                DisplayMetrics metrics, int flags) {
    mParseError = PackageManager.INSTALL_SUCCEEDED;
    mArchiveSourcePath = sourceFile.getPath();
    //...//检查是否为 APK 文件
    XmlResourceParser parser = null;
    AssetManager assmgr = null;
    Resources res = null;
    boolean assetError = true;
    try {
        assmgr = new AssetManager();
        int cookie = assmgr.addAssetPath(mArchiveSourcePath);
        if (cookie != 0) {
            res = new Resources(assmgr, metrics, null);
            assmgr.setConfiguration(0, 0, null, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, Build.VERSION.RESOURCES_SDK_INT);
            /*
              获得一个 XML 资源解析对象，该对象解析的是 APK 中的 AndroidManifest.xml 文件。
              以后再讨论 AssetManager、Resource 及相关的知识
             */
            parser = assmgr.openXmlResourceParser(cookie,
                                                  ANDROID_MANIFEST_FILENAME);
            assetError = false;
        } //...//出错处理
        String[] errorText = new String[1];
        Package pkg = null;
        Exception errorException = null;
        try {
            //调用另外一个 parsePackage 函数
            pkg = parsePackage(res, parser, flags, errorText);
        }//...

        //...//错误处理
        parser.close();
        assmgr.close();
        //保存文件路径，都指向 APK 文件所在的路径
        pkg.mPath = destCodePath;
        pkg.mScanPath = mArchiveSourcePath;
        pkg.mSignatures = null;
        return pkg;
    }
}
```

以上代码中调用了另一个同名的 parsePackage 函数，此函数内容较长，但功能单一，就是解析 AndroidManifest.xml 中的各种标签，这里只提取其中相关的代码：

```java
private Package parsePackage(Resources res, XmlResourceParser parser, int flags, String[] outError)
        throws XmlPullParserException, IOException {
    AttributeSet attrs = parser;
    mParseInstrumentationArgs = null;
    mParseActivityArgs = null;
    mParseServiceArgs = null;
    mParseProviderArgs = null;
    //得到 Package 的名字，其实就是得到 AndroidManifest.xml 中 package 属性的值，
    //每个 APK 都必须定义该属性
    String pkgName = parsePackageName(parser, attrs, flags, outError);
    //...
    int type;
    //...
    //以 pkgName 名字为参数，创建一个 Package 对象。后面的工作就是解析 XML 并填充
    //该 Package 信息
    final Package pkg = new Package(pkgName);
    boolean foundApp = false;
    //...//下面开始解析该文件中的标签，由于这段代码功能简单，所以这里仅列举相关函数
    while (如果解析未完成) {
        //...
        StringtagName = parser.getName(); //得到标签名
        if (tagName.equals("application")) {
            //...//解析 application 标签
            parseApplication(pkg, res, parser, attrs, flags, outError);
        } else if (tagName.equals("permission-group")) {
            //...//解析 permission-group 标签
            parsePermissionGroup(pkg, res, parser, attrs, outError);
        } else if (tagName.equals("permission")) {
            //...//解析 permission 标签
            parsePermission(pkg, res, parser, attrs, outError);
        } else if (tagName.equals("uses-permission")) {
            //从 XML 文件中获取 uses-permission 标签的属性
            sa = res.obtainAttributes(attrs,
                    com.android.internal.R.styleable.AndroidManifestUsesPermission);
            //取出属性值，也就是对应的权限使用声明
            String name = sa.getNonResourceString(com.android.internal.
                    R.styleable.AndroidManifestUsesPermission_name);
            //添加到 Package 的 requestedPermissions 数组
            if (name != null && !pkg.requestedPermissions.contains(name)) {
                pkg.requestedPermissions.add(name.intern());
            }
        } else if (tagName.equals("uses-configuration")) {
            /*
                该标签用于指明本 package 对硬件的一些设置参数，目前主要针对输入设备（触摸屏、键盘
                等）。游戏类的应用可能对此有特殊要求。
            */
            ConfigurationInfocPref = new ConfigurationInfo();
            //...//解析该标签所支持的各种属性
            pkg.configPreferences.add(cPref);//保存到 Package 的 configPreferences 数组
        }
        //...//对其他标签解析和处理
    }
}
```

上面代码展示了 AndroidManifest.xml 解析的流程，其中比较重要的函数是 parserApplication，它用于解析 application 标签及其子标签（Android 的四大组件在 application 标签中已声明）。

PackageParser 及其内部重要成员的信息。

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/03.png" alt=""/>

- PackageParser 定了相当多的内部类，这些内部类的作用就是保存对应的信息。解析 AndroidManifest.xml 文件得到的信息由 Package 保存。从该类的成员变量可看出，和 Android 四大组件相关的信息分别由 activites、receivers、providers、services 保存。由于一个 APK 可声明多个组件，因此 activites 和 receiver s等均声明为 ArrayList。
- 以 PackageParser.Activity 为例，它从 Component<ActivityIntentInfo> 派生。Component 是一个模板类，元素类型是 ActivityIntentInfo，此类的顶层基类是 IntentFilter。PackageParser.Activity 内部有一个 ActivityInfo 类型的成员变量，该变量保存的就是四大组件中 Activity 的信息。细心的读者可能会有疑问，为什么不直接使用 ActivityInfo，而是通过 IntentFilter 构造出一个使用模板的复杂类型 PackageParser.Activity 呢？原来，Package 除了保存信息外，还需要支持 Intent 匹配查询。例如，设置 Intent 的 Action 为某个特定值，然后查找匹配该 Intent 的 Activity。由于 ActivityIntentInfo 是从 IntentFilter 派生的，因此它它能判断自己是否满足该 Intent 的要求，如果满足，则返回对应的 ActivityInfo。
- PackageParser 定了一个轻量级的数据结构 PackageLite，该类仅存储 Package 的一些简单信息。我们在介绍 Package 安装的时候，会遇到  PackageLite。

在 PackageParser 扫描完一个 APK 后，此时系统已经根据该 APK 中 AndroidManifest.xml，创建了一个完整的 Package 对象，下一步就是将该 Package 加入到系统中。此时调用的函数就是另外一个 scanPackageLI，其代码如下：

```java
private PackageParser.PackagescanPackageLI(
    PackageParser.Package pkg, int parseFlags, int scanMode, long currentTime) {
    FilescanFile = new File(pkg.mScanPath);
    //...
    mScanningPath = scanFile;
    //设置 package 对象中 applicationInfo 的 flags 标签，用于标示该 Package 为系统
    //Package
    if ((parseFlags & PackageParser.PARSE_IS_SYSTEM) != 0) {
        pkg.applicationInfo.flags |= ApplicationInfo.FLAG_SYSTEM;
    }

    //下面这句 if 判断极为重要，见下面的解释
    if (pkg.packageName.equals("android")) {
        synchronized (mPackages) {
            if (mAndroidApplication != null) {
                //...

                mPlatformPackage = pkg;
                pkg.mVersionCode = mSdkVersion;
                mAndroidApplication = pkg.applicationInfo;
                mResolveActivity.applicationInfo = mAndroidApplication;
                mResolveActivity.name = ResolverActivity.class.getName();
                mResolveActivity.packageName = mAndroidApplication.packageName;
                mResolveActivity.processName = mAndroidApplication.processName;
                mResolveActivity.launchMode = ActivityInfo.LAUNCH_MULTIPLE;
                mResolveActivity.flags = ActivityInfo.FLAG_EXCLUDE_FROM_RECENTS;
                mResolveActivity.theme = com.android.internal.R.style.Theme_Holo_Dialog_Alert;
                mResolveActivity.exported = true;
                mResolveActivity.enabled = true;
                //mResoveInfo 的 activityInfo 成员指向 mResolveActivity
                mResolveInfo.activityInfo = mResolveActivity;
                mResolveInfo.priority = 0;
                mResolveInfo.preferredOrder = 0;
                mResolveInfo.match = 0;
                mResolveComponentName = new ComponentName(
                        mAndroidApplication.packageName, mResolveActivity.name);
            }
        }
    }
}
```

刚进入 scanPackageLI 函数，我们就发现了一个极为重要的内容，即单独判断并处理 packageName 为 `android` 的 Package。和该 Package 对应的APK是 framework-res.apk，有图为证。

framework-res.apk 的 AndroidManifest.xml：

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/04.png" alt=""/>

实际上，framework-res.apk 还包含了以下几个常用的 Activity。

- ChooserActivity：当多个 Activity 符合某个 Intent 的时候，系统会弹出此 Activity，由用户选择合适的应用来处理。
- RingtonePickerActivity：铃声选择 Activity。
- ShutdownActivity：关机前弹出的选择对话框。

由前述知识可知，该 Package 和系统息息相关，因此它得到了 PKMS 的特别青睐，主要体现在以下几点。

- mPlatformPackage 成员用于保存该 Package 信息。
- mAndroidApplication 用于保存此 Package 中的 ApplicationInfo。
- mResolveActivity 指向用于表示 ChooserActivity 信息的 ActivityInfo。
- mResolveInfo 为 ResolveInfo 类型，它用于存储系统解析 Intent（经 IntentFilter 的过滤）后得到的结果信息，例如：满足某个 Intent 的 Activity 的信息。由前面的代码可知，mResolveInfo 的 activityInfo 其实指向的就是 mResolveActivity。

> 注意：在从 PKMS 中查询满足某个 Intent 的 Activity 时，返回的就是 ResolveInfo，再根据 ResolveInfo 的信息得到具体的 Activity。

此处保存这些信息，主要是为了提高运行过程中的效率。Goolge工 程师可能觉得 ChooserActivity 使用的地方比较多，所以这里单独保存了此 Activity 的信息。

```java
//...//mPackages 用于保存系统内的所有 Package，以 packageName 为 key
if (mPackages.containsKey(pkg.packageName)
        || mSharedLibraries.containsKey(pkg.packageName)) {
    return null;
}

File destCodeFile = newFile(pkg.applicationInfo.sourceDir);
FiledestResourceFile = new File(pkg.applicationInfo.publicSourceDir);
SharedUserSettingsuid = null;//代表该 Package 的 SharedUserSetting 对象
PackageSetting pkgSetting = null;//代表该 Package 的 PackageSetting 对象
synchronized (mPackages) {
    //...//此段代码大约有300行左右，主要做了以下几方面工作
    /*
      1. 如果该 Package 声明了”uses-libraries” 话，那么系统要判断该 library 是否在 mSharedLibraries 中
      2. 如果 package 声明了 SharedUser，则需要处理 SharedUserSettings 相关内容，由 Settings 的 getSharedUserLPw 函数处理
      3. 处理 pkgSetting，通过调用 Settings 的 getPackageLPw 函数完成
      4. 调用 verifySignaturesLP 函数，检查该 Package 的 signature
     */
}
final long scanFileTime = scanFile.lastModified();
final boolean forceDex = (scanMode & SCAN_FORCE_DEX) != 0;
//确定运行该 package 的进程的进程名，一般用 packageName 作为进程名
pkg.applicationInfo.processName = fixProcessName(
        pkg.applicationInfo.packageName,
        pkg.applicationInfo.processName,
        pkg.applicationInfo.uid);

if (mPlatformPackage == pkg) {
    dataPath = new File(Environment.getDataDirectory(), "system");
    pkg.applicationInfo.dataDir = dataPath.getPath();
} else {
    /*
     getDataPathForPackage 函数返回该 package 的目录，一般是 /data/data/packageName/
   */
    dataPath = getDataPathForPackage(pkg.packageName, 0);
    if (dataPath.exists()) {
        //...//如果该目录已经存在，则要处理 uid 的问题
    } else {
        //...//向 installd 发送 install 命令，实际上就是在 /data/data 下
        //建立 packageName 目录。后续将分析 installd 相关知识
        int ret = mInstaller.install(pkgName, pkg.applicationInfo.uid,
                pkg.applicationInfo.uid);
        //为系统所有 user 安装此程序
        mUserManager.installPackageForAllUsers(pkgName,
                pkg.applicationInfo.uid);
        if (dataPath.exists()) {
            pkg.applicationInfo.dataDir = dataPath.getPath();
        } //...

        if (pkg.applicationInfo.nativeLibraryDir == null &&
                pkg.applicationInfo.dataDir != null) {
            //...//为该 Package 确定 native library 所在目录
            //一般是 /data/data/packagename/lib
        }
    }

    //如果该 APK 包含了 native 动态库，则需要将它们从 APK 文件中解压并复制到对应目录中
    if (pkg.applicationInfo.nativeLibraryDir != null) {
        try {
            final File nativeLibraryDir = new
                    File(pkg.applicationInfo.nativeLibraryDir);
            final String dataPathString = dataPath.getCanonicalPath();

            //从 2.3 开始，系统 package 的 native 库统一放在 /system/lib 下。所以
            //系统不会提取系统 Package 目录下 APK 包中的 native 库
            if (isSystemApp(pkg) && !isUpdatedSystemApp(pkg)) {
                NativeLibraryHelper.removeNativeBinariesFromDirLI(
                        nativeLibraryDir)){
                } else if (nativeLibraryDir.getParentFile().getCanonicalPath()
                        .equals(dataPathString)) {
                    boolean isSymLink;
                    try {
                        isSymLink = S_ISLNK(Libcore.os.lstat(
                                nativeLibraryDir.getPath()).st_mode);

                    } //...//判断是否为链接，如果是，需要删除该链接
                    if (isSymLink) {
                        mInstaller.unlinkNativeLibraryDirectory(dataPathString);
                    }

                    //在 lib 下建立和 CPU 类型对应的目录，例如 ARM 平台的是 arm/，MIPS 平台的是 mips/
                    NativeLibraryHelper.copyNativeBinariesIfNeededLI(scanFile,
                            nativeLibraryDir);
                } else {
                    mInstaller.linkNativeLibraryDirectory(dataPathString,
                            pkg.applicationInfo.nativeLibraryDir);
                }
            } //...
        }
        pkg.mScanPath = path;
        if ((scanMode & SCAN_NO_DEX) == 0) {
            //...//对该 APK 做 dex 优化
            performDexOptLI(pkg, forceDex, (scanMode & SCAN_DEFER_DEX);
        }
        //如果该 APK 已经存在，要先杀掉运行该 APK 的进程
        if ((parseFlags & PackageManager.INSTALL_REPLACE_EXISTING) != 0) {
            killApplication(pkg.applicationInfo.packageName,
                    pkg.applicationInfo.uid);
        }
        //...
        /*
         在此之前，四大组件信息都属于 Package 的私有财产，现在需要把它们登记注册到 PKMS 内部的
         财产管理对象中。这样，PKMS 就可对外提供统一的组件信息，而不必拘泥于具体的 Package
         */
        synchronized (mPackages) {
            if ((scanMode & SCAN_MONITOR) != 0) {
                mAppDirs.put(pkg.mPath, pkg);
            }
            mSettings.insertPackageSettingLPw(pkgSetting, pkg);
            mPackages.put(pkg.applicationInfo.packageName, pkg);
            //处理该 Package 中的 Provider 信息
            int N = pkg.providers.size();
            int i;
            for (i = 0; i < N; i++) {
                PackageParser.Providerp = pkg.providers.get(i);
                p.info.processName = fixProcessName(
                        pkg.applicationInfo.processName,
                        p.info.processName, pkg.applicationInfo.uid);
                //mProvidersByComponent 提供基于 ComponentName 的 Provider 信息查询
                mProvidersByComponent.put(new ComponentName(
                        //...
            }
            //处理该 Package 中的 Service 信息
            N = pkg.services.size();
            r = null;
            for (i = 0; i < N; i++) {
                PackageParser.Service s = pkg.services.get(i);
                mServices.addService(s);
            }
            //处理该 Package 中的 BroadcastReceiver 信息
            N = pkg.receivers.size();
            r = null;
            for (i = 0; i < N; i++) {
                PackageParser.Activity a = pkg.receivers.get(i);
                mReceivers.addActivity(a, "receiver");
                //...
            }
            //处理该 Package 中的 Activity 信息
            N = pkg.activities.size();
            r = null;
            for (i = 0; i < N; i++) {
                PackageParser.Activity a = pkg.activities.get(i);
                mActivities.addActivity(a, "activity");
            }
            //处理该 Package 中的 PermissionGroups 信息
            N = pkg.permissionGroups.size();
            //...//permissionGroups 处理
            N = pkg.permissions.size();
            //...//permissions 处理
            N = pkg.instrumentation.size();
            //...//instrumentation 处理
            if (pkg.protectedBroadcasts != null) {
                N = pkg.protectedBroadcasts.size();
                for (i = 0; i < N; i++) {
                    mProtectedBroadcasts.add(pkg.protectedBroadcasts.get(i));
                }
            }
            //...//Package 的私有财产终于完成了公有化改造
            return pkg;
        }
    }
}
```

scanPackageLI() 总结

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/05.png" alt=""/>

扫描非系统 Package，非系统 Package 就是指那些不存储在系统目录下的 APK 文件，这部分代码如下：

```java
if (!mOnlyCore) {//mOnlyCore 用于控制是否扫描非系统 Package
    Iterator<PackageSetting> psit = mSettings.mPackages.values().iterator();

    while (psit.hasNext()) {
        //...//删除系统package中那些不存在的APK
    }

    mAppInstallDir = new File(dataDir, "app");
    //...//删除安装不成功的文件及临时文件
    if (!mOnlyCore) {
        //在普通模式下，还需要扫描 /data/app 以及 /data/app_private 目录
        mAppInstallObserver = new AppDirObserver(
                mAppInstallDir.getPath(), OBSERVER_EVENTS, false);
        mAppInstallObserver.startWatching();
        scanDirLI(mAppInstallDir, 0, scanMode, 0);
        mDrmAppInstallObserver = newAppDirObserver(
                mDrmAppPrivateInstallDir.getPath(), OBSERVER_EVENTS, false);
        mDrmAppInstallObserver.startWatching();
        scanDirLI(mDrmAppPrivateInstallDir,
                PackageParser.PARSE_FORWARD_LOCK, scanMode, 0);
    } else {
        mAppInstallObserver = null;
        mDrmAppInstallObserver = null;
    }
}
```

结合前述代码，这里总结几个存放APK文件的目录。

- 系统 Package 目录包括：/system/frameworks、/system/app 和 /vendor/app。
- 非系统 Package 目录包括：/data/app、/data/app-private。

### 第二阶段总结

PKMS 构造函数第二阶段的工作任务非常繁重，要创建比较多的对象，所以它是一个耗时耗内存的操作。在工作中，我们一直想优化该流程以加快启动速度，例如：延时扫描不重要的 APK，或者保存 Package 信息到文件中，然后在启动时从文件中恢复这些信息以减少 APK 文件读取并解析 XML 的工作量。但是一直没有一个比较完满的解决方案，原因有很多。比如：APK 之间有着比较微妙的依赖关系，因此到底延时扫描哪些 APK，尚不能确定。

### 构造函数扫尾工作

下面分析 PKMS 第三阶段的工作，这部分任务比较简单，就是将第二阶段收集的信息再集中整理一次，比如将有些信息保存到文件中，相关代码如下：

```java
	mSettings.mInternalSdkPlatform= mSdkVersion;

    //汇总并更新和 Permission 相关的信息
    updatePermissionsLPw(null, null, true, regrantPermissions,regrantPermissions);

    //将信息写到 package.xml、package.list 及 package-stopped.xml 文件中
    mSettings.writeLPr();
    Runtime.getRuntime().gc();
    mRequiredVerifierPackage= getRequiredVerifierLPr();
    //...//PKMS 构造函数返回
}
```

从流程角度看，PKMS 构造函数的功能还算清晰，无非是扫描 XML 或 APK 文件，但是其中涉及的数据结构及它们之间的关系却较为复杂。这里有一些建议供读者参考：

- 理解 PKMS 构造函数工作的三个阶段及其各阶段的工作职责。
- 了解 PKMS 第二阶段工作中解析 APK 文件的几个关键步骤。
- 了解重点数据结构的名字和大体功能。

### 获取 PackageManager 服务

ContextImpl.java

```Java
public PackageManager getPackageManager() {
    if (mPackageManager != null) {
        return mPackageManager;
    }
	//见下面分析
    IPackageManager pm = ActivityThread.getPackageManager();
    if (pm != null) {
        //创建 ApplicationPackageManager 对象
        return (mPackageManager = new ApplicationPackageManager(this, pm));
    }
    return null;
}
```

获取 PKMS 服务，并创建 ApplicationPackageManager 对象。

ActivityThread.java

```Java
public static IPackageManager getPackageManager() {
    if (sPackageManager != null) {
        return sPackageManager;
    }
    IBinder b = ServiceManager.getService("package");
    sPackageManager = IPackageManager.Stub.asInterface(b);
    return sPackageManager;
}
```

与 ServiceManager 通讯获取到 PKMS 的代理对象。

### PKMS.performBootDexOpt()

PackageManagerService.java

```Java
public void performBootDexOpt() {
   // 确保只有 system 或者 root uid 有权限执行该方法
   enforceSystemOrRoot("Only the system can request dexopt be performed");

   //运行在同一个进程,此处拿到的 MountService 的服务端
   IMountService ms = PackageHelper.getMountService();
   if (ms != null) {
       final boolean isUpgrade = isUpgrade(); //处于更新状态，则执行fstrim
       boolean doTrim = isUpgrade;
       if (doTrim) {
           Slog.w(TAG, "Running disk maintenance immediately due to system update");
       } else {
           //interval 默认值为 3 天
           final long interval = android.provider.Settings.Global.getLong(
                   mContext.getContentResolver(),
                   android.provider.Settings.Global.FSTRIM_MANDATORY_INTERVAL,
                   DEFAULT_MANDATORY_FSTRIM_INTERVAL);
           if (interval > 0) {
               final long timeSinceLast = System.currentTimeMillis() - ms.lastMaintenance();
               if (timeSinceLast > interval) {
                   doTrim = true; //距离上次 fstrim 时间超过 3 天，则执行 fstrim
               }
           }
       }
       //此处 ms 是指 MountService，该过程发送消息 H_FSTRIM 给 handler，然后再向 vold 发送 fstrim 命令
       if (doTrim) {
           ms.runMaintenance();
       }
   }

   final ArraySet<PackageParser.Package> pkgs;
   synchronized (mPackages) {
       //清空延迟执行 dexopt 操作的 app，获取 dexopt 操作的 app 集合
       pkgs = mPackageDexOptimizer.clearDeferredDexOptPackages();
   }

   if (pkgs != null) {
       ArrayList<PackageParser.Package> sortedPkgs = new ArrayList<PackageParser.Package>();

       for (Iterator<PackageParser.Package> it = pkgs.iterator(); it.hasNext();) {
           PackageParser.Package pkg = it.next();
           //将 pkgs 中的核心 app 添加到 sortedPkgs
           if (pkg.coreApp) {
               sortedPkgs.add(pkg);
               it.remove();
           }
       }

       //获取监听 PRE_BOOT_COMPLETE 的系统 app 集合
       Intent intent = new Intent(Intent.ACTION_PRE_BOOT_COMPLETED);
       ArraySet<String> pkgNames = getPackageNamesForIntent(intent);

       for (Iterator<PackageParser.Package> it = pkgs.iterator(); it.hasNext();) {
           PackageParser.Package pkg = it.next();
           //将 pkg 中监听 PRE_BOOT_COMPLETE 的 app 添加到 sortedPkgs
           if (pkgNames.contains(pkg.packageName)) {
               sortedPkgs.add(pkg);
               it.remove();
           }
       }

       //获取 pkgs 中最近一周使用过的 app，详见下面
       filterRecentlyUsedApps(pkgs);

       //将最近一周的 app 添加到 sortedPkgs
       for (PackageParser.Package pkg : pkgs) {
           sortedPkgs.add(pkg);
       }

       if (mLazyDexOpt) {
           filterRecentlyUsedApps(sortedPkgs);
       }

       int i = 0;
       int total = sortedPkgs.size();
       File dataDir = Environment.getDataDirectory();
       long lowThreshold = StorageManager.from(mContext).getStorageLowBytes(dataDir);
       ...

       for (PackageParser.Package pkg : sortedPkgs) {
           long usableSpace = dataDir.getUsableSpace();
           if (usableSpace < lowThreshold) {
               break;
           }
           //详见下面
           performBootDexOpt(pkg, ++i, total);
       }
   }
}

private void filterRecentlyUsedApps(Collection<PackageParser.Package> pkgs) {

     if (mLazyDexOpt || (!isFirstBoot() && mPackageUsage.isHistoricalPackageUsageAvailable())) {
         int total = pkgs.size();
         int skipped = 0;
         long now = System.currentTimeMillis();
         for (Iterator<PackageParser.Package> i = pkgs.iterator(); i.hasNext();) {
             PackageParser.Package pkg = i.next();
             // 过滤出最近使用过的 app
             long then = pkg.mLastPackageUsageTimeInMills;
             if (then + mDexOptLRUThresholdInMills < now) {
                 i.remove();
                 skipped++;
             }
         }
     }
}

private void performBootDexOpt(PackageParser.Package pkg, int curr, int total) {
    if (!isFirstBoot()) {
        ActivityManagerNative.getDefault().showBootMessage(
              mContext.getResources().getString(R.string.android_upgrading_apk,
                  curr, total), true);
    }
    PackageParser.Package p = pkg;
    synchronized (mInstallLock) {
        mPackageDexOptimizer.performDexOpt(p, null /* instruction sets */,
                false /* force dex */, false /* defer */, true /* include dependencies */,
                false /* boot complete */, false /*useJit*/);
    }
}
```


### PKMS.systemReady()

PackageManagerService.java

```Java
public void systemReady() {
    mSystemReady = true;
    ...

    synchronized (mPackages) {
        ArrayList<PreferredActivity> removed = new ArrayList<PreferredActivity>();
        for (int i=0; i<mSettings.mPreferredActivities.size(); i++) {
            PreferredIntentResolver pir = mSettings.mPreferredActivities.valueAt(i);
            removed.clear();
            for (PreferredActivity pa : pir.filterSet()) {
                if (mActivities.mActivities.get(pa.mPref.mComponent) == null) {
                    removed.add(pa);
                }
            }
            if (removed.size() > 0) {
                for (int r=0; r<removed.size(); r++) {
                    PreferredActivity pa = removed.get(r);
                    pir.removeFilter(pa);
                }
                mSettings.writePackageRestrictionsLPr(
                        mSettings.mPreferredActivities.keyAt(i));
            }
        }

        for (int userId : UserManagerService.getInstance().getUserIds()) {
            if (!mSettings.areDefaultRuntimePermissionsGrantedLPr(userId)) {
                grantPermissionsUserIds = ArrayUtils.appendInt(
                        grantPermissionsUserIds, userId);
            }
        }
    }

    sUserManager.systemReady(); //多用户服务

    //升级所有已获取的默认权限
    for (int userId : grantPermissionsUserIds) {
        mDefaultPermissionPolicy.grantDefaultPermissions(userId);
    }

    //处理所有等待系统准备就绪的消息
    if (mPostSystemReadyMessages != null) {
        for (Message msg : mPostSystemReadyMessages) {
            msg.sendToTarget();
        }
        mPostSystemReadyMessages = null;
    }

    //观察外部存储设备
    final StorageManager storage = mContext.getSystemService(StorageManager.class);
    storage.registerListener(mStorageListener);

    mInstallerService.systemReady();
    mPackageDexOptimizer.systemReady();

    MountServiceInternal mountServiceInternal = LocalServices.getService(MountServiceInternal.class);
    mountServiceInternal.addExternalStoragePolicy(...);
}
```

PackageManagerService 启动完整流程图：

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/07.png" alt=""/>

## installd

PackageManagerServie 服务负责应用的安装、卸载等相关工作，而真正干活的还是 installd。 其中 PKMS 执行权限为 system，而进程 installd 的执行权限为 root。

### 启动

installd 是由 Android 系统的 init 进程(pid=1)，在解析 init.rc 文件的如下代码块时，通过 fork 创建的用户空间的守护进程 installd。

```C
service installd /system/bin/installd
    class main
    socket installd stream 600 system system
```

installd 是随着系统启动过程中 main class 而启动的，并且会创建一个 socket 套接字，用于跟上层的 PKMS 进行交互。 installd 的启动入口 frameworks/base/cmds/installd/installd.c 的 main() 方法，接下来从这里开始说起。

installd.cpp

```C++
int main(const int argc __unused, char *argv[]) {
    char buf[BUFFER_MAX]; //buffer大小为1024Byte
    struct sockaddr addr;
    socklen_t alen;
    int lsocket, s;
    //...

    //初始化全局信息【1】
    if (initialize_globals() < 0) {
            exit(1);
    }
    
    //初始化相关目录【2】
    if (initialize_directories() < 0) {
        exit(1);
    }
    
    //获取套接字"installd"
    lsocket = android_get_control_socket(SOCKET_PATH);
    
    if (listen(lsocket, 5)) { //监听socket消息
        exit(1);
    }
    fcntl(lsocket, F_SETFD, FD_CLOEXEC);

    for (;;) {
        alen = sizeof(addr);
        s = accept(lsocket, &addr, &alen); //接受socket消息
        if (s < 0) {
            continue;
        }
        fcntl(s, F_SETFD, FD_CLOEXEC);

        for (;;) {
            unsigned short count;
            //读取指令的长度
            if (readx(s, &count, sizeof(count))) {
                break;
            }
            if ((count < 1) || (count >= BUFFER_MAX)) {
                break;
            }
            //读取指令的内容
            if (readx(s, buf, count)) {
                break;
            }
            buf[count] = 0;
            //...
            //执行指令【3】
            if (execute(s, buf)) break;
        }
        close(s);
    }
    return 0;
}
```


installd.cpp -> initialize_globals

```C++
int initialize_globals() {
    // 数据目录/data/
    if (get_path_from_env(&android_data_dir, "ANDROID_DATA") < 0) {
        return -1;
    }

    // app目录/data/app/
    if (copy_and_append(&android_app_dir, &android_data_dir, APP_SUBDIR) < 0) {
        return -1;
    }

    // 受保护的app目录/data/priv-app/
    if (copy_and_append(&android_app_private_dir, &android_data_dir, PRIVATE_APP_SUBDIR) < 0) {
        return -1;
    }

    // app本地库目录/data/app-lib/
    if (copy_and_append(&android_app_lib_dir, &android_data_dir, APP_LIB_SUBDIR) < 0) {
        return -1;
    }

    // sdcard挂载点/mnt/asec
    if (get_path_from_env(&android_asec_dir, "ASEC_MOUNTPOINT") < 0) {
        return -1;
    }

    // 多媒体目录/data/media
    if (copy_and_append(&android_media_dir, &android_data_dir, MEDIA_SUBDIR) < 0) {
        return -1;
    }

    // 外部app目录/mnt/expand
    if (get_path_from_string(&android_mnt_expand_dir, "/mnt/expand/") < 0) {
        return -1;
    }

    // 系统和厂商目录
    android_system_dirs.count = 4;

    android_system_dirs.dirs = (dir_rec_t*) calloc(android_system_dirs.count, sizeof(dir_rec_t));
    //...
    dir_rec_t android_root_dir;
    // 目录/system
    if (get_path_from_env(&android_root_dir, "ANDROID_ROOT") < 0) {
        return -1;
    }

    // 目录/system/app
    android_system_dirs.dirs[0].path = build_string2(android_root_dir.path, APP_SUBDIR);
    android_system_dirs.dirs[0].len = strlen(android_system_dirs.dirs[0].path);
    
    // 目录/system/app-lib
    android_system_dirs.dirs[1].path = build_string2(android_root_dir.path, PRIV_APP_SUBDIR);
    android_system_dirs.dirs[1].len = strlen(android_system_dirs.dirs[1].path);

    // 目录/vendor/app/
    android_system_dirs.dirs[2].path = strdup("/vendor/app/");
    android_system_dirs.dirs[2].len = strlen(android_system_dirs.dirs[2].path);

    // 目录/oem/app/
    android_system_dirs.dirs[3].path = strdup("/oem/app/");
    android_system_dirs.dirs[3].len = strlen(android_system_dirs.dirs[3].path);

    return 0;
}
```

installd.cpp -> initialize_directories

```C++
int initialize_directories() {
    int res = -1;

    //读取当前文件系统版本
    char version_path[PATH_MAX];
    snprintf(version_path, PATH_MAX, "%s.layout_version", android_data_dir.path);

    int oldVersion;
    if (fs_read_atomic_int(version_path, &oldVersion) == -1) {
        oldVersion = 0;
    }
    int version = oldVersion;

    // 目录/data/user
    char *user_data_dir = build_string2(android_data_dir.path, SECONDARY_USER_PREFIX);
    // 目录/data/data
    char *legacy_data_dir = build_string2(android_data_dir.path, PRIMARY_USER_PREFIX);
    // 目录/data/user/0
    char *primary_data_dir = build_string3(android_data_dir.path, SECONDARY_USER_PREFIX, "0");
    //...
    //将/data/user/0链接到/data/data
    if (access(primary_data_dir, R_OK) < 0) {
        if (symlink(legacy_data_dir, primary_data_dir)) {
            goto fail;
        }
    }
    //... //处理data/media 相关
    return res;
}
```


installd.cpp -> execute

```C++
static int execute(int s, char cmd[BUFFER_MAX]) {
    char reply[REPLY_MAX];
    char *arg[TOKEN_MAX+1];
    unsigned i;
    unsigned n = 0;
    unsigned short count;
    int ret = -1;
    reply[0] = 0;

    arg[0] = cmd;
    while (*cmd) {
        if (isspace(*cmd)) {
            *cmd++ = 0;
            n++;
            arg[n] = cmd;
            if (n == TOKEN_MAX) {
                goto done;
            }
        }
        if (*cmd) {
          cmd++; //计算参数个数
        }
    }

    for (i = 0; i < sizeof(cmds) / sizeof(cmds[0]); i++) {
        if (!strcmp(cmds[i].name,arg[0])) {
            if (n != cmds[i].numargs) {
                //参数个数不匹配，直接返回
                ALOGE("%s requires %d arguments (%d given)\n",
                    cmds[i].name, cmds[i].numargs, n);
            } else {
                //执行相应的命令[见小节2.5]
                ret = cmds[i].func(arg + 1, reply);
            }
            goto done;
        }
    }

done:
    if (reply[0]) {
        n = snprintf(cmd, BUFFER_MAX, "%d %s", ret, reply);
    } else {
        n = snprintf(cmd, BUFFER_MAX, "%d", ret);
    }
    if (n > BUFFER_MAX) n = BUFFER_MAX;
    count = n;
    
    //将命令执行后的返回值写入socket套接字
    if (writex(s, &count, sizeof(count))) return -1;
    if (writex(s, cmd, count)) return -1;
    return 0;
}
```

### Installer

当守护进程 installd 启动完成后，上层 framework 便可以通过 socket 跟该守护进程进行通信。 在 SystemServer 启动服务的过程中创建 Installer 对象，便会有一次跟 installd 通信的过程。

SystemServer.java

```Java
private void startBootstrapServices() {
    //启动 installer 服务
    Installer installer = mSystemServiceManager.startService(Installer.class);
    //...
}
```

Installer.java

```Java
public Installer(Context context) {
    super(context);
    //创建 InstallerConnection 对象
    mInstaller = new InstallerConnection();
}

public void onStart() {
  Slog.i(TAG, "Waiting for installd to be ready.");
  mInstaller.waitForConnection();
}
```

先创建 Installer 对象，再调用 onStart() 方法，该方法中主要工作是等待 socket 通道建立完成。

InstallerConnection.java

```Java
public void waitForConnection() {
    for (;;) {
        if (execute("ping") >= 0) {
            return;
        }
        Slog.w(TAG, "installd not ready");
        SystemClock.sleep(1000);
    }
}

public int execute(String cmd) {
    String res = transact(cmd);
    try {
        return Integer.parseInt(res);
    } catch (NumberFormatException ex) {
        return -1;
    }
}

public synchronized String transact(String cmd) {
    if (!connect()) {
        return "-1";
    }

    if (!writeCommand(cmd)) {
        if (!connect() || !writeCommand(cmd)) {
            return "-1";
        }
    }

    //读取应答消息
    final int replyLength = readReply();
    if (replyLength > 0) {
        String s = new String(buf, 0, replyLength);
        return s;
    } else {
        return "-1";
    }
}

private boolean connect() {
    if (mSocket != null) {
        return true;
    }
    Slog.i(TAG, "connecting...");
    try {
        mSocket = new LocalSocket();

        LocalSocketAddress address = new LocalSocketAddress("installd",
                LocalSocketAddress.Namespace.RESERVED);

        mSocket.connect(address);

        mIn = mSocket.getInputStream();
        mOut = mSocket.getOutputStream();
    } catch (IOException ex) {
        disconnect();
        return false;
    }
    return true;
}

private boolean writeCommand(String cmdString) {
    final byte[] cmd = cmdString.getBytes();
    final int len = cmd.length;
    if ((len < 1) || (len > buf.length)) {
        return false;
    }

    buf[0] = (byte) (len & 0xff);
    buf[1] = (byte) ((len >> 8) & 0xff);
    try {
        mOut.write(buf, 0, 2); //写入长度
        mOut.write(cmd, 0, len); //写入具体命令
    } catch (IOException ex) {
        disconnect();
        return false;
    }
    return true;
}

private int readReply() {
    if (!readFully(buf, 2)) {
        return -1;
    }

    final int len = (((int) buf[0]) & 0xff) | ((((int) buf[1]) & 0xff) << 8);
    if ((len < 1) || (len > buf.length)) {
        disconnect();
        return -1;
    }

    if (!readFully(buf, len)) {
        return -1;
    }

    return len;
} 

private boolean readFully(byte[] buffer, int len) {
     try {
         Streams.readFully(mIn, buffer, 0, len);
     } catch (IOException ioe) {
         disconnect();
         return false;
     }
     return true;
 }
```

可见，一次 transact 过程为先 connect() 来判断是否建立 socket 连接，如果已连接则通过 writeCommand() 将命令写入 socket 的 mOut 管道，等待从管道的 mIn 中 readFully() 读取应答消息。


## Apk 安装过程分析

### adb install 分析

adb install 有多个参数，这里仅考虑最简单的，如： `adb install frameworktest.apk`。adb 是一个命令，install 是它的参数。此处直接跳到处理 install 参数的代码：

commandline.c

```C
int adb_commandline(int argc, char **argv){
   	//... 
	if(!strcmp(argv[0], "install")) {
       	//...
		//调用 install_app 函数处理
       	return install_app(ttype, serial, argc, argv);
	}
	//...
}

int install_app(transport_type transport, char*serial, int argc, char** argv){
	//要安装的APK现在还在Host机器上，要先把APK复制到手机中。
   	//这里需要设置复制目标的目录，如果安装在内部存储中，则目标目录为/data/local/tmp；
   	//如果安装在SD卡上，则目标目录为/sdcard/tmp。
    static const char *const DATA_DEST = "/data/local/tmp/%s";
    static const char *const SD_DEST = "/sdcard/tmp/%s";
    const char* where = DATA_DEST;
    char apk_dest[PATH_MAX];
    char verification_dest[PATH_MAX];
    char *apk_file;
    char *verification_file = NULL;
    int file_arg = -1;
    int err
    int i;

    for (i =1; i < argc; i++) {
        if(*argv[i] != '-') {
           file_arg = i
           break;
        } else if (!strcmp(argv[i], "-i")) {
            i++;
        } else if (!strcmp(argv[i], "-s")) {
           where = SD_DEST; //-s参数指明该APK安装到SD卡
        }
    }
    //...
    apk_file = argv[file_arg];
    //...
    //获取目标文件的全路径，如果安装在内部存储中，则目标全路径为/data/local/tmp/安装包名，
    //调用do_sync_push将此APK传送到手机的目标路径
    err = do_sync_push(apk_file, apk_dest, 1 /* verify APK */);
	//... 
    //执行 pm 命令【1】

    pm_command(transport,serial, argc, argv);
	//...
  	cleanup_apk:

    //在手机中执行shell rm 命令，删除刚才传送过去的目标 Apk 文件
  	delete_file(transport, serial, apk_dest);
    return err;
}
```

commandline.c

```C
static int pm_command(transport_type transport,char* serial,
	int argc, char** argv){
    char buf[4096];
    snprintf(buf,sizeof(buf), "shell:pm");
  	//...
  	//发送"shell:pm install 参数"给手机端的 adbd
   	send_shellcommand(transport, serial, buf);
    return 0;
}
```

手机端的 adbd 在收到客户端发来的 shell:pm 命令时会启动一个 shell，然后在其中执行 pm。

pm 实际上是一个脚本，其内容如下：

```C
# Script to start "pm" on the device,which has a very rudimentary
# shell.
#

base=/system
export CLASSPATH=$base/frameworks/pm.jar
exec app_process $base/bincom.android.commands.pm.Pm "$@"
```

在编译 system.image 时，Android.mk 中会将该脚本复制到 system/bin 目录下。从 pm 脚本的内容来看，它就是通过 app_process 执行 pm.jar 包的 main 函数。

pm.java

```Java
public static void main(String[] args) {
	new Pm().run(args);//创建一个 Pm 对象，并执行它的 run 函数
}

//直接分析 run 函数
public void run(String[] args) {
	boolean validCommand = false;
	//...
	//获取PKMS的binder客户端
	mPm = IPackageManager.Stub
			.asInterface(ServiceManager.getService("package"));
	//...
	mArgs = args;
	String op = args[0];
	mNextArg = 1;
	//...//处理其他命令，这里仅考虑 install 的处理
	if("install".equals(op)) {
   		runInstall();
   		return;
	}
   //...
}

private void runInstall() {
	intinstallFlags = 0;
	String installerPackageName = null;
	String opt;
	while ((opt=nextOption()) != null) {
   		if (opt.equals("-l")) {
       		installFlags |= PackageManager.INSTALL_FORWARD_LOCK;
		} else if (opt.equals("-r")) {
			installFlags |= PackageManager.INSTALL_REPLACE_EXISTING;
		} else if (opt.equals("-i")) {
			installerPackageName = nextOptionData();
			//... //参数解析
		} 
		//...
	}

	final Uri apkURI;
	final Uri verificationURI;
	final String apkFilePath = nextArg();
	System.err.println("/tpkg: " + apkFilePath);

	if(apkFilePath != null) {
		apkURI = Uri.fromFile(new File(apkFilePath));
	}
	//...
	//获取 Verification Package 的文件位置
	final String verificationFilePath = nextArg();

	if(verificationFilePath != null) {
  		verificationURI = Uri.fromFile(new File(verificationFilePath));
	}else {
   		verificationURI = null;
	}
	//创建 PackageInstallObserver，用于接收 PKMS 的安装结果
	PackageInstallObserver obs = new PackageInstallObserver();
	try{
	  	//调用 PKMS 的 installPackageWithVerification 完成安装
	   	mPm.installPackageWithVerification(apkURI, obs,
                          installFlags,installerPackageName,
                          verificationURI,null);
		synchronized (obs) {
		while(!obs.finished) {
  			try{
          		obs.wait();//等待安装结果
     		}
		//...
 		}
	 	if(obs.result == PackageManager.INSTALL_SUCCEEDED) {
	    	System.out.println("Success");//安装成功，打印 Success
	 	}
		//...//安装失败，打印失败原因
	} 
	//...
}
```

Pm 解析参数后，最终通过 PKMS 的 Binder 客户端调用 installPackageWithVerification 以完成后续的安装工作，所以，下面进入 PKMS 看看安装到底是怎么一回事。

### installPackageWithVerification 分析

PackageManagerService.java::installPackageWithVerification

```C
public void installPackageWithVerification(UripackageURI,
		IPackageInstallObserverobserver,
		int flags, String installerPackageName, Uri verificationURI,
		ManifestDigest manifestDigest) {

	//检查客户端进程是否具有安装 Package 的权限。在本例中，该客户端进程是 shell
	mContext.enforceCallingOrSelfPermission(
	android.Manifest.permission.INSTALL_PACKAGES,null);
	final int uid = Binder.getCallingUid();
	final int filteredFlags;

	if(uid == Process.SHELL_UID || uid == 0) {
		//...//如果通过 shell pm 的方式安装，则增加 INSTALL_FROM_ADB 标志
		filteredFlags = flags | PackageManager.INSTALL_FROM_ADB;
	}else {
		filteredFlags = flags & ~PackageManager.INSTALL_FROM_ADB;
	}

	//创建一个 Message，code 为 INIT_COPY，将该消息发送给之前在 PKMS 构造函数中
	//创建的 mHandler 对象，将在另外一个工作线程中处理此消息
	final Message msg = mHandler.obtainMessage(INIT_COPY);

	//创建一个 InstallParams，其基类是 HandlerParams
	msg.obj = new InstallParams(packageURI, observer,
	filteredFlags,installerPackageName,
	verificationURI,manifestDigest);
	mHandler.sendMessage(msg);
}
```

### INIT_COPY 处理

INIT_COPY 只是安装流程的第一步。先来看相关代码：

PackageManagerService.java::handleMesssage

```C
public void handleMessage(Message msg) {
	try {
		doHandleMessage(msg);//调用 doHandleMessage 函数
	} //...
}

void doHandleMessage(Message msg) {
    switch (msg.what) {
        case INIT_COPY: {
            //这里记录的是 params 的基类类型 HandlerParams，实际类型为 InstallParams
            HandlerParams params = (HandlerParams) msg.obj;
            //idx为当前等待处理的安装请求的个数
            int idx = mPendingInstalls.size();

            if (!mBound) {
                //APK 的安装居然需要使用另外一个 APK 提供的服务，该服务就是
                //DefaultContainerService，由 DefaultCotainerService.apk 提供，
                //下面的 connectToService 函数将调用 bindService 来启动该服务
                if (!connectToService()) {
                    params.serviceError();
                    return;
                } else {
                    ////如果已经连上，则以 idx 为索引，将 params 保存到 mPendingInstalls 中
                    mPendingInstalls.add(idx, params);
                }
            } else {
                mPendingInstalls.add(idx, params);
                if (idx == 0) {
                    //如果安装请求队列之前的状态为空，则表明要启动安装
                    mHandler.sendEmptyMessage(MCS_BOUND);
                }
            }
            break;
        }
        case MCS_BOUND: {
            //稍后分析
        }
    }
}
```

这里假设之前已经成功启动了 DefaultContainerService（以后简称 DCS），并且 idx 为零，所以这是 PKMS 首次处理安装请求，也就是说，下一个将要处理的是 MCS_BOUND 消息。

### MCS_BOUND 处理

```Java
void doHandleMessage(Message msg) {
    switch (msg.what) {
        case INIT_COPY: {
            //...
        }
        case MCS_BOUND: {
            if (msg.obj != null) {
                mContainerService = (IMediaContainerService) msg.obj;
            }
            if (mContainerService == null) {
                if (!mBound) {
                    //如果没法启动该 service，则不能安装程序
                    mPendingInstalls.clear();
                }
            } else if (mPendingInstalls.size() > 0) {
                HandlerParams params = mPendingInstalls.get(0);
                if (params != null) {
                    //调用 params 对象的 startCopy 函数，该函数由基类 HandlerParams 定义
                    if (params.startCopy()) {
                        //...
                        if (mPendingInstalls.size() > 0) {
                            mPendingInstalls.remove(0);//删除队列头
                        }
                        if (mPendingInstalls.size() == 0) {
                            if (mBound) {
                                //如果安装请求都处理完了，则需要和 Service 断绝联系,
                                //通过发送 MSC_UNB 消息处理断交请求
                                removeMessages(MCS_UNBIND);
                                Message ubmsg = obtainMessage(MCS_UNBIND);
                                sendMessageDelayed(ubmsg, 10000);
                            }
                        } else {
                            //如果还有未处理的请求，则继续发送 MCS_BOUND 消息。
                            //为什么不通过一个循环来处理所有请求呢
                            mHandler.sendEmptyMessage(MCS_BOUND);
                        }
                    }
                }
            }
            break;
        }
    }
}
```

MCS_BOUND 的处理还算简单，就是调用 HandlerParams 的 startCopy 函数。

PackageManagerService.java::HandlerParams.startCopy()

```Java
final boolean startCopy() {
	booleanres;
	try {
		//MAX_RETIRES 目前为 4，表示尝试 4 次安装，如果还不成功，则认为安装失败
		if(++mRetries > MAX_RETRIES) {
			mHandler.sendEmptyMessage(MCS_GIVE_UP);
			handleServiceError();
			return false;
		} else {
			handleStartCopy();//调用派生类的 handleStartCopy 函数
			res= true;
		}
	} ...

	handleReturnCode();//调用派生类的 handleReturnCode，返回处理结果
	return res;
}
```

在上述代码中，基类的 startCopy 将调用子类实现的 handleStartCopy 和 handleReturnCode 函数。下面来看 InstallParams 是如何实现这两个函数的。

###  InstallParams 分析

PackageManagerService::InstallParams.handleStartCopy()

```Java
public void handleStartCopy() throwsRemoteException {

	int ret = PackageManager.INSTALL_SUCCEEDED;
	final boolean fwdLocked = (flags &PackageManager.INSTALL_FORWARD_LOCK) != 0;

	//根据 adb install 的参数，判断安装位置
	final boolean onSd = (flags & PackageManager.INSTALL_EXTERNAL) != 0;
	final boolean onInt = (flags & PackageManager.INSTALL_INTERNAL) != 0;

	PackageInfoLite pkgLite = null;

	if(onInt && onSd) {
		//APK 不能同时安装在内部存储和 SD 卡上
		ret = PackageManager.INSTALL_FAILED_INVALID_INSTALL_LOCATION;

	} else if (fwdLocked && onSd) {
		//fwdLocked 的应用不能安装在 SD 卡上
		ret = PackageManager.INSTALL_FAILED_INVALID_INSTALL_LOCATION;
	} else {
		final long lowThreshold;

		//获取 DeviceStorageMonitorService 的 binder 客户端
		final DeviceStorageMonitorService dsm = 
					(DeviceStorageMonitorService) ServiceManager.getService(
					DeviceStorageMonitorService.SERVICE);

		if(dsm == null) {
			lowThreshold = 0L;
		}else {
			//从 DSMS 查询内部空间最小余量，默认是总空间的10%
			lowThreshold = dsm.getMemoryLowThreshold();
		}

		try {
			//授权 DefContainerService URI 读权限
			mContext.grantUriPermission(DEFAULT_CONTAINER_PACKAGE,
						packageURI,Intent.FLAG_GRANT_READ_URI_PERMISSION);
	
			//调用 DCS 的 getMinimalPackageInfo 函数，得到一个 PackageLite 对象，详见下面分析
			pkgLite = mContainerService.getMinimalPackageInfo(packageURI, flags,lowThreshold);

		}finally //...//撤销 URI 授权

		//PacakgeLite 的 recommendedInstallLocation 成员变量保存该 APK 推荐的安装路径
		int loc = pkgLite.recommendedInstallLocation;

		if (loc == PackageHelper.RECOMMEND_FAILED_INVALID_LOCATION) {
			ret = PackageManager.INSTALL_FAILED_INVALID_INSTALL_LOCATION;
		} else if...{
		} else {
			//根据 DCS 返回的安装路径，还需要调用 installLocationPolicy 进行检查
			loc = installLocationPolicy(pkgLite, flags);
	
			if(!onSd && !onInt) {
				if(loc == PackageHelper.RECOMMEND_INSTALL_EXTERNAL) {
					flags |= PackageManager.INSTALL_EXTERNAL;
					flags &=~PackageManager.INSTALL_INTERNAL;
	
				} //...//处理安装位置为内部存储的情况
			}
		}
	}

	//创建一个安装参数对象，对于安装位置为内部存储的情况，args 的真实类型为 FileInstallArgs
	final InstallArgs args = createInstallArgs(this);

	mArgs = args;

	if (ret == PackageManager.INSTALL_SUCCEEDED) {
		final int requiredUid = mRequiredVerifierPackage == null ? -1 : getPackageUid(mRequiredVerifierPackage);
		if(requiredUid != -1 && isVerificationEnabled()) {
			//...//verification 的处理，这部分代码后续再介绍
		} else {
			//调用 args 的 copyApk 函数
			ret = args.copyApk(mContainerService, true);
		}
	}
	mRet = ret;//确定返回值
}
```

在以上代码中，一共列出了五个关键点，总结如下：

- 调用 DCS 的 getMinimalPackageInfo 函数，将得到一个 PackageLite 对象，该对象是一个轻量级的用于描述 APK 的结构（相比PackageParser.Package 来说）。在这段代码逻辑中，主要想取得其 recommendedInstallLocation 的值。此值表示该 APK 推荐的安装路径。
- 调用 installLocationPolicy 检查推荐的安装路径。例如：系统 Package 不允许安装在 SD 卡上。
- createInstallArgs 将根据安装位置创建不同的 InstallArgs。如果是内部存储，则返回 FileInstallArgs，否则为 SdInstallArgs。
- 在正式安装前，应先对该 APK 进行必要的检查。这部分代码后续再介绍。
- 调用 InstallArgs 的 copyApk。对本例来说，将调用 FileInstallArgs 的 copyApk 函数。

### DefaultContainerService 分析

DefaultContainerService.java::getMinimalPackageInfo()

```Java
public PackageInfoLite getMinimalPackageInfo(finalUri fileUri, int flags, longthreshold) {
	//注意该函数的参数：fileUri 指向该 APK 的文件路径（此时还在 /data/local/tmp 下）
	PackageInfoLite ret = new PackageInfoLite();
	//...
	String scheme = fileUri.getScheme();
	//...
	String archiveFilePath = fileUri.getPath();
	DisplayMetrics metrics = new DisplayMetrics();
	metrics.setToDefaults();

	//调用 PackageParser 的 parsePackageLite 解析该 APK 文件
 	PackageParser.PackageLite pkg =
			PackageParser.parsePackageLite(archiveFilePath,0);

	if (pkg == null) {//解析失败
		//...//设置错误值
		return ret;
	}

	ret.packageName = pkg.packageName;
	ret.installLocation = pkg.installLocation;
	ret.verifiers = pkg.verifiers;

	//调用 recommendAppInstallLocation，取得一个合理的安装位置
	ret.recommendedInstallLocation =

	recommendAppInstallLocation(pkg.installLocation,archiveFilePath,
	           flags, threshold);
	return ret;
}
```

APK 可在 AndroidManifest.xml 中声明一个安装位置，不过 DCS 除了解析该位置外，还需要做进一步检查，这个工作由 recommendAppInstallLocation 函数完成，代码如下：

DefaultContainerService.java::recommendAppInstallLocation()

```Java
private int recommendAppInstallLocation(intinstallLocation, 
				StringarchiveFilePath, int flags,long threshold) {
	int prefer;
	boolean checkBoth = false;

	check_inner: {
		if((flags & PackageManager.INSTALL_FORWARD_LOCK) != 0) {
			prefer = PREFER_INTERNAL;
			break check_inner; //根据 FOWRAD_LOCK 的情况，只能安装在内部存储
		} else if ((flags & PackageManager.INSTALL_INTERNAL) != 0) {
			prefer = PREFER_INTERNAL;
			break check_inner;
		}
		//...//检查各种情况
		} else if(installLocation == PackageInfo.INSTALL_LOCATION_AUTO) {
			prefer= PREFER_INTERNAL;//一般设定的位置为 AUTO，默认是内部空间
			checkBoth = true; //设置checkBoth为true
			breakcheck_inner;
		}

		//查询 settings 数据库中的 secure 表，获取用户设置的安装路径
		intinstallPreference =
				Settings.System.getInt(getApplicationContext()
				.getContentResolver(),
		
		Settings.Secure.DEFAULT_INSTALL_LOCATION,
		PackageHelper.APP_INSTALL_AUTO);
		
		if(installPreference == PackageHelper.APP_INSTALL_INTERNAL) {
			prefer = PREFER_INTERNAL;
			break check_inner;
		} else if(installPreference == PackageHelper.APP_INSTALL_EXTERNAL) {
			prefer = PREFER_EXTERNAL;
			breakcheck_inner;
		}

		prefer =PREFER_INTERNAL;
	}

	//判断外部存储空间是否为模拟的，这部分内容我们以后再介绍
	final boolean emulated = Environment.isExternalStorageEmulated();
	final FileapkFile = new File(archiveFilePath);
	boolean fitsOnInternal = false;
	
	if(checkBoth || prefer == PREFER_INTERNAL) {
		try {//检查内部存储空间是否足够大
			fitsOnInternal = isUnderInternalThreshold(apkFile, threshold);
		} //...
	}

	boolean fitsOnSd = false;
	if(!emulated && (checkBoth || prefer == PREFER_EXTERNAL)) {
		try{ //检查外部存储空间是否足够大
			fitsOnSd = isUnderExternalThreshold(apkFile);
		} //...
	}

	if (prefer== PREFER_INTERNAL) {
		if(fitsOnInternal) {//返回推荐安装路径为内部空间
			return PackageHelper.RECOMMEND_INSTALL_INTERNAL;
		}
	} else if (!emulated && prefer == PREFER_EXTERNAL) {
		if(fitsOnSd) {//返回推荐安装路径为外部空间
			returnPackageHelper.RECOMMEND_INSTALL_EXTERNAL;
		}
	}

	if(checkBoth) {
		if(fitsOnInternal) {//如果内部存储满足条件，先返回内部空间
			return PackageHelper.RECOMMEND_INSTALL_INTERNAL;
		}else if (!emulated && fitsOnSd) {
			return PackageHelper.RECOMMEND_INSTALL_EXTERNAL;
		}
	}

	//... //到此，前几个条件都不满足，此处将根据情况返回一个明确的错误值
	return PackageHelper.RECOMMEND_FAILED_INSUFFICIENT_STORAGE;
	}
}
```

DCS 的 getMinimalPackageInfo 函数为了得到一个推荐的安装路径做了不少工作，其中，各种安装策略交叉影响。这里总结一下相关的知识点：

- APK 在 AndroidManifest.xml 中设置的安装点默认为 AUTO，在具体对应时倾向内部空间。
- 用户在 Settings 数据库中设置的安装位置。
- 检查外部存储或内部存储是否有足够空间。

### InstallArgs 的 copyApk 函数分析

至此，我们已经得到了一个合适的安装位置，下一步工作就由 copyApk 来完成。

PackageManagerService.java::InstallArgs.copyApk()

```Java
int copyApk(IMediaContainerService imcs, booleantemp) throws RemoteException {
    if (temp) {
        /*
            本例中temp参数为true，createCopyFile将在/data/app下创建一个临时文件。
            临时文件名为vmdl-随机数.tmp。为什么会用这样的文件名呢？
            因为PKMS通过Linux的inotify机制监控了/data/app,目录，如果新复制生成的文件名后缀
            为apk，将触发PKMS扫描。为了防止发生这种情况，这里复制生成的文件才有了
            如此奇怪的名字
            */
        createCopyFile();
    }

    FilecodeFile = new File(codeFileName);
    //...
    ParcelFileDescriptor out = null;
    try {
        out = ParcelFileDescriptor.open(codeFile, ParcelFileDescriptor.MODE_READ_WRITE);
    }//...

    int ret = PackageManager.INSTALL_FAILED_INSUFFICIENT_STORAGE;
    try {
        mContext.grantUriPermission(DEFAULT_CONTAINER_PACKAGE,
                                    packageURI, Intent.FLAG_GRANT_READ_URI_PERMISSION);
        //调用 DCS 的 copyResource，该函数将执行复制操作，最终结果是 /data/local/tmp
        //下的APK文件被复制到 /data/app 下，文件名也被换成 vmdl-随机数.tmp
        ret = imcs.copyResource(packageURI, out);
    } finally {
        //...//关闭 out，撤销 URI 授权
    }
    return ret;
}
```

### handleReturnCode 分析


在 HandlerParams 的 startCopy 函数中，handleStartCopy 执行完之后，将调用 handleReturnCode 开展后续工作，代码如下：

PackageManagerService.java::InstallParams.HandleParams()

```Java
void handleReturnCode() {
    if (mArgs != null) {
        //调用processPendingInstall函数，mArgs指向之前创建的FileInstallArgs对象
        processPendingInstall(mArgs, mRet);
    }
}

private void processPendingInstall(finalInstallArgs args, final intcurrentStatus) {
    //向 mHandler 中抛一个 Runnable 对象
    mHandler.post(new Runnable() {
        public void run() {
            mHandler.removeCallbacks(this);
            //创建一个 PackageInstalledInfo 对象，
            PackageInstalledInfo res = new PackageInstalledInfo();
            res.returnCode = currentStatus;
            res.uid = -1;
            res.pkg = null;
            res.removedInfo = new PackageRemovedInfo();

            if (res.returnCode == PackageManager.INSTALL_SUCCEEDED) {
                //调用 FileInstallArgs 的 doPreInstall
                args.doPreInstall(res.returnCode);
                synchronized (mInstallLock) {
                    //调用 installPackageLI 进行安装
                    installPackageLI(args, true, res);
                }

                //调用 FileInstallArgs 的 doPostInstall
                args.doPostInstall(res.returnCode);
            }

            final boolean update = res.removedInfo.removedPackage != null;
            boolean doRestore = (!update && res.pkg != null &&
                    res.pkg.applicationInfo.backupAgentName != null);
            int token;//计算一个ID号
            if (mNextInstallToken < 0) mNextInstallToken = 1;
            token = mNextInstallToken++;
            
            //创建一个 PostInstallData 对象
            PostInstallData data = new PostInstallData(args, res);

            //保存到 mRunningInstalls 结构中，以 token 为 key
            mRunningInstalls.put(token, data);
            if (res.returnCode == PackageManager.INSTALL_SUCCEEDED && doRestore){
             //...//备份恢复的情况暂时不考虑
            }

            if (!doRestore) {
                //抛一个 POST_INSTALL 消息给 mHandler 进行处理
                Message msg = mHandler.obtainMessage(POST_INSTALL, token, 0);
                mHandler.sendMessage(msg);
            }
        }
    });
}
```

由上面代码可知，handleReturnCode 主要做了 4 件事情：

- 调用 InstallArgs 的 doPreInstall 函数，在本例中是 FileInstallArgs 的 doPreInstall 函数。
- 调用 PKMS 的 installPackageLI 函数进行 APK 安装，该函数内部将调用 InstallArgs的doRename 对临时文件进行改名。另外，还需要扫描此 APK 文件。此过程和之前介绍的“扫描系统 Package”一节的内容类似。至此，该 APK 中的私有财产就全部被登记到 PKMS 内部进行保存了。
- 调用 InstallArgs 的 doPostInstall 函数，在本例中是 FileInstallArgs 的 doPostInstall 函数。
- 此时，该 APK 已经安装完成（不论失败还是成功），继续向 mHandler 抛送一个 POST_INSTALL 消息，该消息携带一个 token，通过它可从 mRunningInstalls 数组中取得一个 PostInstallData 对象。

这里介绍一下 FileInstallArgs 的 doRename 函数，它的功能是将临时文件改名，最终的文件的名称一般为“包名-数字.apk”。其中，数字是一个 index，从 1 开始。

### POST_INSTALL 处理

PackageManagerService.java::doHandleMessage()

```Java
void doHandleMessage(Message msg) {
    switch (msg.what) {
        case INIT_COPY: {
            //...
        }
        case MCS_BOUND: {
            //...
        }
        case POST_INSTALL: {
            PostInstallData data = mRunningInstalls.get(msg.arg1);
            mRunningInstalls.delete(msg.arg1);
            boolean deleteOld = false;

            if (data != null) {
                InstallArgs args = data.args;
                PackageInstalledInfo res = data.res;

                if (res.returnCode == PackageManager.INSTALL_SUCCEEDED) {
                    final String packageName = res.pkg.applicationInfo.packageName;
                    res.removedInfo.sendBroadcast(false, true, false);
                    Bundle extras = new Bundle(1);
                    extras.putInt(Intent.EXTRA_UID, res.uid);
                    //...
                    final boolean update = res.removedInfo.removedPackage != null;
                    if (update) {
                        extras.putBoolean(Intent.EXTRA_REPLACING, true);
                    }
                    //发送 PACKAGE_ADDED 广播
                    sendPackageBroadcast(Intent.ACTION_PACKAGE_ADDED,
                                         packageName, extras, null, null, updateUsers);
                    if (update) {
                        //如果是 APK 升级，那么发送 PACKAGE_REPLACE 和 MY_PACKAGE_REPLACED 广播
                        //二者不同之处在于 PACKAGE_REPLACE 将携带一个 extra 信息
                        //...
                    }
                    //...
                }
                Runtime.getRuntime().gc();
                if (deleteOld) {
                    synchronized (mInstallLock) {
                        //调用 FileInstallArgs 的 doPostDeleteLI 进行资源清理
                        res.removedInfo.args.doPostDeleteLI(true);
                    }
                }
                if (args.observer != null) {
                    try {
                        // 向 pm 通知安装的结果
                        Bundle extras = extrasForInstallResult(res);
                        args.observer.onPackageInstalled(res.name, res.returnCode,
                                                         res.returnMsg, extras);
                    } catch (RemoteException e) {
                        Slog.i(TAG, "Observer no longer exists.");
                    }
                }
            } else {
                Slog.e(TAG, "Bogus post-install token " + msg.arg1);
            }
        } break;
    }
}
```

### Apk 安装流程总结

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/android_pkms/08.png" alt=""/>


## 参考资料

- [深入理解 PackagerManagerService](http://blog.csdn.net/innost/article/details/47253179)
- [PackageManager 启动篇](http://gityuan.com/2016/11/06/packagemanager/)

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！


