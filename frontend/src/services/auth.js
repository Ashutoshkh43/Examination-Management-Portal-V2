import { apiRequest } from './api'

export function loginUser(data) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export function registerStudent(data) {
  return apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export function getCurrentUser() {
  return apiRequest('/auth/me')
}

export function logoutUser() {
  return apiRequest('/auth/logout', {
    method: 'POST'
  })
}