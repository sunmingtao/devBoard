import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import Login from '../Login.vue'
import authService from '@/services/authService'
import { renderWithRouter } from '@/test/utils'

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    login: vi.fn(),
    isAuthenticated: vi.fn()
  }
}))

// Mock router
const mockPush = vi.fn()
const mockRoute = { query: {} }

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => mockRoute,
  RouterLink: {
    name: 'RouterLink',
    template: '<a><slot /></a>'
  }
}))

describe('Login.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    authService.isAuthenticated.mockReturnValue(false)
  })

  const createWrapper = () => {
    wrapper = mount(Login, {
      global: {
        stubs: {
          RouterLink: true
        }
      }
    })
  }

  describe('initial render', () => {
    it('renders login form', () => {
      createWrapper()

      expect(wrapper.find('h1').text()).toBe('Login')
      expect(wrapper.find('#username').exists()).toBe(true)
      expect(wrapper.find('#password').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').text()).toBe('Login')
    })

    it('redirects if already authenticated', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      
      createWrapper()
      await nextTick()

      expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('shows register link', () => {
      createWrapper()

      const text = wrapper.text()
      expect(text).toContain("Don't have an account?")
      expect(text).toContain('Register here')
    })
  })

  describe('form submission', () => {
    beforeEach(() => {
      createWrapper()
    })

    it('successfully logs in user', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER'
      }

      authService.login.mockResolvedValueOnce(mockUser)

      // Fill in form
      await wrapper.find('#username').setValue('testuser')
      await wrapper.find('#password').setValue('password123')

      // Submit form
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      // Check login was called
      expect(authService.login).toHaveBeenCalledWith('testuser', 'password123')

      // Check redirect
      expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('redirects to returnUrl after login', async () => {
      mockRoute.query = { returnUrl: '/tasks/1' }
      
      authService.login.mockResolvedValueOnce({ id: 1, role: 'USER' })

      await wrapper.find('#username').setValue('testuser')
      await wrapper.find('#password').setValue('password123')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(mockPush).toHaveBeenCalledWith('/tasks/1')
    })

    it('shows error message on login failure', async () => {
      authService.login.mockRejectedValueOnce(new Error('Invalid credentials'))

      await wrapper.find('#username').setValue('testuser')
      await wrapper.find('#password').setValue('wrongpass')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(wrapper.find('.error-message').text()).toContain('Invalid credentials')
    })

    it('disables form during submission', async () => {
      authService.login.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      )

      await wrapper.find('#username').setValue('testuser')
      await wrapper.find('#password').setValue('password123')
      
      const submitPromise = wrapper.find('form').trigger('submit.prevent')
      await nextTick()

      // Check loading state
      expect(wrapper.find('button[type="submit"]').element.disabled).toBe(true)
      expect(wrapper.find('button[type="submit"]').text()).toBe('Logging in...')

      await submitPromise
      await flushPromises()
    })
  })

  describe('form validation', () => {
    beforeEach(() => {
      createWrapper()
    })

    it('requires username', async () => {
      await wrapper.find('#password').setValue('password123')
      await wrapper.find('form').trigger('submit.prevent')

      expect(authService.login).not.toHaveBeenCalled()
    })

    it('requires password', async () => {
      await wrapper.find('#username').setValue('testuser')
      await wrapper.find('form').trigger('submit.prevent')

      expect(authService.login).not.toHaveBeenCalled()
    })

    it('clears error message when typing', async () => {
      // First cause an error
      authService.login.mockRejectedValueOnce(new Error('Invalid credentials'))
      
      await wrapper.find('#username').setValue('testuser')
      await wrapper.find('#password').setValue('wrongpass')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(true)

      // Type in username field
      await wrapper.find('#username').setValue('newuser')
      
      // Error should be cleared
      expect(wrapper.find('.error-message').exists()).toBe(false)
    })
  })

  describe('password visibility toggle', () => {
    beforeEach(() => {
      createWrapper()
    })

    it('toggles password visibility', async () => {
      const passwordInput = wrapper.find('#password')
      const toggleButton = wrapper.find('.password-toggle')

      // Initially password type
      expect(passwordInput.attributes('type')).toBe('password')
      expect(toggleButton.text()).toContain('Show')

      // Click to show
      await toggleButton.trigger('click')
      expect(passwordInput.attributes('type')).toBe('text')
      expect(toggleButton.text()).toContain('Hide')

      // Click to hide
      await toggleButton.trigger('click')
      expect(passwordInput.attributes('type')).toBe('password')
      expect(toggleButton.text()).toContain('Show')
    })
  })
})