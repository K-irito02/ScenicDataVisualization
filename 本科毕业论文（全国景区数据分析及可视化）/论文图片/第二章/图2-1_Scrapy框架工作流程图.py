# 图2-1 Scrapy框架工作流程图
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
import matplotlib.patches as patches

# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))

# 定义框架组件位置
components = [
    (0.2, 0.7, "调度器\n(Scheduler)"),
    (0.5, 0.9, "URL请求队列"),
    (0.5, 0.5, "下载器\n(Downloader)"),
    (0.8, 0.7, "Spider"),
    (0.5, 0.2, "数据处理管道\n(Pipeline)"),
    (0.2, 0.3, "项目\n(Item)")
]

# 绘制组件
for x, y, label in components:
    rect = patches.Rectangle((x-0.15, y-0.1), 0.3, 0.2, 
                             linewidth=2, edgecolor='black', 
                             facecolor='lightblue', alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', fontsize=12, 
            family='SimSun', weight='bold')

# 绘制连接箭头
arrows = [
    # URL请求队列 到 调度器
    [(0.5, 0.85), (0.35, 0.75)],
    # 调度器 到 下载器
    [(0.35, 0.65), (0.45, 0.55)],
    # 下载器 到 Spider
    [(0.55, 0.55), (0.65, 0.65)],
    # Spider 到 URL请求队列(发现新URL)
    [(0.65, 0.75), (0.5, 0.85)],
    # Spider 到 项目
    [(0.65, 0.65), (0.35, 0.35)],
    # 项目 到 数据处理管道
    [(0.35, 0.25), (0.45, 0.2)]
]

# 箭头样式
arrow_style = patches.ArrowStyle("->", head_length=8, head_width=6)

for start, end in arrows:
    arrow = patches.FancyArrowPatch(
        start, end, connectionstyle="arc3,rad=0.2",
        arrowstyle=arrow_style, color='black', linewidth=1.5)
    ax.add_patch(arrow)

# 添加说明文字
annotations = [
    (0.42, 0.8, "URL请求"),
    (0.38, 0.65, "请求网页"),
    (0.6, 0.57, "返回内容"),
    (0.6, 0.8, "新URL"),
    (0.4, 0.45, "提取数据"),
    (0.4, 0.25, "数据处理")
]

for x, y, text in annotations:
    ax.text(x, y, text, ha='center', va='center', fontsize=10, 
            family='SimSun', style='italic')

# 设置图表
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.show()