import axios from 'axios'

const API_URL = 'http://localhost:8080/api/auth'

// Create axios instance with base configuration
const authApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const authService = {
  // Register new user
  async register(userData) {
    const response = await authApi.post('/signup', userData)
    return response.data
  },

  // Login user
  async login(credentials) {
    const response = await authApi.post('/login', credentials)
    return response.data
  },

  // Get current user info
  async getCurrentUser(token) {
    const response = await authApi.get('/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  },

  // Logout (client-side only)
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  // Check if user is logged in
  isAuthenticated() {
    return !!localStorage.getItem('token')
  },

  // Get stored token
  getToken() {
    return localStorage.getItem('token')
  },

  // Get stored user info
  getUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },
}

// Add request interceptor to include token in all requests
authApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token && config.url !== '/login' && config.url !== '/signup') {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle 401 errors
authApi.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      authService.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)