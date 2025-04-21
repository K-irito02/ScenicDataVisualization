# 图2-3 分布式爬虫架构图
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# 创建画布
fig, ax = plt.subplots(figsize=(12, 8))

# 定义组件
components = {
    "redis": (0.5, 0.7, 0.3, 0.15, "Redis服务器\n(URLs队列与结果存储)"),
    "master": (0.2, 0.4, 0.25, 0.15, "主节点\n(城市列表爬虫)"),
    "worker1": (0.5, 0.4, 0.25, 0.15, "工作节点1\n(景点列表爬虫)"),
    "worker2": (0.8, 0.4, 0.25, 0.15, "工作节点2\n(景点详情爬虫)"),
    "db": (0.5, 0.15, 0.3, 0.15, "MongoDB\n(最终数据存储)")
}

# 绘制组件
for key, (x, y, w, h, label) in components.items():
    if key == "redis":
        color = 'lightcoral'
    elif key == "db":
        color = 'lightgreen'
    else:
        color = 'lightblue'
    
    rect = patches.Rectangle((x-w/2, y-h/2), w, h, 
                             linewidth=2, edgecolor='black', 
                             facecolor=color, alpha=0.7)
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center', fontsize=12, 
            family='SimSun', weight='bold')

# 绘制连接线
connections = [
    # 主节点与Redis之间的连接
    ("master", "redis", "存储城市URL\n获取任务状态"),
    # 工作节点1与Redis之间的连接
    ("worker1", "redis", "存储景点URL\n获取城市URL"),
    # 工作节点2与Redis之间的连接
    ("worker2", "redis", "存储景点详情\n获取景点URL"),
    # Redis与数据库之间的连接
    ("redis", "db", "数据持久化存储")
]

# 绘制连接
for start_key, end_key, label in connections:
    start_x, start_y = components[start_key][0], components[start_key][1]
    end_x, end_y = components[end_key][0], components[end_key][1]
    
    # 计算连接点（考虑组件的大小）
    if start_y < end_y:  # 从下到上
        start_point = (start_x, start_y + components[start_key][3]/2)
        end_point = (end_x, end_y - components[end_key][3]/2)
    else:  # 从上到下
        start_point = (start_x, start_y - components[start_key][3]/2)
        end_point = (end_x, end_y + components[end_key][3]/2)
    
    # 绘制箭头
    arrow = patches.FancyArrowPatch(
        start_point, end_point, connectionstyle="arc3,rad=0.1",
        arrowstyle="->", color='black', linewidth=1.5, mutation_scale=15)
    ax.add_patch(arrow)
    
    # 添加标签
    mid_x = (start_point[0] + end_point[0]) / 2
    mid_y = (start_point[1] + end_point[1]) / 2
    
    # 根据连接情况调整标签位置
    if (start_key == "redis" and end_key == "db"):
        # 调整"数据持久化存储"的位置到箭头上
        mid_x = (start_point[0] + end_point[0]) / 2
        mid_y = (start_point[1] + end_point[1]) / 2 - 0.15  # 稍微向下移动
    elif (start_key == "worker1" and end_key == "redis"):
        # 调整"存储景点URL\n获取城市URL"的位置，避免覆盖其他线
        mid_x += 0.05  # 向右移动
    elif (start_key == "worker2" and end_key == "redis"):
        # 调整"存储景点详情\n获取景点URL"的位置，避免覆盖其他线
        mid_x += 0.05  # 向右移动
        
    ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=10, 
            family='SimSun', bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))

# 添加队列说明
queue_info = [
    (0.4, 0.75, "城市URL队列"),
    (0.5, 0.75, "景点URL队列"),
    (0.6, 0.75, "景点详情"),
]

for x, y, text in queue_info:
    ax.text(x, y, text, ha='center', va='center', fontsize=10, 
            family='SimSun', style='italic', 
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))

# 设置图表
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.show()