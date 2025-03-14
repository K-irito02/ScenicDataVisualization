import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/Index.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/login/Register.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/dashboard/Index.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard/basic'
      },
      {
        path: 'basic',
        name: 'Basic',
        component: () => import('../views/dashboard/Basic.vue')
      },
      {
        path: 'classification',
        name: 'Classification',
        component: () => import('../views/dashboard/Classification.vue')
      },
      {
        path: 'ticket',
        name: 'Ticket',
        component: () => import('../views/dashboard/Ticket.vue')
      },
      {
        path: 'comment',
        name: 'Comment',
        component: () => import('../views/dashboard/Comment.vue')
      },
      {
        path: 'transportation',
        name: 'Transportation',
        component: () => import('../views/dashboard/Transportation.vue')
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('../views/dashboard/Search.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/dashboard/Profile.vue')
      }
    ]
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/admin/Index.vue'),
    meta: { requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/users'
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/admin/Users.vue')
      },
      {
        path: 'records',
        name: 'Records',
        component: () => import('../views/admin/Records.vue')
      }
    ]
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/login/ForgotPassword.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _, next) => {
  const token = localStorage.getItem('token')
  const isAdmin = localStorage.getItem('isAdmin') === 'true'

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router 