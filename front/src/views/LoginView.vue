<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../utils/authStore'

const router = useRouter()
const route = useRoute()
const { login, register, state } = useAuthStore()

const form = reactive({ email: '', password: '' })
const submitting = ref(false)
const mode = ref('login')
const error = ref('')

const handleSubmit = async () => {
  submitting.value = true
  error.value = ''
  try {
    if (mode.value === 'login') {
      await login(form.email, form.password)
    } else {
      await register(form.email, form.password)
    }
    const redirect = route.query.redirect || { name: 'blog' }
    router.push(redirect)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '操作失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center px-6 py-12 md:px-12">
    <div class="w-full max-w-md rounded-2xl border border-gray-200 bg-white/90 p-8 shadow-soft">
      <h1 class="text-center text-2xl font-semibold text-gray-900">
        {{ mode === 'login' ? '登录以阅读' : '注册并开始阅读' }}
      </h1>
      <p class="mt-2 text-center text-sm text-gray-500">
        登录后即可查看注册/会员文章
      </p>
      <form class="mt-8 space-y-4" @submit.prevent="handleSubmit">
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
          :disabled="submitting || state.loading"
          class="flex w-full items-center justify-center rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {{ submitting || state.loading ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
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
  </div>
</template>
