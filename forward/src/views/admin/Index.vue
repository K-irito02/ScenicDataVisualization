<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo-container">
        <img src="/vite.svg" alt="景区数据可视化" class="logo" />
        <h2>景区管理系统</h2>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF">
        
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item index="/admin/records">
          <el-icon><DataAnalysis /></el-icon>
          <span>记录管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>返回前台</span>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div class="navbar">
        <div class="left">
          <el-icon class="hamburger" @click="toggleSidebar"><Expand /></el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="right">
          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="action-icon"><FullScreen /></el-icon>
          </el-tooltip>
          
          <el-dropdown trigger="click">
            <div class="avatar-container">
              <el-avatar size="small" src="https://example.com/admin-avatar.jpg"></el-avatar>
              <span class="username">管理员</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item>修改密码</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 页面内容 -->
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  User,
  Expand,
  FullScreen,
  HomeFilled
} from '@element-plus/icons-vue'

const route = useRoute()

// 侧边栏折叠状态
const sidebarCollapse = ref(false)

// 切换侧边栏展开/折叠
const toggleSidebar = () => {
  sidebarCollapse.value = !sidebarCollapse.value
}

// 当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 当前路由名称
const currentRoute = computed(() => {
  const routeName = {
    '/admin/users': '用户管理',
    '/admin/records': '记录管理',
    '/dashboard': '返回前台'
  }
  return routeName[route.path as keyof typeof routeName] || '首页'
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  width: 100%;
}

.sidebar {
  width: 210px;
  height: 100%;
  background-color: #304156;
  overflow-y: auto;
  transition: width 0.3s;
}

.sidebar.collapse {
  width: 64px;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #2b3649;
}

.logo {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.logo-container h2 {
  color: white;
  font-size: 16px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
}

.menu {
  border-right: none;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.navbar {
  height: 50px;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left {
  display: flex;
  align-items: center;
}

.hamburger {
  padding: 0 15px;
  cursor: pointer;
  font-size: 20px;
}

.right {
  display: flex;
  align-items: center;
}

.action-icon {
  font-size: 18px;
  padding: 0 10px;
  cursor: pointer;
  color: #606266;
}

.avatar-container {
  cursor: pointer;
  margin-left: 15px;
  display: flex;
  align-items: center;
}

.username {
  margin-left: 8px;
  font-size: 14px;
  color: #606266;
}

.app-main {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: #f0f2f5;
}
</style> 