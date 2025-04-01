---
title: 编程随笔（五）
date: 2025-04-01
tags:
categories:
- 编程随笔
---

最近我们为 OSome 做了一次兼容性更新，使其能支持新主楼机房的 Firefox 70。

## 背景
上周四（3 月 27 日）是我第一次去新主楼上机，我被那里的环境震惊到了：
 -  讲台上没有教师机，也不能统一控制所有机器开关机。
 -  助教说课程平台只能用 Chrome 浏览器访问，跳板机和 GitLab 仓库只能用火狐浏览器访问。（什么规则怪谈）
 -  电脑无法联网校准时间，只能手动校准。时间过快过慢都进入不了系统。

开始考试的前几分钟，好几个同学反映无法正常访问系统。经过一番排查，我们最终通过换浏览器、校准时间、换座位等方法解决了这些问题。在接下来的一个多小时里，倒是没有多少同学寻求帮助，于是我打算趁机研究一下上面说到的那条“规则怪谈”。

首先看一下电脑配置：
 -  Windows 7
 -  Google Chrome 79.0.3945.117
 -  Mozilla Firefox 70.0.1

<figure>
  <img src="/images/programming-5-background.png" alt="Google Chrome 和 Mozilla Firefox 的关于页面" style="max-height: 20em">
  <figcaption>Google Chrome 和 Mozilla Firefox 的关于页面</figcaption>
</figure>

再看一下症状：
 -  对于课程平台，使用 Chrome 可以正常打开，使用 Firefox 打开后显示为空白。
 -  对于跳板机和 GitLab，使用 Firefox 可以正常打开，使用 Chrome 打开时提示证书错误，但是选择继续访问后可以正常访问。

## 原因
使用 Firefox 打开课程平台，然后打开控制台，可以看到一条报错信息：

```
SyntaxError: invalid regular expression flag s
```

我根据旁边提供的代码行列坐标定位到了出错的语句，然后复制到控制台重新运行了一遍，确认是这条语句导致的错误。

<figure>
  <img src="/images/programming-5-debug.png" alt="使用控制台定位和运行出错的语句" style="max-height: 20em">
  <figcaption>使用控制台定位和运行出错的语句</figcaption>
</figure>

然后我上网搜索了一下。MDN 的报错信息解释页面上说是正则表达式写错了，FreeCodeCamp 上说换成 Chrome 就能解决……还是看看 [Bugzilla](https://bugzilla.mozilla.org/show_bug.cgi?id=1361856) 和 [MDN 浏览器兼容性数据](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/RegExp/dotAll#%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%BC%E5%AE%B9%E6%80%A7)是怎么说的吧：

正则表达式的 `s` 旗标于 ES2018 加入。对 `s` 旗标的支持早在 2017 年就已提出，但直到 2020 年 6 月的 Firefox 78 才支持。反观 Chrome，早在 2017 年 10 月发布的 Chrome 62 中就已支持了这一功能。

考试结束后，我对错误的来源展开了调查。首先我需要安装 Firefox 70 来稳定复现这一漏洞。由于在 Linux 上直接安装旧版可能会破坏系统环境，我暂时换到了 Windows。（有人向我推荐了 mozregression，日后可以试一下。）确认稳定复现之后，就可以开始深入调查了。

使用 debug 构建，并在 `chunk-vendors.js` 中查找出问题的正则表达式 `/^-{3}\\s*[\\n\\r](.*?)[\\n\\r]-{3}\\s*[\\n\\r]+/s`，可以找到来源文件：

```js
/***/ "./node_modules/mermaid/dist/mermaid.min.js":
/*!**************************************************!*\
  !*** ./node_modules/mermaid/dist/mermaid.min.js ***!
  \**************************************************/
/***/ (function(module, exports, __webpack_require__) {

eval("...");

/***/ }),
```

然后使用 `npm list mermaid` 来检查 `mermaid` 的版本：

```console
> npm list mermaid
pendulum-frontend@0.1.0 D:\Code\osome\pendulum-frontend
└─┬ @wekanteam/markdown-it-mermaid@0.6.2
  └── mermaid@9.3.0
```

可以看到，`mermaid` 作为 `@wekanteam/markdown-it-mermaid` 的依赖项被安装，且版本为 `9.3.0`。

我直接在 `mermaid` 的 GitHub 仓库上开了个 GitHub Codespaces。

## 解决方案
