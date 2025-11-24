<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import SiteNav from './components/SiteNav.vue'
import SiteFooter from './components/SiteFooter.vue'
import { useAuthStore } from './utils/authStore'

const { bootstrap } = useAuthStore()

onMounted(() => {
  bootstrap()
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-surface text-gray-900">
    <SiteNav />
    <main class="flex flex-1 flex-col pt-20 pb-24">
      <div class="flex flex-1 flex-col justify-center">
        <RouterView />
      </div>
    </main>
    <SiteFooter />
  </div>
</template>
