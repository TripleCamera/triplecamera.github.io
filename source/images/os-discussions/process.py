"""
将讨论区帖子转换为 Hexo 页面。
作者：TripleCamera（https://triplecamera.github.io/）
协议：MIT
版本：20241225

从网站获取 JSON 文件（https://os.buaa.edu.cn/api/student/discussion/query-topic?id={id}），重命名为
query-topic-{id}.json，并放置到 discussion 目录下。为避免人工操作失误，我们只修改文件名，不修改
内容。

将需要查找替换的内容写入 replace.json，将作者的署名和协议写入 author.json。
"""
from __future__ import annotations

IGNORE_LICENSE: bool = False

import datetime
import json5
import re
import sys

# 记住：每个块开头都没有换行符，结尾都恰好有两个换行符（即：结尾恰好空一行）

# 输出格式，数据来自 post 字典
OUTPUT_FORMAT = """\
---
title: '{title}'
mathjax: true
comments: false
---
<div class="post-info">{replies} 回复</div>
{F_note}
<div id="reply-0" class="reply">
<div class="reply-header">
<span>{F_attribution}</span>
<div class="reply-badges">{F_badges}</div>
</div>
<div class="reply-text">

{F_content}

</div>
<div class="reply-footer">
<span>{F_license}</span>
<div class="reply-datetime">
创建于：<time datetime="{created_at}" title="{created_at}">{F_created_at}</time>
<br>最后修改于：<time datetime="{last_edited_at}" title="{last_edited_at}">{F_last_edited_at}</time>
<br>最后回复于：<time datetime="{last_replied_at}" title="{last_replied_at}">{F_last_replied_at}</time>
</div>
</div>
<div style="clear: both;"></div>
</div>

"""

# 回复格式，数据来自 reply 字典
# 注意 HTML 块必须以行首的标签开始，以空行结束
REPLY_FORMAT = """\
<div id="reply-{id}" class="reply reply-l{Level}">
<div class="reply-header">
<span>{F_header}</span>
<div class="reply-badges">{F_badges}</div>
</div>
<div class="reply-text">

{F_content}

</div>
<div class="reply-footer">
<span>{F_license}</span>
<div class="reply-datetime">
<span>创建于：{F_created_at}</span>
<br><span>最后修改于：{F_last_edited_at}</span>
</div>
</div>
<div style="clear: both;"></div>
</div>

"""

# 表格格式，数据来自 post 字典
# TODO F_created_at -> F_create_date, F_create_datetime
TABLE_FORMAT = """
| {F_link} | {F_attribution}<br><small>{F_created_at}</small> |
""".strip()

discussion_config: dict
author_config: dict
unknown_authors: set = set()
archive_needed_count = 0


# 转换过程中时区信息会保留
def format_iso_time(iso_time: str) -> str:
    return datetime.datetime.fromisoformat(iso_time).strftime('%Y-%m-%d %H:%M:%S')


def format_badges(subscribes: int | None, likes: int, topped: bool, closed: bool, authentic: bool) -> str:
    result = ''

    # subscribes: 大于 0 时显示有色版本，等于 0 时显示无色版本，为 None 时不显示
    if subscribes is not None:
        if subscribes > 0:
            result += f'<div class="badge badge-subscribes">&#x1F516;&#xFE0E; {subscribes} 订阅</div>'
        else:
            result += f'<div class="badge">&#x1F516;&#xFE0E; {subscribes} 订阅</div>'

    # likes: 大于 0 时显示有色版本，等于 0 时显示无色版本
    if likes > 0:
        result += f'<div class="badge badge-likes">&#x1F44D;&#xFE0E; {likes} 点赞</div>'
    else:
        result += f'<div class="badge">&#x1F44D;&#xFE0E; {likes} 点赞</div>'

    # topped: 为 True 时显示有色版本，为 False 时不显示
    if topped:
        result += '<div class="badge badge-topped">&#x1F51D;&#xFE0E; 已置顶</div>'

    # closed: 为 True 时显示有色版本，为 False 时不显示
    if closed:
        result += '<div class="badge badge-closed">&#x274C;&#xFE0E; 已关闭</div>'

    # authentic: 为 True 时显示有色版本，为 False 时不显示
    if authentic:
        result += '<div class="badge badge-authentic">&#x2714;&#xFE0E; 由课程团队认证</div>'

    return result


# 对回复文本进行多功能查找替换
def advanced_replace(post_id: int, text: str, rules: list) -> str:
    global archive_needed_count

    for rule in rules:
        match rule[0]:
            case 'sub':
                assert len(rule) == 3
                text = text.replace(rule[1], rule[2])
            case 'sub.re':
                assert len(rule) == 3
                text = re.sub(rule[1], rule[2], text)
            case 'img':
                assert len(rule) == 3
                text = text.replace(rule[1], f'/images/os-discussions/{post_id}/{rule[2]}')
            case 'img.re':
                assert len(rule) == 2
                text = re.sub(rule[1], f'/images/os-discussions/{post_id}/\\1', text)
            case 'arc':
                assert len(rule) == 3
                text = text.replace(rule[1], f'{rule[1]}<small>（[存档]({rule[2]})）</small>')
            case 'arc_raw':
                assert len(rule) == 3
                text = text.replace(rule[1], f'{rule[1]}<small>（<a target="_blank" rel="noopener" href="{rule[2]}">存档</a>）</small>')
            case 'arc_need':
                assert len(rule) == 2
                text = text.replace(rule[1], f'{rule[1]}<small>（需要存档）</small>')
                archive_needed_count += 1
            case 'arc_noneed':
                assert len(rule) == 2
                text = text.replace(rule[1], f'{rule[1]}<small>（无需存档）</small>')
            case 'arc_lost':
                assert len(rule) == 2
                text = text.replace(rule[1], f'{rule[1]}<small>（已丢失）</small>')
            case _:
                print(f'[ERROR] Unknown function {rule[0]}')
    return text



# aka Post
class Reply:
    discussion_id: int
    id: int
    reply_target: int
    level: int
    created_at: str
    created_at_datetime: str
    last_edited_at: str
    last_edited_at_datetime: str
    badges: str
    content: str
    attribution: str
    license: str
    reply_list: list[Reply]

    def __init__(self, reply_dict: dict, discussion_id: int, level: int):
        _id = reply_dict['id']
        _reply_target = reply_dict['reply_target']
        _author_name = reply_dict['author_name']
        _author_avatar = reply_dict['author_avatar']
        _created_at = reply_dict['created_at']
        _last_edited_at = reply_dict['last_edited_at']
        _likes = reply_dict['likes']
        _liked = reply_dict['liked']
        _authentic = reply_dict['authentic']
        _content = reply_dict['content']

        # author_dict ...
        discussion_dict = discussion_config.get(str(discussion_id), {})
        discussion_note = discussion_dict.get('note')
        discussion_replace = discussion_dict.get('replace')
        author_dict: dict = author_config.get(_author_name, {})
        author_attribution = author_dict.get('attribution')
        author_license = author_dict.get('license')

        self.discussion_id = discussion_id
        self.id = _id
        self.reply_target = _reply_target
        self.level = level
        self.created_at = _created_at
        self.created_at_datetime = format_iso_time(_created_at)
        self.last_edited_at = _last_edited_at
        self.last_edited_at_datetime = format_iso_time(_last_edited_at)

        self.badges = format_badges(None, _likes, False, False, _authentic)
        
        if IGNORE_LICENSE:
            self.content = (
                advanced_replace(discussion_id, _content, discussion_replace)
                if discussion_replace is not None
                else f'【无替换规则】\n\n{_content}'
            )
            # TODO: Add reply target
            self.attribution = author_attribution or f'【未署名】{_author_name}'
            self.license = author_license or '【未选择协议】'
        elif author_attribution and author_license:
            assert discussion_replace is not None
            self.content = advanced_replace(discussion_id, _content, discussion_replace)
            self.attribution = author_attribution
            self.license = author_license
        else:
            self.content = '???'
            self.attribution = '???'
            self.license = '???'
            unknown_authors.add(_author_name)


    def get_output_str(self) -> str:
        result = REPLY_FORMAT.format(
            id=self.id,
            Level=self.level,
            F_header=self.attribution,
            F_badges=self.badges,
            F_content=self.content,
            F_license=self.license,
            F_created_at=self.created_at_datetime,
            F_last_edited_at=self.last_edited_at_datetime,
        )

        for reply in self.reply_list:
            result += '<hr class="reply-separator">\n\n' + reply.get_output_str()

        return result

# aka Thread
class Topic:
    id: int
    title: str
    escaped_title: str
    replies: int
    created_at: str
    created_at_datetime: str
    last_edited_at: str
    last_edited_at_datetime: str
    last_replied_at: str
    last_replied_at_datetime: str
    note: str
    badges: str
    link: str
    content: str
    attribution: str
    license: str
    reply_list: list[Reply] | None
    ignore: bool

    def __init__(self, topic_dict: dict):
        _id = topic_dict['id']
        _title = topic_dict['title']
        _replies = topic_dict['replies']
        _author_name = topic_dict['author_name']
        _author_avatar = topic_dict['author_avatar']
        _created_at = topic_dict['created_at']
        _last_edited_at = topic_dict['last_edited_at']
        _last_replied_at = topic_dict['last_replied_at']
        _subscribes = topic_dict['subscribes']
        _likes = topic_dict['likes']
        _topped = topic_dict['topped']
        _closed = topic_dict['closed']
        _authentic = topic_dict['authentic']
        _subscribed = topic_dict['subscribed']
        _liked = topic_dict['liked']
        _abstract = topic_dict['abstract']
        _content = topic_dict['content']
        _reply_list = topic_dict['reply_list']

        discussion_dict = discussion_config.get(str(_id), {})
        discussion_note = discussion_dict.get('note')
        discussion_replace = discussion_dict.get('replace')
        discussion_ignore = discussion_dict.get('ignore', False)
        author_dict = author_config.get(_author_name, {})
        author_attribution = author_dict.get('attribution')
        author_license = author_dict.get('license')

        self.id = _id
        self.title = _title
        self.escaped_title = _title.replace('_', '\\_')
        self.replies = _replies
        self.created_at = _created_at
        self.created_at_datetime = format_iso_time(_created_at)
        self.last_edited_at = _last_edited_at
        self.last_edited_at_datetime = format_iso_time(_last_edited_at)
        self.last_replied_at = _last_replied_at
        self.last_replied_at_datetime = format_iso_time(_last_replied_at)
        self.note = (
            f"\n> **提示**：{discussion_note}\n"
            if discussion_note
            else ''
        )
        self.badges = format_badges(_subscribes, _likes, _topped, _closed, _authentic)
        self.link = (
            f'[{self.escaped_title}]({self.id})'
            if not discussion_ignore
            else '&#x1F6AB;&#xFE0F;' + self.escaped_title
        )
        self.ignore = discussion_ignore

        if IGNORE_LICENSE:
            self.content = (
                advanced_replace(_id, _content, discussion_replace)
                if discussion_replace is not None
                else f'【无替换规则】\n\n{_content}'
            )
            self.attribution = author_attribution or f'【未署名】{_author_name}'
            self.license = author_license or '【未选择协议】'
        elif author_attribution and author_license:
            assert discussion_replace is not None
            self.content = advanced_replace(_id, _content, discussion_replace)
            self.attribution = author_attribution
            self.license = author_license
        else:
            self.content = '???'
            self.attribution = '???'
            self.license = '???'
            unknown_authors.add(_author_name)


    def get_output_str(self) -> str:
        assert not self.ignore
        result = OUTPUT_FORMAT.format(
            title=self.title,
            replies=self.replies,
            F_note=self.note,
            F_attribution=self.attribution,
            F_badges=self.badges,
            F_content=self.content,
            F_license=self.license,
            created_at=self.created_at,
            F_created_at=self.created_at_datetime,
            last_edited_at=self.last_edited_at,
            F_last_edited_at=self.last_edited_at_datetime,
            last_replied_at=self.last_replied_at,
            F_last_replied_at=self.last_replied_at_datetime,
        )

        for reply in self.reply_list:
            result += '## 回复主题帖\n\n' + reply.get_output_str()

        return result
    
    def get_table_str(self) -> str:
        return TABLE_FORMAT.format(
            F_link=self.link,
            F_attribution=self.attribution,
            F_created_at=self.created_at_datetime,
        )

def process_replies(obj: Topic | Reply, topic_dict: dict, reply_target: int, level: int) -> str:
    discussion_id = topic_dict['id']

    reply_dict_list = topic_dict['reply_list'] or []
    direct_reply_list = [
        reply_dict
        for reply_dict in reply_dict_list
        if reply_dict['reply_target'] == reply_target
    ]
    direct_reply_list.sort(key=lambda r: datetime.datetime.fromisoformat(r['created_at']))

    direct_reply_obj_list = []
    for reply_dict in direct_reply_list:
        reply_id = reply_dict['id']
        reply_obj = Reply(reply_dict, discussion_id, level)
        process_replies(reply_obj, topic_dict, reply_id, level + 1)
        direct_reply_obj_list.append(reply_obj)
    obj.reply_list = direct_reply_obj_list
    return

    for reply in direct_reply_list:
        # TODO: Cleanup code below
        reply_content = REPLY_FORMAT.format(**reply)
        formatted_nested_replies = process_replies(topic, reply['id'], level + 1)
        if formatted_nested_replies:
            formatted_reply_list.append(f'{reply_content}\n<hr class="reply-separator">\n{formatted_nested_replies}')
        else:
            formatted_reply_list.append(reply_content)
    
    if level == 0:
        return '## 回复主题帖\n\n' + '\n\n## 回复主题帖\n\n'.join(formatted_reply_list)
    else:
        return '\n<hr class="reply-separator">\n'.join(formatted_reply_list)


def process_topic(topic_dict: dict) -> Topic:
    topic_obj = Topic(topic_dict)
    process_replies(topic_obj, topic_dict, 0, 0)
    return topic_obj


def main():
    global discussion_config, author_config

    with open('discussion.json', 'r', encoding='utf-8') as f:
        discussion_config = json5.load(f)

    with open('author.json', 'r', encoding='utf-8') as f:
        author_config = json5.load(f)

    topics = []
    for id_str in discussion_config:
        topics.append(int(id_str))
    if topics != sorted(topics):
        print('[WARNING] discussion.json 中帖子 ID 不是递增的。', file=sys.stderr)
    topics.sort()
    if topics != [61, 107, 114, 116, 118, 132, 138, 147, 150, 166, 208, 218, 250, 264, 275, 281, 289, 295, 296, 302, 304, 305, 308, 309, 311, 314, 318, 326, 327]:
        print('[WARNING] discussion.json 中帖子 ID 不是预期的值。', file=sys.stderr)

    for id in topics:
        with open(f'discussion/query-topic-{id}.json', 'r', encoding='utf-8') as f:
            topic_dict = json5.load(f)
        topic_obj = process_topic(topic_dict)
        if not topic_obj.ignore:
            output = topic_obj.get_output_str()
            with open(f'output/{id}.md', 'w', encoding='utf-8') as f:
                f.write(output)
        print(topic_obj.get_table_str())

    print(f'转换了 {len(topics)} 篇帖子。')
    if unknown_authors:
        print('以下作者尚未同意转载其内容：', '、'.join(unknown_authors), sep='')
    if archive_needed_count > 0:
        print(f'{archive_needed_count} 份参考资料需要存档。')


if __name__ == '__main__':
    main()
