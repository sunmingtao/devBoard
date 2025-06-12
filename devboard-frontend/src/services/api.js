import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    console.log('🚀 Making API request:', config.method?.toUpperCase(), config.url)
    
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('🔑 Token added to request:', token.substring(0, 20) + '...')
    } else {
      console.warn('⚠️ No token found in localStorage')
    }
    
    return config
  },
  error => {
    console.error('❌ Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    console.log('✅ API response received:', response.status, response.config.url)
    return response
  },
  error => {
    console.error('❌ API error:', error.response?.status, error.message)
    
    if (error.response?.status === 401) {
      console.error('🔐 Unauthorized - redirecting to login')
      
      // Clear auth data
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Show user-friendly message based on context
      const currentPath = window.location.pathname
      let message = 'Your session has expired. Please log in again.'
      
      if (currentPath.includes('/admin')) {
        message = 'Admin access required. Please log in with admin credentials.'
      } else if (error.config?.url?.includes('/admin/')) {
        message = 'Admin privileges required for this action.'
      }
      
      // Dispatch custom event for other components to handle
      window.dispatchEvent(new CustomEvent('auth-error', {
        detail: { 
          status: 401, 
          message: message,
          redirectTo: '/login'
        }
      }))
      
      // Small delay to allow components to handle the event
      setTimeout(() => {
        window.location.href = '/login'
      }, 100)
    } else if (error.response?.status === 403) {
      console.error('🚫 Forbidden - insufficient permissions')
      
      // Dispatch custom event for permission errors
      window.dispatchEvent(new CustomEvent('auth-error', {
        detail: { 
          status: 403, 
          message: 'You do not have permission to perform this action.',
          redirectTo: null // Don't redirect, just show error
        }
      }))
    } else if (error.response?.status === 404) {
      console.error('🔍 Resource not found')
    } else if (error.response?.status >= 500) {
      console.error('🔥 Server error')
    } else if (error.code === 'ECONNREFUSED') {
      console.error('🔌 Cannot connect to backend server. Is it running on localhost:8080?')
    }
    
    return Promise.reject(error)
  }
)

export default api