#!/usr/bin/env node

/**
 * 数据库切换工具
 * 使用方法: node switch_db.js [数据库名称]
 * 例如: node switch_db.js scenic_area
 */

const { execSync } = require('child_process');
const readline = require('readline');

// 数据库配置
const configs = {
  'scenic_area': {
    mysqlHost: "localhost",
    mysqlPort: 3306,
    mysqlUser: "root",
    mysqlPassword: "3143285505",
    mysqlDatabase: "scenic_area"
  },
  'hierarchy_ticketanalysis': {
    mysqlHost: "localhost",
    mysqlPort: 3306,
    mysqlUser: "root",
    mysqlPassword: "3143285505",
    mysqlDatabase: "hierarchy_ticketanalysis"
  }
};

// 获取命令行参数
const dbName = process.argv[2];

// 如果没有提供数据库名称，显示菜单
if (!dbName) {
  console.log('请选择要连接的数据库:');
  console.log('1. scenic_area');
  console.log('2. hierarchy_ticketanalysis');
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  rl.question('请输入选项 (1 或 2): ', (answer) => {
    let selectedDb;
    if (answer === '1') {
      selectedDb = 'scenic_area';
    } else if (answer === '2') {
      selectedDb = 'hierarchy_ticketanalysis';
    } else {
      console.log('无效的选项！');
      rl.close();
      return;
    }
    
    connectToDatabase(selectedDb);
    rl.close();
  });
} else {
  // 直接连接到指定的数据库
  if (configs[dbName]) {
    connectToDatabase(dbName);
  } else {
    console.log(`错误: 未知的数据库 "${dbName}"`);
    console.log('可用的数据库: scenic_area, hierarchy_ticketanalysis');
  }
}

/**
 * 连接到指定的数据库
 */
function connectToDatabase(dbName) {
  const config = configs[dbName];
  if (!config) {
    console.log(`错误: 未知的数据库 "${dbName}"`);
    return;
  }
  
  console.log(`正在连接到 ${dbName} 数据库...`);
  
  try {
    const configJson = JSON.stringify(config);
    const command = `npx -y @smithery/cli@latest run mysql-mcp-server --client cursor --config '${configJson}'`;
    
    console.log('执行命令:', command);
    execSync(command, { stdio: 'inherit' });
  } catch (error) {
    console.error('连接失败:', error.message);
  }
}