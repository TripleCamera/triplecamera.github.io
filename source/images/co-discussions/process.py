"""
将讨论区帖子转换为 Hexo 页面。
作者：TripleCamera（https://triplecamera.github.io/）
协议：MIT
版本：20240228

原始数据：从网站获得的 JSON 文件。为防止操作失误，我们只修改文件名，不修改内容。
 -  所有 discussion-info 放置在 info 下，并重命名为 discussion-info-{id}.json。
    程序会扫描此文件夹，并提取出所有帖子的 id。
 -  所有 response-list 放置在 responses 下，并重命名为 response-list-{id}.json。
 -  所有 get-tag-details 放置在 tags 下，并重命名为 get-tag-details-{id}.json。

补充数据：人工撰写的 JSON 文件。
 -  license.json：根对象以真名为键，信息对象为值。信息对象包含包含协议（"license"）和署名（"attribution"）。
                  如果未找到某位作者，则该作者的所有文章都不会导出，该作者的所有评论都会被隐藏。
 -  replace.json：根对象以 id 为键，查找替换对象为值。查找替换对象以查找内容（正则表达式）为键，替换内容（支持 match group）为值。
                  注意如果未找到某篇文章，程序会直接报错，请确保所有文章都已写入文件（无需查找替换的文章请将 id 映射到空对象）。
"""

import json5
import os
import re

# 输出格式，数据来自 post 字典
OUTPUT_FORMAT = """
---
title: {title}
mathjax: true
---
<div class="post-info">
<span>{attribution}</span>
|
<abbr title="{create}"><time datetime="{create}">{create_datetime}</time></abbr>
|
<span>\u2B50\uFE0F {follow}</span>
|
<span>\U0001F4AC\uFE0F {reply}</span>
<br>
<div>{tags}</div>
</div>
{note}
{content}
""".strip()

# 回复格式，数据来自 reply 字典
# 注意 HTML 块必须以行首的标签开始，以空行结束
REPLY_FORMAT = """
<div id="reply-{id}" class="reply reply-l{level}">
<div class="reply-header">
<span>{header}</span>{verified}
</div>
<div class="reply-text">

{text}

</div>
<div class="reply-footer">
<abbr title="{create}"><time datetime="{create}">{create_datetime}</time></abbr>
|
<span>{license}</span>
<span class="reply-vote">\u2764\uFE0F {vote}</span>
</div>
</div>
""".strip()

# 表格格式，数据来自 post 字典
TABLE_FORMAT = """
| {link} | {attribution} | {create_date} |
""".strip()

unknown_authors = set()

# ISO 格式转年月日格式
def date(iso: str) -> str:
    return iso[0:10]

# ISO 格式转年月日时分秒格式
def datetime(iso: str) -> str:
    return iso[0:10] + ' ' + iso[11:19]

def process_responses(reply_content_list: list, responses: dict, cite_id: int, level: int) -> None:
    for response in responses:
        if response['Citing_id']['Int32'] == cite_id:
            reply = {}
            reply['id'] = response['Id']
            reply['verified'] = '\n<div class="reply-verified">助教认证</div>' if response['Authority'] else ''
            reply['create'] = response['Created_at']
            reply['create_datetime'] = datetime(reply['create'])
            reply['vote'] = response['Vote_num']
            reply['cite_id'] = response['Citing_id']['Int32']
            reply['cite_author'] = response['Citing_first_name']
            reply['level'] = level

            reply_flag = response['First_name'] in license
            reply_cite = response['Citing_id']['Valid']

            if reply_flag:
                reply_text = response['Content']
                for pattern, repl in replace[str(post['id'])].items():
                    reply_text = re.sub(pattern, repl, reply_text)

                reply['text'] = reply_text
                reply['author'] = license[response['First_name']]['attribution']
                reply['cite_author'] = license[response['Citing_first_name']]['attribution'] if response['Citing_first_name'] in license else '???'
                reply['license'] = license[response['First_name']]['license']

                reply['header'] = (
                    f"{reply['author']} <a href=\"#reply-{reply['cite_id']}\">回复</a> {reply['cite_author']}"
                    if reply_cite
                    else reply['author']
                )
            else:
                reply['text'] = '???'
                reply['author'] = '???'
                reply['cite_author'] = '???'
                reply['license'] = '???'
                reply['header'] = '???'
                unknown_authors.add(response['First_name'])

            reply_content = REPLY_FORMAT.format(**reply)
            reply_content_list.append(reply_content)
            process_responses(reply_content_list, responses, reply['id'], level + 1)



id_list = []
for f in os.listdir('info'):
    result = re.match(r'discussion-info-(\d+).json$', f)
    if result:
        id_list.append(int(result.group(1)))
id_list.sort()

license_file = open('license.json', 'r', encoding='utf-8')
license = json5.load(license_file)
license_file.close()

replace_file = open('replace.json', 'r', encoding='utf-8')
replace = json5.load(replace_file)
replace_file.close()

note_file = open('note.json', 'r', encoding='utf-8')
note = json5.load(note_file)
note_file.close()

converted_posts_count = 0
total_posts_count = len(id_list)

for id in id_list:
    info_file = open(f'info/discussion-info-{id}.json', 'r', encoding='utf-8')
    info = json5.load(info_file)
    info_file.close()

    responses_file = open(f'responses/response-list-{id}.json', 'r', encoding='utf-8')
    responses = json5.load(responses_file)
    responses_file.close()

    tags_file = open(f'tags/get-tag-details-{id}.json', 'r', encoding='utf-8')
    tags = json5.load(tags_file)
    tags_file.close()

    # 从 discussion-search-by-tags.json 迁移到 discussion-info-{id}.json 的注意事项：
    # 1.  info['First_name'] 的值恒为 ''，改用 responses[0]['First_name']
    # 2.  info['Response_num'] 的值恒为 0，改用 len(responses)
    post = {}
    post['author'] = responses[0]['First_name']
    post['create'] = info['Created_at'] # info['Created_at'] 与 info['Updated_at'] 之间可能会相差 0.00001s
    post['create_date'] = date(post['create'])
    post['create_datetime'] = datetime(post['create'])
    post['follow'] = info['Follow_num']
    post['id'] = info['Id']
    post['note'] = f"\n> **提示**：{note[str(post['id'])]}\n" if str(post['id']) in note else ''
    post['reply'] = len(responses)
    post['title'] = info['Title']

    # 是否取得了原作者许可
    post_flag = post['author'] in license

    post['attribution'] = license[post['author']]['attribution'] if post_flag else '???'
    post['link'] = '[{}]({})'.format(post['title'], post['id']) if post_flag else post['title']
    post['license'] = license[post['author']]['license'] if post_flag else '???'
    if post_flag:
        pass # TODO 将三元运算符拆分为 if-else
    else:
        unknown_authors.add(post['author'])

    print(TABLE_FORMAT.format(**post))

    if post_flag:
        # inline-block 元素间换行会产生额外空格，因此必须保持在一行内
        # TODO 使用 flex 代替 inline-block
        tags_list = []
        for tag in tags['tagDataArray']:
            if tag['owned']:
                tags_list.append(f"<div class=\"post-tag\">{tag['tagName']}</div>")
        post['tags'] = ''.join(tags_list)

        reply_content_list = []
        process_responses(reply_content_list, responses, 0, 0)

        post['content'] = '\n<hr class="reply-separator">\n'.join(reply_content_list)
        output = OUTPUT_FORMAT.format(**post)

        output_file = open(f"output/{post['id']}.md", 'w', encoding='utf-8')
        output_file.write(output)
        output_file.close()

        converted_posts_count += 1

print(f'转换了 {converted_posts_count} / {total_posts_count} 篇帖子。')
if unknown_authors:
    print('以下作者尚未同意转载其内容：', '、'.join(unknown_authors), sep='')
