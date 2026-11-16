<template>
  <div class="container-fluid p-0 min-vh-100 bg-aquamarine">
    <!-- Header across the full page -->
    <AppHeader />

    <!-- Sidebar and dashboard content below header -->
    <div class="row g-0">
      <AppSidebar />

      <main class="col-12 col-md-9 col-xl-10 p-3 p-lg-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from '../components/AppSidebar.vue'
import AppHeader from '../components/AppHeader.vue'
</script>

<style scoped>
.bg-aquamarine {
  background-color: #7fffd4 !important; /* Native Aquamarine Hex */
}
</style>
