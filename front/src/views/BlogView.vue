<script setup>
import { onMounted, ref } from 'vue'
import BlogGrid from '../components/BlogGrid.vue'
import { fetchPosts } from '../services/api'

const posts = ref([])
const loading = ref(true)
const error = ref('')

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
      <h1 class="text-3xl font-semibold tracking-tight text-gray-900 md:text-4xl">
        博客
      </h1>
      <p class="mt-4 text-base text-gray-600 md:text-lg">
        记录项目推进、工具实验与工作流思考的笔记合集。
      </p>
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

    <BlogGrid v-else :posts="posts" />
  </div>
</template>
