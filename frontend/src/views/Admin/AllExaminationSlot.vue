<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary mb-1">Home / admin / Slots</div>
    <h3 class="mb-3">All Examination Slots</h3>

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
              <tr v-else-if="filteredSlots.length === 0">
                <td colspan="8" class="text-center py-4">No slots found.</td>
              </tr>
              <tr v-for="slot in filteredSlots" :key="slot.id">
                <td>{{ slot.examination_name }}</td>
                <td>{{ slot.examiner_name || 'Not Assigned' }}</td>
                <td>{{ slot.date }}</td>
                <td>{{ slot.start_time }}–{{ slot.end_time }}</td>
                <td>{{ slot.capacity }}</td>
                <td>{{ slot.available_seats }}</td>
                <td>
                  <span class="badge rounded-pill" :class="statusClass(slot.status)">
                    {{ slot.status }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-1">
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
                <option value="">Not Assigned</option>
                <option v-for="examiner in examiners" :key="examiner.id" :value="String(examiner.id)">
                  {{ examiner.fullname }}
                </option>
              </select>
              <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">Cancel</button>
                <button class="btn btn-primary btn-sm" :disabled="busy">{{ busy ? 'Saving...' : 'Save' }}</button>
              </div>
            </form>

            <div v-else class="d-flex justify-content-end">
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
const examiners = ref([])
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
const slotForm = ref({ date: '', start_time: '', end_time: '', examiner_id: '' })

const modalTitle = computed(() => ({
  view: 'Slot Details',
  reschedule: 'Reschedule Slot',
  reassign: 'Reassign Examiner'
}[modalMode.value]))

const summaryCards = computed(() => [
  { label: 'Total Slots', value: slots.value.length },
  { label: 'Available', value: slots.value.filter(slot => slot.status === 'Available').length },
  { label: 'Full', value: slots.value.filter(slot => slot.status === 'Full').length },
  { label: 'Cancelled', value: slots.value.filter(slot => slot.status === 'Cancelled').length }
])

const filteredSlots = computed(() => {
  const query = search.value.trim().toLowerCase()
  return slots.value.filter(slot => {
    const text = `${slot.examination_name} ${slot.examiner_name} ${slot.date}`.toLowerCase()
    return text.includes(query)
      && (!examinerFilter.value || String(slot.examiner_id ?? '') === examinerFilter.value)
  })
})

function statusClass(status) {
  return {
    Available: 'text-bg-success',
    Full: 'text-bg-danger',
    Cancelled: 'text-bg-secondary'
  }[status] || 'text-bg-secondary'
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

function openReassign(slot) {
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
    const result = await apiRequest(`/admin/slots/${selectedSlot.value.id}`, {
      method: 'PUT',
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
    const result = await apiRequest(`/admin/slots/${selectedSlot.value.id}/examiner`, {
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