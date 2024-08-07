# 分享帖（而不是求助帖/公告帖）
# 不要往届精华帖（因为没法要授权）

import json5

topic_count = 0
likes_count = {}
subscribes_count = {}

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
        likes_count[likes].append(title)
        if not subscribes in subscribes_count:
            subscribes_count[subscribes] = []
        subscribes_count[subscribes].append(title)
    except FileNotFoundError:
        pass

print(f'Topic count: {topic_count}')
for likes in sorted(likes_count.keys()):
    if len(likes_count[likes]) <= 5:
        print(f'{likes} likes: {len(likes_count[likes])} ({likes_count[likes]})')
    else:
        print(f'{likes} likes: {len(likes_count[likes])}')
for subscribes in sorted(subscribes_count.keys()):
    if len(subscribes_count[subscribes]) <= 5:
        print(f'{subscribes} subscribes: {len(subscribes_count[subscribes])} ({subscribes_count[subscribes]})')
    else:
        print(f'{subscribes} subscribes: {len(subscribes_count[subscribes])}')
