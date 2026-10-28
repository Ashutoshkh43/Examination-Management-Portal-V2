<template>
  <div class="d-flex flex-column gap-4">
    <section class="card border-0 shadow-sm">
      <div class="card-body d-flex flex-column flex-lg-row align-items-lg-center justify-content-between gap-3 p-4 p-lg-5">
      <div>
        <span class="badge text-bg-primary mb-2">STUDENT WORKSPACE</span>
        <h1 class="h2 fw-bold mb-2">Welcome{{ name ? `, ${name}` : '' }}</h1>
        <p class="text-secondary mb-0">Find examinations, manage your bookings, and check your results.</p>
      </div>
      <RouterLink class="btn btn-primary flex-shrink-0" to="/student/examinations">Explore examinations</RouterLink>
      </div>
    </section>
    <div v-if="error" class="alert alert-warning mb-0" role="alert">{{ error }}</div>
    <section class="card border-0 shadow-sm"><div class="card-body"><p class="mb-0 text-secondary">{{ greeting }}</p></div></section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { apiRequest } from '../services/api'

const auth = useAuthStore()
const error = ref('')
const name = computed(() => auth.user?.fullname || auth.user?.name || '')
const greeting = ref('Choose an area to get started.')

onMounted(async () => {
  try {
    const data = await apiRequest('/student/dashboard')
    greeting.value = data.message || greeting.value
  } catch (err) {
    error.value = err.message || 'Could not load your dashboard.'
  }
})
</script>
