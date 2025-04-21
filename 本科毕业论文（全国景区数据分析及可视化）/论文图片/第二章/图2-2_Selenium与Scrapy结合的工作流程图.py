# 图2-2 Selenium与Scrapy结合的工作流程图
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path

# 创建画布
fig, ax = plt.subplots(figsize=(12, 8))

# 定义组件位置
components = [
    (0.25, 0.85, "Scrapy爬虫"),
    (0.75, 0.85, "Selenium中间件"),
    (0.25, 0.6, "静态内容请求"),
    (0.75, 0.6, "动态内容请求"),
    (0.25, 0.35, "静态网页解析"),
    (0.75, 0.35, "浏览器渲染引擎"),
    (0.5, 0.15, "数据处理管道")
]

# 绘制组件
for x, y, label in components:
    if "爬虫" in label or "管道" in label or "中间件" in label:
        width, height = 0.3, 0.15
        color = 'lightblue'
    else:
        width, height = 0.25, 0.15
        color = 'lightgreen'
    
    rect = patches.Rectangle((x-width/2, y-height/2), width, height, 
                             linewidth=2, edgecolor='black', 
                             facecolor=color, alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', fontsize=12, 
            family='SimSun', weight='bold')

# 绘制连接箭头
arrows = [
    # Scrapy爬虫 → 静态内容请求
    [(0.25, 0.77), (0.25, 0.68)],
    # Scrapy爬虫 → Selenium中间件 (需要JavaScript渲染)
    [(0.35, 0.85), (0.65, 0.85)],
    # Selenium中间件 → 动态内容请求
    [(0.75, 0.77), (0.75, 0.68)],
    # 静态内容请求 → 静态网页解析
    [(0.25, 0.52), (0.25, 0.43)],
    # 动态内容请求 → 浏览器渲染引擎
    [(0.75, 0.52), (0.75, 0.43)],
    # 静态网页解析 → 数据处理管道
    [(0.25, 0.27), (0.4, 0.18)],
    # 浏览器渲染引擎 → 数据处理管道
    [(0.75, 0.27), (0.6, 0.18)]
]

# 箭头样式
arrow_style = patches.ArrowStyle("->", head_length=8, head_width=6)

for start, end in arrows:
    arrow = patches.FancyArrowPatch(
        start, end, connectionstyle="arc3,rad=0.0",
        arrowstyle=arrow_style, color='black', linewidth=1.5)
    ax.add_patch(arrow)

# 添加说明文字
annotations = [
    (0.28, 0.75, "静态页面"),
    (0.5, 0.89, "动态页面"),
    (0.18, 0.65, "HTTP请求"),
    (0.82, 0.65, "WebDriver控制"),
    (0.18, 0.39, "XPath/CSS选择器"),
    (0.82, 0.39, "JavaScript执行"),
    (0.3, 0.23, "解析结果"),
    (0.7, 0.23, "渲染后内容")
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