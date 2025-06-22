import { describe, it, expect, vi, beforeEach } from 'vitest'
import authService from '../authService'

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('login', () => {
    it('successfully logs in and stores user data', async () => {
      // Clear any previous calls
      localStorage.setItem.mockClear()
      
      const result = await authService.login('testuser', 'password123')

      // Check localStorage
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'mock-jwt-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify({
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER',
        nickname: 'Test User'
      }))

      // Check return value
      expect(result).toEqual({
        token: 'mock-jwt-token',
        type: 'Bearer',
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER',
        nickname: 'Test User'
      })
    })

    it('throws error on login failure', async () => {
      await expect(authService.login('wrong', 'credentials'))
        .rejects.toThrow('Invalid credentials')
    })
  })

  describe('register', () => {
    it('successfully registers a new user', async () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      }

      const result = await authService.register(userData)

      expect(result).toEqual({
        id: 2,
        username: 'newuser',
        email: 'new@example.com',
        role: 'USER'
      })
    })

    it('throws error on registration failure', async () => {
      await expect(authService.register({
        username: 'existinguser',
        email: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow('Username already exists')
    })
  })

  describe('logout', () => {
    it('clears localStorage on logout', () => {
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
      
      // authService has try/catch that returns null for invalid JSON
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
      // Mock a valid JWT token with future expiration
      const futureTime = Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
      const mockToken = `header.${btoa(JSON.stringify({ exp: futureTime }))}.signature`
      
      localStorage.getItem.mockReturnValueOnce(mockToken)

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