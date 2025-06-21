import '@testing-library/jest-dom'
import { config } from '@vue/test-utils'
import { vi } from 'vitest'
import { server } from './mocks/server'

// Mock vue-router globally to prevent import errors
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    createRouter: vi.fn(() => ({
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      beforeEach: vi.fn(),
      afterEach: vi.fn(),
      onError: vi.fn(),
      isReady: vi.fn(() => Promise.resolve()),
      install: vi.fn(),
      currentRoute: {
        value: {
          path: '/',
          name: 'home',
          params: {},
          query: {}
        }
      }
    })),
    RouterLink: {
      name: 'RouterLink',
      template: '<a><slot /></a>'
    },
    RouterView: {
      name: 'RouterView',
      template: '<div></div>'
    },
    useRouter: vi.fn(() => ({
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn()
    })),
    useRoute: vi.fn(() => ({
      path: '/',
      name: 'home',
      params: {},
      query: {}
    }))
  }
})

// Configure Vue Test Utils
config.global.mocks = {
  $t: (msg) => msg, // Mock i18n if you use it
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock window.alert
global.alert = vi.fn()

// Start MSW server
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

// Reset mocks and handlers after each test
afterEach(() => {
  vi.clearAllMocks()
  localStorageMock.getItem.mockReturnValue(null)
  server.resetHandlers()
})

// Clean up after all tests
afterAll(() => server.close())