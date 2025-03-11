# 打开文件并读取内容
with open("C:\\ScenicDataVisualization\\backend\\data_processing\\程度副词.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 替换每一行中的制表符为四个空格
updated_lines = [line.replace('\\t', '    ') for line in lines]

# 将更新后的内容写回文件
with open("C:\\ScenicDataVisualization\\backend\\data_processing\\程度副词.txt", 'w', encoding='utf-8') as file:
    file.writelines(updated_lines)

print("制表符已替换为四个空格。")