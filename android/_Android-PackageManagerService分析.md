# Android - PackageMangerService 分析

## 概述

PackageManagerService（简称 PKMS），是 Android 系统中核心服务之一，管理着所有跟 package 相关的工作，常见的比如安装、卸载应用。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/android_boot_loader/android-bootloader.png" alt=""/>

PackageManagerService 是在 SystemServer 进程中启动的。如不了解 Android 是如何从开机到 Launcher 启动的过程，请先阅读[Android - 系统启动过程](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/android/Android-系统启动过程.md)。


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
    ...
}

private void startOtherServices() {
    ...
    //启动 MountService，后续 PackageManager 会需要使用
    mSystemServiceManager.startService(MOUNT_SERVICE_CLASS);
    //【3】做 dex 优化。dex 是 Android 上针对 Java 字节码的一种优化技术，可提高运行效率
    mPackageManagerService.performBootDexOpt();
    ...  

    // phase 500
    mSystemServiceManager.startBootPhase(SystemService.PHASE_SYSTEM_SERVICES_READY);
    ...

    //【4】
    mPackageManagerService.systemReady();
    ...
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
该方法的主要功能创建 PKMS 对象，并将其注册到 ServiceManager。

关于 PKMS 对象的构造方法很长，分为以下几个阶段，每个阶段会输出相应的EventLog： 除了阶段1的开头部分代码，后续代码都是同时持有同步锁mPackages和mInstallLock的过程中执行的。

```Java
public PackageManagerService(Context context, Installer installer, 
	boolean factoryTest, boolean onlyCore) {

    阶段1：BOOT_PROGRESS_PMS_START
    ...
    synchronized (mInstallLock) {
    synchronized (mPackages) {
        ...
        阶段2：BOOT_PROGRESS_PMS_SYSTEM_SCAN_START
        阶段3：BOOT_PROGRESS_PMS_DATA_SCAN_START
        阶段4：BOOT_PROGRESS_PMS_SCAN_END
        阶段5：BOOT_PROGRESS_PMS_READY
        ...
    }
    }

    Runtime.getRuntime().gc();
    //暴露私有服务，用于系统组件的使用
    LocalServices.addService(PackageManagerInternal.class, 
		new PackageManagerInternalImpl());
}
```
PKMS初始化过程，分为5个阶段：

- PMS_START 阶段：

1. 创建 Settings 对象；
2. 将 6 类 shareUserId 到 mSettings；
3. 初始化 SystemConfig；
4. 创建名为“PackageManager”的 handler 线程 mHandlerThread；
5. 创建 UserManagerService 多用户管理服务；
6. 通过解析 4 大目录中的 xmL 文件构造共享 mSharedLibraries；

- PMS_SYSTEM_SCAN_START 阶段：

1. mSharedLibraries 共享库中的文件执行 dexopt 操作；
2. system/framework 目录中满足条件的 apk 或 jar 文件执行 dexopt 操作；
扫描系统apk;


- PMS_DATA_SCAN_START阶段：

1. 扫描 /data/app 目录下的 apk;
2. 扫描 /data/app-private 目录下的 apk;

- PMS_SCAN_END 阶段：

将上述信息写回 /data/system/packages.xml;

- PMS_READY 阶段：

创建服务 PackageInstallerService；

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

## installd

PackageManagerServie 服务负责应用的安装、卸载等相关工作，而真正干活的还是installd。 其中 PKMS 执行权限为system，而进程 installd 的执行权限为root。

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
    ...

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
            ...
            
            //执行指令【3】
            if (execute(s, buf)) break;
        }
        close(s);
    }
    return 0;
}
```


installd.cpp->initialize_globals

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
    ...

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

installd.cpp->initialize_directories

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
    ...

    //将/data/user/0链接到/data/data
    if (access(primary_data_dir, R_OK) < 0) {
        if (symlink(legacy_data_dir, primary_data_dir)) {
            goto fail;
        }
    }

    ... //处理data/media 相关
    
    return res;
}
```


installd.cpp->execute

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
    ...
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

可见，一次transact 过程为先 connect() 来判断是否建立 socket 连接，如果已连接则通过 writeCommand() 将命令写入 socket 的 mOut 管道，等待从管道的 mIn 中 readFully() 读取应答消息。


## Apk 安装过程分析

### adb install 分析

adb install 有多个参数，这里仅考虑最简单的，如 adb installframeworktest.apk。adb 是一个命令，install 是它的参数。此处直接跳到处理 install 参数的代码：

commandline.c

```C
int adb_commandline(int argc, char **argv){

   	...... 

	if(!strcmp(argv[0], "install")) {
	
       	......
		//调用 install_app 函数处理
       	return install_app(ttype, serial, argc, argv);
	
	}

	......
}

int install_app(transport_type transport, char*serial, int argc, char** argv){

	//要安装的APK现在还在Host机器上，要先把APK复制到手机中。
   	//这里需要设置复制目标的目录，如果安装在内部存储中，则目标目录为/data/local/tmp；
   	//如果安装在SD卡上，则目标目录为/sdcard/tmp。
    staticconst char *const DATA_DEST = "/data/local/tmp/%s";
    staticconst char *const SD_DEST = "/sdcard/tmp/%s";
    constchar* where = DATA_DEST;
    charapk_dest[PATH_MAX];
    charverification_dest[PATH_MAX];
    char*apk_file;
    char*verification_file = NULL;
    intfile_arg = -1;
    int err
    int i;

    for (i =1; i < argc; i++) {
        if(*argv[i] != '-') {
           file_arg = i
           break;
        }else if (!strcmp(argv[i], "-i")) {
            i++;
        }else if (!strcmp(argv[i], "-s")) {
           where = SD_DEST; //-s参数指明该APK安装到SD卡
        }
    }

    ......

    apk_file= argv[file_arg];

    ......

    //获取目标文件的全路径，如果安装在内部存储中，则目标全路径为/data/local/tmp/安装包名，
    //调用do_sync_push将此APK传送到手机的目标路径
    err =do_sync_push(apk_file, apk_dest, 1 /* verify APK */);
    
	...... 

    //执行 pm 命令【1】

    pm_command(transport,serial, argc, argv);

	......

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

    charbuf[4096];
    snprintf(buf,sizeof(buf), "shell:pm");

  	......

  	//发送"shell:pm install 参数"给手机端的 adbd
   	send_shellcommand(transport, serial, buf);
    return 0;
}
```

手机端的 adbd 在收到客户端发来的 shell:pm 命令时会启动一个 shell，然后在其中执行 pm。

pm实际上是一个脚本，其内容如下：

```C
# Script to start "pm" on the device,which has a very rudimentary
# shell.
#

base=/system
export CLASSPATH=$base/frameworks/pm.jar
exec app_process $base/bincom.android.commands.pm.Pm "$@"
```

在编译 system.imag e时，Android.mk 中会将该脚本复制到 system/bin 目录下。从 pm 脚本的内容来看，它就是通过 app_process 执行 pm.jar 包的 main 函数。

pm.java

```Java
public static void main(String[] args) {
	new Pm().run(args);//创建一个 Pm 对象，并执行它的 run 函数
}

//直接分析 run 函数
public void run(String[] args) {
	boolean validCommand = false;

	......

	//获取PKMS的binder客户端

	mPm = IPackageManager.Stub
			.asInterface(ServiceManager.getService("package"));

	......

	mArgs = args;
	String op = args[0];
	mNextArg = 1;

	......//处理其他命令，这里仅考虑 install 的处理

	if("install".equals(op)) {
   		runInstall();
   		return;

	}

   ......
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
			...... //参数解析
		} 
		......
	}

	final Uri apkURI;
	final Uri verificationURI;
	final String apkFilePath = nextArg();
	System.err.println("/tpkg: " + apkFilePath);

	if(apkFilePath != null) {
		apkURI = Uri.fromFile(new File(apkFilePath));
	}

	......

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
		......
 		}

	 	if(obs.result == PackageManager.INSTALL_SUCCEEDED) {
	    	System.out.println("Success");//安装成功，打印 Success
	 	}
		
		......//安装失败，打印失败原因
	} 
	
	......
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
		......//如果通过 shell pm 的方式安装，则增加 INSTALL_FROM_ADB 标志
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
	} ......
}

void doHandleMessage(Message msg) {
	switch(msg.what) {
		case INIT_COPY: {
			//这里记录的是 params 的基类类型 HandlerParams，实际类型为 InstallParams
			HandlerParams params = (HandlerParams) msg.obj;
	
			//idx为当前等待处理的安装请求的个数
			int idx = mPendingInstalls.size();
	
			if(!mBound) {
				/*
				APK 的安装居然需要使用另外一个 APK 提供的服务，该服务就是
				DefaultContainerService，由 DefaultCotainerService.apk 提供，
				下面的 connectToService 函数将调用 bindService 来启动该服务
				*/
				if(!connectToService()) {
				 	return;
				}else {
					//如果已经连上，则以 idx 为索引，将 params 保存到 mPendingInstalls 中
					mPendingInstalls.add(idx, params);
				}
			} else {
				mPendingInstalls.add(idx, params);
	
				if(idx == 0) {
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
	......
}
```

这里假设之前已经成功启动了 DefaultContainerService（以后简称 DCS），并且 idx 为零，所以这是 PKMS 首次处理安装请求，也就是说，下一个将要处理的是 MCS_BOUND 消息。

### MCS_BOUND 处理

```Java
void doHandleMessage(Message msg) {
	switch(msg.what) {
		case INIT_COPY: {
			......
		}
		break;
		case MCS_BOUND: {
			if(msg.obj != null) {
				mContainerService= (IMediaContainerService) msg.obj;
			}

			if(mContainerService == null) {
				......//如果没法启动该 service，则不能安装程序
				mPendingInstalls.clear();
			} else if(mPendingInstalls.size() > 0) {
				HandlerParamsparams = mPendingInstalls.get(0);
				if(params != null) {
					//调用 params 对象的 startCopy 函数，该函数由基类 HandlerParams 定义
					if(params.startCopy()) {

						......

						if(mPendingInstalls.size() > 0) {
							mPendingInstalls.remove(0);//删除队列头
						}

						if (mPendingInstalls.size() == 0) {
							if (mBound) {
								......//如果安装请求都处理完了，则需要和 Service 断绝联系,
								//通过发送 MSC_UNB 消息处理断交请求
								removeMessages(MCS_UNBIND);
								Message ubmsg = obtainMessage(MCS_UNBIND);
								sendMessageDelayed(ubmsg, 10000);
							}
						}else {
							//如果还有未处理的请求，则继续发送 MCS_BOUND 消息。
							//为什么不通过一个循环来处理所有请求呢
							mHandler.sendEmptyMessage(MCS_BOUND);
						}
					}
				}
				......
			}
			break;
		}
	}
	......
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
	} ......

	handleReturnCode();//调用派生类的 handleReturnCode，返回处理结果
	return res;
}
```

在上述代码中，基类的 startCopy 将调用子类实现的 handleStartCopy 和 handleReturnCode 函数。下面来看 InstallParams 是如何实现这两个函数的。

###  InstallParams 分析

PackageManagerService::InstallParams.handleStartCopy()

```Java
public void handleStartCopy() throwsRemoteException {

	int ret= PackageManager.INSTALL_SUCCEEDED;
	final boolean fwdLocked = (flags &PackageManager.INSTALL_FORWARD_LOCK) != 0;

	//根据 adb install 的参数，判断安装位置
	final boolean onSd = (flags & PackageManager.INSTALL_EXTERNAL) != 0;
	final boolean onInt = (flags & PackageManager.INSTALL_INTERNAL) != 0;

	PackageInfoLite pkgLite = null;

	if(onInt && onSd) {
		//APK 不能同时安装在内部存储和 SD 卡上
		ret =PackageManager.INSTALL_FAILED_INVALID_INSTALL_LOCATION;

	} else if (fwdLocked && onSd) {
		//fwdLocked 的应用不能安装在 SD 卡上
		ret =PackageManager.INSTALL_FAILED_INVALID_INSTALL_LOCATION;
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

		}finally ......//撤销 URI 授权

		//PacakgeLite 的 recommendedInstallLocation 成员变量保存该 APK 推荐的安装路径
		int loc =pkgLite.recommendedInstallLocation;

		if (loc== PackageHelper.RECOMMEND_FAILED_INVALID_LOCATION) {
			ret= PackageManager.INSTALL_FAILED_INVALID_INSTALL_LOCATION;
		} else if......{
		} else {

			//根据 DCS 返回的安装路径，还需要调用 installLocationPolicy 进行检查
			loc = installLocationPolicy(pkgLite, flags);
	
			if(!onSd && !onInt) {
				if(loc == PackageHelper.RECOMMEND_INSTALL_EXTERNAL) {
					flags |= PackageManager.INSTALL_EXTERNAL;
					flags &=~PackageManager.INSTALL_INTERNAL;
	
				} ......//处理安装位置为内部存储的情况
			}
		}
	}

	//创建一个安装参数对象，对于安装位置为内部存储的情况，args 的真实类型为 FileInstallArgs
	final InstallArgs args = createInstallArgs(this);

	mArgs =args;

	if (ret== PackageManager.INSTALL_SUCCEEDED) {
		final int requiredUid = mRequiredVerifierPackage == null ? -1 : getPackageUid(mRequiredVerifierPackage);
		if(requiredUid != -1 && isVerificationEnabled()) {
			......//verification 的处理，这部分代码后续再介绍
		}else {
			//调用 args 的 copyApk 函数
			ret = args.copyApk(mContainerService, true);
		}
	}
	mRet =ret;//确定返回值
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

	......

	String scheme = fileUri.getScheme();

	......

	String archiveFilePath = fileUri.getPath();
	DisplayMetrics metrics = new DisplayMetrics();
	metrics.setToDefaults();

	//调用 PackageParser 的 parsePackageLite 解析该 APK 文件
 	PackageParser.PackageLite pkg =
			PackageParser.parsePackageLite(archiveFilePath,0);

	if (pkg== null) {//解析失败

		......//设置错误值
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

		......//检查各种情况

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
		} ......
	}

	boolean fitsOnSd = false;
	if(!emulated && (checkBoth || prefer == PREFER_EXTERNAL)) {
		try{ //检查外部存储空间是否足够大
			fitsOnSd = isUnderExternalThreshold(apkFile);
		} ......
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

	...... //到此，前几个条件都不满足，此处将根据情况返回一个明确的错误值
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

        ......

        ParcelFileDescriptor out = null;
        try {
            out = ParcelFileDescriptor.open(codeFile, ParcelFileDescriptor.MODE_READ_WRITE);
        }......

        int ret = PackageManager.INSTALL_FAILED_INSUFFICIENT_STORAGE;
        try {
            mContext.grantUriPermission(DEFAULT_CONTAINER_PACKAGE,
                    packageURI, Intent.FLAG_GRANT_READ_URI_PERMISSION);
            //调用 DCS 的 copyResource，该函数将执行复制操作，最终结果是 /data/local/tmp
            //下的APK文件被复制到 /data/app 下，文件名也被换成 vmdl-随机数.tmp
            ret = imcs.copyResource(packageURI, out);
        } finally {
            ......//关闭 out，撤销 URI 授权
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
              ......//备份恢复的情况暂时不考虑
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
	switch(msg.what) {
		case INIT_COPY: {
			......
		}
		case MCS_BOUND: {
			......
		}
		case POST_INSTALL:{
            PostInstallData data=mRunningInstalls.get(msg.arg1);
            mRunningInstalls.delete(msg.arg1);
            boolean deleteOld=false;

            if(data!=null){
            	InstallArgs args=data.args;
            	PackageInstalledInfo res=data.res;

            	if(res.returnCode==PackageManager.INSTALL_SUCCEEDED){
            		res.removedInfo.sendBroadcast(false,true);
            		Bundle extras=new Bundle(1);
            		extras.putInt(Intent.EXTRA_UID,res.uid);
					final boolean update=res.removedInfo.removedPackage!=null;

			        if(update){
			        	extras.putBoolean(Intent.EXTRA_REPLACING,true);
			        }

			        //发送 PACKAGE_ADDED 广播
			        sendPackageBroadcast(Intent.ACTION_PACKAGE_ADDED,
			        res.pkg.applicationInfo.packageName,extras,null,null);

			        if(update){
			           /*
			           	如果是 APK 升级，那么发送 PACKAGE_REPLACE 和 MY_PACKAGE_REPLACED 广播。
				        二者不同之处在于 PACKAGE_REPLACE 将携带一个extra信息
				       */
			        }
			
			        Runtime.getRuntime().gc();

			        if(deleteOld){
						synchronized (mInstallLock){
			        		//调用 FileInstallArgs 的 doPostDeleteLI 进行资源清理
			        		res.removedInfo.args.doPostDeleteLI(true);
			        	}
        			}

			        if(args.observer!=null){
				        try{
					        // 向 pm 通知安装的结果
					        args.observer.packageInstalled(res.name,res.returnCode);
				        }......

        			}
			break;
		}
	......
}
```



## 参考资料

- [深入理解 PackagerManagerService](http://blog.csdn.net/innost/article/details/47253179)
- [PackageManager 启动篇](http://gityuan.com/2016/11/06/packagemanager/)


