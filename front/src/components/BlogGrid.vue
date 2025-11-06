<script setup>
defineProps({
  posts: {
    type: Array,
    default: () => [],
  },
})

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date)
}

const resolveExcerpt = (post) => {
  if (post.excerpt) return post.excerpt
  if (post.summary) return post.summary
  return '这篇文章正在整理摘要，敬请期待。'
}

const resolveTag = (post) => {
  if (!post.tags) return ''
  if (Array.isArray(post.tags)) {
    return post.tags.find(Boolean) ?? ''
  }
  if (typeof post.tags === 'string') {
    const segments = post.tags.split(',').map((item) => item.trim()).filter(Boolean)
    return segments[0] ?? ''
  }
  return ''
}

const resolveLink = (post) => {
  if (post.slug) return `/blog/${post.slug}`
  if (post.url) return post.url
  return '#'
}
</script>

<template>
  <section
    id="blog"
    class="w-full px-6 pb-24 md:px-12"
  >
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <article
        v-for="post in posts"
        :key="post.id ?? post.slug ?? post.title"
        class="group flex h-full flex-col justify-between rounded-2xl border border-gray-200 bg-white/90 p-6 shadow-soft transition hover:-translate-y-1 hover:shadow-xl"
      >
        <div class="flex flex-col gap-4">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">
            {{ formatDate(post.created_at ?? post.published_at ?? post.date) }}
          </p>
          <h3 class="text-xl font-semibold text-gray-900">
            {{ post.title }}
          </h3>
          <p class="text-sm leading-relaxed text-gray-500">
            {{ resolveExcerpt(post) }}
          </p>
        </div>
        <div class="mt-6 flex items-center justify-between text-sm">
          <a
            :href="resolveLink(post)"
            class="inline-flex items-center gap-2 font-medium text-gray-600 transition group-hover:text-gray-900"
          >
            阅读全文
            <span aria-hidden="true" class="transition group-hover:translate-x-1"
              >&rarr;</span
            >
          </a>
          <span
            v-if="resolveTag(post)"
            class="text-xs uppercase tracking-[0.3em] text-gray-400"
          >
            {{ resolveTag(post) }}
          </span>
        </div>
      </article>
    </div>
  </section>
</template>
