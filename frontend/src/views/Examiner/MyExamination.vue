
<template>
  <div class="container-fluid py-3">

    <!-- Page heading -->
    <div class="mb-3">
      <div class="small text-muted mb-1">
        Home / Examiner / My Examinations
      </div>
      <h4 class="fw-bold mb-0">My Examinations</h4>
      <p class="text-muted mb-0">
        View and manage examinations assigned to you.
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

    <!-- Examination list -->
    <div class="card examination-section">

      <div class="card-body">

        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
          <div>
            <h6 class="fw-bold mb-1">Assigned Examinations</h6>
            <small class="text-muted">
              Total: {{ examinations.length }} examinations
            </small>
          </div>

          <button
            class="btn btn-sm btn-outline-primary"
            @click="loadExaminations"
            :disabled="loading"
          >
            <span
              v-if="loading"
              class="spinner-border spinner-border-sm me-1"
            ></span>
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-2">Loading examinations...</p>
        </div>

        <!-- Table -->
        <div v-else class="table-responsive">

          <table class="table table-hover align-middle mb-0">

            <thead>
              <tr>
                <th>Examination</th>
                <th>Course</th>
                <th>Date Range</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="exam in examinations"
                :key="exam.id"
              >
                <td class="fw-semibold">
                  {{ exam.examination_name }}
                </td>

                <td>
                  {{ exam.course_code }}
                </td>

                <td>
                  {{ exam.date_range }}
                </td>

                <td>
                  <span
                    class="badge"
                    :class="statusClass(exam.status)"
                  >
                    {{ exam.status }}
                  </span>
                </td>

                <td>
                  <div class="d-flex flex-wrap gap-2">

                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="viewExamination(exam)"
                    >
                      View
                    </button>

                    <button
                      class="btn btn-sm btn-outline-success"
                      :disabled="
                        exam.status === 'Completed' ||
                        completingId === exam.id
                      "
                      @click="markCompleted(exam)"
                    >
                      {{
                        completingId === exam.id
                          ? 'Updating...'
                          : 'Mark Completed'
                      }}
                    </button>

                  </div>
                </td>
              </tr>

              <!-- Empty state -->
              <tr v-if="examinations.length === 0">
                <td
                  colspan="5"
                  class="text-center text-muted py-5"
                >
                  No examinations have been assigned to you.
                </td>
              </tr>

            </tbody>

          </table>

        </div>

      </div>
    </div>

    <!-- Examination Details Modal -->
    <div
      v-if="selectedExam"
      class="modal-backdrop-custom"
      @click.self="selectedExam = null"
    >

      <div class="custom-modal">

        <div class="d-flex justify-content-between align-items-center mb-3">

          <h5 class="fw-bold mb-0">
            Examination Details
          </h5>

          <button
            class="btn-close"
            @click="selectedExam = null"
          ></button>

        </div>

        <div class="detail-row">
          <span>Examination</span>
          <strong>{{ selectedExam.examination_name }}</strong>
        </div>

        <div class="detail-row">
          <span>Course</span>
          <strong>
            {{ selectedExam.course_code }} -
            {{ selectedExam.course_name }}
          </strong>
        </div>

        <div class="detail-row">
          <span>Type</span>
          <strong>{{ selectedExam.examination_type }}</strong>
        </div>

        <div class="detail-row">
          <span>Duration</span>
          <strong>{{ selectedExam.duration }} minutes</strong>
        </div>

        <div class="detail-row">
          <span>Maximum Marks</span>
          <strong>{{ selectedExam.maximum_marks }}</strong>
        </div>

        <div class="detail-row">
          <span>Date Range</span>
          <strong>{{ selectedExam.date_range }}</strong>
        </div>

        <div class="detail-row">
          <span>Status</span>
          <strong>{{ selectedExam.status }}</strong>
        </div>

        <div class="detail-row">
          <span>Created Slots</span>
          <strong>{{ selectedExam.slot_count }}</strong>
        </div>

        <div class="text-end mt-3">
          <button
            class="btn btn-secondary btn-sm"
            @click="selectedExam = null"
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

const loading = ref(true)
const completingId = ref(null)

const error = ref('')
const message = ref('')

const examinations = ref([])
const selectedExam = ref(null)


// Status badge colours
function statusClass(status) {
  if (status === 'Booking Open') return 'text-bg-success'
  if (status === 'Slot Creation') return 'text-bg-primary'
  if (status === 'Completed') return 'text-bg-secondary'
  if (status === 'Closed') return 'text-bg-dark'

  return 'text-bg-light'
}


// Load examinations assigned to the examiner
async function loadExaminations() {
  loading.value = true
  error.value = ''

  try {
    const data = await apiRequest('/examiner/examinations')

    examinations.value = data.examinations || []

  } catch (err) {
    error.value = err.message || 'Unable to load examinations.'
  } finally {
    loading.value = false
  }
}


// Open examination details
function viewExamination(exam) {
  selectedExam.value = exam
}


// Mark examination as completed
async function markCompleted(exam) {

  const confirmed = window.confirm(
    `Are you sure you want to mark "${exam.examination_name}" as completed?`
  )

  if (!confirmed) return

  completingId.value = exam.id
  error.value = ''
  message.value = ''

  try {
    const result = await apiRequest(
      `/examiner/examinations/${exam.id}/complete`,
      {
        method: 'PATCH'
      }
    )

    message.value = result.message || 'Examination marked as completed.'

    await loadExaminations()

  } catch (err) {
    error.value = err.message || 'Unable to complete examination.'
  } finally {
    completingId.value = null
  }
}


// Fetch examinations when the page is mounted
onMounted(loadExaminations)

</script>

<style scoped>

.examination-section {
  border: 1px solid #d9e1ec;
  border-radius: 7px;
  box-shadow: none;
}

.examination-section .card-body {
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

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #edf0f4;
  font-size: 14px;
}

.detail-row span {
  color: #6c757d;
}

.detail-row strong {
  text-align: right;
}

@media (max-width: 576px) {
  .detail-row {
    flex-direction: column;
    gap: 3px;
  }

  .detail-row strong {
    text-align: left;
  }
}

</style>
