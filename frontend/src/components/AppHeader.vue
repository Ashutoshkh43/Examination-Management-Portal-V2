
<template>
    <header class="d-flex justify-content-between align-items-center bg-black text-white px-3 py-2">
        <div class="d-flex align-items-center gap-2">
            <strong style="color: aquamarine;">EMP</strong>
            <span style="color: aquamarine;">Examination Management Portal</span>
        </div>

        <!-- Email and Logout button -->
        <div v-if="auth.isLoggedIn" class="d-flex flex-column align-items-end">
            <span style="color: aquamarine;">
                {{ auth.user?.email }}
            </span>

            <button
                class="btn btn-outline-info btn-sm mt-1"
                type="button"
                @click="logout"
            >
                Logout
            </button>
        </div>
    </header>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
    auth.logout().then(() => {
        router.push('/login')
    })
}
</script>
