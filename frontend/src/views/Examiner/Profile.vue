
<template>
  <div class="container-fluid py-3">

    <!-- Page heading -->
    <div class="mb-4">
      <div class="small text-muted mb-1">
        Home / Examiner / My Profile
      </div>

      <h4 class="fw-bold mb-0">My Profile</h4>
    </div>

    <!-- Success message -->
    <div
      v-if="message"
      class="alert alert-success alert-dismissible"
    >
      {{ message }}

      <button
        class="btn-close"
        @click="message = ''"
      ></button>
    </div>

    <!-- Error message -->
    <div
      v-if="error"
      class="alert alert-danger alert-dismissible"
    >
      {{ error }}

      <button
        class="btn-close"
        @click="error = ''"
      ></button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-2">Loading profile...</p>
    </div>

    <!-- Profile form -->
    <div v-else class="card profile-card">

      <div class="card-body">

        <form @submit.prevent="saveProfile">

          <!-- Full Name -->
          <div class="mb-3">
            <label class="form-label">
              Full Name
            </label>

            <input
              v-model="profile.fullname"
              type="text"
              class="form-control"
              :disabled="!editMode || saving"
              required
            >
          </div>

          <!-- Employee ID -->
          <div class="mb-3">
            <label class="form-label">
              Employee ID
            </label>

            <input
              v-model="profile.employee_id"
              type="text"
              class="form-control"
              disabled
            >
          </div>

          <!-- Email -->
          <div class="mb-3">
            <label class="form-label">
              Email
            </label>

            <input
              v-model="profile.email"
              type="email"
              class="form-control"
              disabled
            >
          </div>

          <!-- Department -->
          <div class="mb-3">
            <label class="form-label">
              Department
            </label>

            <input
              v-model="profile.department"
              type="text"
              class="form-control"
              :disabled="!editMode || saving"
              required
            >
          </div>

          <!-- Designation -->
          <div class="mb-3">
            <label class="form-label">
              Designation
            </label>

            <input
              v-model="profile.designation"
              type="text"
              class="form-control"
              :disabled="!editMode || saving"
              required
            >
          </div>

          <!-- Buttons -->
          <div class="d-flex gap-2">

            <button
              v-if="!editMode"
              type="button"
              class="btn btn-outline-secondary"
              @click="startEditing"
            >
              Edit Profile
            </button>

            <template v-else>

              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="saving"
                @click="cancelEditing"
              >
                Cancel
              </button>

              <button
                type="submit"
                class="btn btn-primary"
                :disabled="saving"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>

            </template>

          </div>

        </form>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '../../services/api.js'

// Loading and editing states
const loading = ref(true)
const saving = ref(false)
const editMode = ref(false)

// Messages
const error = ref('')
const message = ref('')

// Profile data
const profile = ref({
  fullname: '',
  employee_id: '',
  email: '',
  department: '',
  designation: ''
})

// Keep a copy of original profile data
const originalProfile = ref({})


// Fetch examiner profile
async function loadProfile() {

  loading.value = true
  error.value = ''

  try {

    const data = await apiRequest('/examiner/profile')

    if (!data.profile) {
      throw new Error('Profile data was not received.')
    }

    profile.value = {
      fullname: data.profile.fullname || '',
      employee_id: data.profile.employee_id || '',
      email: data.profile.email || '',
      department: data.profile.department || '',
      designation: data.profile.designation || ''
    }

    originalProfile.value = { ...profile.value }

  } catch (err) {

    error.value = err.message || 'Unable to load profile.'

  } finally {

    loading.value = false

  }
}


// Enable editing
function startEditing() {

  originalProfile.value = { ...profile.value }

  editMode.value = true
  message.value = ''
  error.value = ''

}


// Cancel editing and restore original data
function cancelEditing() {

  profile.value = { ...originalProfile.value }

  editMode.value = false
  error.value = ''

}


// Save updated profile
async function saveProfile() {

  if (!profile.value.fullname.trim()) {
    error.value = 'Full name is required.'
    return
  }

  if (!profile.value.department.trim()) {
    error.value = 'Department is required.'
    return
  }

  if (!profile.value.designation.trim()) {
    error.value = 'Designation is required.'
    return
  }

  saving.value = true
  error.value = ''
  message.value = ''

  try {

    const result = await apiRequest('/examiner/profile', {
      method: 'PUT',
      body: JSON.stringify({
        fullname: profile.value.fullname,
        department: profile.value.department,
        designation: profile.value.designation
      })
    })

    if (result.profile) {
      profile.value = {
        ...profile.value,
        ...result.profile
      }
    }

    originalProfile.value = { ...profile.value }

    editMode.value = false

    message.value = result.message || 'Profile updated successfully.'

  } catch (err) {

    error.value = err.message || 'Unable to update profile.'

  } finally {

    saving.value = false

  }
}


// Load profile when page opens
onMounted(loadProfile)

</script>

<style scoped>

.profile-card {
  border: 1px solid #d9e1ec;
  border-radius: 7px;
  box-shadow: none;
}

.profile-card .card-body {
  padding: 16px;
}

.form-label {
  color: #092c5c;
  font-size: 14px;
  margin-bottom: 4px;
}

.form-control {
  border-color: #cbd5e1;
  border-radius: 5px;
  font-size: 14px;
  padding: 7px 10px;
}

.form-control:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.15rem rgba(13, 110, 253, 0.15);
}

.form-control:disabled {
  background-color: #fff;
  color: #092c5c;
  opacity: 1;
}

.btn {
  border-radius: 4px;
  font-size: 14px;
}

</style>
