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
    path: '/admin',
    name: 'AdminLogin',
    component: () => import('@/views/AdminLogin.vue')
  },
  {
    path: '/logout-redirect',
    name: 'LogoutRedirect',
    component: {
      render: () => null,
      beforeRouteEnter(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
        next('/login');
      }
    }
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
  // 使用sessionStorage替代localStorage
  const token = sessionStorage.getItem('token')
  const isAdmin = sessionStorage.getItem('isAdmin')
  
  // 强制重新读取所有sessionStorage项，防止缓存问题
  const allStorage = {
    token: sessionStorage.getItem('token'),
    userId: sessionStorage.getItem('userId'),
    username: sessionStorage.getItem('username'),
    isAdmin: sessionStorage.getItem('isAdmin'),
    tokenExpiry: sessionStorage.getItem('tokenExpiry')
  }
  
  // 检查token是否过期
  const tokenExpiry = parseInt(sessionStorage.getItem('tokenExpiry') || '0')
  const isTokenExpired = tokenExpiry && Date.now() > tokenExpiry
  
  if (token && isTokenExpired) {
    console.log('Token已过期，清除认证信息')
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
  
  console.log('路由守卫详细信息:', {
    to: to.path,
    from: _from.path,
    token: token ? `${token.substring(0, 10)}...` : 'null',
    isAdmin: isAdmin === 'true', 
    sessionStorage_isAdmin: isAdmin,
    allStorage,
    isTokenExpired
  })
  
  // 处理特殊路由的访问逻辑
  
  // 1. 公开页面 - 允许任何人访问
  const publicPages = ['/login', '/register', '/admin']
  const isPublicPage = publicPages.includes(to.path) || to.path === '/'
  
  // 2. 用户仅页面 - 需要普通用户权限
  const userOnlyPages = to.path.startsWith('/dashboard')
  // 3. 管理员页面 - 需要管理员权限
  const adminOnlyPages = to.path.startsWith('/admin-dashboard')
  
  // 处理登录后的循环重定向问题
  if (publicPages.includes(to.path) && token && !isTokenExpired) {
    console.log('已登录用户尝试访问登录页，重定向到dashboard')
    next({ path: '/dashboard' }) 
    return
  }

  // 注入到Vue对象，方便调试
  if (window && !(window as any).vueDebug) {
    (window as any).vueDebug = {
      sessionStorage,
      router,
      getTokenInfo: () => {
        return {
          token: sessionStorage.getItem('token'),
          isAdmin: sessionStorage.getItem('isAdmin'),
          username: sessionStorage.getItem('username'),
          tokenExpiry: sessionStorage.getItem('tokenExpiry')
        }
      }
    }
    console.log('已为window对象添加vueDebug属性，可在控制台查看认证信息')
  }
  
  // 路由访问控制逻辑
  if (userOnlyPages && (!token || isTokenExpired)) {
    console.log('未登录或Token已过期，重定向到登录页')
    next({ name: 'Login' })
  } else if (adminOnlyPages && (!token || isAdmin !== 'true' || isTokenExpired)) {
    console.log('非管理员，重定向到管理员登录页')
    next({ name: 'AdminLogin' })
  } else {
    console.log('允许访问:', to.path)
    next()
  }
})

export default router 