const API_URL = 'http://127.0.0.1:5000/api'

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('emp_token')

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  if (token) {
    headers['Authentication-Token'] = token
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || 'Something went wrong')
  }

  return data
}