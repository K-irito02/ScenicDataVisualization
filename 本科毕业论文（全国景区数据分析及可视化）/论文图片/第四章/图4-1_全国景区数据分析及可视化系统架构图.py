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
fig, ax = plt.subplots(figsize=(10, 12))

# 定义颜色
colors = {
    'data_collection': '#B3D7FF',
    'data_storage': '#FFCCB3',
    'data_processing': '#CCE5CC',
    'application': '#E5CCFF',
    'user_interface': '#FFFFB3',
    'bg_light': '#F8F8F8',
    'border': '#666666',
    'arrow': '#333333'
}

# 定义层的厚度和间距 - 均匀化间距
standard_height = 1.5  # 标准层高度
small_height = 1.1     # 减小的层高度
gap = 0.8  # 层间间距

# 从顶部向下计算各层位置 - 整体上移
top_y = 11  # 上移顶部位置
collection_y = top_y - small_height
storage_y = collection_y - gap - standard_height
processing_y = storage_y - gap - standard_height
application_y = processing_y - gap - small_height
interface_y = application_y - gap - small_height

# 绘制数据采集层 - 减小高度
data_collection = patches.Rectangle((1, collection_y), 8, small_height, 
                                 facecolor=colors['data_collection'], 
                                 edgecolor=colors['border'], 
                                 linewidth=1.5, 
                                 alpha=0.8)
ax.add_patch(data_collection)
ax.text(5, collection_y + 0.75*small_height, '数据采集层', 
        horizontalalignment='center', 
        fontsize=12)
ax.text(5, collection_y + 0.25*small_height, 'Scrapy-Redis + Selenium', 
        horizontalalignment='center', 
        fontproperties=times_font)

# 绘制数据存储层
data_storage = patches.Rectangle((1, storage_y), 8, standard_height, 
                              facecolor=colors['data_storage'], 
                              edgecolor=colors['border'], 
                              linewidth=1.5, 
                              alpha=0.8)
ax.add_patch(data_storage)
ax.text(5, storage_y + 0.75*standard_height, '数据存储层', 
        horizontalalignment='center', 
        fontsize=12)

# 绘制数据存储层的子组件
storage_width = 2
storage_height = 0.8
storage_spacing = 0.5
storage_component_y = storage_y + 0.1  # 组件在存储层中的位置
storage_x_start = 1.8

# MongoDB
mongodb = patches.Rectangle((storage_x_start, storage_component_y), storage_width, storage_height, 
                         facecolor='white', 
                         edgecolor=colors['border'], 
                         linewidth=1, 
                         alpha=0.9)
ax.add_patch(mongodb)
ax.text(storage_x_start + storage_width/2, storage_component_y + storage_height/2, 'MongoDB', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontproperties=times_font)

# MySQL
mysql = patches.Rectangle((storage_x_start + storage_width + storage_spacing, storage_component_y), 
                         storage_width, storage_height, 
                         facecolor='white', 
                         edgecolor=colors['border'], 
                         linewidth=1, 
                         alpha=0.9)
ax.add_patch(mysql)
ax.text(storage_x_start + storage_width + storage_spacing + storage_width/2, 
        storage_component_y + storage_height/2, 'MySQL', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontproperties=times_font)

# Redis
redis = patches.Rectangle((storage_x_start + 2*storage_width + 2*storage_spacing, storage_component_y), 
                         storage_width, storage_height, 
                         facecolor='white', 
                         edgecolor=colors['border'], 
                         linewidth=1, 
                         alpha=0.9)
ax.add_patch(redis)
ax.text(storage_x_start + 2*storage_width + 2*storage_spacing + storage_width/2, 
        storage_component_y + storage_height/2, 'Redis', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontproperties=times_font)

# 绘制数据处理层
data_processing = patches.Rectangle((1, processing_y), 8, standard_height, 
                                 facecolor=colors['data_processing'], 
                                 edgecolor=colors['border'], 
                                 linewidth=1.5, 
                                 alpha=0.8)
ax.add_patch(data_processing)
ax.text(5, processing_y + 0.75*standard_height, '数据处理层', 
        horizontalalignment='center', 
        fontsize=12)

# 绘制数据处理层的子组件
processing_width = 1.65
processing_height = 0.7
processing_spacing = 0.13
processing_component_y = processing_y + 0.1  # 组件在处理层中的位置
processing_x_start = 1.4

# 地理信息处理
geo_proc = patches.Rectangle((processing_x_start, processing_component_y), 
                           processing_width, processing_height, 
                           facecolor='white', 
                           edgecolor=colors['border'], 
                           linewidth=1, 
                           alpha=0.9)
ax.add_patch(geo_proc)
ax.text(processing_x_start + processing_width/2, processing_component_y + processing_height/2, 
        '地理信息处理', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontsize=9)

# 票价分析
price_proc = patches.Rectangle((processing_x_start + processing_width + processing_spacing, 
                             processing_component_y), 
                             processing_width, processing_height, 
                             facecolor='white', 
                             edgecolor=colors['border'], 
                             linewidth=1, 
                             alpha=0.9)
ax.add_patch(price_proc)
ax.text(processing_x_start + processing_width + processing_spacing + processing_width/2, 
        processing_component_y + processing_height/2, 
        '票价分析', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontsize=9)

# 评论情感分析
sentiment_proc = patches.Rectangle((processing_x_start + 2*processing_width + 2*processing_spacing, 
                                 processing_component_y), 
                                 processing_width, processing_height, 
                                 facecolor='white', 
                                 edgecolor=colors['border'], 
                                 linewidth=1, 
                                 alpha=0.9)
ax.add_patch(sentiment_proc)
ax.text(processing_x_start + 2*processing_width + 2*processing_spacing + processing_width/2, 
        processing_component_y + processing_height/2, 
        '评论情感分析', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontsize=9)

# 交通数据处理
transport_proc = patches.Rectangle((processing_x_start + 3*processing_width + 3*processing_spacing, 
                                 processing_component_y), 
                                 processing_width, processing_height, 
                                 facecolor='white', 
                                 edgecolor=colors['border'], 
                                 linewidth=1, 
                                 alpha=0.9)
ax.add_patch(transport_proc)
ax.text(processing_x_start + 3*processing_width + 3*processing_spacing + processing_width/2, 
        processing_component_y + processing_height/2, 
        '交通数据处理', 
        horizontalalignment='center', 
        verticalalignment='center',
        fontsize=9)

# 绘制应用服务层 - 减小高度
application = patches.Rectangle((1, application_y), 8, small_height, 
                             facecolor=colors['application'], 
                             edgecolor=colors['border'], 
                             linewidth=1.5, 
                             alpha=0.8)
ax.add_patch(application)
ax.text(5, application_y + 0.75*small_height, '应用服务层', 
        horizontalalignment='center', 
        fontsize=12)
ax.text(5, application_y + 0.25*small_height, 'Django REST Framework API', 
        horizontalalignment='center', 
        fontproperties=times_font)

# 绘制用户界面层 - 减小高度
user_interface = patches.Rectangle((1, interface_y), 8, small_height, 
                                facecolor=colors['user_interface'], 
                                edgecolor=colors['border'], 
                                linewidth=1.5, 
                                alpha=0.8)
ax.add_patch(user_interface)
ax.text(5, interface_y + 0.75*small_height, '用户界面层', 
        horizontalalignment='center', 
        fontsize=12)
ax.text(5, interface_y + 0.25*small_height, 'Vue 3 + TypeScript + ECharts', 
        horizontalalignment='center', 
        fontproperties=times_font)

# 优化箭头
def add_arrow(ax, x1, y1, x2, y2, width=0.01, curve_factor=0.1):
    # 创建箭头路径，优化曲线形状
    # 通过控制点使箭头更平滑
    verts = [
        (x1, y1),  # 起点
        (x1, y1 - curve_factor),  # 控制点1
        (x2, y2 + curve_factor),  # 控制点2
        (x2, y2),  # 终点
    ]
    codes = [
        path.Path.MOVETO,
        path.Path.CURVE4,
        path.Path.CURVE4,
        path.Path.CURVE4,
    ]
    
    # 绘制箭头主体
    arrow_path = path.Path(verts, codes)
    arrow_patch = patches.PathPatch(
        arrow_path, facecolor='none', edgecolor=colors['arrow'], linewidth=1.2, alpha=0.9)
    ax.add_patch(arrow_patch)
    
    # 添加箭头头部
    head_length = 0.12
    head_width = 0.08
    dx = 0
    dy = -head_length
    
    ax.arrow(x2, y2 + head_length, dx, dy,
             width=width, head_width=head_width, head_length=head_length,
             fc=colors['arrow'], ec=colors['arrow'], alpha=0.9)

# 绘制自下而上的箭头（用于用户界面层 -> 应用服务层）
def add_up_arrow(ax, x1, y1, x2, y2, width=0.01, curve_factor=0.1):
    # 创建向上的箭头路径
    verts = [
        (x1, y1),  # 起点
        (x1, y1 + curve_factor),  # 控制点1
        (x2, y2 - curve_factor),  # 控制点2
        (x2, y2),  # 终点
    ]
    codes = [
        path.Path.MOVETO,
        path.Path.CURVE4,
        path.Path.CURVE4,
        path.Path.CURVE4,
    ]
    
    # 绘制箭头主体
    arrow_path = path.Path(verts, codes)
    arrow_patch = patches.PathPatch(
        arrow_path, facecolor='none', edgecolor=colors['arrow'], linewidth=1.2, alpha=0.9)
    ax.add_patch(arrow_patch)
    
    # 添加箭头头部
    head_length = 0.12
    head_width = 0.08
    dx = 0
    dy = head_length
    
    ax.arrow(x2, y2 - head_length, dx, dy,
             width=width, head_width=head_width, head_length=head_length,
             fc=colors['arrow'], ec=colors['arrow'], alpha=0.9)

# 添加各层之间的连接箭头 - 箭头恰好碰到方框边缘
# 数据采集层 -> 数据存储层
add_arrow(ax, 3, collection_y, 3, storage_y + standard_height)  
add_arrow(ax, 5, collection_y, 5, storage_y + standard_height)
add_arrow(ax, 7, collection_y, 7, storage_y + standard_height)

# 数据存储层 -> 数据处理层
add_arrow(ax, 3, storage_y, 3, processing_y + standard_height)  
add_arrow(ax, 5, storage_y, 5, processing_y + standard_height)
add_arrow(ax, 7, storage_y, 7, processing_y + standard_height)

# 数据处理层 -> 应用服务层
add_arrow(ax, 3, processing_y, 3, application_y + small_height)  
add_arrow(ax, 5, processing_y, 5, application_y + small_height)
add_arrow(ax, 7, processing_y, 7, application_y + small_height)

# 应用服务层 -> 用户界面层（从上到下）
add_arrow(ax, 3, application_y, 3, interface_y + small_height)  
add_arrow(ax, 5, application_y, 5, interface_y + small_height)
add_arrow(ax, 7, application_y, 7, interface_y + small_height)

# 用户界面层 -> 应用服务层（从下到上，修正方向）
add_up_arrow(ax, 4, interface_y + small_height, 4, application_y)  # 修正方向：从下到上
add_up_arrow(ax, 6, interface_y + small_height, 6, application_y)  # 修正方向：从下到上

# 设置坐标轴范围 - 调整坐标范围适应新的图形位置
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)

# 移除坐标轴
ax.axis('off')

plt.tight_layout()

# 保存图像
plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')

# 显示交互式窗口
plt.show()