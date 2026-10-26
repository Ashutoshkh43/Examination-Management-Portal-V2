<template>
    <aside class="sidebar">
        <div class="sidebar-brand">
            <div class="brand-icon small-brand">E</div>

            <div>
                <h5>EMP Portal</h5>
                <small>Examination Management</small>
            </div>
        </div>

        <div class="sidebar-user">
            <div class="avatar">{{ userInitial }}</div>

            <div>
                <strong>{{ displayName }}</strong>
                <small>{{ auth.role }}</small>
            </div>
        </div>

        <nav class="sidebar-nav">
            <p class="nav-heading">WORKSPACE</p>

            <router-link
                :to="`/${auth.role}/dashboard`"
                class="sidebar-link"
            >
                <span>▦</span>
                Dashboard
            </router-link>

            <router-link
                v-for="item in menuItems"
                :key="item.path"
                :to="`/${auth.role}/${item.path}`"
                class="sidebar-link"
            >
                <span>{{ item.icon }}</span>
                {{ item.label }}
            </router-link>
        </nav>

        <button
            class="sidebar-logout"
            @click="handleLogout"
        >
            ↪ Sign Out
        </button>
    </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const menus = {
    admin: [
        { label: 'Courses', path: 'courses', icon: '▤' },
        { label: 'Examinations', path: 'examinations', icon: '▣' },
        { label: 'Rubrics', path: 'rubrics', icon: '☷' },
        { label: 'Examiners', path: 'examiners', icon: '♙' },
        { label: 'Slots', path: 'slots', icon: '◷' },
        { label: 'Bookings', path: 'bookings', icon: '▧' },
        { label: 'Students', path: 'students', icon: '♧' },
        { label: 'Results', path: 'results', icon: '▥' },
        { label: 'Reports', path: 'reports', icon: '▨' }
    ],

    examiner: [
        { label: 'My Examinations', path: 'examinations', icon: '▣' },
        { label: 'Slots', path: 'slots', icon: '◷' },
        { label: 'Booked Students', path: 'bookings', icon: '♙' },
        { label: 'Profile', path: 'profile', icon: '⚙' }
    ],

    student: [
        { label: 'Available Examinations', path: 'examinations', icon: '▣' },
        { label: 'My Bookings', path: 'bookings', icon: '▧' },
        { label: 'Results', path: 'results', icon: '▥' },
        { label: 'Profile', path: 'profile', icon: '⚙' }
    ]
}

const menuItems = computed(() => {
    return menus[auth.role] || menus.student
})

const displayName = computed(() => {
    return auth.user?.fullname
        || auth.user?.name
        || auth.user?.email
        || 'User'
})

const userInitial = computed(() => {
    return displayName.value.charAt(0).toUpperCase()
})

function handleLogout() {
    auth.logout().then(() => {
        router.push('/login')
    })
}
</script>