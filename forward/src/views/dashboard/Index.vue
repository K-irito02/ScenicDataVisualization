<template>
  <div class="dashboard-container">
    <el-container>
      <el-aside width="220px">
        <div class="logo">
          <h2>景区数据可视化</h2>
        </div>
        <el-menu
          router
          :default-active="$route.path"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard/overview">
            <el-icon><DataLine /></el-icon>
            <span>总览</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/geographic">
            <el-icon><MapLocation /></el-icon>
            <span>地理分布</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/attribute">
            <el-icon><Connection /></el-icon>
            <span>属性关联</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/feedback">
            <el-icon><ChatDotRound /></el-icon>
            <span>用户反馈</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/identity">
            <el-icon><SetUp /></el-icon>
            <span>身份交叉</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/traffic">
            <el-icon><Van /></el-icon>
            <span>交通分析</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/search">
            <el-icon><Search /></el-icon>
            <span>景区搜索</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header>
          <div class="header-left">
            <el-icon class="toggle-sidebar" @click="toggleSidebar"><Fold /></el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ getPageTitle() }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="user-dropdown">
                {{ username }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { 
  DataLine, MapLocation, Connection, ChatDotRound, 
  SetUp, Van, Search, User, Fold, ArrowDown 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isCollapse = ref(false)

const username = computed(() => userStore.username)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const getPageTitle = () => {
  const path = route.path
  const routeMap: Record<string, string> = {
    '/dashboard/overview': '总览',
    '/dashboard/geographic': '地理分布',
    '/dashboard/attribute': '属性关联',
    '/dashboard/feedback': '用户反馈',
    '/dashboard/identity': '身份交叉',
    '/dashboard/traffic': '交通分析',
    '/dashboard/search': '景区搜索',
    '/dashboard/profile': '个人中心'
  }
  
  return routeMap[path] || '仪表盘'
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    router.push('/dashboard/profile')
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  width: 100%;
  display: flex;
}

.el-container {
  width: 100%;
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: #bfcbd9;
  transition: width 0.3s;
  height: 100%;
  overflow-y: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background-color: #263445;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
}

.el-menu {
  border-right: none;
}

.el-header {
  background-color: #fff;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar {
  font-size: 20px;
  margin-right: 15px;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.user-dropdown .el-icon {
  margin-left: 5px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  width: 100%;
  height: calc(100vh - 60px); /* 减去头部高度 */
}
</style> 