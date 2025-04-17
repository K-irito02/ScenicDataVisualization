import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  } as RouteRecordRaw,
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue')
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPassword.vue')
  },
  {
    path: '/admin',
    name: 'AdminLogin',
    component: () => import('@/views/AdminLogin.vue')
  },
  {
    path: '/logout-redirect',
    name: 'LogoutRedirect',
    component: {
      render: () => null,
      beforeRouteEnter(_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) {
        next('/login');
      }
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/layouts/DashboardLayout.vue'),
    redirect: '/dashboard/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/dashboard/Home.vue'),
        meta: { title: '全国景区数据分析及可视化系统' }
      },
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
      },
      {
        path: 'error-logs',
        name: 'ErrorLogs',
        component: () => import('@/views/admin/ErrorLogs.vue'),
        meta: { title: '系统错误日志' }
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
  const token = sessionStorage.getItem('token')
  const isAdmin = sessionStorage.getItem('isAdmin')
  
  // 检查token是否过期
  const tokenExpiry = parseInt(sessionStorage.getItem('tokenExpiry') || '0')
  const isTokenExpired = tokenExpiry && Date.now() > tokenExpiry
  
  if (token && isTokenExpired) {
    // 清除过期的token
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('tokenExpiry')
    sessionStorage.removeItem('userId')
    sessionStorage.removeItem('username')
    sessionStorage.removeItem('email')
    sessionStorage.removeItem('avatar')
    sessionStorage.removeItem('location')
    sessionStorage.removeItem('isAdmin')
    sessionStorage.removeItem('favorites')
  }
  
  // 处理特殊路由的访问逻辑
  
  // 1. 公开页面 - 允许任何人访问
  const publicPages = ['/login', '/register', '/admin', '/forgot-password', '/reset-password'];
  const _isPublicPage = publicPages.includes(to.path) || to.path === '/';
  
  // 2. 用户仅页面 - 需要普通用户权限
  const userOnlyPages = to.path.startsWith('/dashboard')
  // 3. 管理员页面 - 需要管理员权限
  const adminOnlyPages = to.path.startsWith('/admin-dashboard')
  
  // 处理可能的查询参数
  const hasError = to.query.disabled === 'true' || to.query.expired === 'true' || to.query.unauthorized === 'true';
  
  // 处理登录后的循环重定向问题 - 但如果有错误参数，不要进行重定向
  if (publicPages.includes(to.path) && token && !isTokenExpired && !hasError) {
    next({ path: '/dashboard' }) 
    return
  }
  
  // 路由访问控制逻辑
  if (userOnlyPages && (!token || isTokenExpired)) {
    // 如果已经有disabled参数，保留它
    if (to.query.disabled === 'true') {
      next({ name: 'Login', query: { disabled: 'true' } })
    } else {
      next({ name: 'Login' })
    }
  } else if (adminOnlyPages && (!token || isAdmin !== 'true' || isTokenExpired)) {
    next({ name: 'AdminLogin' })
  } else {
    next()
  }
})

export default router 