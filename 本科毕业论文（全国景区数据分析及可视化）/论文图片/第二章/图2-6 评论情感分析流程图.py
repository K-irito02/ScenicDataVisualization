# 图2-6 评论情感分析流程图
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# 创建画布
fig, ax = plt.subplots(figsize=(12, 7))

# 定义流程步骤
steps = [
    (0.5, 0.90, "评论文本"),
    (0.5, 0.75, "文本预处理"),
    (0.5, 0.60, "中文分词"),
    (0.25, 0.45, "情感词识别"),
    (0.50, 0.45, "程度副词识别"),
    (0.75, 0.45, "否定词识别"),
    (0.5, 0.30, "情感得分计算"),
    (0.5, 0.15, "情感分类(优/良/中)")
]

# 绘制流程步骤
for i, (x, y, label) in enumerate(steps):
    if i == 0:  # 第一个是数据输入
        rect = patches.Rectangle((x-0.15, y-0.05), 0.3, 0.1, 
                                linewidth=2, edgecolor='black', 
                                facecolor='lightgreen', alpha=0.7)
    elif i == len(steps) - 1:  # 最后一个是结果输出
        rect = patches.Rectangle((x-0.2, y-0.05), 0.4, 0.1, 
                                linewidth=2, edgecolor='black', 
                                facecolor='lightcoral', alpha=0.7)
    elif i >= 3 and i <= 5:  # 三个并行的识别步骤
        rect = patches.Rectangle((x-0.125, y-0.05), 0.25, 0.1, 
                                linewidth=2, edgecolor='black', 
                                facecolor='lightyellow', alpha=0.7)
    else:  # 普通处理步骤
        rect = patches.Rectangle((x-0.15, y-0.05), 0.3, 0.1, 
                                linewidth=2, edgecolor='black', 
                                facecolor='lightblue', alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', fontsize=12, 
            family='SimSun', weight='bold')

# 绘制连接箭头
for i in range(len(steps) - 1):
    if i < 2:  # 前三个步骤是串行的
        ax.arrow(steps[i][0], steps[i][1]-0.05, 0, steps[i+1][1]-steps[i][1]+0.12, 
                head_width=0.02, head_length=0.02, fc='black', ec='black', linewidth=1.5)
    elif i == 2:  # 从分词到三个并行步骤
        ax.arrow(steps[i][0], steps[i][1]-0.05, -0.25, steps[i+1][1]-steps[i][1]+0.1, 
                head_width=0.02, head_length=0.02, fc='black', ec='black', linewidth=1.5)
        ax.arrow(steps[i][0], steps[i][1]-0.05, 0, steps[i+2][1]-steps[i][1]+0.12, 
                head_width=0.02, head_length=0.02, fc='black', ec='black', linewidth=1.5)
        ax.arrow(steps[i][0], steps[i][1]-0.05, 0.25, steps[i+3][1]-steps[i][1]+0.1, 
                head_width=0.02, head_length=0.02, fc='black', ec='black', linewidth=1.5)
    elif i == 5:  # 从三个并行步骤到情感得分计算
        ax.arrow(steps[3][0], steps[3][1]-0.05, 0.25, steps[6][1]-steps[3][1]+0.12, 
                head_width=0, head_length=0, fc='black', ec='black', linewidth=1.5)
        ax.arrow(steps[4][0], steps[4][1]-0.05, 0, steps[6][1]-steps[4][1]+0.12, 
                head_width=0.02, head_length=0.02, fc='black', ec='black', linewidth=1.5)
        ax.arrow(steps[5][0], steps[5][1]-0.05, -0.25, steps[6][1]-steps[5][1]+0.12, 
                head_width=0, head_length=0, fc='black', ec='black', linewidth=1.5)

# 最后一个连接箭头
ax.arrow(steps[6][0], steps[6][1]-0.05, 0, steps[7][1]-steps[6][1]+0.12, 
        head_width=0.02, head_length=0.02, fc='black', ec='black', linewidth=1.5)


# 设置图表
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.show()