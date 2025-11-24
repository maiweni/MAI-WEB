const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const jsonHeaders = {
  'Content-Type': 'application/json',
}

const handleResponse = async (response) => {
  const text = await response.text()
  let data = null
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }
  if (!response.ok) {
    const error = new Error(
      (data && (data.detail || data.message)) || '请求接口时发生错误'
    )
    error.status = response.status
    throw error
  }
  return data
}

export const register = async (payload) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

export const login = async (payload) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

export const fetchMe = async (token) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      ...jsonHeaders,
      Authorization: `Bearer ${token}`,
    },
  })
  return handleResponse(response)
}

export const upgradeMembership = async (token) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/upgrade`, {
    method: 'POST',
    headers: {
      ...jsonHeaders,
      Authorization: `Bearer ${token}`,
    },
  })
  return handleResponse(response)
}
