"""
将讨论区帖子转换为 Hexo 页面。
作者：TripleCamera（https://triplecamera.github.io/）
协议：MIT
版本：20240130

原始数据：从网站获得的 JSON 文件。为防止操作失误，我们只修改文件名，不修改内容。
 -  所有 discussion-info 放置在 info 下，并重命名为 discussion-info-{id}.json。（未使用）
 -  所有 response-list 放置在 post 下，并重命名为 response-list-{id}.json。
 -  所有 get-tag-details 放置在 tag 下，并重命名为 get-tag-details-{id}.json。
 -  discussion-search-by-tag.html 放置在 . 下，并重命名为 discussion-search-by-tag.json。

补充数据：人工撰写的 JSON 文件。
 -  license.json：根对象以真名为键，信息对象为值。信息对象包含包含协议（"license"）和署名（"attribution"）。
                  如果未找到某位作者，则该作者的所有文章都不会导出，该作者的所有评论都会被隐藏。
 -  replace.json：根对象以 id 为键，查找替换对象为值。查找替换对象以查找内容（正则表达式）为键，替换内容（支持 match group）为值。
                  注意如果未找到某篇文章，程序会直接报错，请确保所有文章都已写入文件（无需查找替换的文章请将 id 映射到空对象）。
"""

import json
import os
import re

# 输出格式，数据来自 post 字典
OUTPUT_FORMAT = """
---
title: {title}
date: 2024-01-27
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
<span>{tags}</span>
</div>

{content}
""".strip()

# 回复格式，数据来自 reply 字典
# 注意 HTML 块必须以行首的标签开始，以空行结束
REPLY_FORMAT = """
<div id="reply-{id}" class="reply">
<div class="reply-header">
<span>{author}</span>{verified}
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
| {link} | {attribution} | {create_date} | {license} |
""".strip()

# ISO 格式转年月日格式
def date(iso: str) -> str:
    return iso[0:10]

# ISO 格式转年月日时分秒格式
def datetime(iso: str) -> str:
    return iso[0:10] + ' ' + iso[11:19]


discussions_file = open('discussion-search-by-tags.json', 'r', encoding='utf-8')
discussions = json.load(discussions_file)
discussions_file.close()

license_file = open('license.json', 'r', encoding='utf-8')
license = json.load(license_file)
license_file.close()

replace_file = open('replace.json', 'r', encoding='utf-8')
replace = json.load(replace_file)
replace_file.close()

converted_posts_count = 0
total_posts_count = len(discussions)

for discussion in reversed(discussions):
    post = {}
    post['id'] = discussion['Id']
    post['title'] = discussion['Title']
    post['reply'] = discussion['Response_num']
    post['create'] = discussion['Created_at']
    post['create_date'] = date(post['create'])
    post['create_datetime'] = datetime(post['create'])
    post['update'] = discussion['Updated_at']
    post['follow'] = discussion['Follow_num']
    post['author'] = discussion['First_name']

    # 是否取得了原作者许可
    post_flag = (
        os.path.isfile(f"post/response-list-{post['id']}.json") and
        os.path.isfile(f"tag/get-tag-details-{post['id']}.json") and
        post['author'] in license
    )

    post['license'] = license[post['author']]['license'] if post_flag else '???'
    post['attribution'] = license[post['author']]['attribution'] if post_flag else '???'
    post['link'] = '[{}]({})'.format(post['title'], post['id']) if post_flag else post['title']

    # discussion['Created_at'] 与 discussion['Updated_at'] 之间可能会相差 0.00001s
    # if discussion['Created_at'] != discussion['Updated_at']:
    #     print('ERROR! Created_at({}) != Updated_at({})'.format(discussion['Created_at'], discussion['Updated_at']))
    print(TABLE_FORMAT.format(**post))

    if post_flag:
        responses_file = open(f"post/response-list-{post['id']}.json", 'r', encoding='utf-8')
        responses = json.load(responses_file)
        responses_file.close()

        tags_file = open(f"tag/get-tag-details-{post['id']}.json", 'r', encoding='utf-8')
        tags = json.load(tags_file)
        tags_file.close()

        tags_list = []
        for tag in tags['tagDataArray']:
            if tag['owned']:
                tags_list.append(tag['tagName'])
        post['tags'] = '、'.join(tags_list)

        reply_content_list = []
        for response in responses:
            reply = {}
            reply['id'] = response['Id']
            reply['verified'] = '\n<div class="reply-verified">助教认证</div>' if response['Authority'] else ''
            reply['create'] = response['Created_at']
            reply['create_datetime'] = datetime(reply['create'])
            reply['vote'] = response['Vote_num']

            reply_flag = response['First_name'] in license

            if reply_flag:
                reply['text'] = response['Content']
                for pattern, repl in replace[str(post['id'])].items():
                    reply['text'] = re.sub(pattern, repl, reply['text'])
                reply['author'] = license[response['First_name']]['attribution']
                reply['license'] = license[response['First_name']]['license']
            else:
                reply['text'] = '???'
                reply['author'] = '???'
                reply['license'] = '???'

            reply_content = REPLY_FORMAT.format(**reply)
            reply_content_list.append(reply_content)

        post['content'] = '\n<hr class="reply-separator">\n'.join(reply_content_list)
        output = OUTPUT_FORMAT.format(**post)

        output_file = open(f"output/{post['id']}.md", 'w', encoding='utf-8')
        output_file.write(output)
        output_file.close()

        converted_posts_count += 1

print(f'转换了 {converted_posts_count} / {total_posts_count} 篇帖子。')
