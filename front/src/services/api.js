const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

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

const withAuthHeaders = (options = {}, token) => {
  if (token) {
    return {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    }
  }
  return options
}

export const fetchPosts = async () => {
  const response = await fetch(`${API_BASE_URL}/api/posts`)
  return handleResponse(response)
}

export const fetchPostBySlug = async (slug, token) => {
  const response = await fetch(
    `${API_BASE_URL}/api/posts/slug/${slug}`,
    withAuthHeaders({}, token)
  )
  return handleResponse(response)
}
