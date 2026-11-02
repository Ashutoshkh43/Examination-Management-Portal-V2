<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary mb-1">Home / admin / Examinations</div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">Manage Examinations</h3>
      <button class="btn btn-primary btn-sm" @click="openAdd">
        + Add Examination
      </button>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <div class="card mb-3">
      <div class="card-body d-flex flex-wrap align-items-center gap-2">
        <template v-for="(status, index) in statuses" :key="status">
          <span class="status-step">
            {{ status }} ({{ statusCounts[status] || 0 }})
          </span>
          <span v-if="index < statuses.length - 1" class="text-secondary">→</span>
        </template>
      </div>
    </div>

    <div class="card mb-3">
      <div class="card-body d-flex flex-wrap gap-2">
        <input
          v-model="search"
          class="form-control"
          type="search"
          placeholder="Search..."
          aria-label="Search examinations"
        >
        <select v-model="courseFilter" class="form-select filter-select">
          <option value="">All Courses</option>
          <option v-for="course in courses" :key="course.id" :value="String(course.id)">
            {{ course.course_code }} — {{ course.course_name }}
          </option>
        </select>
        <select v-model="statusFilter" class="form-select filter-select">
          <option value="">All Statuses</option>
          <option v-for="status in statuses" :key="status" :value="status">
            {{ status }}
          </option>
        </select>
      </div>
    </div>

    <div class="card">
      <div class="card-body p-3">
        <div class="table-responsive">
          <table class="table table-sm align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Examination Name</th>
                <th>Course</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Maximum Marks</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4">Loading examinations...</td>
              </tr>
              <tr v-else-if="filteredExaminations.length === 0">
                <td colspan="7" class="text-center py-4">No examinations found.</td>
              </tr>
              <tr v-for="exam in filteredExaminations" :key="exam.id">
                <td>{{ exam.examination_name }}</td>
                <td>{{ exam.course_code }}</td>
                <td>{{ exam.examination_type }}</td>
                <td>{{ exam.duration }} mins</td>
                <td>{{ exam.maximum_marks }}</td>
                <td>
                  <span class="badge rounded-pill" :class="statusClass(exam.status)">
                    {{ exam.status }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-outline-secondary btn-sm" :disabled="busy" @click="openEdit(exam)">
                      Edit
                    </button>
                    <button class="btn btn-outline-primary btn-sm" @click="openView(exam)">
                      View
                    </button>
                    <button class="btn btn-outline-danger btn-sm" :disabled="busy" @click="deleteExam(exam)">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ modalTitle }}</h5>
            <button class="btn-close" :disabled="busy" aria-label="Close" @click="closeModal" />
          </div>

          <div class="modal-body">
            <form @submit.prevent="saveExam">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Examination Name *</label>
                  <input v-model.trim="form.examination_name" class="form-control" required :disabled="isView">
                </div>

                <div class="col-md-6">
                  <label class="form-label">Course *</label>
                  <select v-model="form.course_id" class="form-select" required :disabled="isView">
                    <option value="" disabled>Select course</option>
                    <option v-for="course in courses" :key="course.id" :value="String(course.id)">
                      {{ course.course_code }} — {{ course.course_name }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Examination Type *</label>
                  <select v-model="form.examination_type" class="form-select" required :disabled="isView">
                    <option value="" disabled>Select type</option>
                    <option v-for="type in examinationTypes" :key="type" :value="type">{{ type }}</option>
                  </select>
                </div>

                <div class="col-md-3">
                  <label class="form-label">Duration (mins) *</label>
                  <input v-model.number="form.duration" class="form-control" type="number" min="1" required :disabled="isView">
                </div>

                <div class="col-md-3">
                  <label class="form-label">Maximum Marks *</label>
                  <input v-model.number="form.maximum_marks" class="form-control" type="number" min="0.01" step="any" required :disabled="isView">
                </div>

                <div class="col-md-6">
                  <label class="form-label">Slot Creation Start *</label>
                  <input v-model="form.slot_creation_start" class="form-control" type="datetime-local" required :disabled="isView">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Slot Creation End *</label>
                  <input v-model="form.slot_creation_end" class="form-control" type="datetime-local" required :disabled="isView">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Booking Start *</label>
                  <input v-model="form.slot_booking_start" class="form-control" type="datetime-local" required :disabled="isView">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Booking End *</label>
                  <input v-model="form.slot_booking_end" class="form-control" type="datetime-local" required :disabled="isView">
                </div>

                <div v-if="mode === 'edit'" class="col-md-6">
                  <label class="form-label">Status</label>
                  <select v-model="form.status" class="form-select">
                    <option v-for="status in statuses" :key="status" :value="status">{{ status }}</option>
                  </select>
                </div>
              </div>

              <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">
                  {{ isView ? 'Close' : 'Cancel' }}
                </button>
                <button v-if="!isView" type="submit" class="btn btn-primary btn-sm" :disabled="busy">
                  {{ busy ? 'Saving...' : 'Save Examination' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showModal" class="modal-backdrop show" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '../../services/api.js'

const statuses = ['Draft', 'Slot Creation', 'Booking Open', 'Closed', 'Completed']
const examinationTypes = ['Viva', 'Practical', 'Project Demo', 'Assessment']

const examinations = ref([])
const courses = ref([])
const search = ref('')
const courseFilter = ref('')
const statusFilter = ref('')
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')
const modalError = ref('')
const showModal = ref(false)
const mode = ref('add')
const editingId = ref(null)

const emptyForm = () => ({
  examination_name: '',
  course_id: '',
  examination_type: '',
  duration: 30,
  maximum_marks: 30,
  slot_creation_start: '',
  slot_creation_end: '',
  slot_booking_start: '',
  slot_booking_end: '',
  status: 'Draft'
})

const form = ref(emptyForm())
const isView = computed(() => mode.value === 'view')
const modalTitle = computed(() => ({
  add: 'Add Examination',
  edit: 'Edit Examination',
  view: 'Examination Details'
}[mode.value]))

const statusCounts = computed(() => Object.fromEntries(
  statuses.map(status => [
    status,
    examinations.value.filter(exam => exam.status === status).length
  ])
))

const filteredExaminations = computed(() => {
  const query = search.value.trim().toLowerCase()
  return examinations.value.filter(exam => {
    const searchable = [
      exam.examination_name,
      exam.course_code,
      exam.course_name,
      exam.examination_type,
      exam.status
    ].join(' ').toLowerCase()

    return searchable.includes(query)
      && (!courseFilter.value || String(exam.course_id) === courseFilter.value)
      && (!statusFilter.value || exam.status === statusFilter.value)
  })
})

function statusClass(status) {
  return {
    Draft: 'text-bg-warning',
    'Slot Creation': 'text-bg-primary',
    'Booking Open': 'text-bg-success',
    Closed: 'text-bg-secondary',
    Completed: 'text-bg-dark'
  }[status] || 'text-bg-secondary'
}

function toDateInput(value) {
  return value ? String(value).slice(0, 16) : ''
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [examData, courseData] = await Promise.all([
      apiRequest('/admin/examinations'),
      apiRequest('/admin/courses')
    ])
    examinations.value = examData.examinations || []
    courses.value = (courseData.courses || []).filter(course => course.status === 'active')
  } catch (err) {
    error.value = err.message || 'Could not load examinations.'
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingId.value = null
  form.value = emptyForm()
  mode.value = 'add'
  modalError.value = ''
  message.value = ''
  showModal.value = true
}

function openEdit(exam) {
  editingId.value = exam.id
  form.value = {
    examination_name: exam.examination_name || '',
    course_id: String(exam.course_id ?? ''),
    examination_type: exam.examination_type || '',
    duration: exam.duration ?? 30,
    maximum_marks: exam.maximum_marks ?? 30,
    slot_creation_start: toDateInput(exam.slot_creation_start),
    slot_creation_end: toDateInput(exam.slot_creation_end),
    slot_booking_start: toDateInput(exam.slot_booking_start),
    slot_booking_end: toDateInput(exam.slot_booking_end),
    status: exam.status || 'Draft'
  }
  mode.value = 'edit'
  modalError.value = ''
  message.value = ''
  showModal.value = true
}

function openView(exam) {
  openEdit(exam)
  mode.value = 'view'
}

function closeModal() {
  if (!busy.value) showModal.value = false
}

function validateForm() {
  const value = form.value
  if (!value.course_id || !value.examination_name || !value.examination_type) {
    return 'Please fill in all required fields.'
  }
  if (!value.slot_creation_start || !value.slot_creation_end ||
      !value.slot_booking_start || !value.slot_booking_end) {
    return 'Please enter all scheduling dates.'
  }
  if (value.slot_creation_start > value.slot_creation_end ||
      value.slot_booking_start > value.slot_booking_end) {
    return 'Each start date must be before its end date.'
  }
  return ''
}

async function saveExam() {
  modalError.value = validateForm()
  if (modalError.value) return

  busy.value = true
  try {
    const editing = mode.value === 'edit'
    const payload = {
      ...form.value,
      course_id: Number(form.value.course_id)
    }
    const result = await apiRequest(
      editing ? `/admin/examinations/${editingId.value}` : '/admin/examinations',
      {
        method: editing ? 'PUT' : 'POST',
        body: JSON.stringify(payload)
      }
    )
    message.value = result.message || 'Examination saved successfully.'
    showModal.value = false
    await loadData()
  } catch (err) {
    modalError.value = err.message || 'Could not save examination.'
  } finally {
    busy.value = false
  }
}

async function deleteExam(exam) {
  if (!window.confirm(`Delete "${exam.examination_name}"?`)) return

  busy.value = true
  error.value = ''
  message.value = ''
  try {
    const result = await apiRequest(`/admin/examinations/${exam.id}`, { method: 'DELETE' })
    message.value = result.message || 'Examination deleted successfully.'
    await loadData()
  } catch (err) {
    error.value = err.message || 'Could not delete examination.'
  } finally {
    busy.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.status-step {
  padding: 4px 10px;
  border-radius: 4px;
  background: #e0e7ff;
  color: #263b68;
  font-size: 0.875rem;
}
.filter-select {
  max-width: 220px;
}
</style>