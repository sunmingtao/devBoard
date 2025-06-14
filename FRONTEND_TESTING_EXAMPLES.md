# Frontend Testing Examples - DevBoard

This document shows practical examples of the frontend tests we've implemented and demonstrates key testing concepts.

## 🧪 Test Infrastructure Setup

### Files Created:
- `vitest.config.js` - Vitest configuration
- `src/test/setup.js` - Global test setup
- `src/test/mocks/handlers.js` - MSW API mocks
- `src/test/mocks/server.js` - MSW server setup  
- `src/test/utils.js` - Test utility functions

### Testing Stack:
- **Vitest**: Fast test runner optimized for Vite
- **Vue Test Utils**: Official Vue testing utilities
- **@testing-library/vue**: User-centric testing approach
- **MSW**: Mock Service Worker for API testing
- **happy-dom**: Lightweight DOM implementation

## 📋 Test Scripts

Add these to your `package.json`:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage", 
    "test:run": "vitest run"
  }
}
```

## 🎯 Component Testing Examples

### 1. Simple Component Test (HelloWorld.vue)

**File**: `src/components/__tests__/HelloWorld.test.js`

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../HelloWorld.vue'

describe('HelloWorld.vue', () => {
  it('renders props.msg when passed', () => {
    const msg = 'new message'
    const wrapper = mount(HelloWorld, { props: { msg } })
    expect(wrapper.text()).toContain(msg)
  })

  it('has correct component structure', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'test' } })
    
    expect(wrapper.find('h1').exists()).toBe(true)
    expect(wrapper.find('.card').exists()).toBe(true)
  })
})
```

**Key Concepts:**
- `mount()` renders component for testing
- `props` can be passed to test different states
- `wrapper.text()` gets all text content
- `wrapper.find()` locates specific elements

### 2. Complex Component Test (Counter.vue)

**File**: `src/components/__tests__/Counter.test.js`

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Counter from '../Counter.vue'

describe('Counter.vue', () => {
  it('increments ref counter when + button is clicked', async () => {
    const wrapper = mount(Counter)
    
    // Find specific button using class and text
    const refPlusButton = wrapper.findAll('button').find(btn => 
      btn.text() === '+' && btn.classes().includes('btn-primary')
    )
    
    // Trigger click event
    await refPlusButton.trigger('click')
    
    // Check state changes
    const countSpan = wrapper.findAll('.count')[0]
    expect(countSpan.text()).toBe('1')
    expect(wrapper.text()).toContain('Last action: Incremented ref counter')
  })

  it('resets all counters when reset button is clicked', async () => {
    const wrapper = mount(Counter)
    
    // First change some state
    const refPlusButton = wrapper.findAll('button')[1]
    await refPlusButton.trigger('click')
    
    // Then reset
    const resetButton = wrapper.find('button.btn-warning')
    await resetButton.trigger('click')
    
    // Verify reset worked
    expect(wrapper.findAll('.count')[0].text()).toBe('0')
    expect(wrapper.text()).toContain('Last action: Reset all counters')
  })
})
```

**Key Concepts:**
- `async/await` for handling user interactions
- `trigger()` simulates user events (click, input, etc.)
- `findAll()` gets multiple elements, then filter/find specific ones
- Test both user actions and resulting state changes

### 3. Form Component Test (TaskForm.vue)

**File**: `src/components/__tests__/TaskForm.test.js`

```javascript
describe('TaskForm.vue', () => {
  it('emits save event with form data', async () => {
    const wrapper = mount(TaskForm, {
      props: { mode: 'create' }
    })

    // Fill form inputs
    await wrapper.find('#title').setValue('New Task')
    await wrapper.find('#description').setValue('Task description')
    await wrapper.find('#status').setValue('IN_PROGRESS')
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent')

    // Check emitted events
    expect(wrapper.emitted('save')).toBeTruthy()
    expect(wrapper.emitted('save')[0][0]).toEqual({
      title: 'New Task',
      description: 'Task description', 
      status: 'IN_PROGRESS',
      priority: 'MEDIUM',
      assigneeId: null
    })
  })

  it('validates required fields', async () => {
    const wrapper = mount(TaskForm, {
      props: { mode: 'create' }
    })

    // Submit empty form
    await wrapper.find('form').trigger('submit.prevent')

    // Should not emit save event
    expect(wrapper.emitted('save')).toBeFalsy()
  })
})
```

**Key Concepts:**
- `setValue()` simulates user typing in inputs
- `wrapper.emitted()` checks what events component emitted
- Test both success and validation failure cases
- Use `submit.prevent` to simulate form submission

## 🔌 Service Testing Examples

### 4. Service/API Test (authService.js)

**File**: `src/services/__tests__/authService.test.js`

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import authService from '../authService'
import api from '../api'

// Mock the API module
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

  it('successfully logs in and stores user data', async () => {
    const mockResponse = {
      data: {
        token: 'test-jwt-token',
        username: 'testuser',
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
    
    // Check return value
    expect(result.username).toBe('testuser')
  })

  it('throws error on login failure', async () => {
    api.post.mockRejectedValueOnce(new Error('Invalid credentials'))

    await expect(authService.login('testuser', 'wrongpass'))
      .rejects.toThrow('Invalid credentials')
  })
})
```

**Key Concepts:**
- `vi.mock()` replaces modules with mocks
- `mockResolvedValueOnce()` simulates successful API calls
- `mockRejectedValueOnce()` simulates API errors
- `beforeEach()` resets state between tests
- Test both success and error scenarios

## 🛣️ Router Testing Examples

### 5. View Component Test (Login.vue)

**File**: `src/views/__tests__/Login.test.js`

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Login from '../Login.vue'
import authService from '@/services/authService'

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    login: vi.fn(),
    isAuthenticated: vi.fn().mockReturnValue(false)
  }
}))

// Mock router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: {} })
}))

describe('Login.vue', () => {
  it('successfully logs in user', async () => {
    const wrapper = mount(Login)
    
    authService.login.mockResolvedValueOnce({ username: 'testuser' })

    // Fill form
    await wrapper.find('#username').setValue('testuser')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('form').trigger('submit.prevent')
    
    // Wait for async operations
    await flushPromises()

    expect(authService.login).toHaveBeenCalledWith('testuser', 'password123')
    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('shows error on login failure', async () => {
    const wrapper = mount(Login)
    
    authService.login.mockRejectedValueOnce(new Error('Invalid credentials'))

    await wrapper.find('#username').setValue('testuser')
    await wrapper.find('#password').setValue('wrong')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.find('.error-message').text()).toContain('Invalid credentials')
  })
})
```

**Key Concepts:**
- `flushPromises()` waits for all pending promises
- Mock router functions like `push()` for navigation testing
- Test both successful and failed user flows
- Check for error message display

## 🚀 Running Tests

### Development (Watch Mode)
```bash
npm test
```
Runs tests and watches for changes. Great for TDD.

### Single Run (CI/CD)
```bash
npm run test:run
```
Runs tests once and exits. Perfect for CI/CD pipelines.

### With Coverage
```bash
npm run test:coverage
```
Generates coverage report showing which code is tested.

### Visual UI
```bash
npm run test:ui
```
Opens browser-based test UI for visual test exploration.

## 📊 Test Output Examples

### Successful Test Run
```
✓ HelloWorld.vue > renders props.msg when passed (7ms)
✓ HelloWorld.vue > has correct component structure (2ms)
✓ Counter.vue > renders initial state correctly (5ms)
✓ Counter.vue > increments ref counter when + button is clicked (3ms)

Test Files  2 passed (2)
Tests  4 passed (4)
Duration  1.2s
```

### Failed Test Example
```
× Counter.vue > increments ref counter when + button is clicked
AssertionError: expected 'Total clicks: 0' to contain 'Total clicks: 1'

Expected: "Total clicks: 1"
Received: "Total clicks: 0"

 ❯ Counter.test.js:37:28
```

## 🎯 Testing Best Practices Demonstrated

### 1. Test Structure (AAA Pattern)
```javascript
it('descriptive test name', async () => {
  // Arrange - Setup test data
  const wrapper = mount(Component, { props: { ... } })
  
  // Act - Perform action
  await wrapper.find('button').trigger('click')
  
  // Assert - Check results
  expect(wrapper.text()).toContain('expected result')
})
```

### 2. Mocking External Dependencies
```javascript
// Mock API calls
vi.mock('../api', () => ({ ... }))

// Mock router navigation  
const mockPush = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push: mockPush }) }))
```

### 3. Testing User Interactions
```javascript
// Form inputs
await wrapper.find('#email').setValue('test@example.com')

// Button clicks
await wrapper.find('.submit-btn').trigger('click')

// Form submission
await wrapper.find('form').trigger('submit.prevent')
```

### 4. Async Testing
```javascript
// Wait for promises
await flushPromises()

// Wait for DOM updates
await wrapper.vm.$nextTick()

// Mock async functions
api.post.mockResolvedValueOnce(mockData)
```

### 5. Testing Component Communication
```javascript
// Check emitted events
expect(wrapper.emitted('save')).toBeTruthy()
expect(wrapper.emitted('save')[0][0]).toEqual(expectedData)

// Test props
const wrapper = mount(Component, { props: { userId: 1 } })
```

## 🔍 Debugging Tests

### Common Debug Techniques:
```javascript
// Log component HTML
console.log(wrapper.html())

// Log component data
console.log(wrapper.vm.$data)

// Check if element exists
console.log(wrapper.find('.my-class').exists())

// Debug with Testing Library
import { render } from '@testing-library/vue'
const { debug } = render(Component)
debug() // Prints formatted DOM
```

## 📈 Next Steps

1. **Add More Component Tests**: Test all critical components
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Add Playwright/Cypress for full user journeys
4. **Performance Tests**: Test component rendering performance
5. **Accessibility Tests**: Use @testing-library/jest-dom for a11y testing

## 🎉 Test Coverage Goals

- **Components**: Aim for 80%+ coverage on critical user-facing components
- **Services**: Aim for 90%+ coverage on business logic
- **Utils**: Aim for 95%+ coverage on utility functions
- **Critical Paths**: 100% coverage on authentication, payment, security flows