<template>
  <AppHeader />
  <div class="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-aquamarine-exposure py-5">
    <div class="col-12 col-sm-10 col-md-8 col-lg-6 col-xl-5 col-xxl-4 px-3">
      <!-- Exposure Ring: Translucent layer balances the black block against the bright backdrop -->
      <div class="exposure-shield p-2 rounded-4 shadow-lg">
        <div class="card border-0 rounded-4 overflow-hidden shadow-sm">
          
          <!-- Sharp Black Inner Content Layout Block -->
          <div class="card-body p-4 p-sm-5 bg-black">
            <div class="text-center mb-4">
              <h2 class="fw-black text-white tracking-tight mb-1">Sign In</h2>
              <p class="text-light-50 small text-uppercase tracking-wider">Sign in to your dashboard to continue</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger border-0 rounded-2 small mb-4 d-flex align-items-center" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              <div>{{ errorMessage }}</div>
            </div>

            <form @submit.prevent="login" novalidate>
              <!-- Role Selection -->
              <div class="mb-3">
                <label for="role" class="form-label small fw-bold text-uppercase text-light-50">Login As</label>
                <div class="input-group">
                  <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                    <i class="bi bi-person-badge"></i>
                  </span>
                  <select 
                    id="role" 
                    v-model="role" 
                    class="form-select form-select-lg border-0 rounded-end-2 ps-0 fs-6" 
                    required
                  >
                    <option value="" disabled>Select your role</option>
                    <option value="admin">Admin</option>
                    <option value="examiner">Examiner</option>
                    <option value="student">Student</option>
                  </select>
                </div>
              </div>

              <!-- Email -->
              <div class="mb-3">
                <label for="email" class="form-label small fw-bold text-uppercase text-light-50">Email Address</label>
                <div class="input-group">
                  <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                    <i class="bi bi-envelope"></i>
                  </span>
                  <input 
                    id="email" 
                    v-model.trim="email" 
                    type="email" 
                    class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6" 
                    placeholder="name@example.com" 
                    autocomplete="username" 
                    required 
                  />
                </div>
              </div>

              <!-- Password -->
              <div class="mb-4">
                <label for="password" class="form-label small fw-bold text-uppercase text-light-50">Password</label>
                <div class="input-group">
                  <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input 
                    id="password" 
                    v-model="password" 
                    type="password" 
                    class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6" 
                    placeholder="••••••••" 
                    autocomplete="current-password" 
                    required 
                  />
                </div>
              </div>

              <!-- Submit Button: Crisp White for extreme sharpness against Black background -->
              <button 
                type="submit" 
                class="btn btn-light btn-lg w-100 py-2.5 fw-bold sharp-action d-flex align-items-center justify-content-center gap-2" 
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm text-dark" role="status" aria-hidden="true"></span>
                {{ loading ? 'Signing in...' : 'Sign In' }}
              </button>
            </form>

            <!-- Footer Links -->
            <div class="text-center mt-4 pt-3 border-dark border-top">
              <p class="mb-2 text-light-50 small">
                New student? 
                <RouterLink to="/register" class="text-decoration-none fw-semibold link-white-flush ms-1">
                  Create an account
                </RouterLink>
              </p>
              <RouterLink to="/" class="text-light-50 small text-decoration-none hover-underline">
                <i class="bi bi-arrow-left me-1"></i>Back to Home
              </RouterLink>
              
              <!-- Clean Integrated Copyright Footer -->
              <p class="text-light-50 small mb-0 font-monospace mt-3 pt-2 border-top border-dark border-opacity-25">
                <!-- &copy;  Ashutosh Khatiwada & Co.
                <a href="https://mail.google.com/mail/u/0/#inbox?compose=CllgCJfqccNsDTrlBMVHwjbHCGMxxmqCWzljzLkqkJskNRBxLSzZgTHDmgDhMFpvHWTTtgnKWWg" target="_blank">contact us</a> -->
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const auth = useAuthStore()

const role = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const login = () => {
  errorMessage.value = ''
  loading.value = true

  auth.login({
    email: email.value,
    password: password.value,
    role: role.value
  })
  .then(() => {
    const actualRole = String(
      auth.user?.role || auth.role || ''
    ).toLowerCase()

    if (actualRole === 'admin') {
      return router.push('/admin/dashboard')
    }
    if (actualRole === 'examiner') {
      return router.push('/examiner/dashboard')
    }
    if (actualRole === 'student') {
      return router.push('/student/dashboard')
    }
    errorMessage.value = 'Invalid account role.'
  })
  .catch((error) => {
    errorMessage.value = error.message || 'Login failed. Check your email and password.'
  })
  .finally(() => {
    loading.value = false
  })
}
</script>

<style scoped>
/* High-Exposure Radial Backdrop Gradient */
.bg-aquamarine-exposure {
  background: radial-gradient(circle at top left, #a6ffea 0%, #7fffd4 50%, #5ee6bd 100%);
}

.fw-black {
  font-weight: 900;
  letter-spacing: -0.5px;
}

/* Translucent Exposure Shield Layer */
.exposure-shield {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

/* Text opacity overrides for subheadings */
.text-light-50 {
  color: rgba(255, 255, 255, 0.5) !important;
}

/* High-Contrast Interactive Form Controls */
.sharp-action {
  border-radius: 6px;
  background-color: #ffffff;
  color: #000000;
  border: none;
  transition: all 0.15s ease-in-out;
}
.sharp-action:hover:not(:disabled) {
  background-color: #e6e6e6;
  transform: translateY(-1px);
}
.sharp-action:disabled {
  background-color: #cccccc;
  opacity: 0.6;
}

.link-white-flush {
  color: #ffffff;
  transition: opacity 0.15s ease-in-out;
}
.link-white-flush:hover {
  opacity: 0.8;
  text-decoration: underline;
}

/* Clean Input Field Transitions */
.form-control, .form-select {
  transition: all 0.2s ease-in-out;
}
.form-control:focus, .form-select:focus {
  background-color: #ffffff !important;
  box-shadow: none !important;
}

.hover-underline:hover {
  text-decoration: underline !important;
}
</style>
