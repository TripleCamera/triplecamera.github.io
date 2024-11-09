# 分享帖（而不是求助帖/公告帖）
# 不要往届精华帖（因为没法要授权）

import json5
import math
import matplotlib
import matplotlib.font_manager
import matplotlib.pyplot as plt
import numpy as np
import subprocess

topic_count = 0
likes_count = {}
subscribes_count = {}
likes_subscribes_count = {}
selected_topics = []

for id in range(361):
    try:
        with open(f'discussion/query-topic-{id}.json', 'r', encoding='utf-8') as f:
            s = f.read()
        if s.startswith('No Content'):
            continue

        topic = json5.loads(s)
        title = topic['title']
        likes = topic['likes']
        subscribes = topic['subscribes']

        topic_count += 1
        if not likes in likes_count:
            likes_count[likes] = []
        # likes_count[likes].append((id, title))
        likes_count[likes].append((id, title))
        if not subscribes in subscribes_count:
            subscribes_count[subscribes] = []
        subscribes_count[subscribes].append((id, title))

        if not (likes, subscribes) in likes_subscribes_count:
            likes_subscribes_count[(likes, subscribes)] = []
        likes_subscribes_count[(likes, subscribes)].append((id, title))

        if likes >= 5 or subscribes >= 5:
            selected_topics.append((id, title))
    except FileNotFoundError:
        pass

print(f'Topic count: {topic_count}')
for likes in sorted(likes_count.keys()):
    if True: # len(likes_count[likes]) <= 5:
        print(f'{likes} likes: {len(likes_count[likes])} ({likes_count[likes]})')
    else:
        print(f'{likes} likes: {len(likes_count[likes])}')
for subscribes in sorted(subscribes_count.keys()):
    if True: # len(subscribes_count[subscribes]) <= 5:
        print(f'{subscribes} subscribes: {len(subscribes_count[subscribes])} ({subscribes_count[subscribes]})')
    else:
        print(f'{subscribes} subscribes: {len(subscribes_count[subscribes])}')

max_likes = 0
for likes in likes_count:
    max_likes = max(max_likes, int(likes))

max_subscribes = 0
for subscribes in subscribes_count:
    max_subscribes = max(max_subscribes, int(subscribes))

data = [0] * (max_likes + 1)
for likes in likes_count:
    data[int(likes)] = len(likes_count[likes])

data2 = [0] * (max_subscribes + 1)
for subscribes in subscribes_count:
    data2[int(subscribes)] = len(subscribes_count[subscribes])

print(f'Selected topics: {len(selected_topics)}\n{selected_topics}')

r"""
注意：
先删除 %HOMEPATH%\.matplotlib\fontlist-v330.json，然后在 Python 中运行：
    >>> import matplotlib.font_manager
    >>> matplotlib.font_manager.fontManager.ttflist
在输出中找到思源黑体：
    FontEntry(fname='C:\\Users\\EricQiu\\AppData\\Local\\Microsoft\\Windows\\Fonts\\SourceHanSans.ttc', name='Source Han Sans', style='normal', variant='normal', weight=250, stretch='normal', size='scalable')
"""

# 使用自定义字体，因为 matplotlib 不支持我系统上安装的 OTC
matplotlib.font_manager.fontManager.addfont('SourceHanSansCN-Regular.otf')
plt.rcParams['font.family'] = 'Source Han Sans CN'
# plt.title('OS 2024 讨论区点赞数量统计')
# bc = plt.bar([i for i in range(max_likes + 1)], data)
# plt.bar_label(bc)
# plt.savefig('likes.svg')
# plt.clf()

# plt.title('OS 2024 讨论区订阅数量统计')
# bc = plt.bar([i for i in range(max_subscribes + 1)], data2)
# plt.bar_label(bc)
# plt.savefig('subscribes.svg')

x = []
y = []
z = []
dz = []
count = [[0 for _ in range(21)] for _ in range(22)]
for (like, subscribe) in likes_subscribes_count:
    count[like][subscribe] = len(likes_subscribes_count[(like, subscribe)])
    x.append(like)
    y.append(subscribe)
    z.append(0)
    # dz.append(math.log10(count[like][subscribe]))
    dz.append(count[like][subscribe])
for count_row in count:
    print(count_row)

with open("data.dat", "w") as f:
    for i in range(len(x)):
        f.write(f"{x[i]} {y[i]} {dz[i]}\n")

subprocess.run(["gnuplot", "plot_script.gp"], shell=True)
exit()

# fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

print(x)
print(y)
print(dz)

ax.bar3d(
    x, y, z,
    np.ones_like(x), np.ones_like(x), dz,
    shade=False, edgecolor='black'
)
ax.view_init(elev=30, azim=30)
plt.show()
