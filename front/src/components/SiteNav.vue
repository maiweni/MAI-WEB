<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../utils/authStore'

const route = useRoute()
const router = useRouter()
const { state, logout, bootstrap, upgrade } = useAuthStore()

const links = computed(() => [
  { name: '首页', to: { name: 'home' } },
  { name: '博客', to: { name: 'blog' } },
  { name: '关于', to: { name: 'about' } },
  { name: '联系', to: { name: 'contact' } },
])

const isActive = (target) => route.name === target

const roleLabel = computed(() => {
  if (!state.user) return '未登录'
  if (state.user.role === 'admin') return '管理员'
  if (state.user.role === 'member') return '会员'
  return '注册用户'
})

const displayName = computed(() => {
  if (!state.user) return '未登录'
  if (state.user.name) return state.user.name
  if (state.user.email) {
    const [prefix] = state.user.email.split('@')
    return prefix || state.user.email
  }
  return '用户'
})

const memberStatus = computed(() => {
  if (!state.user) return ''
  if (state.user.role === 'admin') return '管理员'
  if (state.user.role === 'member') return '会员'
  return '注册用户'
})

const showProfile = ref(false)

const toggleProfile = () => {
  showProfile.value = !showProfile.value
}

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date)
}

const handleUpgrade = async () => {
  await upgrade()
  showProfile.value = false
}

const handleLogout = () => {
  logout()
  showProfile.value = false
}

const goLogin = () => {
  if (state.user) return
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}

onMounted(() => {
  bootstrap()
})
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
      <div class="relative flex items-center gap-3">
        <button
          v-if="!state.user"
          type="button"
          class="text-sm font-medium text-gray-600 transition hover:text-gray-900"
          @click="goLogin"
        >
          登录以阅读
        </button>
        <button
          v-else
          type="button"
          class="flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-left text-xs font-semibold text-gray-800 shadow-sm transition hover:bg-gray-200"
          @click="toggleProfile"
        >
          <span class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-gray-800 text-xs font-bold text-white">
            {{ displayName.slice(0, 1).toUpperCase() }}
          </span>
          <span class="flex flex-col leading-tight">
            <span>{{ displayName }}</span>
            <span class="text-[10px] font-normal text-gray-500">{{ memberStatus }}</span>
          </span>
        </button>

        <div
          v-if="showProfile"
          class="absolute right-0 top-12 w-72 rounded-2xl border border-gray-200 bg-white p-4 text-sm shadow-lg"
        >
          <div class="flex items-center gap-3">
            <span class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-gray-800 text-sm font-bold text-white">
              {{ displayName.slice(0, 1).toUpperCase() }}
            </span>
            <div class="flex flex-col">
              <span class="text-base font-semibold text-gray-900">{{ displayName }}</span>
              <span class="text-xs text-gray-500">{{ roleLabel }}</span>
            </div>
          </div>
          <div class="mt-4 space-y-2 text-gray-700">
            <p><span class="text-gray-500">邮箱：</span>{{ state.user.email }}</p>
            <p><span class="text-gray-500">注册时间：</span>{{ formatDate(state.user.created_at) }}</p>
            <p v-if="state.user.membership_expires_at">
              <span class="text-gray-500">会员到期：</span>{{ formatDate(state.user.membership_expires_at) }}
            </p>
          </div>
          <div class="mt-4 flex items-center gap-3">
            <button
              v-if="state.user.role !== 'member' && state.user.role !== 'admin'"
              type="button"
              class="flex-1 rounded-lg bg-amber-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-amber-300"
              :disabled="state.loading"
              @click="handleUpgrade"
            >
              {{ state.loading ? '处理中...' : '升级会员' }}
            </button>
            <button
              type="button"
              class="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-xs font-semibold text-gray-700 transition hover:bg-gray-50"
              @click="handleLogout"
            >
              退出
            </button>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>
