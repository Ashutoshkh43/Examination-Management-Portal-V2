<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <RouterLink class="navbar-brand" to="/">
          EMP Portal
        </RouterLink>

        <div class="navbar-nav ms-auto">
          <RouterLink
            v-if="!auth.isLoggedIn"
            class="nav-link"
            to="/login"
          >
            Login
          </RouterLink>

          <RouterLink
            v-if="!auth.isLoggedIn"
            class="nav-link"
            to="/register"
          >
            Student Registration
          </RouterLink>

          <RouterLink
            v-if="auth.isLoggedIn"
            class="nav-link"
            :to="auth.dashboardPath"
          >
            Dashboard
          </RouterLink>

          <button
            v-if="auth.isLoggedIn"
            class="btn btn-outline-light btn-sm ms-lg-3"
            @click="logout"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  auth.restoreSession()
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>