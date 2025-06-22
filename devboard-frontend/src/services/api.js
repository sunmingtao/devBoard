import axios from 'axios'

// Environment-based configuration
const config = {
  // Use environment variable or fallback to localhost
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
}

// Log configuration in development
if (import.meta.env.VITE_ENABLE_DEBUG_LOGS === 'true') {
  console.log('🔧 API Configuration:', {
    baseURL: config.baseURL,
    environment: import.meta.env.VITE_APP_ENVIRONMENT,
    debugMode: import.meta.env.VITE_ENABLE_DEBUG_LOGS
  })
}

// Create axios instance with environment-based configuration
const api = axios.create(config)

// Environment-aware logging
const isDevelopment = import.meta.env.VITE_APP_ENVIRONMENT === 'development'
const enableDebugLogs = import.meta.env.VITE_ENABLE_DEBUG_LOGS === 'true'
const showApiResponses = import.meta.env.VITE_SHOW_API_RESPONSES === 'true'

// Request interceptor
api.interceptors.request.use(
  config => {
    if (enableDebugLogs) {
      console.log('🚀 Making API request:', config.method?.toUpperCase(), config.url)
    }
    
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      if (enableDebugLogs) {
        console.log('🔑 Token added to request:', token.substring(0, 20) + '...')
      }
    } else if (enableDebugLogs) {
      console.warn('⚠️ No token found in localStorage')
    }
    
    return config
  },
  error => {
    if (isDevelopment) {
      console.error('❌ Request error:', error)
    }
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    if (showApiResponses) {
      console.log('✅ API response received:', response.status, response.config.url)
      if (enableDebugLogs) {
        console.log('📦 Response data:', response.data)
      }
    }
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
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth-error', {
          detail: { 
            status: 401, 
            message: message,
            redirectTo: '/login'
          }
        }))
        
        // Small delay to allow components to handle the event
        setTimeout(() => {
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
        }, 100)
      }
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