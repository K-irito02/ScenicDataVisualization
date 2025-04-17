<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)

const handleLogout = () => {
  // 确保正确清除所有认证信息
  console.log('管理员执行退出登录操作');
  userStore.logout();
  
  // 使用setTimeout确保store状态更新完成后再重定向
  setTimeout(() => {
    console.log('管理员登出完成，准备跳转到登录页面');
    // 先离开当前路由，避免路由守卫拦截
    router.push('/logout-redirect');
    
    // 再跳转到管理员登录页
    setTimeout(() => {
      router.push('/admin');
    }, 100);
  }, 100);
}

const activeMenu = computed(() => {
  return route.path
})

const username = computed(() => {
  return userStore.username || '管理员'
})

const avatar = computed(() => {
  return userStore.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
})

const menuItems = [
  {
    title: '用户管理',
    icon: 'User',
    path: '/admin-dashboard/users'
  },
  {
    title: '用户记录',
    icon: 'List',
    path: '/admin-dashboard/user-records'
  },
  {
    title: '系统错误日志',
    icon: 'Warning',
    path: '/admin-dashboard/error-logs'
  }
]
</script>

<template>
  <div class="common-layout">
    <el-container class="layout-container">
      <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
        <div class="logo-container">
          <img v-if="!isCollapse" src="/logo.png" alt="景区数据可视化平台" class="logo-image" />
          <img v-else src="/logo.png" alt="景区数据可视化平台" class="logo-image-small" />
          <span v-if="!isCollapse" class="admin-badge">管理系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="menu-container"
          :collapse="isCollapse"
          router
          background-color="#001529"
          text-color="#ffffff"
          active-text-color="#409EFF"
        >
          <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </el-menu>
        <div class="collapse-button" @click="isCollapse = !isCollapse">
          <el-icon><arrow-left v-if="!isCollapse" /><arrow-right v-else /></el-icon>
        </div>
      </el-aside>
      
      <el-container>
        <el-header class="layout-header">
          <div class="header-left">
            <h2 class="page-title">{{ route.meta.title || '全国景区的数据分析及可视化系统 - 管理后台' }}</h2>
          </div>
          <div class="header-right">
            <el-dropdown>
              <div class="avatar-container">
                <el-avatar :src="avatar" />
                <span class="username">{{ username }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">
                    <el-icon><switch-button /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="layout-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
        
        <el-footer class="layout-footer">
          <p>© {{ new Date().getFullYear() }} 全国景区的数据分析及可视化系统 - 管理后台 - 版权所有</p>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.layout-aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
  position: relative;
}

.logo-container {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px 0;
  padding: 0 10px;
  overflow: hidden;
  position: relative;
}

.logo-image {
  max-width: 100%;
  max-height: 50px;
  object-fit: contain;
}

.logo-image-small {
  max-width: 40px;
  max-height: 40px;
  object-fit: contain;
}

.admin-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12px;
  color: #ffffff;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 2px 0;
}

.menu-container {
  border-right: none;
}

.collapse-button {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #1890ff;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  z-index: 999;
}

.layout-header {
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.avatar-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  font-size: 14px;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.layout-footer {
  text-align: center;
  background-color: #f0f2f5;
  color: #666;
  font-size: 12px;
  padding: 10px 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 