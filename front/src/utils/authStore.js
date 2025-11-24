import { reactive } from 'vue'
import { fetchMe, login as loginApi, register as registerApi, upgradeMembership } from '../services/auth'

const state = reactive({
  user: null,
  token: localStorage.getItem('mai_token') || '',
  ready: false,
  loading: false,
})

let bootstrapPromise = null

const persistToken = (token) => {
  state.token = token
  if (token) {
    localStorage.setItem('mai_token', token)
  } else {
    localStorage.removeItem('mai_token')
  }
}

const bootstrap = async () => {
  if (state.ready) return
  if (bootstrapPromise) return bootstrapPromise
  bootstrapPromise = (async () => {
    if (!state.token) {
      state.ready = true
      return
    }
    try {
      state.user = await fetchMe(state.token)
    } catch (err) {
      console.error('failed to restore session', err)
      persistToken('')
      state.user = null
    } finally {
      state.ready = true
    }
  })()
  return bootstrapPromise
}

const login = async (email, password) => {
  state.loading = true
  try {
    const data = await loginApi({ email, password })
    persistToken(data.access_token)
    state.user = data.user
    return data.user
  } finally {
    state.loading = false
  }
}

const register = async (email, password) => {
  state.loading = true
  try {
    const data = await registerApi({ email, password })
    persistToken(data.access_token)
    state.user = data.user
    return data.user
  } finally {
    state.loading = false
  }
}

const logout = () => {
  persistToken('')
  state.user = null
}

const upgrade = async () => {
  if (!state.token) throw new Error('需要登录')
  state.loading = true
  try {
    const data = await upgradeMembership(state.token)
    state.user = data
    return data
  } finally {
    state.loading = false
  }
}

export const useAuthStore = () => ({
  state,
  login,
  register,
  logout,
  upgrade,
  bootstrap,
})
