
import { createRouter, createWebHistory } from 'vue-router'

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
    path: '/admin/dashboard',
    component: () => import('../views/AdminDashboard.vue')
  },
  {
    path: '/examiner/dashboard',
    component: () => import('../views/ExaminerDashboard.vue')
  },
  {
    path: '/student/dashboard',
    component: () => import('../views/StudentDashboard.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
