
<template>
  <div class="container-fluid py-3">

    <!-- Page heading -->
    <div class="mb-3">
      <div class="small text-muted mb-1">
        Home / Examiner / Dashboard
      </div>
      <h4 class="fw-bold mb-0">Dashboard</h4>
      <p class="text-muted mb-0">
        Overview of your examination activities.
      </p>
    </div>

    <!-- Success message -->
    <div v-if="message" class="alert alert-success alert-dismissible">
      {{ message }}
      <button class="btn-close" @click="message = ''"></button>
    </div>

    <!-- Error message -->
    <div v-if="error" class="alert alert-danger alert-dismissible">
      {{ error }}
      <button class="btn-close" @click="error = ''"></button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-2">Loading dashboard...</p>
    </div>

    <div v-else>

      <!-- Statistics -->
      <div class="row g-3 mb-3">

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card dashboard-stat h-100">
            <div class="card-body">
              <div class="text-muted">Assigned Examinations</div>
              <h3 class="fw-bold mb-0">
                {{ stats.assigned_examinations }}
              </h3>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card dashboard-stat h-100">
            <div class="card-body">
              <div class="text-muted">Total Slots</div>
              <h3 class="fw-bold mb-0">
                {{ stats.total_slots }}
              </h3>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card dashboard-stat h-100">
            <div class="card-body">
              <div class="text-muted">Booked Students</div>
              <h3 class="fw-bold mb-0">
                {{ stats.booked_students }}
              </h3>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-xl-3">
          <div class="card dashboard-stat h-100">
            <div class="card-body">
              <div class="text-muted">Pending Evaluations</div>
              <h3 class="fw-bold mb-0">
                {{ stats.pending_evaluations }}
              </h3>
            </div>
          </div>
        </div>

      </div>

      <!-- Upcoming Slots -->
      <div class="card dashboard-section">

        <div class="card-body">

          <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">

            <div>
              <h6 class="fw-bold mb-1">Upcoming Slots</h6>
              <small class="text-muted">
                View students booked for your examination slots.
              </small>
            </div>

            <button
              class="btn btn-sm btn-outline-primary"
              @click="loadDashboard"
              :disabled="loading"
            >
              Refresh
            </button>

          </div>

          <div class="table-responsive">

            <table class="table table-hover align-middle mb-0">

              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Examination</th>
                  <th>Booked Students</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>

                <tr
                  v-for="slot in upcomingSlots"
                  :key="slot.id"
                >

                  <td>
                    {{ formatDate(slot.date) }}
                  </td>

                  <td>
                    {{ slot.start_time }} - {{ slot.end_time }}
                  </td>

                  <td>
                    {{ slot.examination_name }}
                  </td>

                  <td>
                    {{ slot.booked_count }} / {{ slot.capacity }}
                  </td>

                  <td>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewSlotStudents(slot)"
                    >
                      Students
                    </button>
                  </td>

                </tr>

                <tr v-if="upcomingSlots.length === 0">
                  <td
                    colspan="5"
                    class="text-center text-muted py-4"
                  >
                    No upcoming slots found.
                  </td>
                </tr>

              </tbody>

            </table>

          </div>

        </div>
      </div>

    </div>

    <!-- Booked Students Modal -->
    <div
      v-if="selectedSlot"
      class="modal-backdrop-custom"
      @click.self="selectedSlot = null"
    >

      <div class="custom-modal custom-modal-wide">

        <div class="d-flex justify-content-between align-items-center mb-3">

          <div>
            <h5 class="fw-bold mb-1">Booked Students</h5>

            <div class="small text-muted">
              {{ selectedSlot.examination_name }} |
              {{ formatDate(selectedSlot.date) }} |
              {{ selectedSlot.start_time }} -
              {{ selectedSlot.end_time }}
            </div>
          </div>

          <button
            class="btn-close"
            @click="selectedSlot = null"
          ></button>

        </div>

        <!-- Students loading -->
        <div v-if="studentsLoading" class="text-center py-4">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-2">Loading students...</p>
        </div>

        <!-- Students table -->
        <div v-else class="table-responsive">

          <table class="table table-hover align-middle">

            <thead>
              <tr>
                <th>Student Name</th>
                <th>Registration Number</th>
                <th>Department</th>
                <th>Semester</th>
                <th>Evaluation</th>
                <th>Marks</th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="student in slotStudents"
                :key="student.booking_id"
              >

                <td>{{ student.student_name }}</td>

                <td>{{ student.registration_number }}</td>

                <td>{{ student.department || '-' }}</td>

                <td>{{ student.semester || '-' }}</td>

                <td>
                  <span
                    class="badge"
                    :class="
                      student.evaluation_status === 'Pending'
                        ? 'text-bg-warning'
                        : 'text-bg-success'
                    "
                  >
                    {{ student.evaluation_status }}
                  </span>
                </td>

                <td>
                  {{ student.total_marks ?? '-' }}
                </td>

              </tr>

              <tr v-if="slotStudents.length === 0">
                <td
                  colspan="6"
                  class="text-center text-muted py-4"
                >
                  No students have booked this slot yet.
                </td>
              </tr>

            </tbody>

          </table>

        </div>

        <div class="text-end mt-2">
          <button
            class="btn btn-secondary btn-sm"
            @click="selectedSlot = null"
          >
            Close
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '../../services/api.js'

// Loading states
const loading = ref(true)
const studentsLoading = ref(false)

// Messages
const error = ref('')
const message = ref('')

// Dashboard statistics
const stats = ref({
  assigned_examinations: 0,
  total_slots: 0,
  booked_students: 0,
  pending_evaluations: 0
})

// Slot data
const slots = ref([])
const upcomingSlots = ref([])

// Selected slot and students
const selectedSlot = ref(null)
const slotStudents = ref([])


// Load dashboard information
async function loadDashboard() {

  loading.value = true
  error.value = ''

  try {

    const [dashboardData, slotData] = await Promise.all([
      apiRequest('/examiner/dashboard'),
      apiRequest('/examiner/slots')
    ])

    // Update statistics
    if (!dashboardData.stats) {
      throw new Error('Dashboard statistics were not received from the backend.')
    }

    const requiredFields = [
      'assigned_examinations',
      'total_slots',
      'booked_students',
      'pending_evaluations'
    ]

    requiredFields.forEach(field => {
      if (typeof dashboardData.stats[field] !== 'number') {
        throw new Error(`Invalid or missing dashboard field: ${field}`)
      }
    })

    stats.value = dashboardData.stats

    // Store slots
    slots.value = slotData.slots || []

    // Filter upcoming slots
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    upcomingSlots.value = slots.value
      .filter(slot => {
        const slotDate = new Date(`${slot.date}T00:00:00`)

        return (
          slotDate >= today &&
          slot.status !== 'Cancelled' &&
          slot.status !== 'Completed'
        )
      })
      .sort((a, b) => {
        const first = `${a.date}T${a.start_time}`
        const second = `${b.date}T${b.start_time}`

        return first.localeCompare(second)
      })

  } catch (err) {

    error.value = err.message || 'Unable to load examiner dashboard.'

  } finally {

    loading.value = false

  }
}


// Format date
function formatDate(value) {

  if (!value) return '-'

  const [year, month, day] = value.split('-')

  return `${day}-${month}-${year}`
}


// View students booked in a slot
async function viewSlotStudents(slot) {

  selectedSlot.value = slot
  slotStudents.value = []
  studentsLoading.value = true
  error.value = ''

  try {

    const data = await apiRequest(
      `/examiner/slots/${slot.id}/students`
    )

    slotStudents.value = data.students || []

  } catch (err) {

    error.value = err.message || 'Unable to load booked students.'

  } finally {

    studentsLoading.value = false

  }
}


// Fetch dashboard data when component is mounted
onMounted(loadDashboard)

</script>

<style scoped>

.dashboard-stat,
.dashboard-section {
  border: 1px solid #d9e1ec;
  border-radius: 7px;
  box-shadow: none;
}

.dashboard-stat .card-body {
  padding: 16px;
}

.dashboard-stat h3 {
  color: #082b59;
  margin-top: 3px;
}

.dashboard-section .card-body {
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

.btn-sm {
  font-size: 12px;
}

.badge {
  font-weight: 500;
  padding: 6px 9px;
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  z-index: 1050;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
}

.custom-modal {
  background: white;
  width: 100%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 8px;
  padding: 22px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.custom-modal-wide {
  max-width: 950px;
}

@media (max-width: 576px) {
  .custom-modal-wide {
    max-width: 100%;
  }
}

</style>
