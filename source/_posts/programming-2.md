---
title: 编程随笔（二）
date: 2023-08-18
updated: 2023-08-26
categories:
- 编程随笔
---
眼下正是八月，当我们正在享受这美好而又漫长的暑假的时候，竟然收到了来自计算机组成原理课程团队的一份礼物——预习任务。~~可喜可贺，可喜可贺。~~

为了省去安装软件的麻烦，课程团队贴心地为我们准备了虚拟机：Debian 11 系统、LXDE 桌面环境。但是虚拟机在我的高分屏电脑上表现不佳。于是我花了好大功夫来调好它。

助教告诉我：

> 课程组提供的虚拟机以“轻量”为目标进行构建，选用的桌面环境为LXDE，其优点是占用资源少，缺点之一便是你遇到的——缺乏完善的图形界面支持，没有一键式的适配配置方案。

但是为什么不换一个桌面环境呢？因为~~我乐意~~教程里说：

> 在本地，我们可以换用 GNOME、KDE Plasma 等其他桌面环境，这类桌面环境的功能较默认的 LXDE 更齐全，兼容性更好。但往往占用的资源也较多，在虚拟化环境下性能表现较差，建议谨慎尝试。

注：以下配置适合于我的电脑，自己操作时请自行调整。

## 修改 DPI
**这一部分按照教程即可。**

向 `~/.Xresources` 文件中写入：
```
Xft.dpi: 283
```
然后 `sudo reboot` 重启。

## 修改文件管理器图标大小
打开文件管理器 PCManFM，在“编辑 > 偏好设置 > 显示 > 图标”里将图标大小调为原来的 2 倍。

## 修改文件管理器字体大小
调高 DPI 会使文件管理器字体过大。右键桌面，在“桌面偏好设置 > 外观 > 文本 > 标签文本字体”中将“大小”调为 8。

## 修改下方面板大小
**感谢助教的帮助！**

右键下方面板，在“面板设置 > 几何形状 > 大小”中将“高度”和“图标大小”修改为原来的 2 倍。这导致了背景出错，于是又在此窗口下的“外观 > 背景”中修改了背景。


## 修改应用文本大小
**这一部分按照教程即可。**

在终端键入 `gsettings set org.gnome.desktop.interface text-scaling-factor 2.5`（教程中推荐使用 0.5 的整数倍），之后重启。

## 修改鼠标光标大小
**感谢助教的帮助！**

打开 `~/.config/lxsession/LXDE/desktop.conf`，将
```
iGtk/CursorThemeSize=18
```
修改为
```
iGtk/CursorThemeSize=72
```
然后重启以确保更改完全生效。（[参考链接](https://www.reddit.com/r/linux4noobs/comments/64nj3y/increasing_cursor_size_arch_lxde/)）

## 修改窗口按钮大小
虚拟机使用的默认主题为 Nightmare，存储路径为 `/usr/share/themes/Nightmare/openbox-3`。窗口按钮的位图为 XBM 文件，大小固定为 5x5。需要将其放大到 20x20，放大后的文件如下：（你可以直接使用它们覆盖你的虚拟机中的对应文件）
 -  [bullet.xbm](/images/openbox-3/bullet.xbm)
 -  [close.xbm](/images/openbox-3/close.xbm)
 -  [iconify.xbm](/images/openbox-3/iconify.xbm)
 -  [max.xbm](/images/openbox-3/max.xbm)
 -  [shade_toggled.xbm](/images/openbox-3/shade_toggled.xbm)
 -  [shade.xbm](/images/openbox-3/shade.xbm)

之后重启即可。（[参考链接](https://forum.xfce.org/viewtopic.php?id=9312)）
