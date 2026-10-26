<template>
    <header class="topbar">
        <div>
            <h5>{{ pageTitle }}</h5>
            <p>Examination Management Portal</p>
        </div>

        <div class="topbar-user">
            <div class="avatar">{{ userInitial }}</div>

            <div>
                <strong>{{ displayName }}</strong>
                <small>{{ auth.role }}</small>
            </div>
        </div>
    </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
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
    if (route.meta.title) {
        return route.meta.title
    }

    const page = String(route.params.page || '')

    return pageNames[page]
        || page.replace(/-/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase())
})
</script>