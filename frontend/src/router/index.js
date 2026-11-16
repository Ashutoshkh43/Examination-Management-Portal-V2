
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
        component: () => import('../views/Admin/AdminDashboard.vue'),
        meta: { title: 'Admin Dashboard' }
      },
      {
        path: 'examiners',
        component: () => import('../views/Admin/RegisterExaminer.vue'),
        meta: { title: 'Examiner Management' }
      },
      {
        path: 'courses',
        component: ()=> import('../views/Admin/Courses.vue')
      },
      {path:'students',
        component:()=> import('../views/Admin/ManageStudents.vue')
      },
      {
        path:'examinations',
        component:()=>import('../views/Admin/ManageExaminations.vue')
      },
      {
        path:'slots',
        component:()=>import('../views/Admin/AllExaminationSlot.vue')
      },
      {
        path: 'bookings',
        component: () => import('../views/Admin/ManageBookings.vue'),
        meta: { title: 'Booking Management' }
      },
      {
        path: 'rubrics',
        component: () => import('../views/Admin/ManageRubrics.vue'),
        meta: { title: 'Evaluation Rubrics' }
      },
      {
        path: 'results',
        component: () => import('../views/Admin/ManageResults.vue'),
        meta: { title: 'Publish Results' }
      },
      {
        path: 'reports',
        component: () => import('../views/Admin/AdminReports.vue'),
        meta: { title: 'Reports & Statistics' }
      }
      
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
        component: () => import('../views/Examiner/Dashboard.vue'),
        meta: { title: 'Examiner Dashboard' }
      },
      {
        path: 'slots',
        component: () => import('../views/Examiner/ManageSlots.vue'),
        meta: { title: 'Manage Examination Slots' }
      },
      {
        path:'examinations',
        component: ()=> import('../views/Examiner/MyExamination.vue')
      },
      {
        path:'booked-students',
        component: ()=> import('../views/Examiner/BookedStudents.vue')
      },
      {
        
        path:'profile',
        component: ()=> import('../views/Examiner/Profile.vue')
      
      }
      
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
        component: () => import('../views/Student/StudentDashboard.vue'),
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
