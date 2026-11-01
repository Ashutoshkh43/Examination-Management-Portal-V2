
<template>
    <div class="container-fluid p-3">

        <!-- Page Heading -->
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <div class="text-secondary small mb-2">
                    Home / admin / Manage Courses
                </div>

                <h6 class="fw-bold mb-0">Manage Courses</h6>
            </div>

            <button
                class="btn btn-primary btn-sm px-3"
                @click="openAddModal"
            >
                + Add Course
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

        <!-- Search -->
        <div class="card mb-3">
            <div class="card-body p-3">
                <input
                    v-model="search"
                    type="search"
                    class="form-control"
                    style="max-width: 260px;"
                    placeholder="Search..."
                    aria-label="Search courses"
                >
            </div>
        </div>

        <!-- Courses Table -->
        <div class="card">
            <div class="card-body p-3">

                <div class="table-responsive">
                    <table class="table table-sm align-middle mb-0">

                        <thead class="table-light">
                            <tr>
                                <th>Course Code</th>
                                <th>Course Name</th>
                                <th>Description</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="course in filteredCourses"
                                :key="course.id"
                            >
                                <td>{{ course.course_code }}</td>

                                <td>{{ course.course_name }}</td>

                                <td>{{ course.description || '-' }}</td>

                                <td>
                                    <span
                                        class="badge rounded-pill"
                                        :class="course.status === 'active'
                                            ? 'text-bg-success'
                                            : 'text-bg-secondary'"
                                    >
                                        {{
                                            course.status === 'active'
                                                ? 'Active'
                                                : 'Inactive'
                                        }}
                                    </span>
                                </td>

                                <td>
                                    <div class="d-flex gap-1">
                                        <button
                                            class="btn btn-outline-primary btn-sm"
                                            :disabled="busy"
                                            @click="openEditModal(course)"
                                        >
                                            Edit
                                        </button>

                                        <button
                                            class="btn btn-outline-danger btn-sm"
                                            :disabled="busy"
                                            @click="deleteCourse(course)"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </td>
                            </tr>

                            <tr v-if="loading">
                                <td
                                    colspan="5"
                                    class="text-center text-secondary py-4"
                                >
                                    Loading courses...
                                </td>
                            </tr>

                            <tr
                                v-if="!loading && filteredCourses.length === 0"
                            >
                                <td
                                    colspan="5"
                                    class="text-center text-secondary py-4"
                                >
                                    No courses found.
                                </td>
                            </tr>
                        </tbody>

                    </table>
                </div>

            </div>
        </div>

        <!-- Add / Edit Course Modal -->
        <div
            v-if="showModal"
            class="modal d-block"
            tabindex="-1"
            role="dialog"
            aria-modal="true"
            @click.self="closeModal"
        >
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">

                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            {{
                                modalMode === 'edit'
                                    ? 'Edit Course'
                                    : 'Add Course'
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

                    <div class="modal-body">
                        <form @submit.prevent="saveCourse">

                            <div class="mb-3">
                                <label class="form-label">
                                    Course Code *
                                </label>

                                <input
                                    v-model.trim="form.course_code"
                                    type="text"
                                    class="form-control"
                                    placeholder="e.g. CS101"
                                    required
                                >
                            </div>

                            <div class="mb-3">
                                <label class="form-label">
                                    Course Name *
                                </label>

                                <input
                                    v-model.trim="form.course_name"
                                    type="text"
                                    class="form-control"
                                    placeholder="Enter course name"
                                    required
                                >
                            </div>

                            <div class="mb-3">
                                <label class="form-label">
                                    Description
                                </label>

                                <textarea
                                    v-model.trim="form.description"
                                    class="form-control"
                                    rows="3"
                                    placeholder="Enter course description"
                                ></textarea>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">
                                    Status
                                </label>

                                <select
                                    v-model="form.status"
                                    class="form-select"
                                >
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                </select>
                            </div>

                            <div
                                v-if="modalError"
                                class="alert alert-danger py-2"
                            >
                                {{ modalError }}
                            </div>

                            <div class="d-flex justify-content-end gap-2">
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
                                                : 'Create Course'
                                    }}
                                </button>
                            </div>

                        </form>
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
import { apiRequest } from '../../services/api'

const courses = ref([])
const search = ref('')

const loading = ref(false)
const busy = ref(false)

const showModal = ref(false)
const modalMode = ref('add')
const selectedCourse = ref(null)

const message = ref('')
const error = ref('')
const modalError = ref('')

const emptyForm = () => ({
    course_code: '',
    course_name: '',
    description: '',
    status: 'active'
})

const form = ref(emptyForm())

const filteredCourses = computed(() => {
    const query = search.value.trim().toLowerCase()

    if (!query) {
        return courses.value
    }

    return courses.value.filter((course) => {
        return [
            course.course_code,
            course.course_name,
            course.description,
            course.status
        ].some((value) =>
            String(value || '').toLowerCase().includes(query)
        )
    })
})


// Load courses from Flask.
function loadCourses() {
    loading.value = true
    error.value = ''

    apiRequest('/admin/courses')
        .then((data) => {
            courses.value = data.courses || []
        })
        .catch((err) => {
            error.value = err.message || 'Could not load courses.'
        })
        .finally(() => {
            loading.value = false
        })
}


// Open Add Course modal.
function openAddModal() {
    modalMode.value = 'add'
    selectedCourse.value = null
    form.value = emptyForm()

    message.value = ''
    error.value = ''
    modalError.value = ''

    showModal.value = true
}


// Open Edit Course modal.
function openEditModal(course) {
    modalMode.value = 'edit'
    selectedCourse.value = course

    form.value = {
        course_code: course.course_code || '',
        course_name: course.course_name || '',
        description: course.description || '',
        status: course.status || 'active'
    }

    message.value = ''
    error.value = ''
    modalError.value = ''

    showModal.value = true
}


// Close modal.
function closeModal() {
    if (busy.value) {
        return
    }

    showModal.value = false
    modalError.value = ''
}


// Create or update course.
function saveCourse() {
    busy.value = true
    modalError.value = ''
    message.value = ''

    const isEditing = modalMode.value === 'edit'

    const courseData = {
        course_code: form.value.course_code,
        course_name: form.value.course_name,
        description: form.value.description,
        status: form.value.status
    }

    const request = isEditing
        ? apiRequest(
            `/admin/courses/${selectedCourse.value.id}`,
            {
                method: 'PUT',
                body: JSON.stringify(courseData)
            }
        )
        : apiRequest(
            '/admin/courses',
            {
                method: 'POST',
                body: JSON.stringify(courseData)
            }
        )

    request
        .then((data) => {
            message.value = data.message || (
                isEditing
                    ? 'Course updated successfully.'
                    : 'Course created successfully.'
            )

            showModal.value = false
            form.value = emptyForm()

            loadCourses()
        })
        .catch((err) => {
            modalError.value = err.message || 'Could not save course.'
        })
        .finally(() => {
            busy.value = false
        })
}


// Delete course.
function deleteCourse(course) {
    const confirmed = window.confirm(
        `Are you sure you want to delete ${course.course_name}?`
    )

    if (!confirmed) {
        return
    }

    busy.value = true
    error.value = ''
    message.value = ''

    apiRequest(`/admin/courses/${course.id}`, {
        method: 'DELETE'
    })
        .then((data) => {
            message.value = data.message || 'Course deleted successfully.'
            loadCourses()
        })
        .catch((err) => {
            error.value = err.message || 'Could not delete course.'
        })
        .finally(() => {
            busy.value = false
        })
}


onMounted(() => {
    loadCourses()
})
</script>
