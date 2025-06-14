import { render } from '@testing-library/vue'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from '@/router'

// Helper to render components with router
export function renderWithRouter(component, options = {}) {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  })

  return render(component, {
    global: {
      plugins: [router],
      ...options.global
    },
    ...options
  })
}

// Helper to wait for async operations
export function waitForElement(callback, options = {}) {
  const { timeout = 1000 } = options
  return new Promise((resolve, reject) => {
    const startTime = Date.now()
    
    const check = () => {
      try {
        const result = callback()
        if (result) {
          resolve(result)
        } else if (Date.now() - startTime > timeout) {
          reject(new Error('Timeout waiting for element'))
        } else {
          setTimeout(check, 50)
        }
      } catch (error) {
        if (Date.now() - startTime > timeout) {
          reject(error)
        } else {
          setTimeout(check, 50)
        }
      }
    }
    
    check()
  })
}

// Mock auth state
export function mockAuthState(isAuthenticated = true, user = null) {
  const defaultUser = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    role: 'USER'
  }

  if (isAuthenticated) {
    localStorage.setItem('token', 'mock-jwt-token')
    localStorage.setItem('user', JSON.stringify(user || defaultUser))
  } else {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}