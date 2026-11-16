
<template>
  <div class="container-fluid py-3">

    <!-- Page heading -->
    <div class="mb-3">
      <div class="small text-muted mb-1">
        Home / Examiner / Booked Students
      </div>

      <h4 class="fw-bold mb-0">Booked Students</h4>
    </div>

    <!-- Error message -->
    <div v-if="error" class="alert alert-danger alert-dismissible">
      {{ error }}
      <button
        class="btn-close"
        @click="error = ''"
      ></button>
    </div>

    <!-- Search section -->
    <div class="card section-card mb-3">
      <div class="card-body">
        <div class="row g-2 align-items-center">
          <div class="col-12 col-md-3">
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search..."
            >
          </div>

          <div class="col-auto ms-md-auto">
            <button
              class="btn btn-outline-primary btn-sm"
              @click="loadBookings"
              :disabled="loading"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Students table -->
    <div class="card section-card">

      <div class="card-body">

        <!-- Loading -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-2">Loading booked students...</p>
        </div>

        <div v-else class="table-responsive">

          <table class="table table-hover align-middle mb-0">

            <thead>
              <tr>
                <th>Student Name</th>
                <th>Registration Number</th>
                <th>Slot</th>
                <th>Booking Status</th>
                <th>Evaluation Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="student in filteredStudents"
                :key="student.booking_id"
              >

                <td>
                  {{ student.student_name }}
                </td>

                <td>
                  {{ student.registration_number }}
                </td>

                <td>
                  {{ student.slot }}
                </td>

                <td>
                  <span
                    class="status-badge"
                    :class="bookingStatusClass(student.booking_status)"
                  >
                    {{ student.booking_status }}
                  </span>
                </td>

                <td>
                  <span
                    class="status-badge"
                    :class="evaluationStatusClass(student.evaluation_status)"
                  >
                    {{ student.evaluation_status }}
                  </span>
                </td>

                <td>
                  <button
                    class="btn btn-primary btn-sm"
                    :disabled="isEvaluated(student)"
                    @click="evaluateStudent(student)"
                  >
                    Evaluate
                  </button>
                </td>

              </tr>

              <!-- No records -->
              <tr v-if="filteredStudents.length === 0">
                <td
                  colspan="6"
                  class="text-center text-muted py-4"
                >
                  {{ searchQuery
                    ? 'No matching students found.'
                    : 'No students have booked your examination slots yet.'
                  }}
                </td>
              </tr>

            </tbody>

          </table>

          <div class="small text-muted mt-3">
            Showing {{ filteredStudents.length }} of
            {{ students.length }} students
          </div>

        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiRequest } from '../../services/api.js'

const router = useRouter()

const loading = ref(true)
const error = ref('')

const searchQuery = ref('')
const students = ref([])


// Filter students using name or registration number
const filteredStudents = computed(() => {
  const search = searchQuery.value.trim().toLowerCase()

  if (!search) {
    return students.value
  }

  return students.value.filter(student => {
    return (
      (student.student_name || '').toLowerCase().includes(search) ||
      (student.registration_number || '').toLowerCase().includes(search)
    )
  })
})


// Check whether student is already evaluated
function isEvaluated(student) {
  return (
    student.evaluation_status &&
    student.evaluation_status.toLowerCase() === 'evaluated'
  )
}


// Booking status badge
function bookingStatusClass(status) {
  if (status === 'Booked') return 'badge-booked'
  if (status === 'Completed') return 'badge-completed'

  return 'badge-default'
}


// Evaluation status badge
function evaluationStatusClass(status) {
  if (status === 'Pending') return 'badge-pending'
  if (status === 'Evaluated') return 'badge-evaluated'

  return 'badge-default'
}


// Fetch all bookings assigned to this examiner
async function loadBookings() {
  loading.value = true
  error.value = ''

  try {
    const data = await apiRequest('/examiner/bookings')

    students.value = data.students || []

  } catch (err) {
    error.value = err.message || 'Unable to load booked students.'
  } finally {
    loading.value = false
  }
}


// Open evaluation page
function evaluateStudent(student) {
  if (isEvaluated(student)) return

  router.push(`/examiner/evaluate/${student.booking_id}`)
}


// Load data when component is mounted
onMounted(loadBookings)

</script>

<style scoped>

.section-card {
  border: 1px solid #d9e1ec;
  border-radius: 7px;
  box-shadow: none;
}

.section-card .card-body {
  padding: 16px;
}

.table {
  font-size: 14px;
  color: #092c5c;
}

.table thead th {
  background-color: #f0f3f8;
  color: #092c5c;
  font-weight: 600;
  white-space: nowrap;
}

.table td,
.table th {
  border-color: #dce3ed;
  vertical-align: middle;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.badge-booked {
  color: #084298;
  background-color: #dbeafe;
}

.badge-pending {
  color: #984b00;
  background-color: #fff0c2;
}

.badge-evaluated {
  color: #084298;
  background-color: #dbeafe;
}

.badge-completed {
  color: #343a40;
  background-color: #e2e3e5;
}

.badge-default {
  color: #495057;
  background-color: #e9ecef;
}

.btn-sm {
  font-size: 12px;
}

</style>
