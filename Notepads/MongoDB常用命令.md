# MongoDB 常用命令

## 基本命令

- **启动MongoDB服务**：
  ```bash
  mongod
  ```

- **连接到MongoDB**：
  ```bash
  mongo
  ```

## 数据库操作

- **显示所有数据库**：
  ```bash
  show dbs
  ```

- **使用或创建数据库**：
  ```bash
  use database_name
  ```

- **删除数据库**：
  ```javascript
  db.dropDatabase()
  ```

## 集合操作

- **查询集合中name字段为"鸽子窝公园"的文档，并查看与其同一文档下的transport字段**
```bash
db.collection_name.find(
  { name: "鸽子窝公园" },
  { transport: 1, _id: 0 }
)
```

流溪河国家森林公园

```bash
db.collection_name.find( {}, { ticket: 1, deep_ticket_price: 1, _id: 0 },
)
```

- **显示当前数据库中的集合**：
  ```bash
  show collections
  ```

- **创建集合**：
  ```javascript
  db.createCollection("collection_name")
  ```

- **删除集合**：
  ```javascript
  db.collection_name.drop()
  ```

## 文档操作

- **插入文档**：
  ```javascript
  db.collection_name.insert({ key: "value" })
  ```

- **查询文档**：
  ```javascript
  db.collection_name.find({ key: "value" })
  ```

- **更新文档**：
  ```javascript
  db.collection_name.update(
    { key: "value" },
    { $set: { key: "new_value" } }
  )
  ```

- **删除文档**：
  ```javascript
  db.collection_name.remove({ key: "value" })
  ```

## 索引操作

- **创建索引**：
  ```javascript
  db.collection_name.createIndex({ key: 1 })
  ```

- **查看集合的索引**：
  ```javascript
  db.collection_name.getIndexes()
  ```

- **删除索引**：
  ```javascript
  db.collection_name.dropIndex("index_name")
  ```

## 其他命令

- **查看当前数据库**：
  ```javascript
  db
  ```

- **查看帮助**：
  ```bash
  help
  ```