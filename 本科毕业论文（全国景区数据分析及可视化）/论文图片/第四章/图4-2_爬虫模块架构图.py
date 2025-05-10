import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import numpy as np

# 设置中文字体和英文字体
plt.rcParams['font.sans-serif'] = ['SimSun']  # 设置中文字体为宋体
plt.rcParams['axes.unicode_minus'] = False    # 正确显示负号
plt.rcParams['font.size'] = 11  # 设置为五号字体大小

# 设置Times New Roman字体用于英文和数字
times_font = fm.FontProperties(family='Times New Roman', size=11)

# 创建图形和坐标轴
fig, ax = plt.subplots(figsize=(10, 8))

# 定义颜色
colors = {
    'master': '#B3D7FF',
    'worker': '#FFCCB3',
    'redis': '#CCE5CC',
    'mongodb': '#E5CCFF',
    'component': '#FFFFB3',
    'bg_light': '#F8F8F8',
    'border': '#666666',
    'arrow': '#333333'
}

# 绘制主背景
main_bg = patches.Rectangle((0.5, 0.5), 9, 7, 
                         facecolor=colors['bg_light'], 
                         edgecolor=colors['border'], 
                         linewidth=1.5, 
                         alpha=0.3)
ax.add_patch(main_bg)

# 绘制标题
ax.text(5, 7.7, '爬虫子系统架构图', 
        horizontalalignment='center', 
        fontsize=14, 
        fontweight='bold')

# 绘制Redis服务器
redis_server = patches.Rectangle((4, 4), 2, 1, 
                              facecolor=colors['redis'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(redis_server)
ax.text(5, 4.7, 'Redis服务器', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(5, 4.3, 'Request Queues / Duplication Filter', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 绘制MongoDB服务器
mongodb_server = patches.Rectangle((4, 1.5), 2, 1, 
                                facecolor=colors['mongodb'], 
                                edgecolor=colors['border'], 
                                linewidth=1.5, 
                                alpha=0.8)
ax.add_patch(mongodb_server)
ax.text(5, 2.2, 'MongoDB服务器', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(5, 1.8, 'Data Storage', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 绘制主节点
master_node = patches.Rectangle((1, 6), 2, 1, 
                              facecolor=colors['master'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(master_node)
ax.text(2, 6.7, '爬虫主节点', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(2, 6.3, 'Task Initialization', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 绘制从节点
worker_node1 = patches.Rectangle((1, 3), 2, 1, 
                              facecolor=colors['worker'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(worker_node1)
ax.text(2, 3.7, '爬虫工作节点1', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(2, 3.3, 'City List Crawler', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

worker_node2 = patches.Rectangle((7, 6), 2, 1, 
                              facecolor=colors['worker'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(worker_node2)
ax.text(8, 6.7, '爬虫工作节点2', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(8, 6.3, 'Attraction List Crawler', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

worker_node3 = patches.Rectangle((7, 3), 2, 1, 
                              facecolor=colors['worker'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(worker_node3)
ax.text(8, 3.7, '爬虫工作节点3', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(8, 3.3, 'Detail Page Crawler', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 绘制组件块
# 主节点组件
master_components = patches.Rectangle((0.7, 4.8), 2.6, 1, 
                                   facecolor=colors['component'], 
                                   edgecolor=colors['border'], 
                                   linewidth=1, 
                                   alpha=0.8)
ax.add_patch(master_components)
ax.text(2, 5.3, '主节点组件', 
        horizontalalignment='center', 
        fontsize=10)
ax.text(2, 5.0, 'URL种子生成器 / 任务分发器', 
        horizontalalignment='center', 
        fontsize=9)

# 工作节点组件
worker_components = patches.Rectangle((6.7, 4.8), 2.6, 1, 
                                   facecolor=colors['component'], 
                                   edgecolor=colors['border'], 
                                   linewidth=1, 
                                   alpha=0.8)
ax.add_patch(worker_components)
ax.text(8, 5.3, '工作节点组件', 
        horizontalalignment='center', 
        fontsize=10)
ax.text(8, 5.0, 'Spider / Middleware / Pipeline', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 监控组件
monitor_components = patches.Rectangle((3.7, 6), 2.6, 1, 
                                    facecolor=colors['component'], 
                                    edgecolor=colors['border'], 
                                    linewidth=1, 
                                    alpha=0.8)
ax.add_patch(monitor_components)
ax.text(5, 6.5, '监控和控制组件', 
        horizontalalignment='center', 
        fontsize=10)
ax.text(5, 6.2, 'run_db_crawler.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 数据导出组件
export_components = patches.Rectangle((3.7, 2.7), 2.6, 1, 
                                   facecolor=colors['component'], 
                                   edgecolor=colors['border'], 
                                   linewidth=1, 
                                   alpha=0.8)
ax.add_patch(export_components)
ax.text(5, 3.2, '数据导出组件', 
        horizontalalignment='center', 
        fontsize=10)
ax.text(5, 2.9, 'export_data.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 绘制箭头连接
def draw_arrow(ax, x1, y1, x2, y2, color=colors['arrow'], width=0.05, head_width=0.15, head_length=0.1, ls='-'):
    ax.arrow(x1, y1, x2-x1, y2-y1, 
             width=width, head_width=head_width, head_length=head_length, 
             fc=color, ec=color, length_includes_head=True, linestyle=ls)

# 主节点到Redis
draw_arrow(ax, 2.5, 6.2, 3.9, 4.5)

# Redis到工作节点1
draw_arrow(ax, 3.9, 3.5, 3.1, 3.5)

# Redis到工作节点2
draw_arrow(ax, 6.1, 4.5, 7.5, 6.2)

# Redis到工作节点3
draw_arrow(ax, 6.1, 3.5, 6.9, 3.5)

# 工作节点1到Redis
draw_arrow(ax, 3.1, 3.3, 3.9, 3.3)

# 工作节点2到Redis
draw_arrow(ax, 7.5, 6.0, 6.1, 4.3)

# 工作节点3到Redis
draw_arrow(ax, 6.9, 3.3, 6.1, 3.3)

# 工作节点1到MongoDB
draw_arrow(ax, 2, 2.9, 3.9, 2)

# 工作节点3到MongoDB
draw_arrow(ax, 8, 2.9, 6.1, 2)

# 监控组件到主节点
draw_arrow(ax, 3.9, 6.5, 3.1, 6.5)

# 监控组件到工作节点2
draw_arrow(ax, 6.3, 6.5, 6.9, 6.5)

# 监控组件到Redis
draw_arrow(ax, 5, 5.9, 5, 5.1)

# 数据导出组件到MongoDB
draw_arrow(ax, 5, 2.6, 5, 2.1)

# 设置坐标轴范围
ax.set_xlim(0, 10)
ax.set_ylim(1, 8)

# 移除坐标轴
ax.axis('off')

plt.tight_layout()

# 保存图像
plt.savefig('crawler_architecture.png', dpi=300, bbox_inches='tight')

# 返回图像路径
'crawler_architecture.png'