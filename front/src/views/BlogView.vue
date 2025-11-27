<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchPosts } from '../services/api'
import {
  categories,
  normalizeTags,
  resolveCategoryKey,
} from '../utils/categories'

const posts = ref([])
const loading = ref(true)
const error = ref('')

const groupedPosts = computed(() => {
  const buckets = {
    ai: [],
    paper: [],
    dev: [],
    other: [],
  }
  posts.value.forEach((post) => {
    const tags = normalizeTags(post.tags)
    const key = resolveCategoryKey(tags)
    buckets[key].push(post)
  })
  return buckets
})

const loadPosts = async () => {
  try {
    const data = await fetchPosts()
    posts.value = data
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载文章失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadPosts)
</script>

<template>
  <div class="space-y-12">
    <section class="w-full px-6 pt-10 text-center md:px-12">
      <p class="text-xs uppercase tracking-[0.35em] text-gray-400">Knowledge Base</p>
      <h1 class="mt-3 text-3xl font-semibold tracking-tight text-gray-900 md:text-4xl">
        知识库
      </h1>
    </section>

    <div v-if="loading" class="px-6 text-center text-sm text-gray-500 md:px-12">
      正在载入文章...
    </div>

    <div v-else-if="error" class="px-6 text-center text-sm text-red-500 md:px-12">
      {{ error }}
    </div>

    <div
      v-else-if="!posts.length"
      class="px-6 text-center text-sm text-gray-500 md:px-12"
    >
      暂无文章，稍后再来看看。
    </div>

    <div v-else class="px-6 pb-24 md:px-12">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <RouterLink
          v-for="category in categories"
          :key="category.key"
          :to="{ name: 'category', params: { key: category.key } }"
          class="space-y-4 rounded-2xl border border-gray-100 bg-white/80 p-6 shadow-soft transition hover:-translate-y-1 hover:shadow-lg"
        >
          <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-gray-400">知识库</p>
              <h2 class="text-2xl font-semibold text-gray-900">{{ category.title }}</h2>
              <p class="text-sm text-gray-500">{{ category.description }}</p>
            </div>
            <span class="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
              {{ groupedPosts[category.key].length }} 篇
            </span>
          </div>
          <div class="flex items-center justify-between text-sm text-gray-500">
            <span>点击进入该知识库</span>
            <span aria-hidden="true" class="transition group-hover:translate-x-1">→</span>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
