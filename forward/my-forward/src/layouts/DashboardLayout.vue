<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)

const handleLogout = () => {
  console.log('执行退出登录操作');
  userStore.logout();
  
  setTimeout(() => {
    console.log('登出完成，准备跳转到登录页面');
    router.push('/logout-redirect');
    
    setTimeout(() => {
      router.push('/login');
    }, 100);
  }, 100);
}

const activeMenu = computed(() => {
  return route.path
})

const username = computed(() => {
  return userStore.username || '用户'
})

const avatar = computed(() => {
  return userStore.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
})

const menuGroups = [
  {
    title: '数据概览',
    items: [
      {
        title: '首页',
        icon: 'House',
        path: '/dashboard/home'
      }
    ]
  },
  {
    title: '数据分析',
    items: [
      {
        title: '景区基础分布分析',
        icon: 'Location',
        path: '/dashboard/scenic-distribution'
      },
      {
        title: '景区等级与分类分析',
        icon: 'Medal',
        path: '/dashboard/scenic-classification'
      },
      {
        title: '门票与开放时间分析',
        icon: 'Ticket',
        path: '/dashboard/ticket-analysis'
      },
      {
        title: '评论与情感分析',
        icon: 'ChatDotRound',
        path: '/dashboard/comment-analysis'
      },
      {
        title: '交通与可达性分析',
        icon: 'Van',
        path: '/dashboard/transportation'
      }
    ]
  },
  {
    title: '用户功能',
    items: [
      {
        title: '搜索与筛选',
        icon: 'Search',
        path: '/dashboard/search'
      },
      {
        title: '个人中心',
        icon: 'User',
        path: '/dashboard/profile'
      }
    ]
  }
]

const menuItems = [
  {
    title: '首页',
    icon: 'House',
    path: '/dashboard/home'
  },
  {
    title: '景区基础分布分析',
    icon: 'Location',
    path: '/dashboard/scenic-distribution'
  },
  {
    title: '景区等级与分类分析',
    icon: 'Medal',
    path: '/dashboard/scenic-classification'
  },
  {
    title: '门票与开放时间分析',
    icon: 'Ticket',
    path: '/dashboard/ticket-analysis'
  },
  {
    title: '评论与情感分析',
    icon: 'ChatDotRound',
    path: '/dashboard/comment-analysis'
  },
  {
    title: '交通与可达性分析',
    icon: 'Van',
    path: '/dashboard/transportation'
  },
  {
    title: '搜索与筛选',
    icon: 'Search',
    path: '/dashboard/search'
  },
  {
    title: '个人中心',
    icon: 'User',
    path: '/dashboard/profile'
  }
]
</script>

<template>
  <div class="common-layout">
    <el-container class="layout-container">
      <el-aside :width="isCollapse ? '54px' : '200px'" class="layout-aside">
        <div class="logo-container">
          <img v-if="!isCollapse" src="/logo.png" alt="景区数据可视化平台" class="logo-image" />
          <img v-else src="/logo.png" alt="景区数据可视化平台" class="logo-image-small" />
          <h1 v-if="!isCollapse" class="system-title">景区数据平台</h1>
        </div>
        
        <div class="menu-wrapper">
          <el-menu
            :default-active="activeMenu"
            class="menu-container"
            :collapse="isCollapse"
            router
            background-color="#001529"
            text-color="#ffffff"
            active-text-color="#40a9ff"
          >
            <template v-for="(group, gIndex) in menuGroups" :key="`group-${gIndex}`">
              <div v-if="!isCollapse" class="menu-group-title">{{ group.title }}</div>
              
              <el-menu-item 
                v-for="item in group.items" 
                :key="item.path" 
                :index="item.path"
                class="menu-item"
              >
                <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
                <template #title>
                  <span class="menu-title">{{ item.title }}</span>
                </template>
              </el-menu-item>
              
              <div v-if="!isCollapse && gIndex < menuGroups.length - 1" class="menu-divider"></div>
            </template>
          </el-menu>
        </div>
        
        <div class="collapse-button" @click="isCollapse = !isCollapse">
          <el-icon><arrow-left v-if="!isCollapse" /><arrow-right v-else /></el-icon>
        </div>
      </el-aside>
      
      <el-container>
        <el-header class="layout-header">
          <div class="header-left">
            <h2 class="page-title">{{ route.meta.title || '全国景区的数据分析及可视化系统' }}</h2>
          </div>
          <div class="header-right">
            <el-dropdown>
              <div class="avatar-container">
                <el-avatar :src="avatar" />
                <span class="username">{{ username }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push('/dashboard/profile')">
                    <el-icon><user /></el-icon>个人中心
                  </el-dropdown-item>
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
          <p>© {{ new Date().getFullYear() }} 全国景区的数据分析及可视化系统 - 版权所有</p>
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
  position: fixed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  height: 100vh;
  z-index: 1000;
}

.logo-container {
  height: 64px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 16px 0;
  padding: 0 10px;
  overflow: hidden;
}

.logo-image {
  max-width: 40px;
  max-height: 40px;
  object-fit: contain;
}

.logo-image-small {
  max-width: 40px;
  max-height: 40px;
  object-fit: contain;
}

.system-title {
  margin: 0 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
}

.menu-wrapper {
  margin-top: 20px;
  height: calc(100vh - 140px);
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 60px;
}

.menu-wrapper::-webkit-scrollbar {
  width: 6px;
}

.menu-wrapper::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.menu-wrapper::-webkit-scrollbar-track {
  background-color: transparent;
}

.menu-container {
  border-right: none;
}

.menu-group-title {
  padding: 12px 16px 5px;
  color: rgba(255, 255, 255, 0.45);
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.menu-divider {
  height: 1px;
  margin: 8px 16px;
  background-color: rgba(255, 255, 255, 0.08);
}

.menu-item {
  margin: 4px 0;
  border-radius: 0 22px 22px 0;
  margin-right: 12px;
}

.menu-icon {
  font-size: 16px;
  margin-right: 8px;
  transition: all 0.3s;
}

.menu-title {
  font-size: 13px;
  transition: all 0.3s;
}

/* hover状态样式 */
.el-menu-item:hover {
  background-color: rgba(64, 169, 255, 0.1) !important;
}

.el-menu-item:hover .menu-icon,
.el-menu-item:hover .menu-title {
  color: #40a9ff !important;
}

/* 激活状态样式 */
.el-menu-item.is-active {
  background-color: rgba(64, 169, 255, 0.2) !important;
  position: relative;
}

.el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background-color: #40a9ff;
}

.collapse-button {
  position: fixed;
  bottom: 20px;
  left: v-bind('isCollapse ? "27px" : "100px"');
  transform: translateX(-50%);
  width: 32px;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #1890ff;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  z-index: 1001;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.5);
  transition: all 0.3s;
}

.collapse-button:hover {
  background-color: #40a9ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.7);
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

/* 为主内容添加左侧边距，以适应固定的侧边栏 */
.el-container:not(.layout-container) {
  margin-left: v-bind('isCollapse ? "54px" : "200px"');
  transition: margin-left 0.3s;
  width: calc(100% - v-bind('isCollapse ? "54px" : "200px"'));
}
</style> 