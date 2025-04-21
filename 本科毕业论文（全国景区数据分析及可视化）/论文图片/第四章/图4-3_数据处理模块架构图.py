import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
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
    'mongodb': '#B3D7FF',
    'mysql': '#FFCCB3',
    'processing': '#CCE5CC',
    'analysis': '#E5CCFF',
    'module': '#FFFFB3',
    'bg_light': '#F8F8F8',
    'border': '#666666',
    'arrow': '#333333'
}

# 绘制MongoDB数据库
mongodb = patches.Rectangle((1, 6.5), 2, 0.8, 
                         facecolor=colors['mongodb'], 
                         edgecolor=colors['border'], 
                         linewidth=1.5, 
                         alpha=0.8)
ax.add_patch(mongodb)
ax.text(2, 6.9, 'MongoDB数据库', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(2, 6.7, '爬虫原始数据', 
        horizontalalignment='center', 
        fontsize=9)

# 绘制MySQL数据库
mysql = patches.Rectangle((7, 6.5), 2, 0.8, 
                       facecolor=colors['mysql'], 
                       edgecolor=colors['border'], 
                       linewidth=1.5, 
                       alpha=0.8)
ax.add_patch(mysql)
ax.text(8, 6.9, 'MySQL数据库', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(8, 6.7, '结构化分析结果', 
        horizontalalignment='center', 
        fontsize=9)

# 绘制数据预处理层
preprocessing = patches.Rectangle((1, 5), 8, 0.8, 
                               facecolor=colors['processing'], 
                               edgecolor=colors['border'], 
                               linewidth=1.5, 
                               alpha=0.8)
ax.add_patch(preprocessing)
ax.text(5, 5.4, '数据预处理层', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(5, 5.2, '缺失值处理 / 异常值检测 / 格式统一 / 数据标准化', 
        horizontalalignment='center', 
        fontsize=9)

# 绘制特征提取层
feature_extraction = patches.Rectangle((1, 4), 8, 0.8, 
                                    facecolor=colors['analysis'], 
                                    edgecolor=colors['border'], 
                                    linewidth=1.5, 
                                    alpha=0.8)
ax.add_patch(feature_extraction)
ax.text(5, 4.4, '特征提取层', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(5, 4.2, '地理信息提取 / 票价解析 / 时间规范化 / 情感分析 / 交通分析', 
        horizontalalignment='center', 
        fontsize=9)

# 绘制数据分析层
data_analysis = patches.Rectangle((1, 3), 8, 0.8, 
                               facecolor=colors['processing'], 
                               edgecolor=colors['border'], 
                               linewidth=1.5, 
                               alpha=0.8)
ax.add_patch(data_analysis)
ax.text(5, 3.4, '数据分析层', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(5, 3.2, '统计分析 / 分类聚类 / 相关性分析 / 分布特征分析', 
        horizontalalignment='center', 
        fontsize=9)

# 绘制数据整合层
data_integration = patches.Rectangle((1, 2), 8, 0.8, 
                                  facecolor=colors['analysis'], 
                                  edgecolor=colors['border'], 
                                  linewidth=1.5, 
                                  alpha=0.8)
ax.add_patch(data_integration)
ax.text(5, 2.4, '数据整合层', 
        horizontalalignment='center', 
        fontsize=11)
ax.text(5, 2.2, '汇总分析结果 / 构建关联关系 / 生成汇总表', 
        horizontalalignment='center', 
        fontsize=9)

# 绘制具体处理模块 - 左移所有方框
module_shift = 0.3  # 左移的距离

# 地理信息处理模块
geo_module = patches.Rectangle((0.8 - module_shift, 1), 1.6, 0.8, 
                            facecolor=colors['module'], 
                            edgecolor=colors['border'], 
                            linewidth=1.5, 
                            alpha=0.8)
ax.add_patch(geo_module)
ax.text(1.6 - module_shift, 1.4, '地理信息处理', 
        horizontalalignment='center', 
        fontsize=9)
ax.text(1.6 - module_shift, 1.2, 'scenic_spots.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 票价分析模块
price_module = patches.Rectangle((2.6 - module_shift, 1), 1.6, 0.8, 
                              facecolor=colors['module'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(price_module)
ax.text(3.4 - module_shift, 1.4, '票价分析', 
        horizontalalignment='center', 
        fontsize=9)
ax.text(3.4 - module_shift, 1.2, 'ticket_prices.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 评论处理模块
comment_module = patches.Rectangle((4.4 - module_shift, 1), 1.6, 0.8, 
                                facecolor=colors['module'], 
                                edgecolor=colors['border'], 
                                linewidth=1.5, 
                                alpha=0.8)
ax.add_patch(comment_module)
ax.text(5.2 - module_shift, 1.4, '评论情感分析', 
        horizontalalignment='center', 
        fontsize=9)
ax.text(5.2 - module_shift, 1.2, 'comment_handling.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 交通分析模块
transport_module = patches.Rectangle((6.2 - module_shift, 1), 1.6, 0.8, 
                                  facecolor=colors['module'], 
                                  edgecolor=colors['border'], 
                                  linewidth=1.5, 
                                  alpha=0.8)
ax.add_patch(transport_module)
ax.text(7 - module_shift, 1.4, '交通方式分析', 
        horizontalalignment='center', 
        fontsize=9)
ax.text(7 - module_shift, 1.2, 'transport_mode.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 数据集成模块
integration_module = patches.Rectangle((8 - module_shift, 1), 1.6, 0.8, 
                                    facecolor=colors['module'], 
                                    edgecolor=colors['border'], 
                                    linewidth=1.5, 
                                    alpha=0.8)
ax.add_patch(integration_module)
ax.text(8.8 - module_shift, 1.4, '数据集成', 
        horizontalalignment='center', 
        fontsize=9)
ax.text(8.8 - module_shift, 1.2, 'summary-table.py', 
        horizontalalignment='center', 
        fontsize=9,
        fontproperties=times_font)

# 绘制箭头连接 - 修改箭头参数使其变细
def draw_arrow(ax, x1, y1, x2, y2, color=colors['arrow'], width=0.03, head_width=0.1, head_length=0.07, ls='-'):
    ax.arrow(x1, y1, x2-x1, y2-y1, 
             width=width, head_width=head_width, head_length=head_length, 
             fc=color, ec=color, length_includes_head=True, linestyle=ls)

# MongoDB到数据预处理层
draw_arrow(ax, 2, 6.5, 2, 5.8)

# 数据预处理层到特征提取层
draw_arrow(ax, 3, 5, 3, 4.8)
draw_arrow(ax, 5, 5, 5, 4.8)
draw_arrow(ax, 7, 5, 7, 4.8)

# 特征提取层到数据分析层
draw_arrow(ax, 3, 4, 3, 3.8)
draw_arrow(ax, 5, 4, 5, 3.8)
draw_arrow(ax, 7, 4, 7, 3.8)

# 数据分析层到数据整合层
draw_arrow(ax, 3, 3, 3, 2.8)
draw_arrow(ax, 5, 3, 5, 2.8)
draw_arrow(ax, 7, 3, 7, 2.8)

# 数据整合层到具体处理模块 - 调整箭头终点位置
draw_arrow(ax, 1.6 - module_shift, 2, 1.6 - module_shift, 1.8)
draw_arrow(ax, 3.4 - module_shift, 2, 3.4 - module_shift, 1.8)
draw_arrow(ax, 5.2 - module_shift, 2, 5.2 - module_shift, 1.8)
draw_arrow(ax, 7 - module_shift, 2, 7 - module_shift, 1.8)
draw_arrow(ax, 8.8 - module_shift, 2, 8.8 - module_shift, 1.8)

# 数据整合层到MySQL
draw_arrow(ax, 8, 2.4, 8, 6.5)

# 设置坐标轴范围
ax.set_xlim(0, 10)
ax.set_ylim(0.5, 8)

# 移除坐标轴
ax.axis('off')

plt.tight_layout()

# 显示图像
plt.show()