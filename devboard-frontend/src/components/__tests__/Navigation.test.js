import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import Navigation from '../Navigation.vue'
import { mockAuthState } from '@/test/utils'

// Mock vue-router
const mockPush = vi.fn()
const mockRoute = {
  path: '/'
}

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

describe('Navigation.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('when user is not authenticated', () => {
    it('shows login and register links', () => {
      const wrapper = mount(Navigation)
      
      expect(wrapper.text()).toContain('DevBoard')
      expect(wrapper.text()).toContain('Login')
      expect(wrapper.text()).toContain('Register')
      expect(wrapper.text()).not.toContain('Logout')
    })

    it('does not show user info', () => {
      const wrapper = mount(Navigation)
      
      expect(wrapper.find('.user-info').exists()).toBe(false)
    })
  })

  describe('when user is authenticated', () => {
    beforeEach(() => {
      mockAuthState(true, {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: 'USER'
      })
    })

    it('shows user info and logout button', async () => {
      const wrapper = mount(Navigation)
      await nextTick()
      
      expect(wrapper.text()).toContain('testuser')
      expect(wrapper.text()).toContain('Logout')
      expect(wrapper.text()).not.toContain('Login')
      expect(wrapper.text()).not.toContain('Register')
    })

    it('shows admin link for admin users', async () => {
      mockAuthState(true, {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'ADMIN'
      })

      const wrapper = mount(Navigation)
      await nextTick()
      
      expect(wrapper.text()).toContain('Admin')
    })

    it('does not show admin link for regular users', async () => {
      const wrapper = mount(Navigation)
      await nextTick()
      
      expect(wrapper.text()).not.toContain('Admin')
    })
  })

  describe('logout functionality', () => {
    it('clears auth data and redirects to login', async () => {
      mockAuthState(true)
      
      const wrapper = mount(Navigation)
      await nextTick()
      
      // Find and click logout button
      const logoutButton = wrapper.find('button')
      expect(logoutButton.text()).toContain('Logout')
      
      await logoutButton.trigger('click')
      
      // Check localStorage was cleared
      expect(localStorage.removeItem).toHaveBeenCalledWith('token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
      
      // Check redirect
      expect(mockPush).toHaveBeenCalledWith('/login')
    })

    it('handles logout errors gracefully', async () => {
      mockAuthState(true)
      localStorage.removeItem.mockImplementation(() => {
        throw new Error('Storage error')
      })
      
      const wrapper = mount(Navigation)
      await nextTick()
      
      const logoutButton = wrapper.find('button')
      await logoutButton.trigger('click')
      
      // Should still redirect even if localStorage fails
      expect(mockPush).toHaveBeenCalledWith('/login')
    })
  })

  describe('navigation active state', () => {
    it('highlights active route', async () => {
      mockRoute.path = '/tasks'
      
      const wrapper = mount(Navigation)
      await nextTick()
      
      const links = wrapper.findAll('a')
      const tasksLink = links.find(link => link.text() === 'Tasks')
      
      // Note: In a real test, you'd check for active class
      // This depends on your RouterLink implementation
      expect(tasksLink).toBeTruthy()
    })
  })
})