"""
将讨论区帖子转换为 Hexo 页面。
作者：TripleCamera（https://triplecamera.github.io/）
协议：MIT
版本：20241109

从网站获取 JSON 文件（https://os.buaa.edu.cn/api/student/discussion/query-topic?id={id}），重命名为
query-topic-{id}.json，并放置到 discussion 目录下。为避免人工操作失误，我们只修改文件名，不修改
内容。

将需要查找替换的内容写入 replace.json，将作者的署名和协议写入 author.json。
"""

IGNORE_LICENSE: bool = False

import datetime
import json5
import re
import sys

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

{F_reply_list}
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

def format_replies(topic: dict, reply_target: int, level: int) -> str:
    global unknown_authors

    formatted_reply_list = []

    filtered_reply_list = []
    for reply in topic['reply_list']:
        if reply['reply_target'] == reply_target:
            filtered_reply_list.append(reply)
    filtered_reply_list.sort(key=lambda x: datetime.datetime.fromisoformat(x['created_at']))

    for reply in filtered_reply_list:
        reply['Level'] = level
        reply['F_badges'] = format_badges(
            None, reply['likes'], False, False, reply['authentic']
        )
        reply['F_created_at'] = format_iso_time(reply['created_at'])
        reply['F_last_edited_at'] = format_iso_time(reply['last_edited_at'])
        if IGNORE_LICENSE:
            reply['F_header'] = (
                author_config[reply['author_name']]['attribution']
                if reply['author_name'] in author_config and 'attribution' in author_config[reply['author_name']]
                else f"【未署名】{reply['author_name']}"
            )
            reply['F_license'] = (
                author_config[reply['author_name']]['license']
                if reply['author_name'] in author_config and 'license' in author_config[reply['author_name']]
                else '【未选择协议】'
            )
            reply['F_content'] = (
                advanced_replace(topic['id'], reply['content'], discussion_config[str(topic['id'])]['replace'])
                if 'replace' in discussion_config[str(topic['id'])]
                else f"【无替换规则】\n\n{reply['content']}"
            )
        elif reply['author_name'] in author_config:
            reply['F_header'] = author_config[reply['author_name']]['attribution']
            reply['F_license'] = author_config[reply['author_name']]['license']
            reply['F_content'] = advanced_replace(topic['id'], reply['content'], discussion_config[str(topic['id'])]['replace'])
        else:
            reply['F_header'] = '???'
            reply['F_license'] = '???'
            reply['F_content'] = '???'
            unknown_authors.add(reply['author_name'])
        reply_content = REPLY_FORMAT.format(**reply)
        formatted_nested_replies = format_replies(topic, reply['id'], level + 1)
        if formatted_nested_replies:
            formatted_reply_list.append(f'{reply_content}\n<hr class="reply-separator">\n{formatted_nested_replies}')
        else:
            formatted_reply_list.append(reply_content)
    
    if level == 0:
        return '## 回复主题帖\n\n' + '\n\n## 回复主题帖\n\n'.join(formatted_reply_list)
    else:
        return '\n<hr class="reply-separator">\n'.join(formatted_reply_list)


def process_topic(topic: dict) -> str:
    # topic['attribution'] = topic['author_name']
    # topic['F_license'] = '???'
    topic['F_created_at'] = format_iso_time(topic['created_at'])
    topic['F_last_edited_at'] = format_iso_time(topic['last_edited_at'])
    topic['F_last_replied_at'] = format_iso_time(topic['last_replied_at'])
    topic['F_link'] = '[{}]({})'.format(topic['title'], topic['id'])
    topic['F_badges'] = format_badges(
        topic['subscribes'], topic['likes'], topic['topped'], topic['closed'], topic['authentic']
    )
    topic['F_note'] = (
        f"\n> **提示**：{discussion_config[str(topic['id'])]['note']}\n"
        if 'note' in discussion_config[str(topic['id'])]
        else ''
    )
    if IGNORE_LICENSE:
        topic['F_attribution'] = (
            author_config[topic['author_name']]['attribution']
            if topic['author_name'] in author_config and 'attribution' in author_config[topic['author_name']]
            else f"【未署名】{topic['author_name']}"
        )
        topic['F_license'] = (
            author_config[topic['author_name']]['license']
            if topic['author_name'] in author_config and 'license' in author_config[topic['author_name']]
            else '【未选择协议】'
        )
        topic['F_content'] = (
            advanced_replace(topic['id'], topic['content'], discussion_config[str(topic['id'])]['replace'])
            if 'replace' in discussion_config[str(topic['id'])]
            else f"【无替换规则】\n\n{topic['content']}"
        )
    elif topic['author_name'] in author_config:
        topic['F_attribution'] = author_config[topic['author_name']]['attribution']
        topic['F_license'] = author_config[topic['author_name']]['license']
        topic['F_content'] = advanced_replace(
            topic['id'],
            topic['content'],
            discussion_config[str(topic['id'])]['replace'] if 'replace' in discussion_config[str(topic['id'])] else [],
        )
    else:
        topic['F_attribution'] = '???'
        topic['F_license'] = '???'
        topic['F_content'] = '???'
        unknown_authors.add(topic['author_name'])

    topic['F_reply_list'] = format_replies(topic, 0, 0) if topic['reply_list'] else ''
    return OUTPUT_FORMAT.format(**topic)


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
            topic = json5.load(f)
        output = process_topic(topic)
        with open(f'output/{id}.md', 'w', encoding='utf-8') as f:
            f.write(output)
        print(TABLE_FORMAT.format(**topic))

    print(f'转换了 {len(topics)} 篇帖子。')
    if unknown_authors:
        print('以下作者尚未同意转载其内容：', '、'.join(unknown_authors), sep='')
    if archive_needed_count > 0:
        print(f'{archive_needed_count} 份参考资料需要存档。')


if __name__ == '__main__':
    main()
