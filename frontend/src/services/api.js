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

  let response
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers
    })
  } catch (error) {
    throw new Error(`Cannot reach the EMP API at ${API_URL}. Check that Flask is running.`)
  }

  const responseText = await response.text()
  let data = {}
  try {
    data = responseText ? JSON.parse(responseText) : {}
  } catch {
    data = { message: '' }
  }

  if (!response.ok) {
    const nestedErrors = data.response?.errors || data.errors
    const nestedMessage = Array.isArray(nestedErrors)
      ? nestedErrors.join(', ')
      : typeof nestedErrors === 'string' ? nestedErrors : ''
    const message = data.message || data.error || nestedMessage
    if (message) throw new Error(message)
    if (response.status === 401) throw new Error('Your session is not authorized. Sign in again and retry.')
    if (response.status === 403) throw new Error('Your account does not have permission to perform this action.')
    if (response.status >= 500) throw new Error(`The EMP server returned HTTP ${response.status}. Check the Flask terminal for the detailed error.`)
    throw new Error(`The request failed with HTTP ${response.status} ${response.statusText}.`)
  }

  return data
}
