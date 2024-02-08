---
title: Arch Linux 害了他
date: 2024-02-06
updated: 2024-02-08
tags:
---
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

    当时我怕极了，以为新装的系统就这样被自己毁了。后来不知道在哪里查到，按 `Ctrl+Alt+F3` 可以开启一个新的终端，我就用这个终端删掉了那行致命的代码，让电脑恢复了正常。

    我把这件事告诉了湖人，湖人建议我装 Wayland。我装了以后，发现面板高度可以跟随整体缩放了。但是窗口中的内容都会变糊，于是放弃了 Wayland。

    第二天我研究的时候，发现右键面板，选择“进入编辑模式”，可以修改面板高度。于是我按比例调高了面板高度，问题就解决了。

## 设置中文（1.25）
[简体中文本地化](https://wiki.archlinuxcn.org/wiki/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87%E6%9C%AC%E5%9C%B0%E5%8C%96) 一文给出了设置中文的详尽步骤，照做即可。

在修改 `/etc/locale.gen`、运行 `locale-gen` 并安装 `noto-fonts-cjk` 之后，我在系统设置的语言选项中添加了简体中文，但是只有系统设置中的文本成功变为中文，其他软件仍是英文。经过查询，发现上述页面中已经提到了 [KDE 可能会生成错误的语言配置文件](https://wiki.archlinuxcn.org/wiki/KDE#Plasma_%E6%A1%8C%E9%9D%A2%E4%B8%8D%E5%B0%8A%E9%87%8D%E5%8C%BA%E5%9F%9F%E8%AE%BE%E7%BD%AE/%E8%AF%AD%E8%A8%80%E8%AE%BE%E7%BD%AE)，最后的解决方法是按教程修改 `~/.config/plasma-localerc` 文件：

修改前：
```ini
[Formats]
LANG=zh_CN

[Translations]
LANGUAGE=zh_CN
```

修改后（与教程完全相同）：
```ini
[Formats]
LANG=zh_CN.UTF-8

[Translations]
LANGUAGE=zh_CN:en_US
```

## 安装 Firefox（2.6）
室友在 Arch Linux 上装了 Chrome，而我选择 Firefox。摆在我面前的有两个选择——用 pacman 安装和用 Discover 安装。

最开始我想用 pacman（其实这里用到了 yay）。[ArchWiki](https://wiki.archlinuxcn.org/wiki/%E7%81%AB%E7%8B%90) 上说有一个“具有更好的 KDE 集成”的版本：`firefox-kde-opensuse`。但是我在编译的时候遇到了错误，于是转而用 Discover 安装。Discover 装东西真方便，现代的应用商店，点一下就装好了。

正巧那天我和一位同学聊天，聊到了这个问题。他说不建议我用 Flatpak 软件包，因为 pacman 安装的软件运行更快、配置更方便。于是我去网上查了一下，看到[论坛](https://bbs.archlinux.org/viewtopic.php?pid=2043312#p2043312)上有人说与其安装 Flatpak 软件不如用木棍戳眼睛（好吓人），那位同学阅后表示赞同。

另外他告诉我不要装 `firefox-kde-opensuse`——那是给 OpenSUSE 用的。于是我卸掉了 Flatpak 版 Firefox，改用了 pacman 安装 `firefox` 和 `firefox-i18n-zh-cn` 这两个包。
