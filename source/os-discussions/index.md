---
title: OS 2024 讨论区优质帖汇总
date: 2024-08-08
updated: 2024-08-27
mathjax: true
---
<style>
th:nth-child(2),
td:nth-child(2) {
    text-align: right;
}
</style>

转眼又是一个学期，OS 的学习也已经结束。按照惯例，我整理出了 OS 的讨论区优质贴。

OS 的讨论区并没有精华帖机制，取而代之的是，助教会定期选择少量帖子进行置顶。因此，我需要选择一种快速筛选优质贴的方式。我先是整理出了所有帖子的点赞数量（这里的点赞数量为主题帖的点赞数量，不包括回复）：

![OS 2024 讨论区点赞数量统计](/images/os-discussions/likes.svg)

注意到拥有至少 5 个赞的讨论帖仅有 22 个，占全部讨论帖的 $\frac{22}{287} \approx 8\%$。

以下是本项目使用的脚本、配置、样式文件，如有建议请不吝赐教。学弟学妹如果对本项目感兴趣，可以联系我获取帮助。
 -  [process.py](/images/os-discussions/process.py)
 -  [discussion.json.example](/images/os-discussions/discussion.json.example)
 -  [author.json.example](/images/os-discussions/author.json.example)（真名已隐藏）
 -  [styles.styl](https://github.com/TripleCamera/triplecamera.github.io/tree/main/source/_data/styles.styl)

**注意**：目前本项目仍处于测试阶段，所有文章及评论暂时**保留所有权利**（评论左下角的协议标注无效），直到正式公开发布。

## 待办事项
 -  `process.py`
     -  [ ] 对 `discussion.json` 的 ID 先进行排序
     -  [ ] 对回复先进行排序（JSON 中回复不保证时间先后顺序）
 -  `discussion.json`
     -  [ ] 加入所有超过 5 赞（3 赞？）的帖子（助教公告帖、往届精华帖除外）
     -  逐一检查校对
         -  [ ] ~~118、314、107~~、61、~~150~~、326、208、289
         -  [ ] 166、138
         -  [ ] ~~147~~、250、309、318
         -  [ ] 114、132、264、311、327、116、218、308
 -  `author.json`
     -  [ ] 取得更多作者的授权
 -  [ ] 撰写本页面

### pre3
 -  `stats.py`
     -  [x] 生成点赞数量条形统计图
 -  `process.py`
     -  [x] 支持替换功能
     -  [x] 对帖子标题进行转义（目前能用）
 -  `discussion.json`
     -  逐一检查校对
         -  [x] 118、314、107、150、147
 -  `author.json`
     -  [x] 取得更多作者的授权
 -  [x] 撰写本页面（部分完成）

### pre2
 -  [x] 美化排版
     -  [x] Badges
     -  [x] 日期时间


| 标题 | 作者<br><small>发布日期</small> |
|-|-|
| [整型字面量与变长参数传递问题探究](118) | 沈锎<br><small>2024-03-28 10:08:41</small> |
| [关于sigaction实现的细节问题](314) | 唐凌<br><small>2024-06-16 15:28:40</small> |
| [关于$ra寄存器的赋初值问题的一些探索](107) | 杜启嵘<br><small>2024-03-22 23:23:36</small> |
| [【总结分享】web端GDB调试的公式化流程与定位/解决bug的方法分析](150) | 纪郅炀<br><small>2024-04-18 19:02:19</small> |
| [【分享】命令行环境下 Vim 无法使用 ctags 的解决方法](147) | qzx<br><small>2024-04-17 17:49:31</small> |
