
<template>
    <aside class="col-12 col-md-3 col-xl-2 bg-dark text-white p-3 d-flex flex-column min-vh-100">

         <h2 style="color: aquamarine;">{{ auth.role }}  </h2>

        <!-- Admin menu -->
        <nav v-if="auth.role === 'admin'" class="nav nav-pills flex-column gap-1">
            <RouterLink class="nav-link text-white" to="/admin/dashboard">
                Dashboard
            </RouterLink>
            <RouterLink class="nav-link text-white" to="/admin/examiners">
                Examiners
            </RouterLink>
<!--             
            <RouterLink class="nav-link text-white" to="/admin/courses">
                Courses
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/admin/examinations">
                Examinations
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/admin/rubrics">
                Rubrics
            </RouterLink>

            

            <RouterLink class="nav-link text-white" to="/admin/slots">
                Slots
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/admin/bookings">
                Bookings
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/admin/students">
                Students
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/admin/results">
                Results
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/admin/reports">
                Reports
            </RouterLink> -->
        </nav>

        <!-- Examiner menu -->
        <nav v-else-if="auth.role === 'examiner'" class="nav nav-pills flex-column gap-1">
            <RouterLink class="nav-link text-white" to="/examiner/dashboard">
                Dashboard
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/examiner/examinations">
                My Examinations
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/examiner/slots">
                Slots
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/examiner/booked-students">
                Booked Students
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/examiner/profile">
                Profile
            </RouterLink>
        </nav>

        <!-- Student menu -->
        <nav v-else-if="auth.role === 'student'" class="nav nav-pills flex-column gap-1">
            <RouterLink class="nav-link text-white" to="/student/dashboard">
                Dashboard
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/student/examinations">
                Available Examinations
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/student/bookings">
                My Bookings
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/student/results">
                Results
            </RouterLink>

            <RouterLink class="nav-link text-white" to="/student/profile">
                Profile
            </RouterLink>
        </nav>

        <!-- Logout at the bottom -->
        <button
            v-if="auth.isLoggedIn"
            class="btn btn-link text-white text-decoration-none text-start mt-auto px-3"
            type="button"
            @click="logout"
        >
            Logout
        </button>

    </aside>
</template>

<script setup>
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
    auth.logout().then(() => {
        router.push('/login')
    })
}

</script>
