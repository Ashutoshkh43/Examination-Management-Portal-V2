import 
<template>
    <div class="container-fluid p-3">

        <!-- Page Heading -->
        <div class="mb-4">
            <div class="text-secondary small mb-2">
                Home / admin / Manage Students
            </div>

            <h6 class="fw-bold mb-0">Manage Students</h6>
        </div>

        <!-- Success Message -->
        <div v-if="message" class="alert alert-success py-2">
            {{ message }}
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger py-2">
            {{ error }}
        </div>

        <!-- Search Bar -->
        <div class="card mb-3">
            <div class="card-body p-3">
                <input
                    v-model="search"
                    type="search"
                    class="form-control"
                    style="max-width: 260px;"
                    placeholder="Search..."
                    aria-label="Search students"
                >
            </div>
        </div>

        <!-- Students Table -->
        <div class="card">
            <div class="card-body p-3">

                <div class="table-responsive">
                    <table class="table table-sm align-middle mb-0">

                        <thead class="table-light">
                            <tr>
                                <th>Student Name</th>
                                <th>Registration Number</th>
                                <th>Email</th>
                                <th>Department</th>
                                <th>Status</th>
                                <th>Bookings</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="student in filteredStudents"
                                :key="student.id"
                            >
                                <td class="text-nowrap">
                                    {{ student.fullname }}
                                </td>

                                <td>
                                    {{ student.registration_number || '-' }}
                                </td>

                                <td>
                                    {{ student.email }}
                                </td>

                                <td>
                                    {{ student.department || '-' }}
                                </td>

                                <td>
                                    <span
                                        class="badge rounded-pill"
                                        :class="student.status === 'active'
                                            ? 'text-bg-success'
                                            : 'text-bg-secondary'"
                                    >
                                        {{
                                            student.status === 'active'
                                                ? 'Active'
                                                : 'Inactive'
                                        }}
                                    </span>
                                </td>

                                <td>{{ student.bookings }}</td>

                                <td>
                                    <div class="d-flex gap-1">
                                        <button
                                            class="btn btn-outline-primary btn-sm"
                                            :disabled="busy"
                                            @click="viewStudent(student)"
                                        >
                                            View
                                        </button>

                                        <button
                                            class="btn btn-outline-secondary btn-sm"
                                            :disabled="busy"
                                            @click="openEditModal(student)"
                                        >
                                            Edit
                                        </button>

                                        <button
                                            class="btn btn-outline-danger btn-sm"
                                            :disabled="busy"
                                            @click="changeStatus(student)"
                                        >
                                            {{
                                                student.status === 'active'
                                                    ? 'Deactivate'
                                                    : 'Activate'
                                            }}
                                        </button>
                                    </div>
                                </td>
                            </tr>

                            <tr v-if="loading">
                                <td
                                    colspan="7"
                                    class="text-center text-secondary py-4"
                                >
                                    Loading students...
                                </td>
                            </tr>

                            <tr
                                v-if="!loading && filteredStudents.length === 0"
                            >
                                <td
                                    colspan="7"
                                    class="text-center text-secondary py-4"
                                >
                                    No students found.
                                </td>
                            </tr>
                        </tbody>

                    </table>
                </div>

            </div>
        </div>

        <!-- View / Edit Modal -->
        <div
            v-if="showModal"
            class="modal d-block"
            tabindex="-1"
            role="dialog"
            aria-modal="true"
            @click.self="closeModal"
        >
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">

                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            {{
                                modalMode === 'edit'
                                    ? 'Edit Student'
                                    : 'Student Details'
                            }}
                        </h5>

                        <button
                            type="button"
                            class="btn-close"
                            aria-label="Close"
                            :disabled="busy"
                            @click="closeModal"
                        ></button>
                    </div>

                    <!-- Edit Form -->
                    <div
                        v-if="modalMode === 'edit'"
                        class="modal-body"
                    >
                        <form @submit.prevent="saveStudent">

                            <div class="row g-3">

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Student Name *
                                    </label>

                                    <input
                                        v-model.trim="form.fullname"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Email *
                                    </label>

                                    <input
                                        v-model.trim="form.email"
                                        type="email"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Registration Number *
                                    </label>

                                    <input
                                        v-model.trim="form.registration_number"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Department
                                    </label>

                                    <input
                                        v-model.trim="form.department"
                                        type="text"
                                        class="form-control"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Semester
                                    </label>

                                    <input
                                        v-model.trim="form.semester"
                                        type="text"
                                        class="form-control"
                                    >
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label">
                                        Contact
                                    </label>

                                    <input
                                        v-model.trim="form.contact"
                                        type="text"
                                        class="form-control"
                                    >
                                </div>

                            </div>

                            <div
                                v-if="modalError"
                                class="alert alert-danger py-2 mt-3 mb-0"
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
                                    Cancel
                                </button>

                                <button
                                    type="submit"
                                    class="btn btn-primary btn-sm"
                                    :disabled="busy"
                                >
                                    {{
                                        busy ? 'Saving...' : 'Save Changes'
                                    }}
                                </button>
                            </div>

                        </form>
                    </div>

                    <!-- View Student Details -->
                    <div
                        v-else-if="selectedStudent"
                        class="modal-body"
                    >
                        <div class="row g-3">

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Student Name
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.fullname }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Email
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.email }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Registration Number
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.registration_number || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Department
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.department || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Semester
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.semester || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Contact
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.contact || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Status
                                </div>
                                <span
                                    class="badge rounded-pill"
                                    :class="selectedStudent.status === 'active'
                                        ? 'text-bg-success'
                                        : 'text-bg-secondary'"
                                >
                                    {{ selectedStudent.status }}
                                </span>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Total Bookings
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedStudent.bookings }}
                                </div>
                            </div>

                        </div>

                        <div class="d-flex justify-content-end gap-2 mt-4">
                            <button
                                class="btn btn-secondary btn-sm"
                                @click="closeModal"
                            >
                                Close
                            </button>

                            <button
                                class="btn btn-primary btn-sm"
                                @click="openEditModal(selectedStudent)"
                            >
                                Edit Student
                            </button>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <!-- Modal Backdrop -->
        <div
            v-if="showModal"
            class="modal-backdrop show"
        ></div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiRequest } from '../../services/api.js'

const students = ref([])
const search = ref('')

const loading = ref(false)
const busy = ref(false)

const showModal = ref(false)
const modalMode = ref('view')
const selectedStudent = ref(null)

const message = ref('')
const error = ref('')
const modalError = ref('')

const emptyForm = () => ({
    fullname: '',
    email: '',
    registration_number: '',
    department: '',
    semester: '',
    contact: ''
})

const form = ref(emptyForm())


// Filter students using the search box.
const filteredStudents = computed(() => {
    const query = search.value.trim().toLowerCase()

    if (!query) {
        return students.value
    }

    return students.value.filter((student) => {
        return [
            student.fullname,
            student.registration_number,
            student.email,
            student.department,
            student.semester,
            student.status
        ].some((value) =>
            String(value || '').toLowerCase().includes(query)
        )
    })
})


// Load students from Flask.
function loadStudents() {
    loading.value = true
    error.value = ''

    apiRequest('/admin/students')
        .then((data) => {
            students.value = (data.students || []).map((student) => ({
                ...student,
                bookings: student.bookings ?? 0
            }))
        })
        .catch((err) => {
            error.value =
                err.message || 'Could not load students.'
        })
        .finally(() => {
            loading.value = false
        })
}


// View student details.
function viewStudent(student) {
    selectedStudent.value = student
    modalMode.value = 'view'
    modalError.value = ''
    showModal.value = true
}


// Open the Edit Student modal.
function openEditModal(student) {
    selectedStudent.value = student
    modalMode.value = 'edit'

    form.value = {
        fullname: student.fullname || '',
        email: student.email || '',
        registration_number: student.registration_number || '',
        department: student.department || '',
        semester: student.semester || '',
        contact: student.contact || ''
    }

    modalError.value = ''
    showModal.value = true
}


// Close the modal.
function closeModal() {
    if (busy.value) {
        return
    }

    showModal.value = false
    modalError.value = ''
}


// Save student edits.
function saveStudent() {
    if (!selectedStudent.value) {
        return
    }

    busy.value = true
    modalError.value = ''
    message.value = ''

    apiRequest(
        `/admin/students/${selectedStudent.value.id}`,
        {
            method: 'PUT',
            body: JSON.stringify(form.value)
        }
    )
        .then((data) => {
            message.value =
                data.message || 'Student updated successfully.'

            showModal.value = false
            loadStudents()
        })
        .catch((err) => {
            modalError.value =
                err.message || 'Could not update student.'
        })
        .finally(() => {
            busy.value = false
        })
}


// Activate or deactivate a student.
function changeStatus(student) {
    const newStatus = student.status === 'active'
        ? 'inactive'
        : 'active'

    const action = newStatus === 'inactive'
        ? 'deactivate'
        : 'activate'

    if (!window.confirm(
        `Are you sure you want to ${action} ${student.fullname}?`
    )) {
        return
    }

    busy.value = true
    error.value = ''
    message.value = ''

    apiRequest(
        `/admin/students/${student.id}/status`,
        {
            method: 'PATCH',
            body: JSON.stringify({
                status: newStatus
            })
        }
    )
        .then((data) => {
            message.value =
                data.message || 'Student status updated.'

            loadStudents()
        })
        .catch((err) => {
            error.value =
                err.message || 'Could not update student status.'
        })
        .finally(() => {
            busy.value = false
        })
}


onMounted(() => {
    loadStudents()
})
</script>
