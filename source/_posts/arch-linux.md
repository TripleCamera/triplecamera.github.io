---
title: Arch Linux 害了他
date: 2024-02-06
updated: 2025-01-21
tags:
---
> 既然选择了 Arch，便只顾风雨兼程。——周国平没说过这句话

我装了 Arch Linux。

我之前上初中学网安的时候用过 Kali Linux，当时不懂事，用着玩的；上高中学 OI 的时候用过 NOI Linux，是基于 Ubuntu 的；还用过计组的虚拟机，是基于 Debian 的。今年寒假，我得到了升级硬盘、重装系统的机会，这也是一次安装双系统的机会。

那么，装什么呢？虽然 Ubuntu 开箱即用、易于上手，但是我想挑战一下自己。之前看到、听到身边有些人在用 Arch Linux，我便暗暗记在心里，想装个 Arch Linux 挑战一下自己。于是，在[官方文档](https://wiki.archlinuxcn.org/wiki/%E5%AE%89%E8%A3%85%E6%8C%87%E5%8D%97)、[B 站视频](https://www.bilibili.com/video/BV1J34y1f74E/)和[知乎教程](https://zhuanlan.zhihu.com/p/596227524)的帮助下，我在（1 月 23 日）一天之内就装好了 Arch。

但是，挑战才刚刚开始……

## 高分屏适配（1.23 &ndash; 1.24）
两次重启之后，黑白的终端和闪烁的光标并没有如期出现；取而代之的是一幅五彩斑斓的桌面。——KDE！屏幕中央的窗口上写着“Welcome to KDE Plasma”，正是对我安装成功最好的祝福。但是……这行字太小了。预装的 Windows 的缩放比例被设置成了 250%，而 KDE 对这一点全然无知。默认的 100% 缩放比例，让这个窗口显得如此渺小。

于是在安装完成后，我做的第一件事情就是适配高分屏。

[ArchWiki](https://wiki.archlinux.org/title/HiDPI#KDE_Plasma) 上对 KDE 的高分屏适配已经有了详细的教程，包括：
 -  调节全局缩放率。
 -  调节光标大小（X11 下光标大小不会跟随全局缩放率）。
 -  调节面板高度（X11 下面板高度不会跟随全局缩放率）。

    这里有个小插曲：根据教程，需要设置环境变量来让面板高度跟随整体缩放。经过一番恶补，我终于学会了如何设置环境变量。但是，当我向 `~/.bash_profile` 的末尾添加 `set PLASMA_USE_QT_SCALING=1` 并重启系统之后，我被卡在了登录页面——输入密码之后会黑屏，然后回到登录页面。

    当时我怕极了，以为新装的系统就这样被自己毁了。后来不知道在哪里查到，按 <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>F3</kbd> 可以开启一个新的终端，我就用这个终端删掉了那行致命的代码，让电脑恢复了正常。

    我把这件事告诉了湖人，湖人建议我装 Wayland。我装了以后，发现面板高度可以跟随整体缩放了。但是窗口中的内容都会变糊，于是放弃了 Wayland。

    第二天我研究的时候，发现右键面板，选择“进入编辑模式”，可以修改面板高度。于是我按比例调高了面板高度，问题就解决了。

## 设置中文（1.25）
[简体中文本地化](https://wiki.archlinuxcn.org/wiki/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87%E6%9C%AC%E5%9C%B0%E5%8C%96)一文给出了设置中文的详尽步骤，照做即可。

在修改 `/etc/locale.gen`、运行 `locale-gen` 并安装 [<samp>noto-fonts-cjk</samp>](https://archlinux.org/packages/extra/any/noto-fonts-cjk/)<sup>包</sup> 之后，我在系统设置的语言选项中添加了简体中文，但是只有系统设置中的文本成功变为中文，其他软件仍是英文。经过查询，发现上述页面中已经提到了 [KDE 可能会生成错误的语言配置文件](https://wiki.archlinuxcn.org/wiki/KDE#Plasma_%E6%A1%8C%E9%9D%A2%E4%B8%8D%E5%B0%8A%E9%87%8D%E5%8C%BA%E5%9F%9F%E8%AE%BE%E7%BD%AE/%E8%AF%AD%E8%A8%80%E8%AE%BE%E7%BD%AE)，最后的解决方法是按教程修改 `~/.config/plasma-localerc` 文件：

```diff
 [Formats]
-LANG=zh_CN
+LANG=zh_CN.UTF-8

 [Translations]
-LANGUAGE=zh_CN
+LANGUAGE=zh_CN:en_US
```

## 安装 Firefox（2.6）
室友在 Arch Linux 上装了 Chrome，而我选择 Firefox。摆在我面前的有两个选择——用包管理器安装和用 Discover 安装。

最开始我想用包管理器（这里用到了 yay）。[ArchWiki](https://wiki.archlinuxcn.org/wiki/%E7%81%AB%E7%8B%90) 上说有一个“具有更好的 KDE 集成”的版本：[<samp>firefox-kde-opensuse</samp>](https://aur.archlinux.org/packages/firefox-kde-opensuse)<sup>AUR</sup>。但是我在编译的时候遇到了错误，于是转而用 Discover 安装。Discover 装东西真方便，现代的应用商店，点一下就装好了。

正巧那天我和一位同学聊天，聊到了这个问题。他说不建议我用 Flatpak 软件包，因为包管理器安装的软件运行更快、配置更方便。于是我去网上查了一下，看到[论坛](https://bbs.archlinux.org/viewtopic.php?pid=2043312#p2043312)上有人说与其安装 Flatpak 软件不如用木棍戳眼睛（好吓人），那位同学阅后表示赞同。

另外他告诉我不要装 <samp>firefox-kde-opensuse</samp>——那是给 OpenSUSE 用的。于是我卸掉了 Flatpak 版 Firefox，改用了包管理器安装 [<samp>firefox</samp>](https://archlinux.org/packages/extra/x86_64/firefox/)<sup>包</sup> 和 [<samp>firefox-i18n-zh-cn</samp>](https://archlinux.org/packages/extra/any/firefox-i18n-zh-cn/)<sup>包</sup> 这两个包。

## 高分屏适配后续（2.6 &ndash; 2.12）
我把我的困惑发到了[讨论页](https://wiki.archlinux.org/title/Talk:HiDPI#False_information_in_KDE_Plasma_-_Tray_icons_with_fixed_size?)，随后与一位大佬展开了长时间对线，最后修正了 ArchWiki 的相关内容。主要内容就是以下几点，感兴趣的可以去看讨论页。
1.  ArchWiki 信息有误。面板上的图标确实可以根据面板大小自动缩放，不能根据全局缩放率自动缩放的是面板本身。
2.  `PLASMA_USE_QT_SCALING=1` 可以解决让面板跟随全局缩放率自动缩放。正确的写法是 `export PLASMA_USE_QT_SCALING=1`，而不是 `set PLASMA_USE_QT_SCALING=1`。
3.  面板高度可以通过右键面板手动调节。
4.  `PLASMA_USE_QT_SCALING=1` 也可以让其他桌面部件自动缩放。
5.  使用 Wayland 可以解决自动缩放问题。但是在修改全局缩放率后需要注销才能生效。

## Vivado&ndash;VCS 联合仿真（2.6、2.17 &ndash; 2.19）
本来是打算安装在虚拟机上的，因为给我们培训的学长大都用的是 Ubuntu 虚拟机。但当我用 Debian 虚拟机安装的时候出现了空间不足的情况，扩容后虚拟机无法登录。于是我只好在群里求助，这时群里的学长纷纷推荐我用实体机 Linux 或者 WSL。想到我之前装的 Arch Linux 还不知道拿来干什么好，我决定试着装在 Arch 上。

学长结合自身经验与网上教程撰写了一篇《vivado-vcs联合仿真环境配置》，它将会带领我们披荆斩棘、乘风破浪。

### Vivado
先安装，再除错。《联合仿真》给了一篇 [Vivado 安装教程](https://blog.csdn.net/lishan_13/article/details/108889234)以供参考。

#### 安装
有同学告诉我，[<samp>vivado</samp>](https://aur.archlinux.org/packages/vivado)<sup>AUR</sup> 在 AUR 上就有包。但是经过研究，我发现 AUR 上的包用起来比较麻烦——由于下载需要经过登录墙，所以必须手动下载完整版压缩包，然后放置在 `PKGBUILD` 所在的目录下。考虑到完整版压缩包大小约 100G，我不认为这是个好主意。但我的同学更愿意用 AUR 上的脚本，因为这样可以让 Vivado 归 pacman 管。他说，在 Linux 下安装软件就得严格使用包管理器，否则就会把系统搞乱，和 Windows 没有区别了。

经过一番思索，我最终还是选择用自带安装程序。下载好（版本 2023.2，大小约 300M）后执行命令：
```
# XINSTALLER_SCALE=2 ./FPGAs_AdaptiveSoCs_Unified_2023.2_1013_2256_Lin64.bin
```
1.  刚启动安装程序就发现 UI 小得可怜，同时控制台有提示：
    ```
    INFO Could not detect the display scale (hDPI).
           If you are using a high resolution monitor, you can set the insaller scale factor like this:
           export XINSTALLER_SCALE=2
           setenv XINSTALLER_SCALE 2
    ```
    所以要加 `XINSTALLER_SCALE=2`。
2.  配置安装选项时发现默认安装到 `/tools/Xilinx`，需要权限，于是只好退出了安装程序，加上 `sudo` 又来了一遍。

安装程序先是花了一个半小时下载了约 22G 的 Vivado，然后在十分钟以内完成了安装。不知道如果用了 AUR 上的包会怎么样。

#### 除错
1.  安装结束时控制台有报错：
    ```
    ######## Execution of Pre/Post Installation Tasks Failed ########
    Warning: AMD software was installed successfully, but an unexpected status was returned from the following post installation task(s) /tools/Xilinx/Vivado/2023.2/bin/unwrapped/lnx64.o/vivado: error while loading shared libraries: libcrypt.so.1: cannot open shared object file: No such file or directory /tools/Xilinx/Vivado/2023.2/bin/unwrapped/lnx64.o/vivado: error while loading shared libraries: libcrypt.so.1: cannot open shared object file: No such file or directory
    ```
    运行 Vivado 时同样产生了报错。
    ```
    $ /tools/Xilinx/Vivado/2023.2/bin/vivado
    ```
    ```
    /tools/Xilinx/Vivado/2023.2/bin/unwrapped/lnx64.o/vivado: error while loading shared libraries: libcrypt.so.1: cannot open shared object file: No such file or directory
    ```
    看来必须得处理了。

    通过搜索 ArchWiki，得知安装 [<samp>libxcrypt-compat</samp>](https://archlinux.org/packages/core/x86_64/libxcrypt-compat/)<sup>包</sup> 即可解决。
2.  我是占位符。
    ```
    application-specific initialization failed: couldn't load file "librdi_commontasks.so": libtinfo.so.5: cannot open shared object file: No such file or directory
    ```
    《联合仿真》中说要安装 `libtinfo5`，但是 Arch Linux 中没有 `libtinfo5`，应该安装的是——[<samp>ncurses5-compat-libs</samp>](https://aur.archlinux.org/packages/ncurses5-compat-libs)<sup>AUR</sup>！

于是成功启动。配置缩放参见 [ArchWiki](https://wiki.archlinuxcn.org/wiki/Xilinx_Vivado#%E5%90%AF%E7%94%A8%E5%B1%8F%E5%B9%95%E7%BC%A9%E6%94%BE%E5%8A%9F%E8%83%BD)。

为了测试 Vivado 的性能，我从龙芯杯官网下载了 [MIPS 团体赛发布包](http://www.nscscc.com/?p=354)，解压后将样例 CPU 的性能测试工程导入 Vivado：
```
$ cd nscscc2023-group-mips/perf_test_v0.01/soc_axi_perf_demo/run_vivado/mycpu_prj1/
$ vivado -source mycpu.xpr
```

### VCS
先安装，再激活，最后除错。《联合仿真》给了一篇 [CSDN 上的联合仿真教程](https://blog.csdn.net/houzi6320/article/details/126768482)，但是过于简略；又给了一篇[激活教程](https://blog.csdn.net/lum250/article/details/123755261)，这篇写得不错。

#### 安装
刚启动 Synopsys Installer，就发现字大得离谱——原来是不支持高分屏。于是我只好把全局缩放率改回了 100%。

配置安装选项时发现默认安装到 `/usr/synopsys`，需要权限，于是只好退出了安装程序，加上 `sudo`（以及 `-install_as_root`）又来了一遍。（梅开二度）

#### 激活
安装完以后就需要激活了。用**魔法**召唤出 `Synopsys.dat`，放到对应目录下，执行：
```
$ /usr/synopsys/scl/2018.06/linux64/bin/lmgrd -c /usr/synopsys/scl/2018.06/admin/license/Synopsys.dat
```
……失败了？
1.  我是占位符。
    ```
    bash: /usr/synopsys/scl/2018.06/linux64/bin/lmgrd: 无法执行：找不到需要的文件
    ```
    激活教程中说要安装 `lsb-core`，但是 Arch Linux 中没有 `lsb-core`，应该安装的是——[<samp>ld-lsb</samp>](https://archlinux.org/packages/extra/x86_64/ld-lsb/)<sup>包</sup>！
2.  我是占位符。
    ```
    (lmgrd) Invalid License File
    ```
    这使我百思不得其解。我一度以为自己的密钥有问题。经过上网查询，发现原来是因为 `Synopsys.dat` 的权限是 755，而 `lmgrd` 执意要把它改成 644。解决方法如下：（[参考链接](http://www.artwork.com/support/flexlm/linux/license_file_error.htm)）
    ```
    # chmod 644 /usr/synopsys/scl/2018.06/admin/license/Synopsys.dat
    ```
3.  我是占位符。
    ```
    (snpslmd) Can't make directory /usr/tmp/.flexlm, errno: 2(No such file or directory)
    ```
    激活教程中已经给了解决方法：
    ```
    # mkdir /usr/tmp
    ```

#### 除错
服务器架设完成后，我们创建一个测试程序，然后打开另一个终端来编译：
```
$ vcs test.v
$ ./simv
```

如果遇到以下报错，参照激活教程中的[参考链接](https://blog.csdn.net/qianniuwei321/article/details/127303086)即可解决。
```
undefined reference to `pthread_yield'
```

如果看到以下输出，说明编译成功。
```
../simv up to date
```

### 联合仿真
联合仿真需要先用 VCS 编译 Vivado 的库，我在编译时就遇到了如下报错：
```
[Vivado 12-23673] compile_simlib failed to compile for vcs_mx with error in 28 libraries (cxl_error.log, Number of error(s) = 122)
```

仿真的时候卡住了，点击取消无用，向控制台发送 <kbd>Ctrl</kbd> + <kbd>C</kbd> 后仿真中止，并弹出如下报错：
```
[SIM-utils-79] Incompatible GCC compiled simulation library found! Library '/home/triplecamera/Documents/Vivado_lib_VCS' is compiled with GCC version '13.2.1', expected version is '9.2.0'. Please recompile the simulation library or set the correct compiled library path for '9.2.0'.
```

唯一的解决方法是安装旧版 gcc，我之后会尝试一下。

## 声音（2.19）
自从装上 KDE 开始右下角的声音图标一直是静音的，今天想把这个问题修好。按照 ArchWiki [ALSA](https://wiki.archlinuxcn.org/wiki/ALSA) 页面中的提示安装了 [<samp>alsa-utils</samp>](https://archlinux.org/packages/extra/x86_64/alsa-utils/)<sup>包</sup>，但是在解除静音时失败了。搜了论坛才发现那个页面后面提到了需要安装 [<samp>sof-firmware<samp>](https://archlinux.org/packages/extra/x86_64/sof-firmware/)<sup>包</sup>，安装并重启后问题解决。

## 输入法（2.23、2.25）
参考 [ArchWiki](https://wiki.archlinuxcn.org/wiki/Fcitx5)，安装 [<samp>fcitx5-im</samp>](https://archlinux.org/groups/x86_64/fcitx5-im/)<sup>包组</sup>、[<samp>fcitx5-chinese-addons</samp>](https://archlinux.org/packages/extra/x86_64/fcitx5-chinese-addons/)<sup>包</sup> 和词库（可选），配置 `/etc/environment` 并重新登录，最后在系统设置中添加输入法。安装之前记得做系统更新，不然就会像我一样失败:upside_down_face:。

## 更多高分屏与中文适配（3.4）
最后还剩下 GRUB 和登录页面没有缩放且没有中文，解决方法如下：
 -  GRUB
     -  缩放：参见 ArchWiki 页面 [HiDPI&sect;降低帧缓冲分辨率](https://wiki.archlinuxcn.org/wiki/HiDPI#%E9%99%8D%E4%BD%8E%E5%B8%A7%E7%BC%93%E5%86%B2%E5%88%86%E8%BE%A8%E7%8E%87)。
     -  中文：由于执行 `grub-mkconfig` 时环境语言为中文，所以生成的 GRUB 配置中语言也变为了中文。
 -  登录页面
     -  缩放：打开系统设置，选择*开机与关机 > 登录屏幕 (SDDM) > 应用 Plasma 设置...*，即可将全局缩放率等设置同步到登录页面。（[参考链接](https://forum.manjaro.org/t/hidpi-login-screen/33852)）
     -  中文：参见[我在 archlinuxcn BBS 发的帖子](https://bbs.archlinuxcn.org/viewtopic.php?id=14095) 和 [Azure Zeng 的博客](https://blog.azurezeng.com/installation-guide-for-archlinux-kde/#header-id-17)。

**3 月 25 日更新**：更新至 KDE 6 后登录页面无法同步缩放，我在 KDE Discuss 上[发帖求助](https://discuss.kde.org/t/login-screen-does-not-respect-plasma-global-scaling/12943)，得知此 bug [已被汇报](https://bugs.kde.org/show_bug.cgi?id=467039)，将在不久后修复。

**4 月 12 日更新**：再次检查发现工单已被标记为解决，但测试发现仍然无法同步缩放。通过查阅 [Azure Zeng 的博客](https://blog.azurezeng.com/installation-guide-for-archlinux-kde/#header-id-20)、上述工单及工单中的链接，我得到了另一种解决方法：修改 SDDM 配置文件 `/etc/sddm.conf`。

```conf
[General]
GreeterEnvironment=QT_SCREEN_SCALE_FACTORS=2.5,LANG=zh_CN.UTF-8
```

## Java（3.4）
根据 [ArchWiki](https://wiki.archlinuxcn.org/wiki/Java)，安装 [<samp>jdk-openjdk</samp>](https://archlinux.org/packages/extra/x86_64/jdk-openjdk/)<sup>包</sup>（[<samp>java-runtime-common</samp>](https://archlinux.org/packages/extra/any/java-runtime-common/)<sup>包</sup> 和 [<samp>java-environment-common</samp>](https://archlinux.org/packages/extra/any/java-environment-common/)<sup>包</sup> 会自动安装；jdk-openjdk 与 [<samp>jre-openjdk</samp>](https://archlinux.org/packages/extra/x86_64/jre-openjdk/)<sup>包</sup> 有冲突，二者只能选其一），重新登录之后使用 `archlinux-java` 配置 Java 版本。

## 蓝牙（3.14）
参见 ArchWiki [蓝牙](https://wiki.archlinuxcn.org/wiki/%E8%93%9D%E7%89%99)页面。对我来说，由于之前没有安装 [<samp>bluedevil</samp>](https://archlinux.org/packages/extra/x86_64/bluedevil/)<sup>包</sup> （其中包含了 [<samp>bluez</samp>](https://archlinux.org/packages/extra/x86_64/bluez/)<sup>包</sup> 等核心组件），所以安装了一下，随后完成教程第四步“[启动/启用](https://wiki.archlinuxcn.org/wiki/%E5%90%AF%E5%8A%A8/%E5%90%AF%E7%94%A8) `bluetooth.service`”，即可使用。

我听说 [KDE 6](https://kde.org/zh-cn/announcements/megarelease/6/) 更新以后，KDE Connect 支持通过蓝牙连接手机，但是在我这里并没有试验成功。为此我在 KDE Discuss 中发帖求助，得知蓝牙连接功能因故暂时关闭。详情请见[我发布的帖子](https://discuss.kde.org/t/how-to-connect-via-bluetooth-using-kde-connect/12299)。

## Vivado again（???）
**WIP**

面对综合报错和仿真无法打开文件的问题，学长建议我安装 Vivado 2019。但是据说今年官方推荐的版本将改为 Vivado 2023，学长建议我保留 2023。

之前同学就建议我安装 AUR 上的 [<span>vivado</span>](https://aur.archlinux.org/packages/vivado)<sup>AUR</sup>，加上 Vivado 2019 的完整版安装包小了很多（26.5G），我觉得值得一试。

我最初的想法是使用支持 Vivado 2019.2 的 PKGBUILD（commit `3dbc515`）进行构建，但是报错说有些包找不到。这是因为在三年多的时间里，有些包已经被其他包取代了。

于是我以最新 commit 为基底，修改了版本信息：

最后值得一提的是，[在升级时跳过 vivado](https://wiki.archlinuxcn.org/wiki/Pacman#%E5%9C%A8%E5%8D%87%E7%BA%A7%E6%97%B6%E8%B7%B3%E8%BF%87%E8%BD%AF%E4%BB%B6%E5%8C%85)。

## 启动速度慢 + CPU 高占用（3.31 &ndash; 4.2）
最近两天，我的 Arch Linux 突然出现了一些问题，对日常使用有很大影响：
1.  启动速度慢。GRUB 加载 Linux 之后会黑屏 2 分钟，然后才能正常启动。
2.  CPU 高占用。开机后风扇一直在高速运转，CPU 有一个核满载。

我在 [archlinuxcn BBS](https://bbs.archlinuxcn.org/viewtopic.php?id=14172) 上发帖求助，两位大佬帮我解决了问题：
1.  检查内核日志可知是 [Nouveau](https://wiki.archlinuxcn.org/wiki/Nouveau)（NVIDIA 显卡开源驱动）的问题。解决方法是使用 NVIDIA 闭源驱动或者禁用独显，我选择了前者。
2.  使用 `top`/`htop` 查看 CPU 占用，得知是 [Baloo](https://wiki.archlinuxcn.org/wiki/Baloo) 的问题，禁用即可。

非常感谢他们，同时使我认识到自己的 Linux 基础知识仍然匮乏。

下面附上安装 NVIDIA 闭源驱动的方法（总结自 ArchWiki 的 [NVIDIA](https://wiki.archlinuxcn.org/wiki/NVIDIA) 页面）：
1.  查询显卡型号：
    ```
    $ lspci -k | grep -A 2 -E "(VGA|3D)"
    ```
2.  根据 ArchWiki 的指引，安装 [<samp>nvidia</samp>](https://archlinux.org/packages/?name=nvidia) 和 [<samp>lib32-nvidia-utils</samp>](https://archlinux.org/packages/?name=lib32-nvidia-utils)（不同型号安装的包有所不同）。
3.  编辑 `/etc/mkinitcpio.conf`，删除 `HOOKS` 中的 `kms`。
4.  重新生成启动镜像：
    ```
    # mkinitcpio -P
    ```
5.  重启，完成。

## 微码（4.15）
微码的作用是将复杂指令分解为一系列简单指令。及时更新微码可以修复 CPU 的重大漏洞。

我根据 [ArchWiki](https://wiki.archlinuxcn.org/wiki/%E5%BE%AE%E7%A0%81) 上的教程，运行了以下命令来检查是否已经安装了微码：
```
# journalctl -k --grep=microcode
4月 15 19:38:29 triplecamera kernel: Register File Data Sampling: Vulnerable: No microcode
4月 15 19:38:29 triplecamera kernel: microcode: Current revision: 0x00000421
```

看来没有。于是我安装了 [<samp>intel-ucode</samp>](https://archlinux.org/packages/?name=intel-ucode)，重启后再次检查：
```
# journalctl -k --grep=microcode
4月 15 20:08:50 triplecamera kernel: microcode: Current revision: 0x00000432
4月 15 20:08:50 triplecamera kernel: microcode: Updated early from: 0x00000421
```

没想到居然已经装好了。赞。

## 电源管理方案（4.19）
查看电池状态时注意到电源管理方案不可用：

<img src="/images/archlinux-power.png" alt="电源管理方案不可用的提示" style="max-height: 20em;">

于是去 [ArchWiki](https://wiki.archlinuxcn.org/wiki/KDE#%E7%94%B5%E6%BA%90%E7%AE%A1%E7%90%86) 上查了一下，发现 KDE 的电源管理依赖于 [<samp>powerdevil</samp>](https://archlinux.org/packages/?name=powerdevil) 和 [<samp>power-profiles-daemon</samp>](https://archlinux.org/packages/?name=power-profiles-daemon)。前者在我安装 [<samp>plasma</samp>](https://archlinux.org/groups/x86_64/plasma/)<sup>组</sup> 时就一并安装了，后者需要手动安装。

安装过后重启，电源管理方案就可以使用了。

## IntelliJ IDEA（4.22）
4 月 21 日那天，我突然想来一场“自我放逐”：从某一天开始，从 Windows 换成 Arch Linux，并且再也不要换回来了。看看自己能坚持多久。

为此我需要将平日会用到的软件在 Arch 上都装一份——其中之一就是 IntelliJ IDEA。去 ArchWiki 上看了发现只有 Community Edition，经过一番搜索才发现 Ultimate Edition 在 AUR 上。

**5 月 1 日更新**：已在 ArchWiki 上补充相关信息。

## 但愿是最后一次适配高分屏（4.25）
刚装上 Arch Linux 的时候，默认启动项是 Windows，所以每次想要启动 Arch 都要在开机时长按 <kbd>F12</kbd>，切换启动项。为了延长键盘寿命（笑），我决定将默认启动项改为 Arch 使用的 GRUB，然后在 GRUB 中选择启动 Windows 还是 Arch。

上回[降低 GRUB 分辨率](#更多高分屏与中文适配（3.4）)之后，Windows 的启动画面也变成了低分辨率（启动后分辨率会恢复正常），由于分辨率太低，厂商徽标无法显示，只能显示低清的 Win11 大蓝标，**特别丑**。Arch 虽然当时没有出问题，但换上 NVIDIA 专有驱动后也出现了启动分辨率同 GRUB 一致的问题。

Arch 的问题是 NVIDIA 专有驱动造成的，无法解决。Windows 的问题倒是可以解决：只需用命令提示符运行 `bcdedit /set {globalsettings} highestmode on` 或用 PowerShell 运行 `bcdedit /set "{globalsettings}" highestmode on`。（[参考链接](https://superuser.com/questions/1723882/low-resolution-boot-screen-on-windows)）

```
> bcdedit /set {globalsettings} highestmode on
操作成功完成。
```

## VLC 高分屏适配（6.8）
使用 VLC 时遇到了下方按钮过小的问题——又要做高分屏适配了。

<img src="/images/archlinux-vlc-nohidpi.png" alt="没有启用 HiDPI 的 VLC 界面" style="max-height: 13em;">

上网一搜就能搜到，传入环境变量 `QT_SCALE_FACTOR`（或 `QT_AUTO_SCREEN_SCALE_FACTOR`、`QT_SCREEN_SCALE_FACTORS`）即可。（[参考链接](https://unix.stackexchange.com/questions/557181/how-to-increase-dpi-for-vlc-media-player-in-cinnamon-on-uhd-display)）

先用命令行尝试一下，确实可以工作：
```
$ QT_SCREEN_SCALE_FACTORS=2.5 vlc
```

~~其实以上内容是我很久之前就研究出来的，今天突然想起来这项研究还没做完就赶紧补完写出来了。~~

我们在应用程序启动器（KDE 的“开始菜单”）中右键 VLC 的快捷方式，选择“编辑应用程序...”，然后切换到“应用程序”选项卡，将“环境变量”设置为 `QT_SCREEN_SCALE_FACTORS=2.5`。点击“确定”，Plasma 就会将 VLC 的系统快捷方式（位于 `/usr/share/applications/vlc.desktop`）拷贝到用户目录（`~/.local/share/applications/`），然后再进行修改，从而避免对系统快捷方式的影响。

再次打开 VLC，可以看到缩放正常了：

<img src="/images/archlinux-vlc-hidpi.png" alt="启用了 HiDPI 的 VLC 界面" style="max-height: 23em;">

我正在担心打开文件的时候该怎么传入环境变量，结果一试，双击文件时也会应用环境变量——这点可比 Windows 做的好。

## 帮助中心（6.9）
每次我查看 KDE 应用程序的使用手册时都会跳转到官网——那么有没有办法离线查看手册呢？我去问湖人，湖人不知道，让我去加[微信群](https://kde-china.org/usergroup.html)。我加群后问了问题，可是一直没有人回答我。

最后我找到了 KDE 的帮助中心 [KHelpCenter](https://apps.kde.org/zh-cn/khelpcenter/)（软件包：[<samp>khelpcenter</samp>](https://archlinux.org/packages/?name=khelpcenter)）。确实是离线的，嗯。

## `paccache`（7.15）
一不注意磁盘占用超过 80% 了。拿 Filelight 看了一下，发现能删的东西中，pacman 和 yay 的缓存占了大部分。

那么怎么清理呢？直接删掉缓存文件夹当然是可以的，但 [ArchWiki](https://wiki.archlinuxcn.org/wiki/Pacman#%E6%B8%85%E7%90%86%E8%BD%AF%E4%BB%B6%E5%8C%85%E7%BC%93%E5%AD%98) 给出的方法是使用 `paccache` 或 `yay -Sc`。前者可以保留最近几个版本的包（默认是 3 个），后者只会保留最新版的包（`yay -Scc` 会全部删除，但没有必要那样做）。

我选择了前者：
```
$ paccache -d

==> finished dry run: 1383 candidates (disk space saved: 17.32 GiB)
$ paccache -r
==> Escalating privileges using sudo
[sudo] triplecamera 的密码：

==> finished: 1383 packages removed (disk space saved: 17.32 GiB)
```

清理完后磁盘占用 74%……有人可能问我（其实没人问）为什么不选择后者，我觉得即使选择后者也只能解一时之急，重新分区才是长远之计。

## `pacdiff`（7.23）
起因是<abbr title="7 月 21 日">星期天</abbr>滚系统的时候，[<samp>sudo</samp>](https://archlinux.org/packages/?name=sudo) 更新了配置文件 `/etc/sudoers`，pacman 将新版本存到了 `/etc/sudoers.pacnew`，让用户手动处理差异。

这可造成了不小麻烦……我先试着用 Kate 打开，结果 Kate 因为权限不足打不开。我又用 sudo 运行 Kate，结果 Kate 拒绝以 sudo 模式运行。于是我只好用 Vim……先把 `/etc/sudoers` 移动到 `/etc/sudoers.bak`，再把 `/etc/sudoers.pacnew` 修改好以后移动到 `/etc/sudoers`——结果这第一步就出了问题，`/etc/sudoers` 不见以后，sudo 没法运行了。于是我只好用 root 账户完成了剩下的操作……

两天以后，[<samp>glibc</samp>](https://archlinux.org/packages/?name=glibc) 更新了 `/etc/locale.gen`。因为手动处理差异太麻烦了，我就根据 [ArchWiki](https://wiki.archlinuxcn.org/wiki/Pacman/pacnew_%E4%B8%8E_pacsave#pacdiff) 的指引尝试了一下 `pacdiff`。

`pacdiff` 支持各种差异工具。我想找个 GUI 的，最好是 KDE 的。嗯……最后找到了 [<samp>kdiff3</samp>](https://archlinux.org/packages/?name=kdiff3) 和 [<samp>kompare</samp>](https://archlinux.org/packages/?name=kompare)（前者是后者的新版）。那就来比试一番吧！
 -  Vim：配色亮<abbr title="瞎">目害</abbr>眼。
 -  gVim：没用过，不熟。
 -  KDiff3：崩溃了……
 -  Kompare：能用，但是不能选择“不应用差异”，只能选择“应用差异”。

就这样。**没一个能用的。**

## 发送崩溃报告（7.23）
书接上回。我在尝试 KDiff3 的时候，KDiff3 崩溃了：
```
$ DIFFPROG=kdiff3 pacdiff
```

幸运的是，崩溃是可以稳定复现的：
```
$ kdiff3 /etc/locale.gen /etc/locale.gen.pacnew
```

此时屏幕右下角弹出了崩溃处理程序的通知，于是我试着汇报了一下：

点击“报告程序缺陷”，就会弹出一个窗口，上面有“发送自动报告”和“查看开发者信息”两个选项。前者会直接将崩溃信息发送到 [crash-reports.kde.org](https://crash-reports.kde.org/)，可惜只有开发者能查看。（[参考链接](https://discuss.kde.org/t/this-week-in-kde-looking-forward-towards-plasma-6-1/13248/4)）

后者则会显示详细的崩溃日志。可是堆栈信息中全是未知的符号——这是因为缺少调试符号包。点击右上角的“安装调试符号包”，安装完成后堆栈信息就清晰可见了。此时发送的崩溃报告就具备参考价值了。

最后介绍两个选项：
 -  [ ] 自动报告崩溃
 -  [x] 自动下载调试符号包以提高崩溃报告价值

后者十分有用，我就把它勾上了。

## 修改分区（8.16 &ndash; 8.20）
上文提到，半年前规划的分区结构不甚合理：经过半年的使用，Arch 的地位不断上升并有可能（部分）取代 Windows，原先分配的 252 GiB 空间根本不够 Arch 施展拳脚。因此现在迫切需要对分区结构进行修改。

虽然 KDE 和 Gnome 的分区管理器都很好用，但它们不允许你在开着 Linux 的情况下修改 Linux 自身所在的分区——这就好比你没法拆掉自己脚下正踩着的那块地板，要想拆掉它，得先把脚拿开。所以，我们需要一股外部力量来完成修改分区的操作——这股力量正是 LiveCD。

### GParted Live
GParted 提供 LiveCD 版本，所以我选择了它。事实证明，这款软件虽然能用，但是存在着一些小问题……

首先是老生常谈的问题——NVIDIA 显卡驱动。第一次进系统时我选了 `GParted Live (Default settings)` 启动项，结果黑屏了。由于之前帮室友装 Ubuntu 的时候遇到过类似的问题，所以我直接给启动参数加上了 `nomodeset`，问题顺利解决。后来查看 GRUB 菜单时，发现启动项 `GParted Live (Safe graphic settings, vga=normal)` 也加了这个参数——下次就用它来启动系统。

接下来是分辨率过高的问题——无论是 GRUB 还是桌面环境，字都小到看不清。幸好我有之前配置 GRUB 的经验，于是直接修改了 `/boot/grub/grub.cfg`：
```diff
 if loadfont $font; then
-  set gfxmode=auto
+  set gfxmode=800x600x32,auto
   insmod gfxterm
   # Set the language for boot menu prompt, e.g., en_US, zh_TW...
   set lang=en_US
   terminal_output gfxterm
 fi
```

GRUB 的分辨率降下来了。令我惊喜的是，系统的分辨率跟随 GRUB，于是系统的分辨率也降下来了。

另外还有截图工具双击没有反应的问题。经过一番翻找，我找到了这个桌面图标对应的配置文件：`~/.idesktop/screenshot.lnk`，里面写着运行程序所需的命令：`gl-screenshot`。我在终端中运行了这个命令，输出如下：
```
$ gl-screenshot
No gdialog or Xdialog was found!
Program terminated!!!
```

[GitLab issue](https://gitlab.gnome.org/GNOME/gparted/-/issues/256) 里面说这个问题在最新的测试版中已经修复。可惜我没有空去试了，因为我想玩点不一样的——群友的 LiveCD。

### 群友的 LiveCD
我在 [archlinuxcn 交流群](https://www.archlinuxcn.org/archlinuxcn-group-mailling-list/)中求助时，有人建议我使用[群友的 LiveCD](https://github.com/archlinux-jerry/custom-archiso)，里面包含了 Xfce 桌面环境和 GParted 等实用软件。

第一次启动的时候图形界面没有自动启动，第二次启动的时候就有图形界面了，原因未知。

调节缩放比（Scale）似乎有问题，于是我只好降低分辨率（Resolution）。

以下是修改前的分区（截图工具没装，只好拍屏了）：

![修改前的分区](/images/archlinux-partition-before.jpg)

### GParted，启动！
终于可以对分区进行大刀阔斧的改造了！下面是分解动作：

1.  将 D 盘压缩至 512 GiB。（为了避免 NTFS 兼容问题，我在这一步使用了 Windows 的磁盘管理工具。）

2.  将 swap 分区删除。

3.  将 Linux 主分区移动到空闲区域的最左侧。

4.  创建 swap 分区，大小为 24 GiB，位于空闲区域的最右侧。

    这台电脑有 16 GiB 内存。ArchWiki 上说，如果要启用休眠，那么 swap 分区的大小应不低于内存大小；RedHat 建议，如果要启用休眠，那么 swap 分区的大小应至少为内存大小的 1.5 倍。虽然我还没有启用休眠，但为了长远考虑，最后我分配了 24 GiB。

5.  将 Linux 主分区扩展，占满空闲区域。

以下是修改后的分区：

![修改后的分区](/images/archlinux-partition-after.jpg)

### 善后工作
GRUB 和 Arch 的配置都是基于原有的分区结构生成的，现在分区结构变了，配置却还没有更新，势必会带来问题。果不其然：启动 Arch 时，虽然系统能正常启动，但 swap 分区没有正确挂载。

我插上 Arch 启动盘，但这次不需要走完装系统的整个流程。只需要依次挂载主分区、挂载 EFI 分区、启用 swap 分区，然后运行 `genfstab -U /mnt >> /mnt/etc/fstab` 更新 `/etc/fstab` 即可。以下是 `/etc/fstab` 的变更情况：
```diff
 # Static information about the filesystems.
 # See fstab(5) for details.

 # <file system> <dir> <type> <options> <dump> <pass>
 # /dev/nvme0n1p7
 UUID=1c13125e-cd3c-427b-adb0-8155a5c5122a	/         	ext4      	rw,relatime	0 1

 # /dev/nvme0n1p1 LABEL=SYSTEM
 UUID=EC68-766C      	/boot     	vfat      	rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro	0 2

 # /dev/nvme0n1p6
-UUID=4c079726-ded2-4448-9e3a-40eefb72eb90	none      	swap      	defaults  	0 0
+UUID=f85dc3e2-6486-4cb2-b002-73bf4bfe232f	none      	swap      	defaults  	0 0

```

注意到只有 swap 分区的 UUID 产生了变化（因为我删除并重新创建了 swap 分区），各个分区的编号都没有变。这就是为什么 GRUB 仍然可以启动 Arch。但保险起见，我还是重新运行了 `grub-mkconfig`。

## 腾讯会议（8.28 &ndash; 8.29）
我在暑假时就安装了腾讯会议（[<samp>wemeet-bin</samp>](https://aur.archlinux.org/packages/wemeet-bin)<sup>AUR</sup>），但一直苦于没有人能帮我测试各项功能是否正常。直到返校以后，才有了和室友一起测试的机会。

经过各方面的测试，我发现：腾讯会议大部分功能都能正常工作，唯一的问题是 Wayland 下不支持屏幕共享：开启屏幕共享后只能操作腾讯会议的控制栏，点击屏幕的其他地方都没有任何反应；同时，会议中其他人看到的只有黑屏。根据 AUR 中的评论，有两种解决方法：

1.  **改用 X11**。注销并使用 X11 重新登录。

2.  **使用 OBS 创建虚拟摄像机**。安装 [<samp>obs-studio</samp>](https://archlinux.org/packages/?name=obs-studio)、[<samp>v4l2loopback-dkms</samp>](https://archlinux.org/packages/?name=v4l2loopback-dkms)、[<samp>linux-headers</samp>](https://archlinux.org/packages/?name=linux-headers)，打开 OBS 即可看到“启动虚拟摄像机”按钮。配置好场景（添加来源“屏幕采集(PipeWire)”并缩放到刚好占满屏幕），点击“启动虚拟摄像机”，然后打开腾讯会议，将摄像头切换为“OBS Virtual Camera”，即可共享屏幕。（[参考链接](https://wiki.archlinuxcn.org/wiki/Open_Broadcaster_Software#%E8%99%9A%E6%8B%9F%E6%91%84%E5%83%8F%E6%9C%BA%E8%BE%93%E5%87%BA)）

    注意：画布比例应为 16:9，否则腾讯会议会裁剪掉多余的部分。另外腾讯会议会对摄像头内容进行重度压缩，并且没有办法关闭。

那么就是这样。

## Fontconfig（？）
TODO

## LLVM（？）
TODO

## 声音问题（1.20）
最近几天，我的 Arch 突然识别不到笔记本自带的扬声器了。“音量”一栏显示“没有找到输出或者输入设备”。但是耳机还可以正常工作。

经过一番检查，我发现原来是设置里声卡被停用了。真无语:sweat:

![系统设置中“声音”一栏的截图。上面显示，我的声卡已停用，需要手动将其开启](/images/archlinux-soundcard.png)
