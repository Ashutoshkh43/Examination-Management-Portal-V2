<template>
    <div class="portal-layout">
        <AppSidebar />

        <main class="portal-main">
            <AppHeader />

            <section class="dashboard-content">
                <router-view />
            </section>
        </main>
    </div>
</template>

<script setup>
import AppSidebar from '../components/AppSidebar.vue'
import AppHeader from '../components/AppHeader.vue'
</script>