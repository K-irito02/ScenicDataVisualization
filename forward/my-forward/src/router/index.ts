import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/admin',
    name: 'AdminLogin',
    component: () => import('@/views/AdminLogin.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/layouts/DashboardLayout.vue'),
    redirect: '/dashboard/scenic-distribution',
    children: [
      {
        path: 'scenic-distribution',
        name: 'ScenicDistribution',
        component: () => import('@/views/dashboard/ScenicDistribution.vue'),
        meta: { title: '景区基础分布分析' }
      },
      {
        path: 'scenic-classification',
        name: 'ScenicClassification',
        component: () => import('@/views/dashboard/ScenicClassification.vue'),
        meta: { title: '景区等级与分类分析' }
      },
      {
        path: 'ticket-analysis',
        name: 'TicketAnalysis',
        component: () => import('@/views/dashboard/TicketAnalysis.vue'),
        meta: { title: '门票与开放时间分析' }
      },
      {
        path: 'comment-analysis',
        name: 'CommentAnalysis',
        component: () => import('@/views/dashboard/CommentAnalysis.vue'),
        meta: { title: '评论与情感分析' }
      },
      {
        path: 'transportation',
        name: 'Transportation',
        component: () => import('@/views/dashboard/Transportation.vue'),
        meta: { title: '交通与可达性分析' }
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('@/views/dashboard/Search.vue'),
        meta: { title: '搜索与筛选' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/dashboard/Profile.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'scenic/:id',
        name: 'ScenicDetail',
        component: () => import('@/views/dashboard/ScenicDetail.vue'),
        meta: { title: '景区详情' }
      }
    ]
  },
  {
    path: '/admin-dashboard',
    name: 'AdminDashboard',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin-dashboard/users',
    children: [
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'user-records',
        name: 'UserRecords',
        component: () => import('@/views/admin/UserRecords.vue'),
        meta: { title: '用户记录' }
      }
    ]
  },
  {
    path: '/:catchAll(.*)',
    redirect: '/',
    component: () => import('@/views/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  // 简单的路由守卫，可以在这里做登录验证
  const token = localStorage.getItem('token')
  const isAdmin = localStorage.getItem('isAdmin')
  
  console.log('路由守卫:', {
    to: to.path,
    token: !!token,
    isAdmin: isAdmin === 'true', 
    localStorage_isAdmin: isAdmin
  })
  
  if (to.path.startsWith('/dashboard') && !token) {
    console.log('未登录，重定向到登录页')
    next({ name: 'Login' })
  } else if (to.path.startsWith('/admin-dashboard') && (!token || isAdmin !== 'true')) {
    console.log('非管理员，重定向到管理员登录页')
    next({ name: 'AdminLogin' })
  } else {
    console.log('允许访问:', to.path)
    next()
  }
})

export default router 