---
title: Arch Linux 害了他
date: 2024-02-06
updated: 2024-02-20
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
