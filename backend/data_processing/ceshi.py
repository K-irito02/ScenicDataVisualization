import pymongo
import json

# 连接到 MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["scenic_area"]
collection = db["china_attractions_copy"]

# 查询并统计字段的不同数据种类及其数量
field_name = "deep_wetland_level"  # 替换为实际字段名
pipeline = [
    {"$group": {"_id": "$" + field_name, "count": {"$sum": 1}}}
]

results = list(collection.aggregate(pipeline))

# 将结果转换为字典格式
output = {result["_id"]: result["count"] for result in results}

# 将结果保存为 JSON 文件
with open("湿地级别.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("统计结果已保存到 json 文件中。")





# 假设你要查找没有 'deep_cultural_relic_protection_unit' 字段的文档
# field_name = "deep_cultural_relic_protection_unit"

# # 查询没有该字段的文档
# missing_field_docs = collection.find({field_name: {"$exists": False}})

# # 查询该字段为：xxx 的文档
# missing_field_docs = collection.find({field_name: "xxx"})

# # 打印结果
# for doc in missing_field_docs:
#     print(doc)