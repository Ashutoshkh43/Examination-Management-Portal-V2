<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary mb-1">Home / admin / Results</div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
      <h3 class="mb-0">Publish Results</h3>
      <button class="btn btn-primary btn-sm" :disabled="busy || publishableCount === 0" @click="publishResults">Publish Results</button>
    </div>
    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <div class="row g-3 mb-3">
      <div v-for="card in cards" :key="card.label" class="col-6 col-lg-3"><div class="card h-100"><div class="card-body"><div class="small text-secondary">{{ card.label }}</div><div class="fs-4 fw-bold">{{ card.value }}</div></div></div></div>
    </div>
    <div class="alert alert-info py-2">Only evaluations submitted by examiners can be published.</div>
    <div class="card mb-3"><div class="card-body d-flex flex-wrap gap-2">
      <input v-model="search" class="form-control search" type="search" placeholder="Search student, examination, or ID">
      <select v-model="resultFilter" class="form-select filter"><option value="">All result statuses</option><option value="Published">Published</option><option value="Pending">Pending</option></select>
    </div></div>
    <div class="card"><div class="table-responsive"><table class="table table-sm align-middle mb-0">
      <thead class="table-light"><tr><th>Student</th><th>Examination</th><th>Course</th><th>Marks</th><th>Evaluation Status</th><th>Result Status</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-if="loading"><td colspan="7" class="text-center py-4">Loading results…</td></tr>
        <tr v-else-if="visibleResults.length === 0"><td colspan="7" class="text-center text-secondary py-4">No examination records found.</td></tr>
        <tr v-for="row in visibleResults" :key="row.booking_id">
          <td>{{ row.student_name }}<br><small class="text-secondary">{{ row.registration_number }}</small></td><td>{{ row.examination_name }}</td><td>{{ row.course_code }}</td>
          <td>{{ row.total_marks == null ? '—' : `${row.total_marks} / ${row.maximum_marks}` }}</td><td>{{ row.evaluation_status }}</td>
          <td><span class="badge" :class="row.result_published ? 'text-bg-success' : 'text-bg-secondary'">{{ row.result_published ? 'Published' : 'Pending' }}</span></td>
          <td><button class="btn btn-outline-primary btn-sm" @click="view(row)">View Evaluation</button></td>
        </tr>
      </tbody>
    </table></div></div>

    <div v-if="selected" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" @click.self="selected = null">
      <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Evaluation Details</h5><button class="btn-close" @click="selected = null" /></div>
        <div class="modal-body">
          <p><b>Student:</b> {{ selected.student_name }} ({{ selected.registration_number }})</p><p><b>Examination:</b> {{ selected.examination_name }} — {{ selected.course_code }}</p>
          <p><b>Exam date:</b> {{ selected.date }}</p><p><b>Total:</b> {{ selected.total_marks ?? '—' }} / {{ selected.maximum_marks }}</p>
          <div class="table-responsive"><table class="table table-sm"><thead><tr><th>Criterion</th><th>Marks</th><th>Maximum</th></tr></thead><tbody>
            <tr v-for="(criterion, index) in selected.criteria" :key="index"><td>{{ criterion.criterion_name }}</td><td>{{ criterion.marks_obtained }}</td><td>{{ criterion.maximum_marks }}</td></tr>
            <tr v-if="!selected.criteria?.length"><td colspan="3" class="text-secondary">No criterion marks recorded.</td></tr>
          </tbody></table></div>
          <p><b>Remarks:</b> {{ selected.remarks || '—' }}</p>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary btn-sm" @click="selected = null">Close</button></div>
      </div></div>
    </div><div v-if="selected" class="modal-backdrop show" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '../../services/api.js'

const results = ref([])
const search = ref('')
const resultFilter = ref('')
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')
const selected = ref(null)
const cards = computed(() => [
  { label: 'Examination Records', value: results.value.length },
  { label: 'Evaluated', value: results.value.filter(row => ['Submitted', 'Evaluated'].includes(row.evaluation_status)).length },
  { label: 'Published', value: results.value.filter(row => row.result_published).length },
  { label: 'Awaiting Evaluation', value: results.value.filter(row => row.evaluation_status === 'Pending').length }
])
const publishableCount = computed(() => results.value.filter(row => ['Submitted', 'Evaluated'].includes(row.evaluation_status) && !row.result_published).length)
const visibleResults = computed(() => {
  const q = search.value.trim().toLowerCase()
  return results.value.filter(row => (!resultFilter.value || (row.result_published ? 'Published' : 'Pending') === resultFilter.value)
    && `${row.booking_id} ${row.student_name} ${row.registration_number} ${row.examination_id} ${row.examination_name} ${row.course_code}`.toLowerCase().includes(q))
})
async function loadResults() {
  loading.value = true; error.value = ''
  try { const data = await apiRequest('/admin/results'); results.value = data.results || [] }
  catch (err) { error.value = err.message || 'Could not load results.' }
  finally { loading.value = false }
}
function view(row) { selected.value = row }
async function publishResults() {
  if (!window.confirm('Publish all submitted examination results?')) return
  busy.value = true; error.value = ''; message.value = ''
  try { const data = await apiRequest('/admin/results/publish', { method: 'POST' }); message.value = data.message || 'Results published.'; await loadResults() }
  catch (err) { error.value = err.message || 'Could not publish results.' }
  finally { busy.value = false }
}
onMounted(loadResults)
</script>

<style scoped>
.search { max-width: 340px; }
.filter { max-width: 210px; }
</style>
