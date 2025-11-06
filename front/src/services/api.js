const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const handleResponse = async (response) => {
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || '请求接口时发生错误')
  }
  return response.json()
}

export const fetchPosts = async () => {
  const response = await fetch(`${API_BASE_URL}/api/posts`)
  return handleResponse(response)
}

export const fetchPostBySlug = async (slug) => {
  const response = await fetch(`${API_BASE_URL}/api/posts/slug/${slug}`)
  return handleResponse(response)
}
