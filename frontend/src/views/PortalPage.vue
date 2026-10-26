<template>
    <div>
        <div class="welcome-section">
            <div>
                <h2>{{ pageTitle }}</h2>

                <p>
                    Manage and view your {{ pageTitle.toLowerCase() }}.
                </p>
            </div>

            <router-link
                :to="`/${auth.role}/dashboard`"
                class="btn btn-outline-primary"
            >
                Back to Dashboard
            </router-link>
        </div>

        <div class="content-card placeholder-card">
            <div class="placeholder-icon">▤</div>

            <h4>{{ pageTitle }}</h4>

            <p>
                This module will contain its tables, forms, and actions
                when its API and functionality are implemented.
            </p>

            <span class="coming-soon">
                Module pending implementation
            </span>
        </div>
    </div>
</template>

<script setup>
import { computed} from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()

const pageNames = {
    courses: 'Courses',
    examinations: 'Examinations',
    rubrics: 'Rubrics',
    examiners: 'Examiners',
    slots: 'Examination Slots',
    bookings: 'Bookings',
    students: 'Students',
    results: 'Results',
    reports: 'Reports',
    profile: 'My Profile'
}

const pageTitle = computed(() => {
    const page = String(route.params.page || '')

    return pageNames[page]
        || page.replace(/-/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase())
})

watchEffect(() => {
    route.meta.title = pageTitle.value
})
</script>