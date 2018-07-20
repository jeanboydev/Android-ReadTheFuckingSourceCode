## 准备 Mac OS 环境

- 准备一台 Mac 电脑

- Windows 上安装虚拟机

  1. 安装 `Vmware` 虚拟机

     [下载 Vmware 虚拟机](http://www.vmware.com/cn/products/workstation/workstation-evaluation.html)

  2. 使用 `unlocker20x` 破解补丁破解虚拟机

  3. 安装 Mac OS 安装盘镜像，cdr 文件

## 创建 Mac OS 安装盘

- 下载最新版 Mac OS 系统

  在 Mac 系统环境中，打开 `App Store` -> `登陆 Apple ID`，下载最新版 `macOS xxx`。

  下载完后在 `Finder` -> `应用程序` -> `安装 macOS xxx.app`。

- 制作安装盘

  然后插入 U 盘在 lanuchpad 里打开 终端 程序，输入命令：

  > $ sudo （拖拽文件“createinstallmedia”到终端【文件位置在“安装 macOS Sierra.app”-右键-显示包文件-Contents-Resources里】） --volume （拖拽之前插入的U盘图标到终端） --applicationpath （拖拽“应用程序”里的“安装 macOS Sierra.app”到终端） --nointeraction

  输入密码 -> 回车（等待安装盘建立完成）

## 创建 Clover 引导盘

- 下载最新版的 Clover

  [推荐 RehabMan 下载](https://sourceforge.net/projects/cloverefiboot/files/)

  [sourceforge.net 下载](https://bitbucket.org/RehabMan/clover/downloads/)

- 格式化 U 盘

  插入第二只 U 盘，在 `磁盘工具` 中用 `MS-DOS(FAT) 格式`抹掉，名称为 `EFI`，方案为 `主引导记录` 。

  > 注：若找不到，可点击磁盘工具左上角方框按钮选择显示更多。

- 安装 Clover 到 U 盘

  选择自定义：

  - [x] 仅安装 UEFI 开机版本

  - [x] 安装 Clover 到 EFI 系统区

  - [x] 开机主题

  - [x] drivers64UEFI

    - [x] EmuVariableUefi-64.efi

    - [x] OsxAptioFix3Drv-64.efi

    - [x] PartitionDxe-64.efi
    - [x] UsbkbDxe-64
    - [x] UsbMouseDxe-64

  > 注：若不能安装，使用下面命令，打开不明软件来源限制
  >
  > $ sudo spctl --master-disable
  >
  > Clover 中 EFI 说明参考附录1。
  >
  > Clover 中 drivers64UEFI 说明参考附录2。

- 配置 config.plist

  下载最新版的 Clover Configurator：[去下载](https://mackie100projects.altervista.org/download-clover-configurator/)

  使用 Clover Configurator 打开：`EFI` -> `CLOVER` -> `config.plist`

  参考连接：http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1739079&extra=page%3D1%26filter%3Dtypeid%26typeid%3D1300%26typeid%3D1300

## 主板设置

- 无论是哪个系列的芯片组，进入BIOS要把 `VT-d`、`VT-x` 虚拟化关掉。
- USB 选项中的 `EHCI`、`XHCI Hand-off` 打开，不然在引导安装过程中无法识别 U 盘导致无法继续安装。
- `Super IO` 选项也要关闭，各个主板的命名可能不一样（技嘉中叫 IOAPIC 24-119）这个选项和苹果的电源管理可能会发生冲突，导致 AppleLPC.kext 无法加载，无法启用原生电源管理
- 关闭 `CSM`，纯 UEFI 引导
- 电源管理相关的设置会对后期的 Mac 系统优化有所影响，所以我们前期可以先为后期优化做好铺垫。打开 `Intel(R) Speed Shift Technlolgy`、`CPU EIST` 这两个选项对后期的打开 Skylake（Kabylake... 更新的CPU架构）HWP 有所帮助，可以实现对 CPU 的睿频和自动降频节能

## 单盘双系统

- 先安装 Windows

  进入 Windows 系统安装分区界面，按 Shift+F10 进入 Diskpart 命令操作界面使用命令分区。

  > $ list disk	//列出所有磁盘
  >
  > $ select disk 0	//选取磁盘号 0 的磁盘
  >
  > $ convert GPT	//转换成 GPT 分区表
  >
  > $ create partition EFI size=500	//创建 EFI 分区大小为 500M
  >
  > $ create partition MSR size=16	//创建 MSR 分区大小为 16M
  >
  > $ create partition primary size=122885	 //120G=120*1024+5M，加5是为了显示完整的整数G
  >
  > $ list partition	//列出所有分区
  >
  > $ select partition 1	//选择 EFI 分区
  >
  > $ format fs=fat32 label=EFI quick	//格式化 EFI 分区
  >
  > $ select partition 3	//MSR 分区不用格式化，安装程序会自动格式化
  >
  > $ format fs=ntfs label=WIN10 quick		//格式化系统分区
  >
  > $ exit

  正常安装系统。

- Windows 系统下挂在 EFI 分区

  > $ list disk
  > $ select disk 0	//选择EFI引导分区所在的磁盘
  > $ list partition
  > $ select partition 1	//选择EFI引导分区
  > $ assign letter=p	//为所选分区分配盘符，请分配空闲盘符
  > $ remove letter=p	//修改完成后，移除盘符（如果不移除，重启计算机以后，会自动移除）

  这时候 你就可以在 电脑盘里找到 p 盘了，然后下载  [Total Commander](https://www.ghisler.com/download.htm) 就可以正常访问了。

- 安装 Mac OS

  使用磁盘工具，系统盘抹掉为 `APFS` 格式，名称 `Mac OS`，抹完后关闭磁盘工具。

  然后继续选择安装 Mac OS。

  > 注：出现禁止符号可能是 USB 接口不对，换个 USB 接口试试。

## 驱动完善

- 核显

  打开 `config` 文件，左边栏选择 `Graphics`，加入 ig-platform-id 0x19120000，并勾选 `inject Intel`，保存文件。

  下载 `IntelGrapicsFixup` 驱动放到 `other` 文件夹，重启电脑后进入 bios 开启核显，这样核显和 N 卡都驱动了。

- 独显

  10 系列显卡使用 WebDriver：[下载最新的 WebDriver](https://www.tonymacx86.com/nvidia-drivers/)

- 声卡

  声卡驱动推荐使用 [AppleALC](https://github.com/vit9696/AppleALC/releases)，这个驱动可以让你的电脑加载原生的 AppleHDA。

- USB 驱动

- 电源管理

- WIN + MAC 时间不同步问题

  让 Window s把硬件时间当作 UTC 运行，在 CMD 中执行命令：

  > $ Reg add HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation /v RealTimeIsUniversal /t REG_DWORD /d 1

- 开启 HIDPI

  激活 HIDPI

  > $ sudo defaults write /Library/Preferences/com.apple.windowserver.plist DisplayResolutionEnabled -bool true

  获取显示器的 `DisplayVendorID` 和 `DisplayProductID`：

  > $ ioreg -l | grep "DisplayVendorID"
  >
  > $ ioreg -l | grep "DisplayProductID"

  将得到的 ID 数字转换为 16进制，然后创建文件夹及文件：

  ```json
  DisplayVendorID-<DisplayVendorID 的16进制，文件夹>
  	|-DisplayProductID-<DisplayProductID 的16进制，文件没有后缀>
  
  例如：
  DisplayVendorID-10ac
  	|-DisplayProductID-d06e
  ```

  生成自己的 `DisplayProductID-d06e` 中的内容如下：[去生成配置内容](https://comsysto.github.io/Display-Override-PropertyList-File-Parser-and-Generator-with-HiDPI-Support-For-Scaled-Resolutions/)

  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
  <plist version="1.0">
  <dict>
    <key>DisplayProductName</key>
    <string>DELL U2515H</string>
    <key>DisplayProductID</key>
    <integer>53358</integer>
    <key>DisplayVendorID</key>
    <integer>4268</integer>
    <key>scale-resolutions</key>
    <array>
      <data>AAAKAAAABaAAAAABACAAAA==</data>
      <data>AAAFAAAAAtAAAAABACAAAA==</data>
      <data>AAAPAAAACHAAAAABACAAAA==</data>
      <data>AAAHgAAABDgAAAABACAAAA==</data>
      <data>AAAMgAAABwgAAAABACAAAA==</data>
      <data>AAAGQAAAA4QAAAABACAAAA==</data>
      <data>AAAKAgAABaAAAAABACAAAA==</data>
      <data>AAAKrAAABgAAAAABACAAAA==</data>
      <data>AAAFVgAAAwAAAAABACAAAA==</data>
    </array>
  </dict>
  </plist>
  ```

  如果显示器使用 HDMI 链接需要验证下 ProductID：

  > $ ioreg -l -w0 -d0 -r -c AppleDisplay | grep ID | grep -v IO

  用以下配置覆盖之前的配置：

  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
  <plist version="1.0">
  <dict>
    <key>DisplayProductName</key>
    <string>Dell U2515H (HiDPI + RGB)</string>
    <key>IODisplayEDID</key>
      <data>AP///////wAQrG/QTEE0MCkZAQSlNx94JkRVqVVNnSYPUFSlSwCzANEAcU+p
  QIGAd4ABAQEBVl4AoKCgKVAwIDUAKTchAAAaAAAA/wBYWFhYWFhYWFhYWFgK
  AAAA/ABERUxMIFUyNTE1SAogAAAA/QA4Vh5xHgEKICAgICAgAKM=</data>
    <key>DisplayVendorID</key>
    <integer>4268</integer>
    <key>DisplayProductID</key>
    <integer>53360</integer>
    <key>scale-resolutions</key>
      <array>
      <data>AAAPAAAACHAAAAAB</data>
      <data>AAAMgAAABwgAAAAB</data>
      <data>AAALQAAABlQAAAAB</data>
    </array>
  </dict>
  </plist>
  ```

  将刚创建的文件夹以及文件复制到系统目录：

  > /System/Library/Displays/Contents/Resources/Overrides/
  >
  > 注：打开 FInder 按快捷键 Command + Shift + G 可转到指定目录

  完成以后重启电脑，然后 [下载 RDM](http://avi.alkalay.net/software/RDM/) 方便切换分辨率（[RDM 开源项目](https://github.com/avibrazil/RDM)）。

  参考链接：

  - https://comsystoreply.de/blog-post/force-hidpi-resolutions-for-dell-u2515h-monitor
  - https://www.insanelymac.com/forum/topic/310345-qhd-monitor-1920x1080-hidpi/

  [更简便的方式](https://github.com/syscl/Enable-HiDPI-OSX)

## kext 扩展库

- **Lilu.kext**：其实是个补丁驱动，多用于配合其他驱动使用

  https://github.com/acidanthera/Lilu

- **AppleALC.kext**：主要的作用就是加载原生AppleHDA声卡驱动（需要配合lilu.kext使用）

  https://github.com/acidanthera/AppleALC

- **IntelGraphicsFixup.kext**：英特尔GPU内核补丁驱动文件（需要配合lilu.kext使用）

  https://github.com/lvs1974/IntelGraphicsFixup

- **HibernationFixup.kext**：解决某些机器 3&25 模式下的休眠问题

  https://github.com/lvs1974/HibernationFixup

- IntelGraphicsDVMTFixup.kext：主要作用于破解苹果的framebuffer kext的64MB值，一般笔记本bios固定32m 的需要用到它（需要和lilu.kext、IntelGraphicsFixup.kext一起使用）

  https://github.com/BarbaraPalvin/IntelGraphicsDVMTFixup 

- **NvidiaGraphicsFixup.kext**：解决一些 smbios 引起的 n 卡黑屏 并动态添加 HDMI/DP 音频输出

  https://github.com/lvs1974/NvidiaGraphicsFixup

- CoreDisplayFixup.kext：4k分辨率破解驱动需要配合lilu.kext使用

  https://github.com/PMheart/CoreDisplayFixup 

- **CodecCommander.kext**：解决睡眠后声卡没声音

  https://bitbucket.org/RehabMan/os-x-eapd-codec-commander/downloads/

- **AtherosE2200Ethernet.kext**：killer 网卡驱动

  https://github.com/Mieze/AtherosE2200Ethernet

- **FakeSMC.kext**：HWSensors

  https://bitbucket.org/RehabMan/os-x-fakesmc-kozlek/downloads/

- **FakePCIID.kext**：增加 IOPCIDevice 

  https://bitbucket.org/RehabMan/os-x-fake-pci-id/downloads/

- **USBInjectAll.kext**：注入 USB 接口

  https://bitbucket.org/RehabMan/os-x-usb-inject-all/downloads/

> 常见的 kext 资源更新：
>
> - [RehabMan 维护的 kext](https://bitbucket.org/RehabMan/)
> - [vit9696 维护的 kext](https://github.com/vit9696?tab=repositories)
> - [lvs1974 维护的 kext](https://github.com/lvs1974?tab=repositories)
> - [Acidanthera 维护的 kext](https://github.com/acidanthera)

## 附录1 - EFI 目录内文件夹说明

- ACPI：放置 DSDT.aml、ssdt.aml 等
- bak：个人为测试筛选 drivers 而新建，里面放置有备用的 .efi 文件
- **BOOT**：BOOTX64.efi，为 CLOVERX64.efi 改名而来，font 外挂字体，refit.conf 启动菜单配置文件，themes 为主题
- **config.plist**：OSX 启动配置文件，可视作 org.chameleon.Boot.plist 与 SMBios.plist 的合体
- doc：boot1f32 安装脚本（UEFI 可忽略），启动配置示例，修复 DSDT 说明，通过InstallESD.dmg 安装 OSX 说明，Clover 安装说明（UEFI 可忽略），实现 UEFI 启动说明（有参考价值，但稍显简略）
- **drivers64UEFI**：放置 rEFIt  启动时加载的 .efi drivers，某些关乎到 OSX 能否引导成功，如 OsxAptioFixDrv-64.efi
- **kexts**：分类放置不同版本 OSX 的第三方 kexts
- **misc**：放置启动界面 F10 截图、系统启动记录 system.log（Debug 开启时）、preboot.log（GUI中按F2）等
- OEM：按主板或本本型号放置多份 ACPI、kexts 及 ROM，实现单个 U 盘引导多个黑果平台
- ROM：放置显卡 BIOS 等
- tools：放置用于进入 shell 环境的 .efi，不可用于引导 OSX，但可运行一些 .efi 程序

## 附录2 - drivers64UEFI 文件功能说明

- AptioInputFixVit9696

  编写的针对FileVault2启动界面的键盘和鼠标输入设备的支持

- AptioMemoryFix

  Vit9696自OsxAptioFix2驱动优化而来的新驱动，支持更多新特性，例如：

  自动为boot.efi寻找最适合的内存地址，避免启动错误
  当slide值不能被使用的时候提供对KASLR的支持
  新增系统在低内存地址下的安全模式的支持
  确保系统不会出现slide溢出的问题
  尝试修复更多的内存分布问题
  支持硬件NVRAM
  优化一些休眠的问题（暂时不稳定）
  （请勿与其余内存修复驱动同时使用）

- CsmVideoDxe-64

  提供对CSM模块的支持，某些主板若要安装非UEFI系统或者非安全启动的系统，例如Windows7，Linux等设备，需要开启CSM模块，此时需要加入该驱动以修复CloverGUI的显示问题
  Clover推荐关闭CSM模块启用原生GOP显示模块

- **EmuVariableUefi-64**

  macOS使用NVRAM存储一些系统变量，大部分的UEFI主板在配合合适的Aptio驱动后支持原生硬件NVRAM，但是少部分主板不支持NVRAM或者NVRAM的支持有问题，此时建议加入该驱动，该驱动通过开机时加载位于EFI分区内的nvram.plist内容到nvram中，以模拟NVRAM支持
  需要注意的是，是用此驱动，需要勾选“安装RC scripts到目标磁区”选项才有效

- Fat-64

  可选择的64位FAT文件系统的支持

- OsxAptioFixDrv-64

  Dmazar编写的针对UEFI固件的内存问题修复的驱动，对休眠支持不完善
  （请勿与其余内存修复驱动同时使用）

- OsxAptioFix2Drv-64

  Dmazar编写的针对UEFI固件的内存问题修复的驱动，在1代基础之上完善了休眠等高级功能的支持，部分机型需要手动设置slide值
  （请勿与其余内存修复驱动同时使用）

- OsxAptioFix3Drv-64

  Vit9696等作者在OsxAptioFix2Drv-64的基础之上进行了优化，修复了大多数新设备的NVRAM支持，该驱动在部分机型依然需要手动设置slide值
  （请勿与其余内存修复驱动同时使用）

- OsxFatBinaryDrv-64

  可选择的64位FAT文件系统的支持

- OsxLowMemFixDrv-64

  针对UEFI固件内存问题修复的驱动简化版
  （请勿与其余内存修复驱动同时使用）

- **PartitionDxe-64**

  支持非常态的分区配置，如苹果混合分区或Apple分区图。

- **UsbkbDxe-64**

  FileVault2启动界面的键盘输入设备的支持

- UsbMouseDxe-64

  FileVault2启动界面的鼠标输入设备的支持

## 参考链接

- [（7月12日）Lilu.kext扩展库本体1.2.5以及AppleALC 1.3.0等必备插件更新 支持10.14+](http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1765509&highlight=LILU)
- [基本概念_efi驱动程序](https://clover-wiki.zetam.org/zh-CN/What-is-what#%E5%9F%BA%E6%9C%AC%E6%A6%82%E5%BF%B5_efi%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8F)
- [新版Clover中Drivers64UEFI中驱动详解](http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1775839&highlight=drivers64UEFI)
- [ Drivers64UEFI目录下的驱动作用.......................](http://bbs.pcbeta.com/viewthread-1584909-1-1.html)
- [Clover+UEFI+GPT全新单碟双系统安装WIN10+OS10.11.2基本完美宽屏惊艳](http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1668544&highlight=%B5%A5%B5%FA%CB%AB%CF%B5%CD%B3)
- [幸运草Clover引导UEFI纯GPT分区多系统 ML Lion Win8 Win7 ubuntu FusionDrive同样适用](http://bbs.pcbeta.com/viewthread-1197452-1-1.html)
- [【GA-Z270X Gaming 7】+i7-7700k+GTX 1080公版+NVMe 100%完美！](http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1739079&extra=page%3D1%26filter%3Dtypeid%26typeid%3D1300%26typeid%3D1300)
- [最通俗易懂的黑苹果安装教程，送给苦苦爬贴的小白们](http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1726460&page=1&authorid=3000840)
- [分享下10.13系统安装教程](http://bbs.pcbeta.com/forum.php?mod=viewthread&tid=1778772&page=1)