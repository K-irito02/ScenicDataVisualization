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
        redirect: '/dashboard/overview'
      },
      {
        path: 'overview',
        name: 'Overview',
        component: () => import('../views/dashboard/Overview.vue')
      },
      {
        path: 'geographic',
        name: 'Geographic',
        component: () => import('../views/dashboard/Geographic.vue')
      },
      {
        path: 'attribute',
        name: 'Attribute',
        component: () => import('../views/dashboard/Attribute.vue')
      },
      {
        path: 'feedback',
        name: 'Feedback',
        component: () => import('../views/dashboard/Feedback.vue')
      },
      {
        path: 'identity',
        name: 'Identity',
        component: () => import('../views/dashboard/Identity.vue')
      },
      {
        path: 'traffic',
        name: 'Traffic',
        component: () => import('../views/dashboard/Traffic.vue')
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