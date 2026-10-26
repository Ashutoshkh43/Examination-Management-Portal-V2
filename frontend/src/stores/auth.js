import { defineStore } from 'pinia'
import { apiRequest } from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('emp_token') || '',
    user: JSON.parse(localStorage.getItem('emp_user') || 'null'),
    sessionChecked: false
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.user),

    role: (state) => state.user?.role || '',

    dashboardPath: (state) => {
      if (state.user?.role === 'admin') {
        return '/admin-dashboard'
      }

      if (state.user?.role === 'examiner') {
        return '/examiner-dashboard'
      }

      if (state.user?.role === 'student') {
        return '/student-dashboard'
      }

      return '/login'
    }
  },

  actions: {
    async login(formData) {
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(formData)
      })

      this.token = data.token
      this.user = data.user
      this.sessionChecked = true

      localStorage.setItem('emp_token', data.token)
      localStorage.setItem('emp_user', JSON.stringify(data.user))

      return data
    },

    async register(formData) {
      return apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(formData)
      })
    },

    async restoreSession() {
      if (!this.token) {
        this.sessionChecked = true
        return
      }

      return apiRequest('/auth/me')
        .then((data) => {
          const savedRole = this.user?.role

          if (!data.roles?.includes(savedRole)) {
            this.clearSession()
            return
          }

          this.user = {
            id: data.id,
            email: data.email,
            role: savedRole
          }

          localStorage.setItem('emp_user', JSON.stringify(this.user))
        })
        .catch(() => {
          this.clearSession()
        })
        .finally(() => {
          this.sessionChecked = true
        })
    },

    clearSession() {
      this.token = ''
      this.user = null

      localStorage.removeItem('emp_token')
      localStorage.removeItem('emp_user')
    },

    async logout() {
      if (this.token) {
        await apiRequest('/auth/logout', {
          method: 'POST'
        }).catch(() => {})
      }

      this.clearSession()
      this.sessionChecked = true
    }
  }
})