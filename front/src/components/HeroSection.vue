<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <section
    id="home"
    class="relative isolate flex w-full flex-col gap-6 px-6 py-24 text-center md:px-12 md:py-28"
  >
    <span class="mx-auto w-16 border-t border-gray-300" aria-hidden="true"></span>
    <h1 class="text-4xl font-semibold tracking-tight text-gray-900 md:text-5xl">
      理解世界的方式不止一种，代码只是其中之一
    </h1>
    <p class="mx-auto max-w-2xl text-base text-gray-600 md:text-lg">
      欢迎来到 MAI，这里以极简的方式记录灵感与实践
    </p>
    <div class="flex flex-wrap items-center justify-center gap-4 pt-4 text-sm">
      <RouterLink
        :to="{ name: 'blog' }"
        class="rounded-full border border-gray-300 px-5 py-2 text-gray-900 transition hover:border-gray-500 hover:text-gray-700"
      >
        阅读最新文章
      </RouterLink>
      <span class="text-gray-400">或</span>
      <RouterLink
        :to="{ name: 'about' }"
        class="text-gray-500 underline-offset-4 transition hover:text-gray-800 hover:underline"
      >
        了解 MAI 的理念
      </RouterLink>
    </div>
  </section>
</template>
