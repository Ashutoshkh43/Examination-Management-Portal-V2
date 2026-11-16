<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary mb-1">Home / admin / Bookings</div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
      <h3 class="mb-0">All Bookings</h3>
      <button class="btn btn-outline-secondary btn-sm" :disabled="loading" @click="loadData">Refresh</button>
    </div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div class="row g-3 mb-3">
      <div v-for="card in cards" :key="card.label" class="col-6 col-lg-3">
        <div class="card h-100"><div class="card-body"><div class="small text-secondary">{{ card.label }}</div><div class="fs-4 fw-bold">{{ card.value }}</div></div></div>
      </div>
    </div>
    <div class="card mb-3"><div class="card-body d-flex flex-wrap gap-2">
      <input v-model="search" class="form-control search" type="search" placeholder="Search student or examination">
      <select v-model="statusFilter" class="form-select filter"><option value="">All statuses</option><option>Booked</option><option>Completed</option><option>Cancelled</option></select>
    </div></div>
    <div class="card"><div class="table-responsive"><table class="table table-sm align-middle mb-0">
      <thead class="table-light"><tr><th>Student</th><th>Examination</th><th>Course</th><th>Examiner</th><th>Date &amp; Time</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-if="loading"><td colspan="7" class="text-center py-4">Loading bookings…</td></tr>
        <tr v-else-if="visibleBookings.length === 0"><td colspan="7" class="text-center text-secondary py-4">{{ bookings.length ? 'No bookings match these filters.' : 'No bookings have been made yet.' }}</td></tr>
        <tr v-for="booking in visibleBookings" :key="booking.id">
          <td><div>{{ booking.student_name }}</div><small class="text-secondary">{{ booking.registration_number }}</small></td>
          <td>{{ booking.examination_name }}</td><td>{{ booking.course_code }}</td><td>{{ booking.examiner_name }}</td>
          <td>{{ booking.date }}<br><small>{{ booking.start_time }}–{{ booking.end_time }}</small></td>
          <td><span class="badge" :class="booking.status === 'Booked' ? 'text-bg-success' : booking.status === 'Cancelled' ? 'text-bg-secondary' : 'text-bg-primary'">{{ booking.status }}</span></td>
          <td><div class="d-flex flex-wrap gap-1">
            <button class="btn btn-outline-primary btn-sm" @click="viewBooking(booking)">View</button>
            <button class="btn btn-outline-secondary btn-sm" :disabled="busy || booking.status !== 'Booked'" @click="openReschedule(booking)">Reschedule</button>
            <button class="btn btn-outline-secondary btn-sm" :disabled="busy || booking.status !== 'Booked'" @click="openReassign(booking)">Reassign</button>
            <button class="btn btn-outline-danger btn-sm" :disabled="busy || booking.status !== 'Booked'" @click="cancelBooking(booking)">Cancel</button>
          </div></td>
        </tr>
      </tbody>
    </table></div></div>

    <div v-if="modal" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">{{ modalTitle }}</h5><button class="btn-close" :disabled="busy" @click="closeModal" /></div>
        <div class="modal-body">
          <template v-if="mode === 'view'">
            <p><b>Student:</b> {{ selected?.student_name }} ({{ selected?.registration_number }})</p><p><b>Examination:</b> {{ selected?.examination_name }} — {{ selected?.course_code }}</p>
            <p><b>Examiner:</b> {{ selected?.examiner_name }}</p><p><b>Slot:</b> {{ selected?.date }}, {{ selected?.start_time }}–{{ selected?.end_time }}</p>
            <p><b>Booked:</b> {{ selected?.booking_date }}</p><p><b>Status:</b> {{ selected?.status }}</p>
          </template>
          <template v-else-if="mode === 'reschedule'"><label class="form-label">New slot</label><select v-model="form.slot_id" class="form-select"><option value="" disabled>Select an available slot</option><option v-for="slot in candidateSlots" :key="slot.id" :value="String(slot.id)">{{ slot.date }} · {{ slot.start_time }}–{{ slot.end_time }} ({{ slot.available_seats }} seats)</option></select></template>
          <template v-else><label class="form-label">Examiner</label><select v-model="form.examiner_id" class="form-select"><option value="" disabled>Select an examiner assigned to this examination</option><option v-for="examiner in eligibleExaminers" :key="examiner.id" :value="String(examiner.id)">{{ examiner.fullname }}</option></select><small class="text-secondary">Examiner is stored on the slot, so this changes the examiner for all bookings in that slot.</small></template>
          <div v-if="modalError" class="alert alert-danger mt-3 mb-0">{{ modalError }}</div>
        </div>
        <div v-if="mode !== 'view'" class="modal-footer"><button class="btn btn-secondary btn-sm" :disabled="busy" @click="closeModal">Close</button><button class="btn btn-primary btn-sm" :disabled="busy || (mode === 'reschedule' ? !form.slot_id : !form.examiner_id)" @click="saveAction">{{ busy ? 'Saving…' : 'Save' }}</button></div>
        <div v-else class="modal-footer"><button class="btn btn-secondary btn-sm" @click="closeModal">Close</button></div>
      </div></div>
    </div><div v-if="modal" class="modal-backdrop show" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '../../services/api.js'

const bookings = ref([])
const search = ref('')
const statusFilter = ref('')
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')
const modalError = ref('')
const modal = ref(false)
const mode = ref('view')
const selected = ref(null)
const candidateSlots = ref([])
const eligibleExaminers = ref([])
const form = ref({ slot_id: '', examiner_id: '' })

const cards = computed(() => [
  { label: 'Total Bookings', value: bookings.value.length },
  { label: 'Booked', value: bookings.value.filter(row => row.status === 'Booked').length },
  { label: 'Completed', value: bookings.value.filter(row => row.status === 'Completed').length },
  { label: 'Cancelled', value: bookings.value.filter(row => row.status === 'Cancelled').length }
])
const visibleBookings = computed(() => {
  const q = search.value.trim().toLowerCase()
  return bookings.value.filter(row => (!statusFilter.value || row.status === statusFilter.value)
    && `${row.id} ${row.student_id} ${row.registration_number} ${row.examination_id} ${row.slot_id} ${row.student_name} ${row.examination_name} ${row.examiner_name} ${row.course_code}`.toLowerCase().includes(q))
})
const modalTitle = computed(() => ({ view: 'Booking Details', reschedule: 'Reschedule Booking', reassign: 'Reassign Slot Examiner' }[mode.value]))

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiRequest('/admin/bookings')
    bookings.value = data.bookings || []
  } catch (err) {
    error.value = err.message || 'Could not load bookings.'
  } finally {
    loading.value = false
  }
}
function viewBooking(booking) { selected.value = booking; mode.value = 'view'; modalError.value = ''; modal.value = true }
function closeModal() { if (!busy.value) modal.value = false }
async function openReschedule(booking) {
  selected.value = booking; mode.value = 'reschedule'; modalError.value = ''; form.value = { slot_id: '' }; candidateSlots.value = []; modal.value = true
  try {
    const data = await apiRequest('/admin/slots')
    candidateSlots.value = (data.slots || []).filter(slot => slot.examination_id === booking.examination_id && slot.id !== booking.slot_id && slot.status !== 'Cancelled' && slot.available_seats > 0)
  } catch (err) { modalError.value = err.message || 'Could not load available slots.' }
}
async function openReassign(booking) {
  selected.value = booking; mode.value = 'reassign'; modalError.value = ''; form.value = { examiner_id: String(booking.examiner_id || '') }; eligibleExaminers.value = []; modal.value = true
  try {
    const data = await apiRequest(`/admin/slot-examiners?examination_id=${booking.examination_id}`)
    eligibleExaminers.value = data.examiners || []
  } catch (err) { modalError.value = err.message || 'Could not load assigned examiners.' }
}
async function saveAction() {
  busy.value = true; modalError.value = ''
  try {
    const isReschedule = mode.value === 'reschedule'
    const endpoint = isReschedule ? 'reschedule' : 'reassign'
    const body = isReschedule ? { slot_id: Number(form.value.slot_id) } : { examiner_id: Number(form.value.examiner_id) }
    const result = await apiRequest(`/admin/bookings/${selected.value.id}/${endpoint}`, { method: 'PATCH', body: JSON.stringify(body) })
    message.value = result.message || 'Booking updated.'
    modal.value = false
    await loadData()
  } catch (err) { modalError.value = err.message || 'Could not update the booking.' }
  finally { busy.value = false }
}
async function cancelBooking(booking) {
  if (!window.confirm(`Cancel ${booking.student_name}'s booking for ${booking.examination_name}?`)) return
  busy.value = true; error.value = ''; message.value = ''
  try { const result = await apiRequest(`/admin/bookings/${booking.id}/cancel`, { method: 'PATCH' }); message.value = result.message || 'Booking cancelled.'; await loadData() }
  catch (err) { error.value = err.message || 'Could not cancel booking.' }
  finally { busy.value = false }
}
onMounted(loadData)
</script>

<style scoped>
.search { max-width: 320px; }
.filter { max-width: 190px; }
</style>
