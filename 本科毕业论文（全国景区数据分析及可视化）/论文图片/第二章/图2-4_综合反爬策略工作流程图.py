# 图2-4 综合反爬策略工作流程图
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.path import Path

# 创建画布
fig, ax = plt.subplots(figsize=(10, 8))

# 定义流程步骤
steps = [
    (0.5, 0.9, "爬虫请求初始化"),
    (0.25, 0.75, "User-Agent\n随机化"),
    (0.75, 0.75, "IP代理\n选择"),
    (0.5, 0.6, "请求速率\n控制"),
    (0.5, 0.45, "浏览器特征\n隐藏"),
    (0.5, 0.3, "请求发送"),
    (0.2, 0.15, "正常响应\n处理"),
    (0.8, 0.15, "异常响应\n智能重试")
]

# 绘制流程步骤
for x, y, label in steps:
    if '初始化' in label or '发送' in label:
        width, height = 0.3, 0.1
        color = 'lightblue'
    elif '正常响应' in label:
        width, height = 0.25, 0.1
        color = 'lightgreen'
    elif '异常响应' in label:
        width, height = 0.25, 0.1
        color = 'lightcoral'
    else:
        width, height = 0.25, 0.1
        color = 'lightyellow'
    
    rect = patches.Rectangle((x-width/2, y-height/2), width, height, 
                             linewidth=2, edgecolor='black', 
                             facecolor=color, alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', fontsize=12, 
            family='SimSun', weight='bold')

# 绘制连接箭头
arrows = [
    # 爬虫请求初始化 → User-Agent随机化
    [(0.45, 0.85), (0.3, 0.8)],
    # 爬虫请求初始化 → IP代理选择
    [(0.55, 0.85), (0.7, 0.8)],
    # User-Agent随机化 → 请求速率控制
    [(0.3, 0.7), (0.45, 0.65)],
    # IP代理选择 → 请求速率控制
    [(0.7, 0.7), (0.55, 0.65)],
    # 请求速率控制 → 浏览器特征隐藏
    [(0.5, 0.55), (0.5, 0.5)],
    # 浏览器特征隐藏 → 请求发送
    [(0.5, 0.4), (0.5, 0.35)],
    # 请求发送 → 正常响应处理
    [(0.45, 0.25), (0.25, 0.2)],
    # 请求发送 → 异常响应智能重试
    [(0.55, 0.25), (0.75, 0.2)],
    # 异常响应智能重试 → 请求速率控制（重试循环）
    [(0.85, 0.15), (0.9, 0.45), (0.6, 0.6)]
]

# 箭头样式
arrow_style = patches.ArrowStyle("->", head_length=8, head_width=6)

for points in arrows:
    if len(points) == 2:  # 简单直线箭头
        start, end = points
        connection_style = "arc3,rad=0.0"
    else:  # 多段曲线箭头（用于重试循环）
        start, mid, end = points
        # 使用FancyArrowPatch创建曲线箭头
        connection_style = f"arc3,rad=0.3"
        arrow = patches.FancyArrowPatch(
            start, end, connectionstyle=connection_style,
            arrowstyle=arrow_style, color='black', linewidth=1.5)
        ax.add_patch(arrow)
        continue
    
    arrow = patches.FancyArrowPatch(
        start, end, connectionstyle=connection_style,
        arrowstyle=arrow_style, color='black', linewidth=1.5)
    ax.add_patch(arrow)

# 添加说明文字
annotations = [
    (0.2, 0.85, "请求准备"),
    (0.35, 0.73, "随机选择UA"),
    (0.68, 0.73, "随机选择代理"),
    (0.65, 0.6, "随机延迟"),
    (0.35, 0.45, "WebDriver特征隐藏"),
    (0.35, 0.3, "发起HTTP请求"),
    (0.2, 0.25, "正常响应"),
    (0.8, 0.25, "被拦截/失败"),
    (0.92, 0.3, "智能重试")
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