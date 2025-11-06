<script setup>
import { RouterView } from 'vue-router'
import SiteNav from './components/SiteNav.vue'
import SiteFooter from './components/SiteFooter.vue'
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
