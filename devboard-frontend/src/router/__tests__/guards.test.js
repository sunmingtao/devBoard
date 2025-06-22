import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import authService from '@/services/authService'
import { routes } from '../index'

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isAdmin: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock window.alert
global.alert = vi.fn()

describe('Router Guards', () => {
  let router

  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Create a fresh router for each test with memory history
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
    
    // Add the navigation guard from index.js
    router.beforeEach((to, from, next) => {
      // Update page title
      document.title = to.meta.title || 'DevBoard'
      
      // Check if route requires authentication
      if (to.meta.requiresAuth) {
        if (!authService.isAuthenticated()) {
          // Redirect to login with return URL
          next({
            path: '/login',
            query: { returnUrl: to.fullPath }
          })
          return
        }
        
        // Check if route requires admin role
        if (to.meta.requiresAdmin) {
          if (!authService.isAdmin()) {
            // Redirect to home if not admin
            alert('Access denied: Admin role required')
            next('/')
            return
          }
        }
        
        next()
      } else {
        // Handle guest routes (login/register)
        if ((to.path === '/login' || to.path === '/register') && authService.isAuthenticated()) {
          // Redirect authenticated users away from login/register
          next('/')
          return
        }
        
        next()
      }
    })
    
    // Wait for router to be ready
    await router.isReady()
  })

  describe('requiresAuth guard', () => {
    it('allows authenticated users to access protected routes', async () => {
      authService.isAuthenticated.mockReturnValue(true)

      await router.push('/tasks')
      
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
      expect(global.alert).toHaveBeenCalledWith('Access denied: Admin role required')
    })

    it('redirects unauthenticated users to login', async () => {
      authService.isAuthenticated.mockReturnValue(false)

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