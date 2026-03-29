import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import TaskForm from '../TaskForm.vue'

describe('TaskForm.vue', () => {
  let wrapper

  const defaultTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'TODO',
    priority: 'MEDIUM',
    assignee: null
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Set up authentication for API calls
    localStorage.setItem('token', 'mock-jwt-token')
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'USER'
    }))
  })

  afterEach(() => {
    localStorage.clear()
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Create mode', () => {
    beforeEach(() => {
      wrapper = mount(TaskForm, {
        props: {
          mode: 'create',
          visible: true
        }
      })
    })

    it('renders form with empty fields', () => {
      expect(wrapper.find('h2').text()).toBe('➕ Create New Task')
      expect(wrapper.find('#title').element.value).toBe('')
      expect(wrapper.find('#description').element.value).toBe('')
      expect(wrapper.find('#status').element.value).toBe('TODO')
      expect(wrapper.find('#priority').element.value).toBe('MEDIUM')
    })

    it('validates required fields', async () => {
      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // Title is required, so form shouldn't emit
      expect(wrapper.emitted('submit')).toBeFalsy()
    })

    it('emits save event with form data', async () => {
      // Fill in form
      await wrapper.find('#title').setValue('New Task')
      await wrapper.find('#description').setValue('Task description')
      await wrapper.find('#status').setValue('IN_PROGRESS')
      await wrapper.find('#priority').setValue('HIGH')

      // Submit form
      await wrapper.find('form').trigger('submit.prevent')

      // Check emitted event
      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')[0][0]).toEqual({
        title: 'New Task',
        description: 'Task description',
        status: 'IN_PROGRESS',
        priority: 'HIGH',
        assigneeId: null
      })
    })

    it('emits cancel event when cancel button is clicked', async () => {
      const cancelButton = wrapper.find('button[type="button"]')
      await cancelButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('Edit mode', () => {
    beforeEach(() => {
      wrapper = mount(TaskForm, {
        props: {
          mode: 'edit',
          task: defaultTask,
          visible: true
        }
      })
    })

    it('renders form with task data', () => {
      expect(wrapper.find('h2').text()).toBe('✏️ Edit Task')
      expect(wrapper.find('#title').element.value).toBe('Test Task')
      expect(wrapper.find('#description').element.value).toBe('Test Description')
      expect(wrapper.find('#status').element.value).toBe('TODO')
      expect(wrapper.find('#priority').element.value).toBe('MEDIUM')
    })

    it('emits save event with updated data', async () => {
      // Update title
      await wrapper.find('#title').setValue('Updated Task')

      // Submit form
      await wrapper.find('form').trigger('submit.prevent')

      // Check emitted event includes all fields
      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')[0][0]).toEqual({
        title: 'Updated Task',
        description: 'Test Description',
        status: 'TODO',
        priority: 'MEDIUM',
        assigneeId: null
      })
    })

    it('updates form when task prop changes', async () => {
      const newTask = {
        ...defaultTask,
        title: 'Changed Task',
        status: 'DONE'
      }

      await wrapper.setProps({ task: newTask })
      await nextTick()

      expect(wrapper.find('#title').element.value).toBe('Changed Task')
      expect(wrapper.find('#status').element.value).toBe('DONE')
    })
  })

  describe('Form validation', () => {
    beforeEach(() => {
      wrapper = mount(TaskForm, {
        props: {
          mode: 'create',
          visible: true
        }
      })
    })

    it('requires title field', async () => {
      await wrapper.find('#description').setValue('Description only')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.emitted('submit')).toBeFalsy()
    })

    it('trims whitespace from title', async () => {
      await wrapper.find('#title').setValue('  Trimmed Title  ')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.emitted('submit')[0][0].title).toBe('Trimmed Title')
    })

    it('allows empty description', async () => {
      await wrapper.find('#title').setValue('Title Only')
      await wrapper.find('#description').setValue('')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')[0][0].description).toBe('')
    })
  })

  describe('Status and Priority options', () => {
    beforeEach(() => {
      wrapper = mount(TaskForm, {
        props: {
          mode: 'create',
          visible: true
        }
      })
    })

    it('renders all status options', () => {
      const statusOptions = wrapper.find('#status').findAll('option')
      const values = statusOptions.map(opt => opt.element.value)
      
      expect(values).toEqual(['TODO', 'IN_PROGRESS', 'DONE'])
    })

    it('renders all priority options', () => {
      const priorityOptions = wrapper.find('#priority').findAll('option')
      const values = priorityOptions.map(opt => opt.element.value)
      
      expect(values).toEqual(['LOW', 'MEDIUM', 'HIGH'])
    })
  })

  describe('Loading state', () => {
    it('disables form during save', async () => {
      wrapper = mount(TaskForm, {
        props: {
          mode: 'create',
          loading: true,
          visible: true
        }
      })

      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('button[type="submit"]')
      const cancelButton = wrapper.find('button[type="button"]')
      const titleInput = wrapper.find('#title')
      
      expect(submitButton.element.disabled).toBe(true)
      expect(cancelButton.element.disabled).toBe(true)
      expect(titleInput.attributes('disabled')).toBeDefined()
    })
  })
})