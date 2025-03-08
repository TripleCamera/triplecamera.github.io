---
title: OS 2024 讨论区优质帖汇总
date: 2024-08-08
updated: 2025-03-05
mathjax: true
---
<style>
th:nth-child(2),
td:nth-child(2) {
    text-align: right;
}
</style>

转眼又是一个学期，OS 的学习也已经结束。按照惯例，我整理出了 OS 的讨论区优质贴。

OS 的讨论区并没有精华帖机制，取而代之的是，助教会定期选择少量帖子进行置顶。因此，我需要找出一种快速筛选优质贴的方式。我先是整理出了所有帖子的点赞数量（这里的点赞数量为主题帖的点赞数量，不包括回复）：

![OS 2024 讨论区点赞数量统计](/images/os-discussions/likes.svg)
![OS 2024 讨论区点赞与订阅数量统计](/images/os-discussions/stats.svg)

注意到拥有至少 5 个赞的讨论帖仅有 22 个，占全部讨论帖的 $\frac{22}{287} \approx 8\%$；而拥有至少 5 个赞**或** 5 个订阅的讨论帖共有 29 个，占全部讨论帖的 $\frac{29}{287} \approx 10\%$。因此，我最终决定收录所有拥有至少 5 个赞或 5 个订阅的讨论帖。需要说明的是，这里面有 3 篇往届精华帖，由于原作者不明，没法获得原作者的授权，所以没有转载。最终我们一共得到了 26 篇优质的帖子，它们有的是经验分享，干货满满；有的是长篇讨论，生动有趣。

以下是本项目使用的脚本、配置、样式文件，如有建议请不吝赐教。学弟学妹如果对本项目感兴趣，可以联系我获取帮助。
 -  [stats.py](/images/os-discussions/stats.py)
 -  [process.py](/images/os-discussions/process.py)
 -  [discussion.json.example](/images/os-discussions/discussion.json.example)
 -  [author.json.example](/images/os-discussions/author.json.example)（真名已隐藏）
 -  [styles.styl](https://github.com/TripleCamera/triplecamera.github.io/tree/main/source/_data/styles.styl)
 -  [OS discussion-2024-06-23.user.js](/images/os-discussions/OS%20discussion-2024-06-23.user.js)

很遗憾我直到下一届 OS 开课时才把这些帖子整理出来——我实在是太忙了。

| 标题 | 作者<br><small>发布日期</small> |
|-|-|
| [适用于操作系统课程的 Docker 镜像 v0.0.4](61) | 离.nvme0n1p2<br><small>2024-02-24 21:48:22</small> |
| [关于$ra寄存器的赋初值问题的一些探索](107) | 杜启嵘<br><small>2024-03-22 23:23:36</small> |
| &#x1F6AB;&#xFE0F;【往年精华帖】简析lab2中page组织结构中链表指针问题理解 | 王哲（助教）<br><small>2024-03-26 23:02:00</small> |
| &#x1F6AB;&#xFE0F;【往年精华帖】举例说明 \`vprintfmt\` 中 \`void *data\` 的作用 | 王哲（助教）<br><small>2024-03-27 16:23:15</small> |
| [整型字面量与变长参数传递问题探究](118) | 沈锎<br><small>2024-03-28 10:08:41</small> |
| &#x1F6AB;&#xFE0F;【往年精华贴】浅谈 \_\_attribute\_\_ | 王哲（助教）<br><small>2024-04-09 18:40:20</small> |
| [lab2 thinking 三级页表自映射](138) | 黄星阳（助教）<br><small>2024-04-12 15:15:24</small> |
| [【分享】命令行环境下 Vim 无法使用 ctags 的解决方法](147) | 仇志轩<br><small>2024-04-17 17:49:31</small> |
| [【总结分享】web端GDB调试的公式化流程与定位/解决bug的方法分析](150) | 纪郅炀<br><small>2024-04-18 19:02:19</small> |
| [【代码展示方式】助教！我哪写错了？](166) | Akashi（助教）<br><small>2024-04-24 23:26:53</small> |
| [关于magic number的一点疑问](208) | 彭欣阳<br><small>2024-05-14 21:13:12</small> |
| [open函数原理的疑问](218) | 爱吃糖的猫<br><small>2024-05-18 16:01:08</small> |
| [ [娱乐性任务][Rust] 获取内核调用栈 ](250) | 离.nvme0n1p2<br><small>2024-05-28 22:47:07</small> |
| [挑战性任务sigaction的一些问题](264) | fickle<br><small>2024-06-02 16:39:58</small> |
| [挑战性任务 shell 求助](275) | Nadleeh<br><small>2024-06-10 16:09:09</small> |
| [sigaction优先级疑问](281) | siven<br><small>2024-06-12 09:57:05</small> |
| [「Sigaction 挑战性任务」为什么进程控制块会变成预期之外的值？](289) | 杨振炜（助教）<br><small>2024-06-13 13:52:18</small> |
| [sigaction评测结果信息](295) | &#x5F;&#x5F;cxc&#x5F;&#x5F;<br><small>2024-06-13 21:57:06</small> |
| [sigaction的bug在哪里？](296) | RyotoTannhauser<br><small>2024-06-13 22:00:38</small> |
| [sigaction的EPC等细节求助](302) | alpha<br><small>2024-06-14 20:05:18</small> |
| [sigaction测试方式求助](304) | 唐锡浩<br><small>2024-06-15 01:07:37</small> |
| [【已解决】 shell增强 测试点1，5求助](305) | Nadleeh<br><small>2024-06-15 11:10:16</small> |
| [Sigaction挑战性任务问题集合](308) | 戴波（助教）<br><small>2024-06-16 01:45:41</small> |
| [Shell挑战性任务问题集合](309) | 戴波（助教）<br><small>2024-06-16 02:09:57</small> |
| [能否对sigaction提供更强的样例](311) | &#x5F;&#x5F;cxc&#x5F;&#x5F;<br><small>2024-06-16 10:06:43</small> |
| [关于sigaction实现的细节问题](314) | 唐凌<br><small>2024-06-16 15:28:40</small> |
| [一组测试sigset的样例](318) | fickle<br><small>2024-06-18 13:29:49</small> |
| [Shell 挑战性任务对历史指令的评测问题](326) | 陈睿正<br><small>2024-06-20 19:40:51</small> |
| [Sigaction测试点4求助：16/18 【已解决】](327) | Daytoy<br><small>2024-06-20 21:08:54</small> |
