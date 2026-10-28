
<template>
    <div class="container-fluid p-3">

        <!-- Page Heading -->
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <div class="text-secondary small mb-2">
                    Home / admin / Manage Examiners
                </div>

                <h6 class="fw-bold mb-0">Manage Examiners</h6>
            </div>

            <button
                class="btn btn-primary btn-sm px-3"
                @click="openAddModal"
            >
                + Add Examiner
            </button>
        </div>

        <!-- Success Message -->
        <div v-if="message" class="alert alert-success py-2">
            {{ message }}
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger py-2">
            {{ error }}
        </div>

        <!-- Examiner Table -->
        <div class="card">
            <div class="card-body p-3">
                <div class="table-responsive">
                    <table class="table table-sm align-middle mb-0">

                        <thead class="table-light">
                            <tr>
                                <th>Name</th>
                                <th>Employee ID</th>
                                <th>Department</th>
                                <th>Designation</th>
                                <th>Status</th>
                                <th>Assigned Examinations</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="examiner in examiners"
                                :key="examiner.id"
                            >
                                <td class="text-nowrap">
                                    {{ examiner.fullname }}
                                </td>

                                <td>{{ examiner.employee_id }}</td>

                                <td>
                                    {{ examiner.department || '-' }}
                                </td>

                                <td>
                                    {{ examiner.designation || '-' }}
                                </td>

                                <td>
                                    <span
                                        class="badge rounded-pill"
                                        :class="examiner.status === 'active'
                                            ? 'text-bg-success'
                                            : 'text-bg-secondary'"
                                    >
                                        {{
                                            examiner.status === 'active'
                                                ? 'Active'
                                                : 'Inactive'
                                        }}
                                    </span>
                                </td>

                                <td>
                                    {{ examiner.assigned_examinations ?? 0 }}
                                </td>

                                <td>
                                    <div class="d-flex gap-1">
                                        <button
                                            class="btn btn-outline-primary btn-sm"
                                            @click="viewExaminer(examiner)"
                                        >
                                            View
                                        </button>

                                        <button
                                            class="btn btn-outline-secondary btn-sm"
                                            :disabled="busy"
                                            @click="openEditModal(examiner)"
                                        >
                                            Edit
                                        </button>

                                        <button
                                            class="btn btn-outline-danger btn-sm"
                                            :disabled="busy"
                                            @click="changeStatus(examiner)"
                                        >
                                            {{
                                                examiner.status === 'active'
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
                                    Loading examiners...
                                </td>
                            </tr>

                            <tr v-if="!loading && examiners.length === 0">
                                <td
                                    colspan="7"
                                    class="text-center text-secondary py-4"
                                >
                                    No examiners found.
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
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">

                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            {{ modalTitle }}
                        </h5>

                        <button
                            type="button"
                            class="btn-close"
                            aria-label="Close"
                            :disabled="busy"
                            @click="closeModal"
                        ></button>
                    </div>

                    <!-- Add / Edit Form -->
                    <div
                        v-if="modalMode !== 'view'"
                        class="modal-body"
                    >
                        <form @submit.prevent="saveExaminer">

                            <div class="row g-3">

                                <!-- Full Name -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        Full Name *
                                    </label>

                                    <input
                                        v-model.trim="form.fullname"
                                        type="text"
                                        class="form-control"
                                        placeholder="Enter full name"
                                        required
                                    >
                                </div>

                                <!-- Email -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        Email *
                                    </label>

                                    <input
                                        v-model.trim="form.email"
                                        type="email"
                                        class="form-control"
                                        placeholder="Enter email address"
                                        required
                                    >
                                </div>

                                <!-- Employee ID -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        Employee ID *
                                    </label>

                                    <input
                                        v-model.trim="form.employee_id"
                                        type="text"
                                        class="form-control"
                                        placeholder="Enter employee ID"
                                        required
                                    >
                                </div>

                                <!-- Password -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        {{
                                            modalMode === 'edit'
                                                ? 'New Password (optional)'
                                                : 'Temporary Password *'
                                        }}
                                    </label>

                                    <input
                                        v-model="form.password"
                                        type="password"
                                        class="form-control"
                                        :placeholder="modalMode === 'edit'
                                            ? 'Leave blank to keep current password'
                                            : 'Enter temporary password'"
                                        minlength="8"
                                        autocomplete="new-password"
                                        :required="modalMode === 'add'"
                                    >

                                    <div
                                        v-if="modalMode === 'edit'"
                                        class="form-text"
                                    >
                                        
                                    </div>

                                    <div
                                        v-else
                                        class="form-text"
                                    >
                                        Password must contain at least 8 characters.
                                    </div>
                                </div>

                                <!-- Department -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        Department
                                    </label>

                                    <input
                                        v-model.trim="form.department"
                                        type="text"
                                        class="form-control"
                                        placeholder="Enter department"
                                    >
                                </div>

                                <!-- Designation -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        Designation
                                    </label>

                                    <input
                                        v-model.trim="form.designation"
                                        type="text"
                                        class="form-control"
                                        placeholder="Enter designation"
                                    >
                                </div>

                                <!-- Contact -->
                                <div class="col-md-6">
                                    <label class="form-label">
                                        Contact
                                    </label>

                                    <input
                                        v-model.trim="form.contact"
                                        type="text"
                                        class="form-control"
                                        placeholder="Enter contact number"
                                    >
                                </div>

                            </div>

                            <!-- Modal Error -->
                            <div
                                v-if="modalError"
                                class="alert alert-danger mt-3 mb-0"
                            >
                                {{ modalError }}
                            </div>

                            <!-- Form Buttons -->
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
                                        busy
                                            ? 'Saving...'
                                            : modalMode === 'edit'
                                                ? 'Save Changes'
                                                : 'Create Examiner'
                                    }}
                                </button>
                            </div>

                        </form>
                    </div>

                    <!-- View Examiner Details -->
                    <div
                        v-else-if="selectedExaminer"
                        class="modal-body"
                    >
                        <div class="row g-3">

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Full Name
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.fullname }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Email
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.email }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Employee ID
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.employee_id }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Department
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.department || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Designation
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.designation || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Contact
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.contact || '-' }}
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Status
                                </div>
                                <span
                                    class="badge rounded-pill"
                                    :class="selectedExaminer.status === 'active'
                                        ? 'text-bg-success'
                                        : 'text-bg-secondary'"
                                >
                                    {{ selectedExaminer.status }}
                                </span>
                            </div>

                            <div class="col-md-6">
                                <div class="text-secondary small">
                                    Assigned Examinations
                                </div>
                                <div class="fw-semibold">
                                    {{ selectedExaminer.assigned_examinations ?? 0 }}
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
                                @click="openEditModal(selectedExaminer)"
                            >
                                Edit Examiner
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
import { apiRequest } from '../services/api'

const examiners = ref([])

const loading = ref(false)
const busy = ref(false)

const showModal = ref(false)
const modalMode = ref('add')

const selectedExaminer = ref(null)

const message = ref('')
const error = ref('')
const modalError = ref('')

const emptyForm = () => ({
    fullname: '',
    email: '',
    employee_id: '',
    password: '',
    contact: '',
    department: '',
    designation: ''
})

const form = ref(emptyForm())

const modalTitle = computed(() => {
    if (modalMode.value === 'view') {
        return 'Examiner Details'
    }

    if (modalMode.value === 'edit') {
        return 'Edit Examiner'
    }

    return 'Create Examiner Account'
})


// Load examiners from the backend.
function loadExaminers() {
    loading.value = true
    error.value = ''

    apiRequest('/admin/examiners')
        .then((data) => {
            examiners.value = data.examiners || []
        })
        .catch((err) => {
            error.value =
                err.message || 'Could not load examiners.'
        })
        .finally(() => {
            loading.value = false
        })
}


// Open the Add Examiner modal.
function openAddModal() {
    modalMode.value = 'add'
    selectedExaminer.value = null
    form.value = emptyForm()

    modalError.value = ''
    message.value = ''
    error.value = ''

    showModal.value = true
}


// Open the Edit Examiner modal.
function openEditModal(examiner) {
    modalMode.value = 'edit'
    selectedExaminer.value = examiner

    modalError.value = ''
    error.value = ''

    form.value = {
        fullname: examiner.fullname || '',
        email: examiner.email || '',
        employee_id: examiner.employee_id || '',
        password: '',
        contact: examiner.contact || '',
        department: examiner.department || '',
        designation: examiner.designation || ''
    }

    showModal.value = true
}


// Open the View Examiner modal.
function viewExaminer(examiner) {
    modalMode.value = 'view'
    selectedExaminer.value = examiner

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


// Create or update an examiner.
function saveExaminer() {
    busy.value = true
    modalError.value = ''
    message.value = ''

    const isEditing = modalMode.value === 'edit'

    const examinerData = {
        fullname: form.value.fullname,
        email: form.value.email,
        employee_id: form.value.employee_id,
        contact: form.value.contact,
        department: form.value.department,
        designation: form.value.designation
    }

    // Add requires a password.
    // Edit sends a password only if the admin entered one.
    if (!isEditing || form.value.password) {
        examinerData.password = form.value.password
    }

    const request = isEditing
        ? apiRequest(
            `/admin/examiners/${selectedExaminer.value.id}`,
            {
                method: 'PUT',
                body: JSON.stringify(examinerData)
            }
        )
        : apiRequest(
            '/admin/examiners',
            {
                method: 'POST',
                body: JSON.stringify(examinerData)
            }
        )

    request
        .then((data) => {
            message.value = data.message || (
                isEditing
                    ? 'Examiner updated successfully.'
                    : 'Examiner created successfully.'
            )

            showModal.value = false
            form.value = emptyForm()

            loadExaminers()
        })
        .catch((err) => {
            modalError.value =
                err.message || 'Could not save examiner.'
        })
        .finally(() => {
            busy.value = false
        })
}


// Activate or deactivate an examiner.
function changeStatus(examiner) {
    const action = examiner.status === 'active'
        ? 'deactivate'
        : 'activate'

    const confirmed = window.confirm(
        `Are you sure you want to ${action} ${examiner.fullname}?`
    )

    if (!confirmed) {
        return
    }

    busy.value = true
    error.value = ''
    message.value = ''

    apiRequest(
        `/admin/examiners/${examiner.id}/status`,
        {
            method: 'PATCH',
            body: JSON.stringify({
                status: examiner.status === 'active'
                    ? 'inactive'
                    : 'active'
            })
        }
    )
        .then((data) => {
            message.value =
                data.message || 'Examiner status updated.'

            loadExaminers()
        })
        .catch((err) => {
            error.value =
                err.message || 'Could not update examiner status.'
        })
        .finally(() => {
            busy.value = false
        })
}


onMounted(() => {
    loadExaminers()
})
</script>
