<template>
  <div class="auth-container">
    <div class="card portal-card">
      <div class="card-body p-4">
        <h2 class="portal-heading text-center">Student Registration</h2>
        <p class="text-muted text-center mb-4">
          Create your student account
        </p>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input
              v-model.trim="form.fullname"
              type="text"
              class="form-control"
              placeholder="Enter your full name"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Email Address</label>
            <input
              v-model.trim="form.email"
              type="email"
              class="form-control"
              placeholder="Enter your email"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              placeholder="Minimum 8 characters"
              minlength="8"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Registration Number</label>
            <input
              v-model.trim="form.registration_number"
              type="text"
              class="form-control"
              placeholder="Enter registration number"
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Department</label>
            <input
              v-model.trim="form.department"
              type="text"
              class="form-control"
              placeholder="Enter department"
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Semester</label>
            <input
              v-model.trim="form.semester"
              type="text"
              class="form-control"
              placeholder="Enter semester"
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Contact Number</label>
            <input
              v-model.trim="form.contact"
              type="tel"
              class="form-control"
              placeholder="Enter contact number"
            />
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100"
            :disabled="loading"
          >
            {{ loading ? 'Creating account...' : 'Register' }}
          </button>
        </form>

        <div
          v-if="message"
          class="alert mt-3"
          :class="success ? 'alert-success' : 'alert-danger'"
          role="alert"
        >
          {{ message }}
        </div>

        <p class="text-center mt-3 mb-0">
          Already registered?
          <RouterLink to="/login">Login</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

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