const fs = require('fs');
const mysql = require('mysql2/promise');
const path = require('path');

// 读取配置文件
const configPath = path.join(__dirname, 'HieTic_and_SceAr.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 建立数据库连接
async function createConnection(dbName) {
  const connectionInfo = config.connections.find(conn => conn.name === dbName);
  
  if (!connectionInfo) {
    console.error(`找不到数据库 "${dbName}" 的配置信息`);
    return null;
  }
  
  try {
    const connection = await mysql.createConnection({
      host: connectionInfo.host,
      port: connectionInfo.port,
      user: connectionInfo.user,
      password: connectionInfo.password,
      database: connectionInfo.database
    });
    console.log(`成功连接到 ${dbName} 数据库`);
    return connection;
  } catch (error) {
    console.error(`连接到 ${dbName} 数据库时出错:`, error);
    return null;
  }
}

// 功能1: 查看数据库中的所有表
async function showTables(dbName) {
  const connection = await createConnection(dbName);
  if (!connection) return;
  
  try {
    const [rows] = await connection.execute('SHOW TABLES');
    console.log(`${dbName} 数据库中的表:`);
    rows.forEach((row, index) => {
      console.log(`${index + 1}. ${Object.values(row)[0]}`);
    });
    return rows;
  } catch (error) {
    console.error('查询表时出错:', error);
  } finally {
    await connection.end();
  }
}

// 功能2: 查看指定表的结构
async function describeTable(dbName, tableName) {
  const connection = await createConnection(dbName);
  if (!connection) return;
  
  try {
    const [rows] = await connection.execute(`DESCRIBE ${tableName}`);
    console.log(`表 ${tableName} 的结构:`);
    console.table(rows);
    return rows;
  } catch (error) {
    console.error(`查询表 ${tableName} 结构时出错:`, error);
  } finally {
    await connection.end();
  }
}

// 功能3: 查看指定表的数据
async function queryTable(dbName, tableName, limit = 10) {
  const connection = await createConnection(dbName);
  if (!connection) return;
  
  try {
    const [rows] = await connection.execute(`SELECT * FROM ${tableName} LIMIT ${limit}`);
    console.log(`表 ${tableName} 的数据 (限制 ${limit} 条):`);
    console.table(rows);
    return rows;
  } catch (error) {
    console.error(`查询表 ${tableName} 数据时出错:`, error);
  } finally {
    await connection.end();
  }
}

// 命令行参数处理
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const dbName = args[1];
  
  if (!command || !dbName) {
    console.log('用法:');
    console.log('node db_operations.js show-tables <数据库名>');
    console.log('node db_operations.js describe-table <数据库名> <表名>');
    console.log('node db_operations.js query-table <数据库名> <表名> [限制数量]');
    return;
  }
  
  switch (command) {
    case 'show-tables':
      await showTables(dbName);
      break;
    case 'describe-table':
      const tableName1 = args[2];
      if (!tableName1) {
        console.error('需要提供表名');
        return;
      }
      await describeTable(dbName, tableName1);
      break;
    case 'query-table':
      const tableName2 = args[2];
      const limit = parseInt(args[3]) || 10;
      if (!tableName2) {
        console.error('需要提供表名');
        return;
      }
      await queryTable(dbName, tableName2, limit);
      break;
    default:
      console.error('未知命令:', command);
      break;
  }
}

main().catch(console.error); 