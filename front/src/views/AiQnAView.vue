<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchPosts } from '../services/api'
import {
  categories,
  normalizeTags,
  resolveCategoryKey,
} from '../utils/categories'

const posts = ref([])
const loading = ref(true)
const error = ref('')

const state = reactive({
  selectedKeys: ['ai', 'paper', 'dev', 'other'],
  query: '',
  messages: [],
  drafting: '',
  sending: false,
})

const groupedPosts = computed(() => {
  const buckets = {
    ai: [],
    paper: [],
    dev: [],
    other: [],
  }
  posts.value.forEach((post) => {
    const key = resolveCategoryKey(normalizeTags(post.tags))
    buckets[key].push(post)
  })
  return buckets
})

const selectedPosts = computed(() =>
  posts.value.filter((post) => state.selectedKeys.includes(resolveCategoryKey(normalizeTags(post.tags))))
)

const matchedPosts = computed(() => {
  if (!state.query.trim()) return selectedPosts.value
  const term = state.query.trim().toLowerCase()
  return selectedPosts.value.filter((post) => {
    const titleMatch = (post.title || '').toLowerCase().includes(term)
    const excerptMatch = (post.excerpt || post.summary || '').toLowerCase().includes(term)
    const tagMatch = normalizeTags(post.tags).some((tag) => tag.toLowerCase().includes(term))
    return titleMatch || excerptMatch || tagMatch
  })
})

const toggleKey = (key) => {
  if (state.selectedKeys.includes(key)) {
    state.selectedKeys = state.selectedKeys.filter((item) => item !== key)
  } else {
    state.selectedKeys = [...state.selectedKeys, key]
  }
}

const addMessage = (role, content) => {
  state.messages = [...state.messages, { role, content, at: new Date().toISOString() }]
}

const handleSend = async () => {
  if (!state.drafting.trim()) return
  const userText = state.drafting.trim()
  addMessage('user', userText)
  state.drafting = ''
  state.sending = true
  try {
    const references = matchedPosts.value.slice(0, 3)
    const refList = references
      .map((post) => `- ${post.title}`)
      .join('\n') || '- 暂无检索结果'
    const reply = `基于当前勾选的知识库，找到了 ${references.length} 条相关资料：\n${refList}\n\n这是一个占位回答，可接入真实大模型接口。`
    addMessage('assistant', reply)
  } finally {
    state.sending = false
  }
}

const loadPosts = async () => {
  loading.value = true
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
  <div class="flex flex-col pt-4">
    <div class="mx-auto flex w-full items-start px-2 py-1 md:px-4 lg:px-8">
      <div
        class="grid w-full gap-4 bg-transparent p-0 md:grid-cols-[260px_minmax(0,1fr)_260px] md:gap-6"
      >
        <!-- 左侧：知识库勾选 -->
        <aside class="flex flex-col gap-3">
          <div>
            <p class="text-xs uppercase tracking-[0.3em] text-gray-400">知识库</p>
            <h2 class="text-xl font-semibold text-gray-900">选择知识库</h2>
            <p class="mt-1 text-sm text-gray-500">勾选后用于检索和回答。</p>
          </div>
          <div class="space-y-3">
            <label
              v-for="category in categories"
              :key="category.key"
              class="flex cursor-pointer items-center justify-between rounded-xl bg-gray-50 px-4 py-3 text-sm transition hover:bg-gray-100"
            >
              <div>
                <p class="font-semibold text-gray-900">{{ category.title }}</p>
                <p class="text-xs text-gray-500">{{ category.description }}</p>
              </div>
              <input
                type="checkbox"
                class="h-4 w-4 rounded border-gray-300 text-gray-900 focus:ring-gray-500"
                :checked="state.selectedKeys.includes(category.key)"
                @change="toggleKey(category.key)"
              />
            </label>
          </div>
          <div class="rounded-xl bg-gray-50 p-4 text-sm">
            <p class="text-gray-700">
              已选 {{ state.selectedKeys.length }} / {{ categories.length }} 个知识库，覆盖
              {{ selectedPosts.length }} 篇文章。
            </p>
          </div>
        </aside>

        <!-- 中间：对话区域 -->
        <main class="flex flex-col items-center gap-2">
          <div class="text-center">
            <p class="text-xs uppercase tracking-[0.3em] text-gray-400">AI 问答</p>
            <h1 class="text-3xl font-semibold text-gray-900">大模型对话</h1>
            <p class="mt-1 text-sm text-gray-500">
              输入问题，系统将基于勾选的知识库检索文章并生成回答。
            </p>
          </div>

          <div class="flex w-full max-w-4xl flex-col gap-2 rounded-2xl bg-gray-50 p-3">
            <div
              v-if="!state.messages.length"
              class="flex flex-1 items-center justify-center text-sm text-gray-500"
            >
              还没有对话，输入问题开始吧。
            </div>
            <div
              v-else
              class="flex-1 space-y-4 overflow-y-auto pr-1"
            >
              <div
                v-for="(msg, index) in state.messages"
                :key="msg.at + index"
                class="flex"
                :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-xl rounded-2xl px-4 py-3 text-sm"
                  :class="msg.role === 'user' ? 'bg-gray-900 text-white' : 'bg-white text-gray-900 shadow-sm'"
                >
                  <p class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</p>
                </div>
              </div>
            </div>

            <form class="flex flex-col gap-2 rounded-xl bg-white p-2.5 shadow-sm" @submit.prevent="handleSend">
              <textarea
                v-model="state.drafting"
                rows="3"
                class="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-gray-400 focus:outline-none"
                placeholder="提出你的问题，按下发送开始对话"
              ></textarea>
              <div class="flex items-center justify-between">
                <p class="text-xs text-gray-500">
                  回答会引用勾选知识库中与问题相关的文章。
                </p>
                <button
                  type="submit"
                  class="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-400"
                  :disabled="state.sending"
                >
                  {{ state.sending ? '生成中...' : '发送' }}
                </button>
              </div>
            </form>
          </div>
        </main>

        <!-- 右侧：检索结果 -->
        <aside class="flex flex-col gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.3em] text-gray-400">检索结果</p>
            <h2 class="text-xl font-semibold text-gray-900">相关文章</h2>
            <p class="mt-1 text-sm text-gray-500">来自已选知识库的文章链接。</p>
          </div>

          <div v-if="loading" class="text-sm text-gray-500">正在载入知识库...</div>
          <div v-else-if="error" class="text-sm text-red-500">{{ error }}</div>
          <div v-else-if="!matchedPosts.length" class="text-sm text-gray-500">
            暂无匹配结果，试试更换关键词或勾选更多知识库。
          </div>
          <ul v-else class="space-y-3">
            <li
              v-for="post in matchedPosts"
              :key="post.id ?? post.slug ?? post.title"
              class="rounded-xl bg-gray-50 p-3 transition hover:bg-gray-100"
            >
              <a
                :href="post.slug ? `/blog/${post.slug}` : post.url ?? '#'"
                class="text-sm font-semibold text-gray-900 hover:underline"
              >
                {{ post.title }}
              </a>
              <p class="mt-1 text-xs text-gray-500 line-clamp-2">
                {{ post.excerpt || post.summary || '暂无摘要' }}
              </p>
              <p class="mt-1 text-[11px] uppercase tracking-[0.2em] text-gray-400">
                {{ resolveCategoryKey(normalizeTags(post.tags)).toUpperCase() }}
              </p>
            </li>
          </ul>
        </aside>
      </div>
    </div>
  </div>
</template>
