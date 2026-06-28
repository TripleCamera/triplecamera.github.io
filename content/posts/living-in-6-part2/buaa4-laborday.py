import matplotlib.pyplot as plt

data = [515, 393, 255, 182, 98, 240]
labels = ['OO hw9', 'OO hw10', '整理宿舍', 'OS Lab4', '离散数学', '其他']

def pct2text(pct):
    alltime = sum(data)
    time = int(alltime * pct / 100 + 0.01)
    return f'{time // 60}h{time % 60}min' if time % 60 != 0 else f'{time // 60}h'

plt.rcParams['font.family'] = 'Source Han Sans CN'
plt.title('劳动节学习用时统计')
plt.pie(
    data,
    labels = labels,
    autopct = lambda pct: pct2text(pct)
)

# plt.show()
plt.savefig('buaa4-laborday.svg')
