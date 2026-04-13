---
title: Arch Linux 如何检查上次更新包大小变化
date: 2026-04-13
tags:
---

![pacman 提示净更新大小为 -3710.18 MiB，十分反常](/images/archlinux-pkgsizediff/intro.png)

昨天晚上，我在滚系统的时候遇到了一个问题：如何得知哪些包的体积显著变小了？

在滚完系统以后，我去群里提问。群友告诉我，应该在 `pacman.conf` 里打开 `VerbosePkgLists` 选项。——可是这样做只能对以后的更新产生效果，而我已经滚完系统了。那么，有没有办法知道上一次更新时包的大小变化呢？

我最开始让 ChatGPT 帮我写了一个脚本。ChatGPT 从日志里提取出了上一次更新的包名，然后从缓存里查找更新前后的包，最后计算差值并排序。可是运行结果显示，`magma-cuda` 是体积减小最多的包，减小了约 `75 MiB`。——这并不能解释为什么净更新大小为负三千多兆。

经过一番摸索，我找到了问题的原因：ChatGPT 比较的是压缩包的大小，而压缩前后的大小有时会有很大出入。我试着从压缩包里提取 `.PKGINFO` 并读取其中存储的压缩前大小，最后发现是 `magma-cuda` 这个包变小了 3 个多 G，这才和 pacman 汇报的结果对上了。

以下是完整流程（注意，这个方法奏效的前提是更新前后的版本都残留在缓存中）：

---

首先，从 `/var/log/pacman.log` 里提取上次更新的日志，保存在另一个文件中，比如 `update-log`。

接下来，从日志中提取包名、旧版本、新版本这三个关键信息，保存在另一个文件中，比如 `update-log2`。

```console
$ grep 'upgraded' update-log | sed -E 's/.*upgraded ([^ ]*) \(([^ ]*) -> ([^ ]*)\)/\1 \2 \3/' > update-log2
```

然后，去缓存中查找更新前后的包，提取 `.PKGINFO` 并读取其中存储的压缩前大小，保存在另一个文件中，比如 `update-diff`。

```console
$ while read pkg old_ver new_ver
do
    old_size=$(tar -xO --zstd -f /var/cache/pacman/pkg/$pkg-$old_ver-*.pkg.tar.zst .PKGINFO | grep size | awk '{ print $3 }')
    new_size=$(tar -xO --zstd -f /var/cache/pacman/pkg/$pkg-$new_ver-*.pkg.tar.zst .PKGINFO | grep size | awk '{ print $3 }')
    diff_size=$(( new_size - old_size ))
    echo $diff_size $pkg
done < update-log2
```

运行时会出现一些奇怪的报错信息（“忽略未知的扩展头关键字‘……’”），我们不要管它。

注意：最开始 GPT 是直接比较的压缩包大小，问题在于原文件的大小和压缩包的大小有时会有很大出入。

```bash
old_size=$(stat -c %s /var/cache/pacman/pkg/$pkg-$old_ver-*.pkg.tar.zst)
new_size=$(stat -c %s /var/cache/pacman/pkg/$pkg-$new_ver-*.pkg.tar.zst)
```

最后一步，对 `update-diff` 中的内容排序，就能知道哪些包体积变化最大了。

```console
$ sort -n update-diff
```

---

最后附上我自己的情况作为测试样例（点击下载）：

 -  [`update-log`](../images/archlinux-pkgsizediff/update-log)
 -  [`update-log2`](../images/archlinux-pkgsizediff/update-log2)
 -  [`update-diff`](../images/archlinux-pkgsizediff/update-diff)
