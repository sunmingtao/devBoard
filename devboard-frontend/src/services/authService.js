import axios from 'axios'

const API_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'}/auth`

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
  async login(username, password) {
    const response = await authApi.post('/login', { username, password })
    const data = response.data
    
    // Store token and user data
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify({
      id: data.id,
      username: data.username,
      email: data.email,
      role: data.role
    }))
    
    return data
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

  // Check if user is logged in and token is not expired
  isAuthenticated() {
    const token = localStorage.getItem('token')
    if (!token) return false
    
    // Check if token is expired
    if (this.isTokenExpired(token)) {
      this.logout() // Auto logout if expired
      return false
    }
    
    return true
  },

  // Get stored token
  getToken() {
    return localStorage.getItem('token')
  },

  // Get stored user info
  getUser() {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    
    try {
      return JSON.parse(userStr)
    } catch (error) {
      console.error('Failed to parse user data:', error)
      return null
    }
  },

  // Alias for getUser to match test expectations
  getCurrentUser() {
    return this.getUser()
  },

  // Check if current user is admin
  isAdmin() {
    const user = this.getUser()
    return !!(user && user.role === 'ADMIN')
  },

  // Decode JWT token to get payload
  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('Failed to decode token:', error)
      return null
    }
  },

  // Check if token is expired
  isTokenExpired(token) {
    if (!token) return true
    
    const decoded = this.decodeToken(token)
    if (!decoded || !decoded.exp) return true
    
    const currentTime = Date.now() / 1000
    return decoded.exp < currentTime
  },

  // Get time until token expires (in minutes)
  getTokenExpiryTime(token = null) {
    const tokenToCheck = token || this.getToken()
    if (!tokenToCheck) return 0
    
    const decoded = this.decodeToken(tokenToCheck)
    if (!decoded || !decoded.exp) return 0
    
    const currentTime = Date.now() / 1000
    const timeLeft = decoded.exp - currentTime
    return Math.max(0, Math.floor(timeLeft / 60)) // Return minutes
  },

  // Check if token will expire soon (within 5 minutes)
  isTokenExpiringSoon(token = null) {
    const minutesLeft = this.getTokenExpiryTime(token)
    return minutesLeft <= 5 && minutesLeft > 0
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

export default authService