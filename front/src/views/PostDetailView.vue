<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

import { fetchPostBySlug } from '../services/api'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(true)
const error = ref('')
const contentHtml = ref('')

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

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

const loadMarkdownContent = async (markdownPath) => {
  if (!markdownPath) {
    contentHtml.value = ''
    return
  }
  const url = new URL(markdownPath, API_BASE_URL).toString()
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('文章正文加载失败')
  }
  const rawMarkdown = await response.text()
  contentHtml.value = md.render(rawMarkdown)
}

const loadPost = async () => {
  try {
    const data = await fetchPostBySlug(route.params.slug)
    post.value = data
    await loadMarkdownContent(data.content_path)
    error.value = ''
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载文章失败'
    if (error.value.includes('文章不存在')) {
      router.replace({ name: 'blog' })
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadPost)
watch(
  () => route.params.slug,
  () => {
    loading.value = true
    error.value = ''
    contentHtml.value = ''
    loadPost()
  }
)
</script>

<template>
  <div class="w-full px-6 pb-24 md:px-12">
    <div v-if="loading" class="text-center text-sm text-gray-500">
      正在载入文章...
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
        <p v-if="post.excerpt" class="text-base text-gray-500">
          {{ post.excerpt }}
        </p>
      </header>

      <div class="content-body mx-auto max-w-none text-left" v-html="contentHtml"></div>
    </article>
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
