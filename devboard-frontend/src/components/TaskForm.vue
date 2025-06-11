<template>
  <div class="task-form-overlay" @click="handleOverlayClick">
    <div class="task-form-modal" @click.stop>
      <div class="form-header">
        <h2>{{ isEditing ? '✏️ Edit Task' : '➕ Create New Task' }}</h2>
        <button class="close-btn" @click="$emit('close')" title="Close">✖️</button>
      </div>

      <form @submit.prevent="handleSubmit" class="task-form">
        <!-- Title Field -->
        <div class="form-group">
          <label for="title" class="form-label">
            Title <span class="required">*</span>
          </label>
          <input
            id="title"
            v-model="formData.title"
            type="text"
            class="form-input"
            :class="{ 'error': errors.title }"
            placeholder="Enter task title..."
            maxlength="255"
            required
          />
          <div v-if="errors.title" class="error-message">{{ errors.title }}</div>
          <div class="char-count">{{ formData.title.length }}/255</div>
        </div>

        <!-- Description Field -->
        <div class="form-group">
          <label for="description" class="form-label">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            class="form-textarea"
            :class="{ 'error': errors.description }"
            placeholder="Describe the task details..."
            rows="4"
            maxlength="1000"
          ></textarea>
          <div v-if="errors.description" class="error-message">{{ errors.description }}</div>
          <div class="char-count">{{ formData.description.length }}/1000</div>
        </div>

        <!-- Status and Priority Row -->
        <div class="form-row">
          <div class="form-group">
            <label for="status" class="form-label">Status</label>
            <select id="status" v-model="formData.status" class="form-select">
              <option value="TODO">📝 To Do</option>
              <option value="IN_PROGRESS">🔄 In Progress</option>
              <option value="DONE">✅ Done</option>
            </select>
          </div>

          <div class="form-group">
            <label for="priority" class="form-label">Priority</label>
            <select id="priority" v-model="formData.priority" class="form-select">
              <option value="LOW">🟢 Low</option>
              <option value="MEDIUM">🟡 Medium</option>
              <option value="HIGH">🔴 High</option>
            </select>
          </div>
        </div>

        <!-- Assignee Field -->
        <div class="form-group">
          <label for="assignee" class="form-label">Assignee</label>
          <select id="assignee" v-model="formData.assigneeId" class="form-select">
            <option value="">Select assignee (optional)</option>
            <option 
              v-for="user in users" 
              :key="user.id" 
              :value="user.id"
            >
              {{ user.nickname || user.username }} ({{ user.username }})
            </option>
          </select>
          <div class="form-help">Leave empty if no specific assignee</div>
        </div>

        <!-- Error Display -->
        <div v-if="submitError" class="form-error">
          <div class="error-icon">⚠️</div>
          <div>
            <strong>Failed to {{ isEditing ? 'update' : 'create' }} task</strong>
            <p>{{ submitError }}</p>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button
            type="button"
            class="btn btn-secondary"
            @click="$emit('close')"
            :disabled="loading"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading">
              ⏳ {{ isEditing ? 'Updating...' : 'Creating...' }}
            </span>
            <span v-else>
              {{ isEditing ? '✅ Update Task' : '➕ Create Task' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { userService } from '../services/userService'

export default {
  name: 'TaskForm',
  props: {
    task: {
      type: Object,
      default: null
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'submit'],
  setup(props, { emit }) {
    const loading = ref(false)
    const submitError = ref('')
    const users = ref([])

    // Form data
    const formData = reactive({
      title: '',
      description: '',
      status: 'TODO',
      priority: 'MEDIUM',
      assigneeId: ''
    })

    // Form validation errors
    const errors = reactive({
      title: '',
      description: ''
    })

    // Computed properties
    const isEditing = computed(() => !!props.task)

    const isFormValid = computed(() => {
      return formData.title.trim().length > 0 && 
             formData.title.length <= 255 &&
             formData.description.length <= 1000 &&
             !loading.value
    })

    // Methods
    const resetForm = () => {
      formData.title = ''
      formData.description = ''
      formData.status = 'TODO'
      formData.priority = 'MEDIUM'
      formData.assigneeId = ''
      
      errors.title = ''
      errors.description = ''
      submitError.value = ''
    }

    const loadFormData = () => {
      if (props.task) {
        formData.title = props.task.title || ''
        formData.description = props.task.description || ''
        formData.status = props.task.status || 'TODO'
        formData.priority = props.task.priority || 'MEDIUM'
        formData.assigneeId = props.task.assignee?.id || ''
      } else {
        resetForm()
      }
    }

    const validateForm = () => {
      errors.title = ''
      errors.description = ''

      if (!formData.title.trim()) {
        errors.title = 'Title is required'
        return false
      }

      if (formData.title.length > 255) {
        errors.title = 'Title must be at most 255 characters'
        return false
      }

      if (formData.description.length > 1000) {
        errors.description = 'Description must be at most 1000 characters'
        return false
      }

      return true
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      submitError.value = ''

      try {
        const taskData = {
          title: formData.title.trim(),
          description: formData.description.trim(),
          status: formData.status,
          priority: formData.priority,
          assigneeId: formData.assigneeId || null
        }

        emit('submit', taskData)
      } catch (error) {
        submitError.value = error.message || 'An unexpected error occurred'
        loading.value = false
      }
    }

    const handleOverlayClick = () => {
      emit('close')
    }

    const loadUsers = async () => {
      try {
        const allUsers = await userService.getAllUsers()
        users.value = allUsers
      } catch (error) {
        console.error('Failed to load users:', error)
        // Fallback: at least include current user info from localStorage
        const userData = localStorage.getItem('user')
        if (userData) {
          try {
            const user = JSON.parse(userData)
            users.value = [user]
          } catch (e) {
            console.error('Failed to parse user data from localStorage')
          }
        }
      }
    }

    // Watchers
    watch(() => props.visible, (newVisible) => {
      if (newVisible) {
        loadFormData()
        loadUsers()
      }
    })

    watch(() => props.task, () => {
      if (props.visible) {
        loadFormData()
      }
    })

    // Lifecycle
    onMounted(() => {
      if (props.visible) {
        loadFormData()
        loadUsers()
      }
    })

    return {
      formData,
      errors,
      loading,
      submitError,
      users,
      isEditing,
      isFormValid,
      handleSubmit,
      handleOverlayClick
    }
  }
}
</script>

<style scoped>
.task-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.task-form-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
}

.form-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.task-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.required {
  color: #dc3545;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-input.error,
.form-textarea.error {
  border-color: #dc3545;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.char-count {
  font-size: 0.875rem;
  color: #666;
  text-align: right;
  margin-top: 0.25rem;
}

.form-help {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-error {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.error-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.form-error strong {
  color: #dc2626;
  margin-bottom: 0.25rem;
  display: block;
}

.form-error p {
  margin: 0;
  color: #b91c1c;
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-secondary {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
}

.btn-secondary:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

@media (max-width: 768px) {
  .task-form-overlay {
    padding: 0.5rem;
  }

  .task-form-modal {
    max-height: 95vh;
  }

  .form-header {
    padding: 1rem;
  }

  .task-form {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}
</style>