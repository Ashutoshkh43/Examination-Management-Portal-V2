<template>
  <AppHeader />
  <div class="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-aquamarine-exposure py-5">
    <div class="col-12 col-sm-11 col-md-10 col-lg-8 col-xl-7 col-xxl-6 px-3">
      <!-- Exposure Ring: Translucent layer fixes color bleeding -->
      <div class="exposure-shield p-2 rounded-4 shadow-lg">
        <div class="card border-0 rounded-4 overflow-hidden shadow-sm">
          
          <!-- Sharp Black Content Block -->
          <div class="card-body p-4 p-sm-5 bg-black">
            <div class="text-center mb-4">
              <h2 class="fw-black text-white tracking-tight mb-1">Student Registration</h2>
              <p class="text-light-50 small text-uppercase tracking-wider">Create your student account</p>
            </div>

            <div 
              v-if="message" 
              class="alert border-0 rounded-2 small mb-4 d-flex align-items-center" 
              :class="success ? 'alert-success text-success bg-opacity-10' : 'alert-danger text-danger bg-opacity-10'"
              role="alert"
            >
              <i class="bi me-2" :class="success ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'"></i>
              <div>{{ message }}</div>
            </div>

            <form @submit.prevent="handleRegister" novalidate>
              <div class="row g-3 mb-4">
                <!-- Full Name -->
                <div class="col-12 col-md-6">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Full Name</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-person"></i>
                    </span>
                    <input
                      v-model.trim="form.fullname"
                      type="text"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="Enter your full name"
                      required
                    />
                  </div>
                </div>

                <!-- Email Address -->
                <div class="col-12 col-md-6">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Email Address</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input
                      v-model.trim="form.email"
                      type="email"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="name@example.com"
                      required
                    />
                  </div>
                </div>

                <!-- Password -->
                <div class="col-12 col-md-6">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input
                      v-model="form.password"
                      type="password"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="Min. 8 characters"
                      minlength="8"
                      required
                    />
                  </div>
                </div>

                <!-- Registration Number -->
                <div class="col-12 col-md-6">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Registration Number</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-card-text"></i>
                    </span>
                    <input
                      v-model.trim="form.registration_number"
                      type="text"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="Enter reg number"
                    />
                  </div>
                </div>

                <!-- Department -->
                <div class="col-12 col-md-4">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Department</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-building"></i>
                    </span>
                    <input
                      v-model.trim="form.department"
                      type="text"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="e.g. CSE"
                    />
                  </div>
                </div>

                <!-- Semester -->
                <div class="col-12 col-md-4">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Semester</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-calendar3"></i>
                    </span>
                    <input
                      v-model.trim="form.semester"
                      type="text"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="e.g. 5th"
                    />
                  </div>
                </div>

                <!-- Contact Number -->
                <div class="col-12 col-md-4">
                  <label class="form-label small fw-bold text-uppercase text-light-50">Contact Number</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white border-0 text-muted rounded-start-2">
                      <i class="bi bi-telephone"></i>
                    </span>
                    <input
                      v-model.trim="form.contact"
                      type="tel"
                      class="form-control form-select-lg border-0 rounded-end-2 ps-0 fs-6"
                      placeholder="Phone number"
                    />
                  </div>
                </div>
              </div>

              <!-- Action Register Switch -->
              <button
                type="submit"
                class="btn btn-light btn-lg w-100 py-2.5 fw-bold sharp-action d-flex align-items-center justify-content-center gap-2"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm text-dark" role="status"></span>
                {{ loading ? 'Creating Account...' : 'Complete Registration' }}
              </button>
            </form>

            <!-- Footer / Redirection Zone -->
            <div class="text-center mt-4 pt-3 border-dark border-top">
              <p class="mb-2 text-light-50 small">
                Already registered?
                <RouterLink to="/login" class="text-decoration-none fw-semibold link-white-flush ms-1">
                  Login here
                </RouterLink>
              </p>
              
              <!-- Clean Copyright Inclusion -->
              <p class="text-light-50 small mb-0 font-monospace mt-2 pt-1 border-top border-dark border-opacity-25">
                &copy; {{ new Date().getFullYear() }} Ashutosh Khatiwada & Co.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppHeader from '@/components/AppHeader.vue'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({
  fullname: '',
  email: '',
  password: '',
  registration_number: '',
  department: '',
  semester: '',
  contact: ''
})

const loading = ref(false)
const message = ref('')
const success = ref(false)

function handleRegister() {
  message.value = ''
  success.value = false
  loading.value = true

  auth.register(form)
    .then(() => {
      success.value = true
      message.value = 'Registration successful. Please log in.'

      setTimeout(() => {
        router.push('/login')
      }, 1200)
    })
    .catch((error) => {
      message.value = error.message || 'Registration failed'
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<style scoped>
/* High-Exposure Sharp Aquamarine Backdrop */
.bg-aquamarine-exposure {
  background: radial-gradient(circle at top left, #a6ffea 0%, #7fffd4 50%, #5ee6bd 100%);
}

.fw-black {
  font-weight: 900;
  letter-spacing: -0.5px;
}

/* Translucent Exposure Shield (Creates the blend transition) */
.exposure-shield {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

/* Text transparency levels */
.text-light-50 {
  color: rgba(255, 255, 255, 0.5) !important;
}

/* Form element transitions and focus overrides */
.form-control {
  transition: all 0.2s ease-in-out;
}
.form-control:focus {
  background-color: #ffffff !important;
  box-shadow: none !important;
}

/* High Sharpness UI Control Elements */
.sharp-action {
  border-radius: 6px;
  background-color: #ffffff;
  color: #000000;
  border: none;
  transition: all 0.15s ease-in-out;
}
.sharp-action:hover {
  background-color: #e6e6e6;
  transform: translateY(-1px);
}

.link-white-flush {
  color: #ffffff;
  transition: opacity 0.15s ease-in-out;
}
</style>