# Frontend Unit Testing Guide for DevBoard

## 📚 Introduction to Frontend Testing

Frontend testing ensures your Vue.js components work correctly, handle user interactions properly, and maintain expected behavior as your application evolves.

### Types of Frontend Tests

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test how components work together
3. **E2E Tests**: Test complete user workflows (not covered in this guide)

## 🛠️ Testing Stack

We'll use the following tools:

- **Vitest**: Fast unit test framework designed for Vite
- **Vue Test Utils**: Official testing utilities for Vue components
- **@testing-library/vue**: User-centric testing utilities
- **happy-dom**: Lightweight DOM implementation for tests
- **MSW**: Mock Service Worker for API mocking

## 📦 Step 1: Install Testing Dependencies

First, let's install all necessary testing packages:

```bash
cd devboard-frontend
npm install -D vitest @vue/test-utils @testing-library/vue @testing-library/jest-dom happy-dom msw
```

### Package Explanations:

- `vitest`: Test runner that reuses Vite's config and transformations
- `@vue/test-utils`: Provides methods to mount and interact with Vue components
- `@testing-library/vue`: Provides utilities for testing components from user's perspective
- `@testing-library/jest-dom`: Custom matchers for DOM assertions
- `happy-dom`: Fast DOM implementation for Node.js
- `msw`: Intercepts HTTP requests for testing

## ⚙️ Step 2: Configure Vitest

Create `vitest.config.js` in the frontend root:

```javascript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

## 🔧 Step 3: Create Test Setup File

Create `src/test/setup.js`:

```javascript
import '@testing-library/jest-dom'
import { config } from '@vue/test-utils'
import { vi } from 'vitest'

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

// Reset mocks before each test
beforeEach(() => {
  vi.clearAllMocks()
  localStorageMock.getItem.mockReturnValue(null)
})
```

## 📝 Step 4: Update package.json Scripts

Add test scripts to `package.json`:

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

### Script Explanations:
- `npm test`: Run tests in watch mode
- `npm run test:ui`: Open Vitest UI for visual test exploration
- `npm run test:coverage`: Generate coverage report
- `npm run test:run`: Run tests once (for CI/CD)

## 🧪 Step 5: Writing Your First Test

Let's start with a simple component test. Create `src/components/__tests__/Counter.test.js`:

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Counter from '../Counter.vue'

describe('Counter.vue', () => {
  it('renders initial count', () => {
    const wrapper = mount(Counter)
    expect(wrapper.text()).toContain('count is 0')
  })

  it('increments count when button is clicked', async () => {
    const wrapper = mount(Counter)
    const button = wrapper.find('button')
    
    await button.trigger('click')
    expect(wrapper.text()).toContain('count is 1')
    
    await button.trigger('click')
    expect(wrapper.text()).toContain('count is 2')
  })
})
```

## 🎯 Testing Patterns and Best Practices

### 1. Component Testing Pattern

```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { screen } from '@testing-library/vue'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('should render correctly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        title: 'Test Title'
      }
    })
    
    // Vue Test Utils approach
    expect(wrapper.find('h1').text()).toBe('Test Title')
    
    // Testing Library approach (more user-centric)
    expect(screen.getByRole('heading')).toHaveTextContent('Test Title')
  })
})
```

### 2. Testing User Interactions

```javascript
it('handles user input', async () => {
  const wrapper = mount(MyForm)
  
  // Find input and type
  const input = wrapper.find('input[type="text"]')
  await input.setValue('New Task')
  
  // Submit form
  await wrapper.find('form').trigger('submit.prevent')
  
  // Assert result
  expect(wrapper.emitted('task-created')).toBeTruthy()
  expect(wrapper.emitted('task-created')[0]).toEqual(['New Task'])
})
```

### 3. Testing Async Operations

```javascript
it('loads data on mount', async () => {
  const mockData = [{ id: 1, title: 'Task 1' }]
  
  // Mock API call
  vi.mock('@/services/taskService', () => ({
    getAllTasks: vi.fn().mockResolvedValue(mockData)
  }))
  
  const wrapper = mount(TaskList)
  
  // Wait for async operations
  await wrapper.vm.$nextTick()
  
  // Assert
  expect(wrapper.findAll('.task-item')).toHaveLength(1)
})
```

### 4. Testing Router Navigation

```javascript
import { useRouter } from 'vue-router'

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

it('navigates to detail page', async () => {
  const push = vi.fn()
  useRouter.mockReturnValue({ push })
  
  const wrapper = mount(TaskItem, {
    props: { taskId: 1 }
  })
  
  await wrapper.find('.view-details').trigger('click')
  
  expect(push).toHaveBeenCalledWith('/tasks/1')
})
```

### 5. Testing Vuex/Pinia Store

```javascript
it('commits to store', async () => {
  const mockStore = {
    dispatch: vi.fn()
  }
  
  const wrapper = mount(MyComponent, {
    global: {
      mocks: {
        $store: mockStore
      }
    }
  })
  
  await wrapper.find('button').trigger('click')
  
  expect(mockStore.dispatch).toHaveBeenCalledWith('updateTask', expect.any(Object))
})
```

## 🎨 Testing Components with API Calls

Create `src/test/mocks/handlers.js` for MSW:

```javascript
import { rest } from 'msw'

export const handlers = [
  rest.get('/api/tasks', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, title: 'Test Task 1', status: 'TODO' },
        { id: 2, title: 'Test Task 2', status: 'DONE' }
      ])
    )
  }),
  
  rest.post('/api/tasks', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({ id: 3, ...req.body })
    )
  })
]
```

Create `src/test/mocks/server.js`:

```javascript
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

Update `src/test/setup.js` to use MSW:

```javascript
import { server } from './mocks/server'

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

// Reset handlers after each test
afterEach(() => server.resetHandlers())

// Clean up after all tests
afterAll(() => server.close())
```

## 📊 Test Coverage

To set up coverage reporting:

1. Install coverage tool:
```bash
npm install -D @vitest/coverage-v8
```

2. Add coverage configuration to `vitest.config.js`:
```javascript
export default defineConfig({
  test: {
    coverage: {
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
      ],
    },
  },
})
```

3. Run coverage:
```bash
npm run test:coverage
```

## 🚀 Running Tests

### During Development
```bash
npm test              # Watch mode
npm run test:ui       # Visual UI
```

### For CI/CD
```bash
npm run test:run      # Single run
npm run test:coverage # With coverage
```

## 📁 Recommended Test Structure

```
src/
├── components/
│   ├── TaskForm.vue
│   └── __tests__/
│       └── TaskForm.test.js
├── views/
│   ├── TaskBoard.vue
│   └── __tests__/
│       └── TaskBoard.test.js
├── services/
│   ├── taskService.js
│   └── __tests__/
│       └── taskService.test.js
└── test/
    ├── setup.js
    ├── utils.js
    └── mocks/
        ├── handlers.js
        └── server.js
```

## ✅ Testing Checklist

When testing a component, ensure you cover:

- [ ] Initial render state
- [ ] Props handling
- [ ] User interactions (clicks, input)
- [ ] Emitted events
- [ ] Computed properties
- [ ] Watchers
- [ ] Lifecycle hooks
- [ ] Error states
- [ ] Loading states
- [ ] Edge cases

## 🔍 Debugging Tests

### Useful debugging techniques:

```javascript
// Log component HTML
console.log(wrapper.html())

// Log component data
console.log(wrapper.vm.$data)

// Debug specific element
console.log(wrapper.find('.my-class').exists())

// Use debug from Testing Library
import { render } from '@testing-library/vue'
const { debug } = render(MyComponent)
debug() // Prints formatted DOM
```

## 📚 Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils Guide](https://test-utils.vuejs.org/)
- [Testing Library Vue](https://testing-library.com/docs/vue-testing-library/intro/)
- [MSW Documentation](https://mswjs.io/)

## 🎯 Next Steps

1. Start with simple component tests
2. Add tests for critical user flows
3. Test error scenarios
4. Add integration tests for complex features
5. Aim for 80% coverage on critical paths