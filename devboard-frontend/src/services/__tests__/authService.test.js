import { describe, it, expect, vi, beforeEach } from 'vitest'
import authService from '../authService'
import api from '../api'

// Mock the api module
vi.mock('../api', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('login', () => {
    it('successfully logs in and stores user data', async () => {
      const mockResponse = {
        data: {
          token: 'test-jwt-token',
          type: 'Bearer',
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          role: 'USER'
        }
      }

      api.post.mockResolvedValueOnce(mockResponse)

      const result = await authService.login('testuser', 'password123')

      // Check API was called correctly
      expect(api.post).toHaveBeenCalledWith('/auth/login', {
        username: 'testuser',
        password: 'password123'
      })

      // Check localStorage
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'test-jwt-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify({
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER'
      }))

      // Check return value
      expect(result).toEqual({
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER'
      })
    })

    it('throws error on login failure', async () => {
      const mockError = new Error('Invalid credentials')
      mockError.response = { status: 401 }
      
      api.post.mockRejectedValueOnce(mockError)

      await expect(authService.login('testuser', 'wrongpass'))
        .rejects.toThrow('Invalid credentials')

      // Check localStorage wasn't modified
      expect(localStorage.setItem).not.toHaveBeenCalled()
    })
  })

  describe('register', () => {
    it('successfully registers a new user', async () => {
      const mockResponse = {
        data: {
          id: 2,
          username: 'newuser',
          email: 'new@example.com',
          role: 'USER'
        }
      }

      api.post.mockResolvedValueOnce(mockResponse)

      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      }

      const result = await authService.register(userData)

      expect(api.post).toHaveBeenCalledWith('/auth/register', userData)
      expect(result).toEqual(mockResponse.data)
    })

    it('throws error on registration failure', async () => {
      const mockError = new Error('Username already exists')
      mockError.response = { status: 400 }
      
      api.post.mockRejectedValueOnce(mockError)

      await expect(authService.register({
        username: 'existinguser',
        email: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow('Username already exists')
    })
  })

  describe('logout', () => {
    it('clears localStorage on logout', () => {
      // Set some data first
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', JSON.stringify({ id: 1 }))

      authService.logout()

      expect(localStorage.removeItem).toHaveBeenCalledWith('token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    })
  })

  describe('getCurrentUser', () => {
    it('returns user from localStorage', () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER'
      }

      localStorage.getItem.mockReturnValueOnce(JSON.stringify(mockUser))

      const user = authService.getCurrentUser()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('user')
      expect(user).toEqual(mockUser)
    })

    it('returns null when no user in localStorage', () => {
      localStorage.getItem.mockReturnValueOnce(null)

      const user = authService.getCurrentUser()
      
      expect(user).toBeNull()
    })

    it('returns null when localStorage has invalid JSON', () => {
      localStorage.getItem.mockReturnValueOnce('invalid-json')

      const user = authService.getCurrentUser()
      
      expect(user).toBeNull()
    })
  })

  describe('getToken', () => {
    it('returns token from localStorage', () => {
      localStorage.getItem.mockReturnValueOnce('test-jwt-token')

      const token = authService.getToken()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('token')
      expect(token).toBe('test-jwt-token')
    })

    it('returns null when no token', () => {
      localStorage.getItem.mockReturnValueOnce(null)

      const token = authService.getToken()
      
      expect(token).toBeNull()
    })
  })

  describe('isAuthenticated', () => {
    it('returns true when token exists', () => {
      localStorage.getItem.mockReturnValueOnce('test-jwt-token')

      expect(authService.isAuthenticated()).toBe(true)
    })

    it('returns false when no token', () => {
      localStorage.getItem.mockReturnValueOnce(null)

      expect(authService.isAuthenticated()).toBe(false)
    })
  })

  describe('isAdmin', () => {
    it('returns true for admin user', () => {
      const adminUser = {
        id: 1,
        username: 'admin',
        role: 'ADMIN'
      }

      localStorage.getItem.mockReturnValueOnce(JSON.stringify(adminUser))

      expect(authService.isAdmin()).toBe(true)
    })

    it('returns false for regular user', () => {
      const regularUser = {
        id: 1,
        username: 'user',
        role: 'USER'
      }

      localStorage.getItem.mockReturnValueOnce(JSON.stringify(regularUser))

      expect(authService.isAdmin()).toBe(false)
    })

    it('returns false when no user', () => {
      localStorage.getItem.mockReturnValueOnce(null)

      expect(authService.isAdmin()).toBe(false)
    })
  })
})