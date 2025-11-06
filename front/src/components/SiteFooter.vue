<script setup>
import { RouterLink } from 'vue-router'

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer
    id="contact"
    class="border-t border-gray-200 bg-gray-100/80 py-10"
  >
    <div
      class="flex w-full flex-col gap-3 px-6 text-sm text-gray-500 md:flex-row md:items-center md:justify-between md:px-12"
    >
      <p>© {{ currentYear }} MAI。以专注与宁静打造。</p>
      <div class="flex flex-wrap items-center gap-4">
        <RouterLink class="transition hover:text-gray-800" :to="{ name: 'about' }">
          关于
        </RouterLink>
        <RouterLink class="transition hover:text-gray-800" :to="{ name: 'blog' }">
          博客
        </RouterLink>
        <a href="mailto:mafan671@gmail.com" class="transition hover:text-gray-800">电子邮件</a>
        <a href="https://github.com/mafan12?tab=repositories" class="transition hover:text-gray-800">开源仓库</a>
        <a href="https://x.com/" class="transition hover:text-gray-800">社交平台</a>
      </div>
    </div>
  </footer>
</template>
