<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const links = computed(() => [
  { name: '首页', to: { name: 'home' } },
  { name: '博客', to: { name: 'blog' } },
  { name: '关于', to: { name: 'about' } },
  { name: '联系', to: { name: 'contact' } },
])

const isActive = (target) => route.name === target
</script>

<template>
  <header
    class="fixed inset-x-0 top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur"
  >
    <nav class="flex h-16 w-full items-center justify-between px-6 md:px-12">
      <RouterLink
        :to="{ name: 'home' }"
        class="text-lg font-semibold tracking-wide text-gray-900"
      >
        MAI
      </RouterLink>
      <ul class="flex items-center gap-8 text-sm font-medium text-gray-600">
        <li v-for="link in links" :key="link.name">
          <RouterLink
            :to="link.to"
            class="transition hover:text-gray-900"
            :class="isActive(link.to.name) ? 'text-gray-900' : ''"
          >
            {{ link.name }}
          </RouterLink>
        </li>
      </ul>
    </nav>
  </header>
</template>
