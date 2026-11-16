<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary">Home / examiner / Slots</div>
    <div class="d-flex justify-content-between align-items-center my-2">
      <h3 class="m-0">Manage Examination Slots</h3>
      <button
        class="btn btn-primary btn-sm"
        :disabled="eligibleExaminations.length === 0"
        @click="openCreate"
      >
        + Create Slot
      </button>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <div v-if="!loading && eligibleExaminations.length === 0" class="alert alert-info py-2">
      No assigned examination is currently in Slot Creation status.
    </div>

    <div class="card">
      <div class="card-body p-3 table-responsive">
        <table class="table table-sm align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Date</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Examination</th>
              <th>Capacity</th>
              <th>Available Seats</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4">Loading slots...</td>
            </tr>
            <tr v-else-if="slots.length === 0">
              <td colspan="7" class="text-center py-4">No slots found. Create a slot for an assigned examination.</td>
            </tr>
            <tr v-for="slot in slots" :key="slot.id">
              <td>{{ slot.date }}</td>
              <td>{{ slot.start_time }}</td>
              <td>{{ slot.end_time }}</td>
              <td>{{ slot.examination_name }}</td>
              <td>{{ slot.capacity }}</td>
              <td>{{ slot.available_seats }}</td>
              <td><span class="badge rounded-pill" :class="statusClass(slot.status)">{{ slot.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="modal d-block" tabindex="-1" aria-modal="true" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Slot</h5>
            <button class="btn-close" :disabled="busy" aria-label="Close" @click="closeModal" />
          </div>
          <form @submit.prevent="createSlot">
            <div class="modal-body">
              <label class="form-label">Examination *</label>
              <select v-model="form.examination_id" class="form-select mb-3" required>
                <option value="" disabled>Select examination</option>
                <option v-for="exam in eligibleExaminations" :key="exam.id" :value="String(exam.id)">
                  {{ exam.examination_name }} — {{ exam.course_code }}
                </option>
              </select>

              <label class="form-label">Date *</label>
              <input v-model="form.date" class="form-control mb-3" type="date" required>

              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label class="form-label">Start Time *</label>
                  <input v-model="form.start_time" class="form-control" type="time" required>
                </div>
                <div class="col-6">
                  <label class="form-label">End Time *</label>
                  <input v-model="form.end_time" class="form-control" type="time" required>
                </div>
              </div>

              <label class="form-label">Maximum Student Capacity *</label>
              <input v-model.number="form.capacity" class="form-control mb-3" type="number" min="1" required>

              <label class="form-label">Meeting Link</label>
              <input v-model.trim="form.meeting_link" class="form-control" type="url" maxlength="500">

              <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">Cancel</button>
              <button class="btn btn-primary btn-sm" :disabled="busy">
                {{ busy ? 'Saving...' : 'Save Slot' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-if="showModal" class="modal-backdrop show" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '../../services/api.js'

const examinations = ref([])
const slots = ref([])
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')
const modalError = ref('')
const showModal = ref(false)
const eligibleExaminations = computed(() =>
  examinations.value.filter(exam => exam.status === 'Slot Creation')
)

const emptyForm = () => ({
  examination_id: '',
  date: '',
  start_time: '',
  end_time: '',
  capacity: 5,
  meeting_link: ''
})
const form = ref(emptyForm())

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
    const [examData, slotData] = await Promise.all([
      apiRequest('/examiner/examinations'),
      apiRequest('/examiner/slots')
    ])
    examinations.value = examData.examinations || []
    slots.value = slotData.slots || []
  } catch (err) {
    error.value = err.message || 'Could not load examiner slots.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.value = emptyForm()
  form.value.examination_id = String(eligibleExaminations.value[0]?.id || '')
  modalError.value = ''
  message.value = ''
  showModal.value = true
}

function closeModal() {
  if (!busy.value) showModal.value = false
}

async function createSlot() {
  if (!form.value.examination_id) {
    modalError.value = 'Select an examination.'
    return
  }
  if (form.value.end_time <= form.value.start_time) {
    modalError.value = 'End time must be later than start time.'
    return
  }
  if (!(Number(form.value.capacity) > 0)) {
    modalError.value = 'Capacity must be greater than zero.'
    return
  }

  busy.value = true
  modalError.value = ''
  try {
    const result = await apiRequest('/examiner/slots', {
      method: 'POST',
      body: JSON.stringify({
        ...form.value,
        examination_id: Number(form.value.examination_id),
        capacity: Number(form.value.capacity)
      })
    })
    message.value = result.message || 'Slot created successfully.'
    showModal.value = false
    await loadData()
  } catch (err) {
    modalError.value = err.message || 'Could not create slot.'
  } finally {
    busy.value = false
  }
}

onMounted(loadData)
</script>
