import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import authService from '@/services/authService'
import { routes } from '../index'

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isAdmin: vi.fn()
  }
}))

describe('Router Guards', () => {
  let router

  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Create fresh router instance
    router = createRouter({
      history: createWebHistory(),
      routes
    })
    
    // Wait for router to be ready
    await router.isReady()
  })

  describe('requiresAuth guard', () => {
    it('allows authenticated users to access protected routes', async () => {
      authService.isAuthenticated.mockReturnValue(true)

      const result = await router.push('/tasks')
      
      expect(router.currentRoute.value.path).toBe('/tasks')
    })

    it('redirects unauthenticated users to login', async () => {
      authService.isAuthenticated.mockReturnValue(false)

      await router.push('/tasks')
      
      expect(router.currentRoute.value.path).toBe('/login')
      expect(router.currentRoute.value.query.returnUrl).toBe('/tasks')
    })

    it('includes returnUrl for nested routes', async () => {
      authService.isAuthenticated.mockReturnValue(false)

      await router.push('/tasks/1')
      
      expect(router.currentRoute.value.path).toBe('/login')
      expect(router.currentRoute.value.query.returnUrl).toBe('/tasks/1')
    })
  })

  describe('requiresAdmin guard', () => {
    it('allows admin users to access admin routes', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)

      await router.push('/admin')
      
      expect(router.currentRoute.value.path).toBe('/admin')
    })

    it('redirects non-admin users to home', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(false)

      await router.push('/admin')
      
      expect(router.currentRoute.value.path).toBe('/')
    })

    it('redirects unauthenticated users to login', async () => {
      authService.isAuthenticated.mockReturnValue(false)
      authService.isAdmin.mockReturnValue(false)

      await router.push('/admin')
      
      expect(router.currentRoute.value.path).toBe('/login')
      expect(router.currentRoute.value.query.returnUrl).toBe('/admin')
    })
  })

  describe('guest guard', () => {
    it('allows unauthenticated users to access login', async () => {
      authService.isAuthenticated.mockReturnValue(false)

      await router.push('/login')
      
      expect(router.currentRoute.value.path).toBe('/login')
    })

    it('redirects authenticated users from login to home', async () => {
      authService.isAuthenticated.mockReturnValue(true)

      await router.push('/login')
      
      expect(router.currentRoute.value.path).toBe('/')
    })

    it('redirects authenticated users from register to home', async () => {
      authService.isAuthenticated.mockReturnValue(true)

      await router.push('/register')
      
      expect(router.currentRoute.value.path).toBe('/')
    })
  })

  describe('navigation flow', () => {
    it('allows navigation between unprotected routes', async () => {
      authService.isAuthenticated.mockReturnValue(false)

      await router.push('/')
      expect(router.currentRoute.value.path).toBe('/')

      await router.push('/about')
      expect(router.currentRoute.value.path).toBe('/about')
    })

    it('preserves query params during redirects', async () => {
      authService.isAuthenticated.mockReturnValue(false)

      await router.push('/tasks?filter=active&sort=date')
      
      expect(router.currentRoute.value.path).toBe('/login')
      expect(router.currentRoute.value.query.returnUrl).toBe('/tasks?filter=active&sort=date')
    })
  })

  describe('404 handling', () => {
    it('shows 404 page for unknown routes', async () => {
      await router.push('/non-existent-route')
      
      expect(router.currentRoute.value.name).toBe('NotFound')
    })

    it('preserves 404 behavior for authenticated users', async () => {
      authService.isAuthenticated.mockReturnValue(true)

      await router.push('/non-existent-route')
      
      expect(router.currentRoute.value.name).toBe('NotFound')
    })
  })
})