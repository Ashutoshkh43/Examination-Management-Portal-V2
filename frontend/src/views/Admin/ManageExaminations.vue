
<template>
    <div class="container-fluid p-3">

        <!-- Heading -->
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <div class="small text-secondary mb-2">
                    Home / admin / Manage Examinations
                </div>
                <h6 class="fw-bold mb-0">Manage Examinations</h6>
            </div>

            <button class="btn btn-primary btn-sm" @click="openAdd">
                + Add Examination
            </button>
        </div>

        <!-- Messages -->
        <div v-if="message" class="alert alert-success py-2">
            {{ message }}
        </div>

        <div v-if="error" class="alert alert-danger py-2">
            {{ error }}
        </div>

        <!-- Examination Status Pipeline -->
        <div class="card mb-4">
            <div class="card-body d-flex flex-wrap align-items-center gap-2">
                <template
                    v-for="(status, index) in statusNames"
                    :key="status"
                >
                    <button
                        class="btn btn-sm"
                        :class="selectedStatus === status
                            ? 'btn-primary'
                            : 'btn-light'"
                        @click="selectStatus(status)"
                    >
                        {{ status }}
                        ( {{ statusCounts[status] || 0 }} )
                    </button>

                    <span
                        v-if="index < statusNames.length - 1"
                        class="text-secondary"
                    >
                        →
                    </span>
                </template>

                <button
                    v-if="selectedStatus"
                    class="btn btn-outline-secondary btn-sm ms-auto"
                    @click="selectStatus('')"
                >
                    Clear Filter
                </button>
            </div>
        </div>

        <!-- Search -->
        <div class="card mb-3">
            <div class="card-body p-3">
                <input
                    v-model="search"
                    type="search"
                    class="form-control"
                    style="max-width: 260px;"
                    placeholder="Search..."
                >
            </div>
        </div>

        <!-- Table -->
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
                            <tr
                                v-for="exam in filteredExaminations"
                                :key="exam.id"
                            >
                                <td>{{ exam.examination_name }}</td>
                                <td>{{ exam.course_code }}</td>
                                <td>{{ exam.examination_type }}</td>
                                <td>{{ exam.duration }} mins</td>
                                <td>{{ exam.maximum_marks }}</td>

                                <td>
                                    <span
                                        class="badge rounded-pill"
                                        :class="statusClass(exam.status)"
                                    >
                                        {{ exam.status }}
                                    </span>
                                </td>

                                <td>
                                    <div class="d-flex gap-1">
                                        <button
                                            class="btn btn-outline-secondary btn-sm"
                                            :disabled="busy"
                                            @click="openEdit(exam)"
                                        >
                                            Edit
                                        </button>

                                        <button
                                            class="btn btn-outline-primary btn-sm"
                                            :disabled="busy"
                                            @click="viewExam(exam)"
                                        >
                                            View
                                        </button>

                                        <button
                                            class="btn btn-outline-danger btn-sm"
                                            :disabled="busy"
                                            @click="deleteExam(exam)"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </td>
                            </tr>

                            <tr v-if="loading">
                                <td colspan="7" class="text-center py-4">
                                    Loading examinations...
                                </td>
                            </tr>

                            <tr
                                v-if="!loading && filteredExaminations.length === 0"
                            >
                                <td colspan="7" class="text-center py-4">
                                    No examinations found.
                                </td>
                            </tr>
                        </tbody>

                    </table>
                </div>
            </div>
        </div>

        <!-- Add / Edit / View Modal -->
        <div
            v-if="showModal"
            class="modal d-block"
            tabindex="-1"
            role="dialog"
            aria-modal="true"
            @click.self="closeModal"
        >
            <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
                <div class="modal-content">

                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            {{ modalTitle }}
                        </h5>

                        <button
                            class="btn-close"
                            :disabled="busy"
                            @click="closeModal"
                        ></button>
                    </div>

                    <div class="modal-body">
                        <form @submit.prevent="saveExam">

                            <div class="row g-3">

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Examination Name *
                                    </label>
                                    <input
                                        v-model.trim="form.examination_name"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Course *
                                    </label>
                                    <select
                                        v-model="form.course_id"
                                        class="form-select"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                        <option value="" disabled>
                                            Select course
                                        </option>
                                        <option
                                            v-for="course in courses"
                                            :key="course.id"
                                            :value="String(course.id)"
                                        >
                                            {{ course.course_code }} -
                                            {{ course.course_name }}
                                        </option>
                                    </select>
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Examination Type *
                                    </label>
                                    <select
                                        v-model="form.examination_type"
                                        class="form-select"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                        <option value="" disabled>
                                            Select type
                                        </option>
                                        <option>Viva</option>
                                        <option>Practical</option>
                                        <option>Project Demo</option>
                                        <option>Assessment</option>
                                    </select>
                                </div>

                                <div class="col-md-3">
                                    <label class="form-label">
                                        Duration (mins) *
                                    </label>
                                    <input
                                        v-model.number="form.duration"
                                        type="number"
                                        min="1"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div class="col-md-3">
                                    <label class="form-label">
                                        Maximum Marks *
                                    </label>
                                    <input
                                        v-model.number="form.maximum_marks"
                                        type="number"
                                        min="0.01"
                                        step="any"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Slot Creation Start *
                                    </label>
                                    <input
                                        v-model="form.slot_creation_start"
                                        type="datetime-local"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Slot Creation End *
                                    </label>
                                    <input
                                        v-model="form.slot_creation_end"
                                        type="datetime-local"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Booking Start *
                                    </label>
                                    <input
                                        v-model="form.slot_booking_start"
                                        type="datetime-local"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Booking End *
                                    </label>
                                    <input
                                        v-model="form.slot_booking_end"
                                        type="datetime-local"
                                        class="form-control"
                                        required
                                        :disabled="modalMode === 'view'"
                                    >
                                </div>

                                <div
                                    v-if="modalMode === 'edit'"
                                    class="col-md-6"
                                >
                                    <label class="form-label">
                                        Status
                                    </label>
                                    <select
                                        v-model="form.status"
                                        class="form-select"
                                    >
                                        <option>Draft</option>
                                        <option>Slot Creation</option>
                                        <option>Booking Open</option>
                                        <option>Closed</option>
                                        <option>Completed</option>
                                    </select>
                                </div>

                            </div>

                            <div
                                v-if="modalError"
                                class="alert alert-danger mt-3 mb-0"
                            >
                                {{ modalError }}
                            </div>

                            <div class="d-flex justify-content-end gap-2 mt-4">
                                <button
                                    type="button"
                                    class="btn btn-secondary btn-sm"
                                    :disabled="busy"
                                    @click="closeModal"
                                >
                                    {{ modalMode === 'view' ? 'Close' : 'Cancel' }}
                                </button>

                                <button
                                    v-if="modalMode !== 'view'"
                                    type="submit"
                                    class="btn btn-primary btn-sm"
                                    :disabled="busy"
                                >
                                    {{ busy ? 'Saving...' : 'Save Examination' }}
                                </button>
                            </div>

                        </form>
                    </div>

                </div>
            </div>
        </div>

        <div v-if="showModal" class="modal-backdrop show"></div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiRequest } from '../../services/api.js'

const examinations = ref([])
const courses = ref([])

const search = ref('')
const selectedStatus = ref('')

const loading = ref(false)
const busy = ref(false)

const message = ref('')
const error = ref('')
const modalError = ref('')

const showModal = ref(false)
const modalMode = ref('add')

const statusNames = [
    'Draft',
    'Slot Creation',
    'Booking Open',
    'Closed',
    'Completed'
]

const statusCounts = ref({
    'Draft': 0,
    'Slot Creation': 0,
    'Booking Open': 0,
    'Closed': 0,
    'Completed': 0
})

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

const modalTitle = computed(() => {
    if (modalMode.value === 'add') {
        return 'Add Examination'
    }

    if (modalMode.value === 'edit') {
        return 'Edit Examination'
    }

    return 'Examination Details'
})

const filteredExaminations = computed(() => {
    const query = search.value.trim().toLowerCase()

    return examinations.value.filter((exam) => {
        const matchesSearch = [
            exam.examination_name,
            exam.course_code,
            exam.course_name,
            exam.examination_type,
            exam.status
        ].some((value) =>
            String(value || '').toLowerCase().includes(query)
        )

        const matchesStatus = !selectedStatus.value
            || exam.status === selectedStatus.value

        return matchesSearch && matchesStatus
    })
})

function statusClass(status) {
    const classes = {
        'Draft': 'text-bg-warning',
        'Slot Creation': 'text-bg-primary',
        'Booking Open': 'text-bg-success',
        'Closed': 'text-bg-secondary',
        'Completed': 'text-bg-dark'
    }

    return classes[status] || 'text-bg-secondary'
}

function toInputDate(value) {
    if (!value) {
        return ''
    }

    return value.slice(0, 16)
}

function selectStatus(status) {
    selectedStatus.value = selectedStatus.value === status
        ? ''
        : status
}

function loadExaminations() {
    loading.value = true
    error.value = ''

    apiRequest('/admin/examinations')
        .then((data) => {
            examinations.value = data.examinations || []

            statusCounts.value = {
                ...statusCounts.value,
                ...(data.status_counts || {})
            }
        })
        .catch((err) => {
            error.value =
                err.message || 'Could not load examinations.'
        })
        .finally(() => {
            loading.value = false
        })
}

function loadCourses() {
    return apiRequest('/admin/courses')
        .then((data) => {
            courses.value = (data.courses || []).filter(
                (course) => course.status === 'active'
            )
        })
        .catch((err) => {
            error.value = err.message || 'Could not load courses.'
        })
}

function openAdd() {
    form.value = emptyForm()
    modalMode.value = 'add'
    modalError.value = ''
    message.value = ''
    showModal.value = true
}

function openEdit(exam) {
    form.value = {
        examination_name: exam.examination_name,
        course_id: String(exam.course_id),
        examination_type: exam.examination_type,
        duration: exam.duration,
        maximum_marks: exam.maximum_marks,
        slot_creation_start: toInputDate(exam.slot_creation_start),
        slot_creation_end: toInputDate(exam.slot_creation_end),
        slot_booking_start: toInputDate(exam.slot_booking_start),
        slot_booking_end: toInputDate(exam.slot_booking_end),
        status: exam.status
    }

    modalMode.value = 'edit'
    modalError.value = ''
    message.value = ''
    showModal.value = true
}

function viewExam(exam) {
    openEdit(exam)
    modalMode.value = 'view'
}

function closeModal() {
    if (busy.value) {
        return
    }

    showModal.value = false
    modalError.value = ''
}

function saveExam() {
    if (
        !form.value.slot_creation_start
        || !form.value.slot_creation_end
        || !form.value.slot_booking_start
        || !form.value.slot_booking_end
    ) {
        modalError.value = 'Please enter all scheduling dates.'
        return
    }

    busy.value = true
    modalError.value = ''
    message.value = ''

    const payload = {
        ...form.value,
        course_id: Number(form.value.course_id),
        slot_creation_start: form.value.slot_creation_start,
        slot_creation_end: form.value.slot_creation_end,
        slot_booking_start: form.value.slot_booking_start,
        slot_booking_end: form.value.slot_booking_end
    }

    const isEditing = modalMode.value === 'edit'

    const endpoint = isEditing
        ? `/admin/examinations/${editingId.value}`
        : '/admin/examinations'

    apiRequest(endpoint, {
        method: isEditing ? 'PUT' : 'POST',
        body: JSON.stringify(payload)
    })
        .then((data) => {
            message.value =
                data.message || 'Examination saved successfully.'

            showModal.value = false
            loadExaminations()
        })
        .catch((err) => {
            modalError.value =
                err.message || 'Could not save examination.'
        })
        .finally(() => {
            busy.value = false
        })
}

const editingId = ref(null)

// Keep track of the selected examination when opening Edit or View.
const originalOpenEdit = openEdit

function openEditWithId(exam) {
    editingId.value = exam.id
    originalOpenEdit(exam)
}

// Replace the actions with ID-aware versions.
function deleteExam(exam) {
    if (!window.confirm(
        `Are you sure you want to delete "${exam.examination_name}"?`
    )) {
        return
    }

    busy.value = true
    error.value = ''
    message.value = ''

    apiRequest(`/admin/examinations/${exam.id}`, {
        method: 'DELETE'
    })
        .then((data) => {
            message.value =
                data.message || 'Examination deleted successfully.'

            loadExaminations()
        })
        .catch((err) => {
            error.value =
                err.message || 'Could not delete examination.'
        })
        .finally(() => {
            busy.value = false
        })
}

onMounted(() => {
    loadExaminations()
    loadCourses()
})
</script>
