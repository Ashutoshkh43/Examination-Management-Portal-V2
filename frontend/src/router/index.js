
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/admin',
    component: () => import('../layouts/AppLayout.vue'),
    meta: {
      requiresAuth: true,
      role: 'admin'
    },
    children: [
      {
        path: 'dashboard',
        component: () => import('../views/AdminDashboard.vue'),
        meta: { title: 'Admin Dashboard' }
      },
      {
        path: 'examiners',
        component: () => import('../views/RegisterExaminer.vue'),
        meta: { title: 'Examiner Management' }
      },
      
    ]
  },
  {
    path: '/examiner',
    component: () => import('../layouts/AppLayout.vue'),
    meta: {
      requiresAuth: true,
      role: 'examiner'
    },
    children: [
      {
        path: 'dashboard',
        component: () => import('../views/ExaminerDashboard.vue'),
        meta: { title: 'Examiner Dashboard' }
      },
      
    ]
  },
  {
    path: '/student',
    component: () => import('../layouts/AppLayout.vue'),
    meta: {
      requiresAuth: true,
      role: 'student'
    },
    children: [
      {
        path: 'dashboard',
        component: () => import('../views/StudentDashboard.vue'),
        meta: { title: 'Student Dashboard' }
      },
      
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  await auth.restoreSession()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  if (to.meta.role && auth.role !== to.meta.role) {
    if (auth.isLoggedIn) {
      return auth.dashboardPath
    }

    return '/login'
  }

  if (
    (to.path === '/login' || to.path === '/register') &&
    auth.isLoggedIn
  ) {
    return auth.dashboardPath
  }

  return true
})

export default router
