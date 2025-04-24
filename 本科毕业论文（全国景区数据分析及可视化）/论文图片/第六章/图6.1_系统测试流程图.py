import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
import numpy as np
from matplotlib.patches import FancyArrowPatch
import os
import platform

# 设置中文字体支持
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# 定义字体
def get_font_properties():
    # 根据操作系统设置字体路径
    system = platform.system()
    
    if system == 'Windows':
        # Windows系统字体路径
        simsun_path = r'C:\Windows\Fonts\simsun.ttc'
        times_path = r'C:\Windows\Fonts\times.ttf'
    elif system == 'Darwin':  # macOS
        simsun_path = '/System/Library/Fonts/STHeiti Light.ttc'  # 可用的中文字体
        times_path = '/System/Library/Fonts/Times.ttc'
    else:  # Linux
        simsun_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'  # 可用的中文字体
        times_path = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
    
    # 尝试使用指定字体，如果失败则使用系统默认字体
    try:
        # 中文使用宋体(SimSun)，大小为五号（约10.5磅）
        chinese_font = FontProperties(fname=simsun_path, size=10.5)
        # 英文和数字使用Times New Roman
        english_font = FontProperties(fname=times_path, size=10.5)
    except:
        print("无法加载指定字体，使用系统默认字体")
        chinese_font = FontProperties(family='SimSun', size=10.5)
        english_font = FontProperties(family='Times New Roman', size=10.5)
    
    return chinese_font, english_font

def create_test_flow_diagram():
    # 获取字体
    chinese_font, english_font = get_font_properties()
    
    # 创建图形
    plt.figure(figsize=(10, 12), dpi=300)
    
    # 绘制图形背景为白色
    ax = plt.gca()
    ax.set_facecolor('white')
    
    # 定义测试流程各阶段的位置
    stages = [
        "准备阶段", 
        "单元测试阶段", 
        "集成测试阶段", 
        "系统测试阶段"
    ]
    
    # 定义每个阶段的子任务
    sub_tasks = {
        "准备阶段": [
            "构建测试环境", 
            "准备测试数据集", 
            "编写测试用例"
        ],
        "单元测试阶段": [
            "数据采集模块测试", 
            "数据处理模块测试", 
            "后端API模块测试", 
            "前端组件测试"
        ],
        "集成测试阶段": [
            "爬虫与数据处理集成测试", 
            "数据处理与后端集成测试", 
            "后端与前端集成测试"
        ],
        "系统测试阶段": [
            "功能测试", 
            "性能测试", 
            "用户体验测试"
        ]
    }
    
    # 计算布局位置
    y_positions = {}
    
    # 主阶段y位置
    stage_y_pos = {}
    total_height = len(stages) * 2
    current_y = total_height
    
    for i, stage in enumerate(stages):
        stage_y_pos[stage] = current_y
        y_step = 1.5
        current_y -= y_step
        
        # 子任务y位置
        subtasks = sub_tasks[stage]
        subtask_height = len(subtasks) * 0.8
        subtask_start_y = current_y - 0.3
        
        for j, subtask in enumerate(subtasks):
            y_positions[(stage, subtask)] = subtask_start_y - j * 0.8
        
        current_y -= subtask_height + 0.7
    
    # 绘制主流程节点和连线
    x_main = 2
    for i, stage in enumerate(stages):
        y = stage_y_pos[stage]
        
        # 绘制主阶段节点
        plt.plot(x_main, y, 'o', markersize=15, markerfacecolor='lightblue', 
                 markeredgecolor='navy', markeredgewidth=2)
        
        # 添加阶段文本
        plt.text(x_main + 0.3, y, stage, fontproperties=chinese_font, 
                 verticalalignment='center', horizontalalignment='left')
        
        # 绘制连接线
        if i < len(stages) - 1:
            next_y = stage_y_pos[stages[i+1]]
            plt.arrow(x_main, y - 0.2, 0, next_y - y + 0.4, head_width=0.1, 
                      head_length=0.2, fc='black', ec='black', linewidth=2)
    
    # 绘制子任务节点和连线
    x_sub = 5
    for stage in stages:
        subtasks = sub_tasks[stage]
        
        for j, subtask in enumerate(subtasks):
            y_sub = y_positions[(stage, subtask)]
            
            # 绘制子任务节点
            plt.plot(x_sub, y_sub, 's', markersize=10, markerfacecolor='lightyellow', 
                     markeredgecolor='darkgoldenrod', markeredgewidth=1.5)
            
            # 添加子任务文本
            plt.text(x_sub + 0.3, y_sub, subtask, fontproperties=chinese_font, 
                     verticalalignment='center', horizontalalignment='left')
            
            # 连接到主阶段
            if j == 0:
                y_main = stage_y_pos[stage]
                # 使用虚线连接主阶段和第一个子任务
                plt.plot([x_main + 0.15, x_sub - 0.1], [y_main, y_sub], 
                         'k--', linewidth=1.5, dashes=(5, 2))
            
            # 绘制子任务间的连线
            if j < len(subtasks) - 1:
                next_y_sub = y_positions[(stage, subtasks[j+1])]
                plt.arrow(x_sub, y_sub - 0.1, 0, next_y_sub - y_sub + 0.2, 
                          head_width=0.05, head_length=0.1, fc='darkgoldenrod', 
                          ec='darkgoldenrod', linewidth=1, linestyle='-')
    
    # 设置图形属性
    plt.title('全国景区数据分析及可视化系统测试流程图', fontproperties=chinese_font, fontsize=14)
    plt.grid(False)
    plt.axis('off')  # 不显示坐标轴
    
    # 创建输出目录（如果不存在）
    output_dir = './'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存图形
    plt.tight_layout()
    plt.savefig(f"{output_dir}/test_flow_diagram.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/test_flow_diagram.pdf", format='pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/test_flow_diagram.svg", format='svg', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"测试流程图已保存至 {output_dir} 目录下，格式包括PNG、PDF和SVG。")

if __name__ == "__main__":
    create_test_flow_diagram() 