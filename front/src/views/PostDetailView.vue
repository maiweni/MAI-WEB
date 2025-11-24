<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

import { fetchPostBySlug, fetchPosts } from '../services/api'
import { useAuthStore } from '../utils/authStore'

const route = useRoute()
const router = useRouter()
const { state: auth, login, register, upgrade, bootstrap } = useAuthStore()

const post = ref(null)
const loading = ref(true)
const error = ref('')
const contentHtml = ref('')
const permission = ref('') // '', 'login', 'upgrade'
const form = reactive({ email: '', password: '' })
const submitting = ref(false)
const mode = ref('login')

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, {
          language: lang,
        }).value}</code></pre>`
      } catch (e) {
        // ignore and fall back to auto highlight
      }
    }
    try {
      return `<pre class="hljs"><code>${hljs.highlightAuto(str).value}</code></pre>`
    } catch (e) {
      return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
    }
  },
})

const loadPost = async () => {
  loading.value = true
  permission.value = ''
  contentHtml.value = ''
  try {
    const data = await fetchPostBySlug(route.params.slug, auth.token)
    post.value = data
    contentHtml.value = data.content ? md.render(data.content) : ''
    error.value = ''
  } catch (err) {
    const message = err instanceof Error ? err.message : '加载文章失败'
    error.value = message
    if (err.status === 401) {
      await hydratePostMeta()
      permission.value = 'login'
      return
    }
    if (err.status === 403) {
      await hydratePostMeta()
      permission.value = 'upgrade'
      return
    }
    if (message.includes('文章不存在')) {
      router.replace({ name: 'blog' })
    }
  } finally {
    loading.value = false
  }
}

const hydratePostMeta = async () => {
  try {
    const items = await fetchPosts()
    const matched = items.find((item) => item.slug === route.params.slug)
    if (matched) {
      post.value = matched
    }
  } catch (e) {
    console.error('failed to hydrate post meta', e)
  }
}

const handleLogin = async () => {
  submitting.value = true
  try {
    await login(form.email, form.password)
    await loadPost()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    submitting.value = false
  }
}

const handleRegister = async () => {
  submitting.value = true
  try {
    await register(form.email, form.password)
    await loadPost()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '注册失败'
  } finally {
    submitting.value = false
  }
}

const handleUpgrade = async () => {
  submitting.value = true
  try {
    await upgrade()
    await loadPost()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '升级失败'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await bootstrap()
  await loadPost()
})

watch(
  () => route.params.slug,
  async () => {
    error.value = ''
    await loadPost()
  }
)
</script>

<template>
  <div class="w-full px-6 pb-24 md:px-12">
    <div v-if="loading" class="text-center text-sm text-gray-500">
      正在载入文章...
    </div>

    <div v-else>
      <div v-if="permission === 'login'" class="mx-auto max-w-xl rounded-2xl border border-gray-200 bg-white/80 p-8 shadow-soft">
        <h1 class="text-center text-2xl font-semibold text-gray-900">
          {{ post?.title ?? '登录后查看全文' }}
        </h1>
        <p class="mt-3 text-center text-sm text-gray-500">
          这是一篇仅限注册用户阅读的文章，请先登录或注册账号。
        </p>
        <form
          class="mt-8 space-y-4"
          @submit.prevent="mode === 'login' ? handleLogin() : handleRegister()"
        >
          <label class="block space-y-2 text-sm text-gray-600">
            <span>邮箱</span>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:border-gray-400 focus:outline-none"
              placeholder="you@example.com"
            />
          </label>
          <label class="block space-y-2 text-sm text-gray-600">
            <span>密码</span>
            <input
              v-model="form.password"
              type="password"
              required
              class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:border-gray-400 focus:outline-none"
              placeholder="至少 6 位"
            />
          </label>
          <button
            type="submit"
            :disabled="submitting"
            class="flex w-full items-center justify-center rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            {{ submitting ? '处理中...' : mode === 'login' ? '登录并阅读' : '注册并阅读' }}
          </button>
        </form>
        <div class="mt-4 text-center text-xs text-gray-500">
          <button
            type="button"
            class="font-medium text-gray-700 underline"
            @click="mode = mode === 'login' ? 'register' : 'login'"
          >
            {{ mode === 'login' ? '没有账号？点击注册' : '已有账号？点击登录' }}
          </button>
        </div>
        <p v-if="error" class="mt-3 text-center text-sm text-red-500">{{ error }}</p>
      </div>

      <div
        v-else-if="permission === 'upgrade'"
        class="mx-auto max-w-xl rounded-2xl border border-amber-200 bg-amber-50 p-8 text-amber-900 shadow-soft"
      >
        <h1 class="text-center text-2xl font-semibold">
          {{ post?.title ?? '会员专享内容' }}
        </h1>
        <p class="mt-3 text-center text-sm">
          这篇文章仅对会员开放。升级会员后即可立即阅读全文。
        </p>
        <div class="mt-6 flex flex-col items-center gap-3 text-sm">
          <button
            type="button"
            :disabled="submitting"
            class="w-full rounded-lg bg-amber-600 px-4 py-2 font-semibold text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-amber-300"
            @click="handleUpgrade"
          >
            {{ submitting ? '处理中...' : '升级会员并解锁' }}
          </button>
          <p class="text-amber-800">
            当前身份：{{ auth.user ? (auth.user.role === 'member' ? '会员' : '注册用户') : '未登录' }}
          </p>
        </div>
        <p v-if="error" class="mt-3 text-center text-sm text-amber-800">{{ error }}</p>
      </div>

      <div v-else-if="error" class="text-center text-sm text-red-500">
        {{ error }}
      </div>

      <article v-else class="mx-auto max-w-3xl space-y-12">
        <header class="space-y-3 text-center">
          <p class="text-xs uppercase tracking-[0.3em] text-gray-400">
            {{ new Date(post.created_at).toLocaleDateString('zh-CN', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            }) }}
          </p>
          <h1 class="text-3xl font-semibold tracking-tight text-gray-900 md:text-4xl">
            {{ post.title }}
          </h1>
          <!-- <p v-if="post.excerpt" class="text-base text-gray-500">
            {{ post.excerpt }}
          </p> -->
          <p class="text-xs text-gray-400">
            可见性：
            <span class="font-semibold text-gray-700">
              {{ post.visibility === 'member' ? '会员可读' : '注册用户可读' }}
            </span>
          </p>
        </header>

        <div class="content-body mx-auto max-w-none text-left" v-html="contentHtml"></div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.content-body {
  color: #4b5563;
  line-height: 1.8;
  font-size: 1rem;
}
.content-body :deep(h1),
.content-body :deep(h2),
.content-body :deep(h3),
.content-body :deep(h4) {
  color: #111827;
  font-weight: 600;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  line-height: 1.4;
}
.content-body :deep(h1) {
  font-size: 2rem;
}
.content-body :deep(h2) {
  font-size: 1.75rem;
}
.content-body :deep(h3) {
  font-size: 1.45rem;
}
.content-body :deep(h4) {
  font-size: 1.25rem;
}
.content-body :deep(p) {
  margin: 1.25rem 0;
}
.content-body :deep(ul),
.content-body :deep(ol) {
  margin: 1.5rem 0 1.5rem 1.75rem;
  padding: 0;
}
.content-body :deep(ul) {
  list-style: disc;
}
.content-body :deep(ol) {
  list-style: decimal;
}
.content-body :deep(li) {
  margin: 0.5rem 0;
}
.content-body :deep(code) {
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  background: #f8fafc;
  border-radius: 0.375rem;
  padding: 0.2rem 0.4rem;
}
.content-body :deep(pre) {
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  background: #0f172a;
  color: #e2e8f0;
  padding: 1.25rem 1.5rem;
  border-radius: 0.75rem;
  overflow-x: auto;
  margin: 2rem 0;
}
.content-body :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  display: block;
  white-space: pre;
}
.content-body :deep(a) {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.content-body :deep(blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  color: #6b7280;
  font-style: italic;
  margin: 2rem 0;
}
.content-body :deep(img) {
  border-radius: 0.75rem;
  margin: 2.5rem auto;
  display: block;
  max-width: 100%;
}
.content-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 2rem 0;
}
.content-body :deep(th),
.content-body :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  text-align: left;
}
</style>
