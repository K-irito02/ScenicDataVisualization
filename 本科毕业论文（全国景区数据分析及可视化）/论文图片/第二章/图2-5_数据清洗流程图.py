# 图2-5 数据清洗流程图
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))

# 定义流程步骤
steps = [
    (0.5, 0.9, "原始景区数据"),
    (0.5, 0.75, "文本预处理"),
    (0.5, 0.6, "结构化处理"),
    (0.25, 0.45, "景区基础信息处理"),
    (0.75, 0.45, "评论文本处理"),
    (0.5, 0.3, "数据集成"),
    (0.5, 0.15, "清洗后景区数据")
]

# 绘制流程步骤
for i, (x, y, label) in enumerate(steps):
    if i == 0 or i == len(steps) - 1:  # 第一个和最后一个框使用椭圆
        ellipse = patches.Ellipse((x, y), 0.3, 0.1, 
                                 linewidth=2, edgecolor='black', 
                                 facecolor='lightgreen', alpha=0.7)
        ax.add_patch(ellipse)
    else:  # 中间步骤使用矩形
        rect = patches.Rectangle((x-0.2, y-0.05), 0.4, 0.1, 
                                linewidth=2, edgecolor='black', 
                                facecolor='lightblue', alpha=0.7)
        ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', fontsize=12, 
            family='SimSun', weight='bold')

# 绘制箭头连接
for i in range(len(steps) - 1):
    if i < 2:  # 前两个是直线连接配置
        ax.arrow(steps[i][0], steps[i][1]-0.05, 0, steps[i+1][1]-steps[i][1]+0.11,
                head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)
    if i == 2:  # 第三个是直线连接配置
        ax.arrow(steps[i][0], steps[i][1]-0.05, 0, steps[i+1][1]-steps[i][1]-0.04,
                head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)
    elif i == 3:  # 从"结构化处理"到两个分支
        ax.arrow(steps[2][0], steps[2][1]-0.05, -0.25, steps[3][1]-steps[2][1]+0.1,
                head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)
        ax.arrow(steps[2][0], steps[2][1]-0.05, 0.25, steps[4][1]-steps[2][1]+0.1,
                head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)
    else:  # 两个分支汇合到"数据集成"
        ax.arrow(steps[3][0], steps[3][1]-0.05, 0.23, steps[5][1]-steps[3][1]+0.1,
                head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)
        ax.arrow(steps[4][0], steps[4][1]-0.05, -0.23, steps[5][1]-steps[4][1]+0.1,
                head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)

# 最后一个连接
ax.arrow(steps[5][0], steps[5][1]-0.05, 0, steps[6][1]-steps[5][1]+0.11,
        head_width=0.01, head_length=0.01, fc='black', ec='black', linewidth=1)

# 添加处理说明
explanations = [
    (0.12, 0.75, "• 去除URL、HTML标签\n• 繁体转简体\n• 特殊字符处理"),
    (0.72, 0.6, "• 标准化数据格式\n• 统一数值单位\n• 缺失值处理"),
    (0.09, 0.36, "• 地理位置标准化\n• 景区级别提取\n• 票价格式化"),
    (0.9, 0.36, "• 分词与停用词过滤\n• 繁简转换\n• 标点符号处理"),
    (0.15, 0.28, "• 多源数据合并\n• 冗余数据去除\n• 数据一致性检查")
]

for x, y, text in explanations:
    ax.text(x, y, text, ha='left', va='center', fontsize=10, 
            family='SimSun', style='italic', 
            bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.5'))

# 设置图表
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.show()