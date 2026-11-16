<template>
  <div class="container-fluid p-3">
    <div class="small text-secondary mb-1">Home / admin / Rubrics</div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
      <h3 class="mb-0">Evaluation Rubrics</h3>
      <button class="btn btn-primary btn-sm" :disabled="examinations.length === 0" @click="openCreate">+ Add Rubric</button>
    </div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="examinations.length === 0 && !loading" class="alert alert-info">Create an examination before adding rubric criteria.</div>
    <div class="card mb-3"><div class="card-body d-flex flex-wrap gap-2">
      <input v-model="search" class="form-control search" type="search" placeholder="Search criterion or examination">
      <select v-model="examinationFilter" class="form-select filter"><option value="">All examinations</option><option v-for="exam in examinations" :key="exam.id" :value="String(exam.id)">{{ exam.examination_name }}</option></select>
    </div></div>
    <div class="card"><div class="table-responsive"><table class="table table-sm align-middle mb-0">
      <thead class="table-light"><tr><th>Rubric / Criterion</th><th>Examination</th><th>Course</th><th>Maximum Marks</th><th>Weightage</th><th>Description</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-if="loading"><td colspan="7" class="text-center py-4">Loading rubrics…</td></tr>
        <tr v-else-if="visibleRubrics.length === 0"><td colspan="7" class="text-center text-secondary py-4">{{ rubrics.length ? 'No rubrics match these filters.' : 'No rubric criteria have been added yet.' }}</td></tr>
        <tr v-for="rubric in visibleRubrics" :key="rubric.id">
          <td class="fw-semibold">{{ rubric.criterion_name }}</td><td>{{ rubric.examination_name }}</td><td>{{ rubric.course_code }}</td>
          <td>{{ rubric.maximum_marks }}</td><td>{{ rubric.weightage == null ? '—' : `${rubric.weightage}%` }}</td><td class="description">{{ rubric.description || '—' }}</td>
          <td><div class="d-flex gap-1"><button class="btn btn-outline-primary btn-sm" @click="openEdit(rubric)">Edit</button><button class="btn btn-outline-danger btn-sm" :disabled="busy" @click="deleteRubric(rubric)">Delete</button></div></td>
        </tr>
      </tbody>
    </table></div></div>

    <div v-if="showForm" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" @click.self="closeForm">
      <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
        <form @submit.prevent="saveRubric">
          <div class="modal-header"><h5 class="modal-title">{{ editing ? 'Edit Rubric' : 'Add Rubric' }}</h5><button type="button" class="btn-close" :disabled="busy" @click="closeForm" /></div>
          <div class="modal-body">
            <label class="form-label">Examination *</label><select v-model.number="form.examination_id" class="form-select mb-3" required><option disabled :value="null">Select examination</option><option v-for="exam in examinations" :key="exam.id" :value="exam.id">{{ exam.examination_name }} ({{ exam.course_code }})</option></select>
            <label class="form-label">Criterion Name *</label><input v-model.trim="form.criterion_name" class="form-control mb-3" maxlength="200" required>
            <div class="row"><div class="col-sm-6"><label class="form-label">Maximum Marks *</label><input v-model.number="form.maximum_marks" class="form-control mb-3" type="number" min="0.01" step="0.01" required></div><div class="col-sm-6"><label class="form-label">Weightage (%)</label><input v-model.number="form.weightage" class="form-control mb-3" type="number" min="0" max="100" step="0.01"></div></div>
            <label class="form-label">Description</label><textarea v-model.trim="form.description" class="form-control" rows="3" maxlength="2000" />
            <div v-if="formError" class="alert alert-danger mt-3 mb-0">{{ formError }}</div>
          </div>
          <div class="modal-footer"><button type="button" class="btn btn-secondary btn-sm" :disabled="busy" @click="closeForm">Cancel</button><button class="btn btn-primary btn-sm" :disabled="busy">{{ busy ? 'Saving…' : 'Save Rubric' }}</button></div>
        </form>
      </div></div>
    </div><div v-if="showForm" class="modal-backdrop show" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '../../services/api.js'

const rubrics = ref([])
const examinations = ref([])
const search = ref('')
const examinationFilter = ref('')
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')
const formError = ref('')
const showForm = ref(false)
const editing = ref(false)
const editingId = ref(null)
const blankForm = () => ({ examination_id: null, criterion_name: '', maximum_marks: 10, weightage: null, description: '' })
const form = ref(blankForm())

const visibleRubrics = computed(() => {
  const q = search.value.trim().toLowerCase()
  return rubrics.value.filter(row => (!examinationFilter.value || String(row.examination_id) === examinationFilter.value)
    && `${row.criterion_name} ${row.examination_name} ${row.course_code}`.toLowerCase().includes(q))
})

async function loadData() {
  loading.value = true; error.value = ''
  try {
    const [rubricData, examinationData] = await Promise.all([apiRequest('/admin/rubrics'), apiRequest('/admin/examinations')])
    rubrics.value = rubricData.rubrics || []
    examinations.value = examinationData.examinations || []
  } catch (err) { error.value = err.message || 'Could not load rubrics.' }
  finally { loading.value = false }
}
function openCreate() { editing.value = false; editingId.value = null; form.value = { ...blankForm(), examination_id: examinations.value[0]?.id ?? null }; formError.value = ''; showForm.value = true }
function openEdit(rubric) { editing.value = true; editingId.value = rubric.id; form.value = { examination_id: rubric.examination_id, criterion_name: rubric.criterion_name, maximum_marks: rubric.maximum_marks, weightage: rubric.weightage, description: rubric.description || '' }; formError.value = ''; showForm.value = true }
function closeForm() { if (!busy.value) showForm.value = false }
async function saveRubric() {
  if (!form.value.criterion_name || Number(form.value.maximum_marks) <= 0) { formError.value = 'Enter a criterion name and positive maximum marks.'; return }
  if (form.value.weightage !== null && (Number(form.value.weightage) < 0 || Number(form.value.weightage) > 100)) { formError.value = 'Weightage must be between 0 and 100.'; return }
  busy.value = true; formError.value = ''; error.value = ''; message.value = ''
  try {
    const endpoint = editing.value ? `/admin/rubrics/${editingId.value}` : '/admin/rubrics'
    const result = await apiRequest(endpoint, { method: editing.value ? 'PUT' : 'POST', body: JSON.stringify(form.value) })
    message.value = result.message || 'Rubric saved.'; showForm.value = false; await loadData()
  } catch (err) { formError.value = err.message || 'Could not save rubric.' }
  finally { busy.value = false }
}
async function deleteRubric(rubric) {
  if (!window.confirm(`Delete the rubric criterion “${rubric.criterion_name}”?`)) return
  busy.value = true; error.value = ''; message.value = ''
  try { const result = await apiRequest(`/admin/rubrics/${rubric.id}`, { method: 'DELETE' }); message.value = result.message || 'Rubric deleted.'; await loadData() }
  catch (err) { error.value = err.message || 'Could not delete rubric.' }
  finally { busy.value = false }
}
onMounted(loadData)
</script>

<style scoped>
.search { max-width: 320px; }
.filter { max-width: 260px; }
.description { min-width: 180px; max-width: 300px; white-space: normal; }
</style>
