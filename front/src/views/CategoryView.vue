<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BlogGrid from '../components/BlogGrid.vue'
import { fetchPosts } from '../services/api'
import {
  categories,
  getCategoryMeta,
  normalizeTags,
  resolveCategoryKey,
} from '../utils/categories'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const loading = ref(true)
const error = ref('')

const categoryKey = computed(() => route.params.key)
const categoryMeta = computed(() => getCategoryMeta(categoryKey.value))

const filteredPosts = computed(() =>
  posts.value.filter(
    (post) => resolveCategoryKey(normalizeTags(post.tags)) === categoryKey.value
  )
)

const loadPosts = async () => {
  loading.value = true
  try {
    const data = await fetchPosts()
    posts.value = data
    if (!categoryMeta.value) {
      router.replace({ name: 'blog' })
      return
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载文章失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadPosts)

watch(
  () => route.params.key,
  () => {
    error.value = ''
    loadPosts()
  }
)
</script>

<template>
  <div class="space-y-10 px-6 pb-24 pt-10 md:px-12">
    <div class="flex flex-col items-center gap-2 text-center">
      <p class="text-xs uppercase tracking-[0.3em] text-gray-400">知识库</p>
      <h1 class="text-3xl font-semibold text-gray-900 md:text-4xl">
        {{ categoryMeta?.title ?? '知识库' }}
      </h1>
      <p class="mt-2 text-sm text-gray-500">
        {{ categoryMeta?.description ?? '查看该分类下的文章。' }}
      </p>
    </div>

    <div v-if="loading" class="text-center text-sm text-gray-500">正在载入文章...</div>
    <div v-else-if="error" class="text-center text-sm text-red-500">{{ error }}</div>
    <div v-else-if="!filteredPosts.length" class="text-center text-sm text-gray-500">
      敬请期待
    </div>
    <div v-else>
      <BlogGrid :posts="filteredPosts" />
    </div>
  </div>
</template>
