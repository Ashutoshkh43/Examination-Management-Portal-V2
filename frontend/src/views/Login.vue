
<template>
   
  <div
    class="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-light py-4"
  >
 
    <div
      class="card border-0 shadow-lg rounded-4 w-100 col-12 col-sm-10 col-md-8 col-lg-6 col-xl-5 col-xxl-4"
    >
      <div class="card-body p-4 p-md-5">

        <div class="text-center mb-4">
          <h2 class="fw-bold text-primary">Examination Portal</h2>
          <p class="text-muted">
            Sign in to access your account
          </p>
        </div>

        <div
          v-if="errorMessage"
          class="alert alert-danger"
          role="alert"
        >
          {{ errorMessage }}
        </div>

        <form @submit.prevent="login">

          <!-- Role Selection -->
          <div class="mb-3">
            <label for="role" class="form-label fw-semibold">
              Login As
            </label>

            <select
              id="role"
              v-model="role"
              class="form-select form-select-lg"
              required
            >
              <option value="" disabled>Select your role</option>
              <option value="admin">Admin</option>
              <option value="examiner">Examiner</option>
              <option value="student">Student</option>
            </select>
          </div>

          <!-- Email -->
          <div class="mb-3">
            <label for="email" class="form-label fw-semibold">
              Email Address
            </label>

            <input
              id="email"
              v-model.trim="email"
              type="email"
              class="form-control form-control-lg"
              placeholder="Enter your email"
              autocomplete="username"
              required
            />
          </div>

          <!-- Password -->
          <div class="mb-4">
            <label for="password" class="form-label fw-semibold">
              Password
            </label>

            <input
              id="password"
              v-model="password"
              type="password"
              class="form-control form-control-lg"
              placeholder="Enter your password"
              autocomplete="current-password"
              required
            />
          </div>

          <!-- Submit -->
          <button
            type="submit"
            class="btn btn-primary btn-lg w-100 shadow-sm fw-semibold"
            :disabled="loading"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>

        </form>

        <div class="text-center mt-4">
          <span class="text-muted">New student?</span>

          <RouterLink
            to="/register"
            class="text-decoration-none fw-semibold ms-1"
          >
            Create an account
          </RouterLink>
        </div>

        <div class="text-center mt-3">
          <RouterLink
            to="/"
            class="text-muted small text-decoration-none"
          >
            Back to Home
          </RouterLink>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

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
      errorMessage.value =
        error.message || 'Login failed. Check your email and password.'
    })
    .finally(() => {
      loading.value = false
    })
}


</script>
