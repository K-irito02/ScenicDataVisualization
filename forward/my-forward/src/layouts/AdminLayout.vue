<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)

const handleLogout = () => {
  userStore.logout()
  router.push('/admin')
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
  }
]
</script>

<template>
  <div class="common-layout">
    <el-container class="layout-container">
      <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
        <div class="logo-container">
          <div class="logo-text" v-if="!isCollapse">管理系统</div>
          <div class="logo-small-text" v-else>管</div>
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
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
}

.logo-small-text {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
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