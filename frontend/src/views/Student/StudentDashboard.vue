
<template>
  <div class="container-fluid py-3">

    <!-- Welcome Section -->
    <section class="card border-0 shadow-sm mb-4">
      <div class="card-body d-flex flex-column flex-lg-row align-items-lg-center justify-content-between gap-3 p-4 p-lg-5">

        <div>
          <span class="badge text-bg-primary mb-2">
            STUDENT WORKSPACE
          </span>

          <h1 class="h2 fw-bold mb-2">
            Welcome{{ name ? `, ${name}` : '' }}
          </h1>

          <p class="text-secondary mb-0">
            Find examinations, manage your bookings, and check your results.
          </p>
        </div>

        <RouterLink
          class="btn btn-primary flex-shrink-0"
          to="/student/examinations"
        >
          Explore Examinations
        </RouterLink>

      </div>
    </section>

    <!-- Error Message -->
    <div
      v-if="error"
      class="alert alert-danger"
      role="alert"
    >
      {{ error }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-2">Loading dashboard statistics...</p>
    </div>

    <!-- Statistics -->
    <div v-else>

      <h5 class="fw-bold mb-3">Dashboard Overview</h5>

      <div class="row g-3">

        <!-- Total Examinations -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card stat-card h-100">
            <div class="card-body">
              <div class="stat-label">
                Total Examinations
              </div>
              <h3>{{ stats.total_examinations }}</h3>
            </div>
          </div>
        </div>

        <!-- Available Examinations -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card stat-card h-100">
            <div class="card-body">
              <div class="stat-label">
                Available Examinations
              </div>
              <h3>{{ stats.available_examinations }}</h3>
            </div>
          </div>
        </div>

        <!-- My Bookings -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card stat-card h-100">
            <div class="card-body">
              <div class="stat-label">
                My Bookings
              </div>
              <h3>{{ stats.my_bookings }}</h3>
            </div>
          </div>
        </div>

        <!-- Upcoming Examinations -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card stat-card h-100">
            <div class="card-body">
              <div class="stat-label">
                Upcoming Examinations
              </div>
              <h3>{{ stats.upcoming_examinations }}</h3>
            </div>
          </div>
        </div>

        <!-- Published Results -->
        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card stat-card h-100">
            <div class="card-body">
              <div class="stat-label">
                Published Results
              </div>
              <h3>{{ stats.published_results }}</h3>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { apiRequest } from '../../services/api.js'

const auth = useAuthStore()

const loading = ref(true)
const error = ref('')

const name = computed(() =>
  auth.user?.fullname || auth.user?.name || ''
)

const stats = ref({
  total_examinations: 0,
  available_examinations: 0,
  my_bookings: 0,
  upcoming_examinations: 0,
  published_results: 0
})


// Fetch student dashboard statistics
async function loadDashboard() {

  loading.value = true
  error.value = ''

  try {

    const data = await apiRequest('/student/dashboard')

    if (!data.stats) {
      throw new Error('Dashboard statistics were not received.')
    }

    stats.value = {
      total_examinations: data.stats.total_examinations ?? 0,
      available_examinations: data.stats.available_examinations ?? 0,
      my_bookings: data.stats.my_bookings ?? 0,
      upcoming_examinations: data.stats.upcoming_examinations ?? 0,
      published_results: data.stats.published_results ?? 0
    }

  } catch (err) {

    error.value = err.message || 'Could not load dashboard statistics.'

  } finally {

    loading.value = false

  }
}


// Load statistics when component opens
onMounted(loadDashboard)

</script>

<style scoped>

.stat-card {
  border: 1px solid #d9e1ec;
  border-radius: 7px;
  box-shadow: none;
}

.stat-card .card-body {
  padding: 20px;
}

.stat-label {
  color: #092c5c;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.stat-card h3 {
  color: #082b59;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

</style>
