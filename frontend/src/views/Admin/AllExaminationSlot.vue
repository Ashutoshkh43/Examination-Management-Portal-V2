<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary mb-1">Home / admin / Slots</div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">All Examination Slots</h3>
      <button class="btn btn-primary btn-sm" @click="openCreate">+ Create Slot</button>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <div class="row g-3 mb-3">
      <div v-for="card in summaryCards" :key="card.label" class="col-6 col-xl-3">
        <div class="card h-100">
          <div class="card-body">
            <div class="text-secondary">{{ card.label }}</div>
            <div class="summary-number">{{ card.value }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="awaitingExaminations.length" class="alert alert-info py-2">
      Examinations appear directly in this table when created. Rows marked <strong>Not Scheduled</strong> do not have a bookable date and time yet.
    </div>

    <div class="card mb-3">
      <div class="card-body d-flex flex-wrap gap-2">
        <input v-model="search" class="form-control search-input" type="search" placeholder="Search...">
        <select v-model="examinerFilter" class="form-select filter-select">
          <option value="">All Examiners</option>
          <option v-for="examiner in examiners" :key="examiner.id" :value="String(examiner.id)">
            {{ examiner.fullname }}
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
                <th>Examination</th>
                <th>Examiner</th>
                <th>Date</th>
                <th>Time</th>
                <th>Capacity</th>
                <th>Available Seats</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-4">Loading slots...</td>
              </tr>
              <tr v-else-if="slotTableRows.length === 0">
                <td colspan="8" class="text-center py-4 text-secondary">
                  No examination slots match these filters.
                </td>
              </tr>
              <tr v-for="slot in slotTableRows" :key="slot.id">
                <td>{{ slot.examination_name }} <small v-if="slot.isUnscheduled" class="d-block text-secondary">Examination #{{ slot.examination_id }} · {{ slot.examination_status }}</small></td>
                <td>{{ slot.examiner_name || 'Not Assigned' }}</td>
                <td>{{ slot.date }}</td>
                <td>{{ slot.end_time ? `${slot.start_time}–${slot.end_time}` : '—' }}</td>
                <td>{{ slot.capacity }}</td>
                <td>{{ slot.available_seats }}</td>
                <td>
                  <span class="badge rounded-pill" :class="statusClass(slot.status)">
                    {{ slot.status }}
                  </span>
                </td>
                <td>
                  <div v-if="!slot.isUnscheduled" class="d-flex gap-1">
                    <button class="btn btn-outline-primary btn-sm" @click="viewSlot(slot)">View</button>
                    <button class="btn btn-outline-secondary btn-sm" :disabled="busy || slot.status === 'Cancelled'" @click="openReschedule(slot)">
                      Reschedule
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" :disabled="busy || slot.status === 'Cancelled'" @click="openReassign(slot)">
                      Reassign
                    </button>
                    <button class="btn btn-outline-danger btn-sm" :disabled="busy || slot.status === 'Cancelled'" @click="cancelSlot(slot)">
                      Cancel
                    </button>
                  </div>
                  <span v-else class="text-secondary small">No timed slot yet</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ modalTitle }}</h5>
            <button class="btn-close" :disabled="busy" aria-label="Close" @click="closeModal" />
          </div>
          <div class="modal-body">
            <form v-if="modalMode === 'create'" @submit.prevent="createSlot">
              <div v-if="creationExaminations.length === 0" class="alert alert-info">No examination is currently in Slot Creation status.</div>
              <label class="form-label">Examination *</label>
              <select v-model="slotForm.examination_id" class="form-select mb-3" required @change="loadCreationExaminers">
                <option value="" disabled>Select examination</option>
                <option v-for="exam in creationExaminations" :key="exam.id" :value="String(exam.id)">{{ exam.examination_name }} ({{ exam.course_code }})</option>
              </select>
              <label class="form-label">Assigned Examiner *</label>
              <select v-model="slotForm.examiner_id" class="form-select mb-3" required>
                <option value="" disabled>Select examiner</option>
                <option v-for="examiner in creationExaminers" :key="examiner.id" :value="String(examiner.id)">{{ examiner.fullname }}</option>
              </select>
              <label class="form-label">Date *</label><input v-model="slotForm.date" class="form-control mb-3" type="date" required>
              <div class="row"><div class="col-sm-6"><label class="form-label">Start Time *</label><input v-model="slotForm.start_time" class="form-control mb-3" type="time" required></div><div class="col-sm-6"><label class="form-label">End Time *</label><input v-model="slotForm.end_time" class="form-control mb-3" type="time" required></div></div>
              <label class="form-label">Capacity *</label><input v-model.number="slotForm.capacity" class="form-control mb-3" type="number" min="1" required>
              <label class="form-label">Meeting Link</label><input v-model.trim="slotForm.meeting_link" class="form-control" type="url" maxlength="500">
              <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>
              <div class="d-flex justify-content-end gap-2 mt-4"><button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">Cancel</button><button class="btn btn-primary btn-sm" :disabled="busy || creationExaminations.length === 0">{{ busy ? 'Creating...' : 'Create Slot' }}</button></div>
            </form>
            <div v-if="modalMode === 'view'">
              <p><strong>Examination:</strong> {{ selectedSlot?.examination_name }}</p>
              <p><strong>Examiner:</strong> {{ selectedSlot?.examiner_name || 'Not Assigned' }}</p>
              <p><strong>Date:</strong> {{ selectedSlot?.date }}</p>
              <p><strong>Time:</strong> {{ selectedSlot?.start_time }}–{{ selectedSlot?.end_time }}</p>
              <p><strong>Booked:</strong> {{ selectedSlot?.booked_count }} of {{ selectedSlot?.capacity }}</p>
              <p><strong>Meeting link:</strong> {{ selectedSlot?.meeting_link || '—' }}</p>
            </div>

            <form v-else-if="modalMode === 'reschedule'" @submit.prevent="saveReschedule">
              <label class="form-label">Date *</label>
              <input v-model="slotForm.date" class="form-control mb-3" type="date" required>
              <label class="form-label">Start Time *</label>
              <input v-model="slotForm.start_time" class="form-control mb-3" type="time" required>
              <label class="form-label">End Time *</label>
              <input v-model="slotForm.end_time" class="form-control" type="time" required>
              <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">Cancel</button>
                <button class="btn btn-primary btn-sm" :disabled="busy">{{ busy ? 'Saving...' : 'Save' }}</button>
              </div>
            </form>

            <form v-else-if="modalMode === 'reassign'" @submit.prevent="saveReassignment">
              <label class="form-label">Examiner</label>
              <select v-model="slotForm.examiner_id" class="form-select">
                <option value="" disabled>Select an assigned examiner</option>
                <option v-for="examiner in slotExaminers" :key="examiner.id" :value="String(examiner.id)">
                  {{ examiner.fullname }}
                </option>
              </select>
              <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">Cancel</button>
                <button class="btn btn-primary btn-sm" :disabled="busy">{{ busy ? 'Saving...' : 'Save' }}</button>
              </div>
            </form>

            <div v-else-if="modalMode !== 'create'" class="d-flex justify-content-end">
              <button class="btn btn-secondary btn-sm" @click="closeModal">Close</button>
            </div>
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

const slots = ref([])
const awaitingExaminations = ref([])
const examiners = ref([])
const slotExaminers = ref([])
const search = ref('')
const examinerFilter = ref('')
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')
const showModal = ref(false)
const modalMode = ref('view')
const modalError = ref('')
const selectedSlot = ref(null)
const slotForm = ref({ examination_id: '', date: '', start_time: '', end_time: '', capacity: 1, meeting_link: '', examiner_id: '' })
const creationExaminations = ref([])
const creationExaminers = ref([])

const modalTitle = computed(() => ({
  create: 'Create Examination Slot',
  view: 'Slot Details',
  reschedule: 'Reschedule Slot',
  reassign: 'Reassign Examiner'
}[modalMode.value]))

const summaryCards = computed(() => [
  { label: 'Total Slots', value: slots.value.length },
  { label: 'Available', value: slots.value.filter(slot => slot.status === 'Available').length },
  { label: 'Full', value: slots.value.filter(slot => slot.status === 'Full').length },
  { label: 'Cancelled', value: slots.value.filter(slot => slot.status === 'Cancelled').length },
  { label: 'Unscheduled Examinations', value: awaitingExaminations.value.length }
])

const filteredSlots = computed(() => {
  const query = search.value.trim().toLowerCase()
  return slots.value.filter(slot => {
    const text = `${slot.id} ${slot.examination_name} ${slot.examiner_name} ${slot.date}`.toLowerCase()
    return text.includes(query)
      && (!examinerFilter.value || String(slot.examiner_id ?? '') === examinerFilter.value)
  })
})
const filteredAwaitingExaminations = computed(() => {
  const query = search.value.trim().toLowerCase()
  return awaitingExaminations.value.filter(exam => {
    const matchesText = `${exam.id} ${exam.examination_name} ${exam.course_code} ${exam.examiner_name} ${exam.status}`.toLowerCase().includes(query)
    return matchesText && (!examinerFilter.value || String(exam.examiner_id ?? '') === examinerFilter.value)
  })
})
const slotTableRows = computed(() => [
  ...filteredAwaitingExaminations.value.map(exam => ({
    id: `exam-${exam.id}`,
    examination_id: exam.id,
    examination_name: exam.examination_name,
    course_code: exam.course_code,
    examiner_id: exam.examiner_id,
    examiner_name: exam.examiner_name,
    examination_status: exam.status,
    date: '—',
    start_time: '—',
    end_time: '',
    capacity: '—',
    available_seats: '—',
    status: 'Not Scheduled',
    isUnscheduled: true
  })),
  ...filteredSlots.value.map(slot => ({ ...slot, isUnscheduled: false }))
])

function statusClass(status) {
  return {
    Available: 'text-bg-success',
    Full: 'text-bg-danger',
    Cancelled: 'text-bg-secondary',
    'Not Scheduled': 'text-bg-warning'
  }[status] || 'text-bg-secondary'
}

async function openCreate() {
  slotForm.value = { examination_id: '', date: '', start_time: '', end_time: '', capacity: 1, meeting_link: '', examiner_id: '' }
  creationExaminations.value = []
  creationExaminers.value = []
  modalMode.value = 'create'
  modalError.value = ''
  showModal.value = true
  try {
    const data = await apiRequest('/admin/examinations')
    creationExaminations.value = (data.examinations || []).filter(exam => exam.status === 'Slot Creation')
    if (creationExaminations.value.length) {
      slotForm.value.examination_id = String(creationExaminations.value[0].id)
      await loadCreationExaminers()
    }
  } catch (err) {
    modalError.value = err.message || 'Could not load examinations.'
  }
}

async function loadCreationExaminers() {
  slotForm.value.examiner_id = ''
  creationExaminers.value = []
  if (!slotForm.value.examination_id) return
  try {
    const data = await apiRequest(`/admin/slot-examiners?examination_id=${slotForm.value.examination_id}`)
    creationExaminers.value = data.examiners || []
    if (creationExaminers.value.length === 1) {
      slotForm.value.examiner_id = String(creationExaminers.value[0].id)
    }
  } catch (err) {
    modalError.value = err.message || 'Could not load assigned examiners.'
  }
}

async function createSlot() {
  if (!slotForm.value.examination_id || !slotForm.value.examiner_id || !slotForm.value.date || !slotForm.value.start_time || !slotForm.value.end_time || Number(slotForm.value.capacity) < 1) {
    modalError.value = 'Complete all required fields.'
    return
  }
  if (slotForm.value.end_time <= slotForm.value.start_time) {
    modalError.value = 'End time must be later than start time.'
    return
  }

  busy.value = true
  modalError.value = ''
  try {
    const result = await apiRequest('/admin/slots', {
      method: 'POST',
      body: JSON.stringify({
        examination_id: Number(slotForm.value.examination_id),
        examiner_id: Number(slotForm.value.examiner_id),
        date: slotForm.value.date,
        start_time: slotForm.value.start_time,
        end_time: slotForm.value.end_time,
        capacity: Number(slotForm.value.capacity),
        meeting_link: slotForm.value.meeting_link
      })
    })
    showModal.value = false
    message.value = result.message || 'Examination slot created.'
    examinerFilter.value = ''
    search.value = ''
    await loadData()
  } catch (err) {
    modalError.value = err.message || 'Could not create slot.'
  } finally {
    busy.value = false
  }
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [slotData, examinerData] = await Promise.all([
      apiRequest('/admin/slots'),
      apiRequest('/admin/examiners')
    ])
    slots.value = (slotData.slots || []).map(slot => ({
      ...slot,
      examination_name: slot.examination_name || slot.examination?.examination_name || '',
      examiner_name: slot.examiner_name || slot.examiner?.fullname || '',
      capacity: slot.capacity ?? slot.maximum_student_capacity ?? 0,
      available_seats: slot.available_seats ?? 0,
      booked_count: slot.booked_count ?? Math.max(0, (slot.capacity ?? slot.maximum_student_capacity ?? 0) - (slot.available_seats ?? 0)),
      status: slot.status || 'Available'
    }))
    awaitingExaminations.value = slotData.awaiting_examinations || []
    examiners.value = examinerData.examiners || []
  } catch (err) {
    error.value = err.message || 'Could not load slots.'
  } finally {
    loading.value = false
  }
}

function viewSlot(slot) {
  selectedSlot.value = slot
  modalMode.value = 'view'
  modalError.value = ''
  showModal.value = true
}

function openReschedule(slot) {
  selectedSlot.value = slot
  slotForm.value = {
    date: slot.date || '',
    start_time: slot.start_time || '',
    end_time: slot.end_time || '',
    examiner_id: ''
  }
  modalMode.value = 'reschedule'
  modalError.value = ''
  showModal.value = true
}

async function openReassign(slot) {
  selectedSlot.value = slot
  slotForm.value = {
    date: '',
    start_time: '',
    end_time: '',
    examiner_id: slot.examiner_id == null ? '' : String(slot.examiner_id)
  }
  modalMode.value = 'reassign'
  modalError.value = ''
  showModal.value = true
  slotExaminers.value = []
  try {
    const data = await apiRequest(`/admin/slot-examiners?examination_id=${slot.examination_id}`)
    slotExaminers.value = data.examiners || []
  } catch (err) {
    modalError.value = err.message || 'Could not load assigned examiners.'
  }
}

function closeModal() {
  if (!busy.value) showModal.value = false
}

async function saveReschedule() {
  if (!selectedSlot.value || slotForm.value.end_time <= slotForm.value.start_time) {
    modalError.value = 'Enter an end time after the start time.'
    return
  }

  busy.value = true
  modalError.value = ''
  try {
    const result = await apiRequest(`/admin/slots/${selectedSlot.value.id}/reschedule`, {
      method: 'PATCH',
      body: JSON.stringify({
        date: slotForm.value.date,
        start_time: slotForm.value.start_time,
        end_time: slotForm.value.end_time
      })
    })
    message.value = result.message || 'Slot rescheduled.'
    showModal.value = false
    await loadData()
  } catch (err) {
    modalError.value = err.message || 'Could not reschedule slot.'
  } finally {
    busy.value = false
  }
}

async function saveReassignment() {
  busy.value = true
  modalError.value = ''
  try {
    const examinerId = slotForm.value.examiner_id
    const result = await apiRequest(`/admin/slots/${selectedSlot.value.id}/reassign`, {
      method: 'PATCH',
      body: JSON.stringify({ examiner_id: examinerId ? Number(examinerId) : null })
    })
    message.value = result.message || 'Examiner updated.'
    showModal.value = false
    await loadData()
  } catch (err) {
    modalError.value = err.message || 'Could not reassign examiner.'
  } finally {
    busy.value = false
  }
}

async function cancelSlot(slot) {
  if (!window.confirm(`Cancel the slot for "${slot.examination_name}"?`)) return

  busy.value = true
  error.value = ''
  message.value = ''
  try {
    const result = await apiRequest(`/admin/slots/${slot.id}/cancel`, { method: 'PATCH' })
    message.value = result.message || 'Slot cancelled.'
    await loadData()
  } catch (err) {
    error.value = err.message || 'Could not cancel slot.'
  } finally {
    busy.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.search-input {
  max-width: 260px;
}
.filter-select {
  max-width: 220px;
}
.summary-number {
  color: #0f2447;
  font-size: 1.6rem;
  font-weight: 700;
}
</style>
