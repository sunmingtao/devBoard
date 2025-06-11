<template>
  <div class="task-board">
    <div class="container">
      <header class="board-header">
        <h1>Task Board</h1>
        <p>Manage your development tasks efficiently</p>
      </header>

      <!-- Error Display -->
      <div v-if="error" class="error-banner">
        ⚠️ {{ error }}
      </div>

      <div class="board-columns">
        <div class="column">
          <div class="column-header todo">
            <h2>📝 To Do</h2>
            <span class="task-count">{{ todoTasks.length }}</span>
          </div>
          <div class="task-list">
            <div
              v-for="task in todoTasks"
              :key="task.id"
              class="task-card"
              :class="task.priority.toLowerCase()"
              @click="editTask(task)"
            >
              <div class="task-header">
                <h3>{{ task.title }}</h3>
                <div class="task-actions">
                  <button @click.stop="editTask(task)" class="action-btn edit" title="Edit">✏️</button>
                  <button 
                    v-if="canDeleteTask(task)" 
                    @click.stop="deleteTask(task)" 
                    class="action-btn delete" 
                    title="Delete"
                  >🗑️</button>
                </div>
              </div>
              <p v-if="task.description">{{ task.description }}</p>
              <div class="task-meta">
                <span class="priority">{{ getPriorityIcon(task.priority) }} {{ task.priority }}</span>
                <span class="status">{{ task.status }}</span>
              </div>
              <div class="task-users">
                <div class="user-info">
                  <span class="user-label">Creator:</span>
                  <span class="user-name">{{ task.creator?.username || 'Unknown' }}</span>
                </div>
                <div v-if="task.assignee" class="user-info">
                  <span class="user-label">Assignee:</span>
                  <span class="user-name">{{ task.assignee.username }}</span>
                </div>
              </div>
            </div>
            <div v-if="todoTasks.length === 0" class="empty-state">
              No tasks in To Do
            </div>
          </div>
        </div>

        <div class="column">
          <div class="column-header in-progress">
            <h2>🔄 In Progress</h2>
            <span class="task-count">{{ inProgressTasks.length }}</span>
          </div>
          <div class="task-list">
            <div
              v-for="task in inProgressTasks"
              :key="task.id"
              class="task-card"
              :class="task.priority.toLowerCase()"
              @click="editTask(task)"
            >
              <div class="task-header">
                <h3>{{ task.title }}</h3>
                <div class="task-actions">
                  <button @click.stop="editTask(task)" class="action-btn edit" title="Edit">✏️</button>
                  <button 
                    v-if="canDeleteTask(task)" 
                    @click.stop="deleteTask(task)" 
                    class="action-btn delete" 
                    title="Delete"
                  >🗑️</button>
                </div>
              </div>
              <p v-if="task.description">{{ task.description }}</p>
              <div class="task-meta">
                <span class="priority">{{ getPriorityIcon(task.priority) }} {{ task.priority }}</span>
                <span class="status">{{ task.status }}</span>
              </div>
              <div class="task-users">
                <div class="user-info">
                  <span class="user-label">Creator:</span>
                  <span class="user-name">{{ task.creator?.username || 'Unknown' }}</span>
                </div>
                <div v-if="task.assignee" class="user-info">
                  <span class="user-label">Assignee:</span>
                  <span class="user-name">{{ task.assignee.username }}</span>
                </div>
              </div>
            </div>
            <div v-if="inProgressTasks.length === 0" class="empty-state">
              No tasks in progress
            </div>
          </div>
        </div>

        <div class="column">
          <div class="column-header done">
            <h2>✅ Done</h2>
            <span class="task-count">{{ doneTasks.length }}</span>
          </div>
          <div class="task-list">
            <div
              v-for="task in doneTasks"
              :key="task.id"
              class="task-card"
              :class="task.priority.toLowerCase()"
              @click="editTask(task)"
            >
              <div class="task-header">
                <h3>{{ task.title }}</h3>
                <div class="task-actions">
                  <button @click.stop="editTask(task)" class="action-btn edit" title="Edit">✏️</button>
                  <button 
                    v-if="canDeleteTask(task)" 
                    @click.stop="deleteTask(task)" 
                    class="action-btn delete" 
                    title="Delete"
                  >🗑️</button>
                </div>
              </div>
              <p v-if="task.description">{{ task.description }}</p>
              <div class="task-meta">
                <span class="priority">{{ getPriorityIcon(task.priority) }} {{ task.priority }}</span>
                <span class="status">{{ task.status }}</span>
              </div>
              <div class="task-users">
                <div class="user-info">
                  <span class="user-label">Creator:</span>
                  <span class="user-name">{{ task.creator?.username || 'Unknown' }}</span>
                </div>
                <div v-if="task.assignee" class="user-info">
                  <span class="user-label">Assignee:</span>
                  <span class="user-name">{{ task.assignee.username }}</span>
                </div>
              </div>
            </div>
            <div v-if="doneTasks.length === 0" class="empty-state">
              No completed tasks
            </div>
          </div>
        </div>
      </div>

      <div class="board-actions">
        <router-link to="/" class="btn btn-secondary">
          ← Back to Home
        </router-link>
        <button class="btn btn-success" @click="createTask">
          ➕ New Task
        </button>
        <button class="btn btn-primary" @click="loadTasks" :disabled="loading">
          {{ loading ? '⏳ Loading...' : '🔄 Refresh Tasks' }}
        </button>
      </div>

      <!-- Task Form Modal -->
      <TaskForm
        v-if="showTaskForm"
        :task="selectedTask"
        :visible="showTaskForm"
        @close="closeTaskForm"
        @submit="handleTaskSubmit"
      />
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted } from 'vue'
  import taskService from '../services/taskService'
  import TaskForm from '../components/TaskForm.vue'
  import { authService } from '../services/authService'

  export default {
    name: 'TaskBoard',
    components: {
      TaskForm
    },
    setup() {
      const tasks = ref([])
      const loading = ref(false)
      const error = ref('')
      const showTaskForm = ref(false)
      const selectedTask = ref(null)
      const currentUser = ref(null)

      const todoTasks = computed(() =>
        tasks.value.filter(task => task.status === 'TODO')
      )

      const inProgressTasks = computed(() =>
        tasks.value.filter(task => task.status === 'IN_PROGRESS')
      )

      const doneTasks = computed(() =>
        tasks.value.filter(task => task.status === 'DONE')
      )

      const loadTasks = async () => {
        loading.value = true
        error.value = ''

        try {
          console.log('🔄 Loading tasks from API...')
          const fetchedTasks = await taskService.getAllTasks()
          tasks.value = fetchedTasks
          console.log('✅ Tasks loaded successfully:', fetchedTasks.length, 'tasks')
        } catch (err) {
          error.value = `Failed to load tasks: ${err.message}`
          console.error('❌ Failed to load tasks:', err)
          
          // Fallback to sample data if API fails
          console.log('📝 Using fallback sample data')
          tasks.value = [
            {
              id: 999,
              title: 'API Connection Failed',
              description: 'Using sample data. Check if backend is running on localhost:8080',
              status: 'TODO',
              priority: 'HIGH',
              creator: { username: 'system' },
              assignee: null
            }
          ]
        } finally {
          loading.value = false
        }
      }

      const createTask = () => {
        selectedTask.value = null
        showTaskForm.value = true
      }

      const editTask = (task) => {
        selectedTask.value = task
        showTaskForm.value = true
      }

      const closeTaskForm = () => {
        showTaskForm.value = false
        selectedTask.value = null
      }

      const handleTaskSubmit = async (taskData) => {
        try {
          if (selectedTask.value) {
            // Update existing task
            console.log('🔄 Updating task:', selectedTask.value.id)
            const updatedTask = await taskService.updateTask(selectedTask.value.id, taskData)
            
            // Update task in local array
            const index = tasks.value.findIndex(t => t.id === selectedTask.value.id)
            if (index !== -1) {
              tasks.value[index] = updatedTask
            }
            console.log('✅ Task updated successfully')
          } else {
            // Create new task
            console.log('🔄 Creating new task')
            const newTask = await taskService.createTask(taskData)
            tasks.value.push(newTask)
            console.log('✅ Task created successfully')
          }
          
          closeTaskForm()
        } catch (err) {
          console.error('❌ Failed to save task:', err)
          // Let TaskForm handle the error display
          throw err
        }
      }

      const deleteTask = async (task) => {
        if (!confirm(`Are you sure you want to delete "${task.title}"?`)) {
          return
        }

        try {
          console.log('🔄 Deleting task:', task.id)
          await taskService.deleteTask(task.id)
          
          // Remove task from local array
          tasks.value = tasks.value.filter(t => t.id !== task.id)
          console.log('✅ Task deleted successfully')
        } catch (err) {
          console.error('❌ Failed to delete task:', err)
          error.value = `Failed to delete task: ${err.message}`
        }
      }

      const getPriorityIcon = (priority) => {
        const icons = {
          HIGH: '🔴',
          MEDIUM: '🟡',
          LOW: '🟢'
        }
        return icons[priority] || '⚪'
      }

      const canDeleteTask = (task) => {
        if (!currentUser.value) return false
        
        // Creator can always delete
        const isCreator = task.creator?.id === currentUser.value.id
        
        // Admin can always delete
        const isAdmin = currentUser.value.role === 'ADMIN'
        
        return isCreator || isAdmin
      }

      const loadCurrentUser = async () => {
        try {
          currentUser.value = authService.getUser()
        } catch (error) {
          console.error('Failed to load current user:', error)
        }
      }

      onMounted(() => {
        loadCurrentUser()
        loadTasks()
      })

      return {
        tasks,
        todoTasks,
        inProgressTasks,
        doneTasks,
        loading,
        error,
        showTaskForm,
        selectedTask,
        loadTasks,
        createTask,
        editTask,
        closeTaskForm,
        handleTaskSubmit,
        deleteTask,
        getPriorityIcon,
        canDeleteTask
      }
    },
  }
</script>

<style scoped>
  .task-board {
    min-height: 100vh;
    background-color: #f8f9fa;
    padding: 2rem;
  }

  .container {
    max-width: 1400px;
    margin: 0 auto;
  }

  .board-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .board-header h1 {
    font-size: 3rem;
    color: #333;
    margin-bottom: 0.5rem;
  }

  .board-header p {
    font-size: 1.25rem;
    color: #666;
  }

  .error-banner {
    background: #fee2e2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 2rem;
    border-left: 4px solid #dc2626;
    font-weight: 500;
  }

  .board-columns {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .column {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .column-header {
    padding: 1rem;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .column-header.todo {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .column-header.in-progress {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }

  .column-header.done {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }

  .column-header h2 {
    margin: 0;
    font-size: 1.5rem;
  }

  .task-count {
    background: rgba(255, 255, 255, 0.3);
    padding: 0.25rem 0.5rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: bold;
  }

  .task-list {
    padding: 1rem;
    min-height: 400px;
  }

  .task-card {
    background: #f8f9fa;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #ddd;
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .task-actions {
    display: flex;
    gap: 0.25rem;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .task-card:hover .task-actions {
    opacity: 1;
  }

  .action-btn {
    background: none;
    border: none;
    padding: 0.25rem;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s ease;
  }

  .action-btn.edit:hover {
    background: rgba(102, 126, 234, 0.1);
  }

  .action-btn.delete:hover {
    background: rgba(220, 53, 69, 0.1);
  }

  .task-card.high {
    border-left-color: #f56565;
  }

  .task-card.medium {
    border-left-color: #ed8936;
  }

  .task-card.low {
    border-left-color: #48bb78;
  }

  .task-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    color: #333;
  }

  .task-card p {
    margin: 0 0 1rem 0;
    color: #666;
    line-height: 1.4;
  }

  .task-meta {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .priority,
  .status {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }

  .priority {
    background: #e2e8f0;
    color: #4a5568;
  }

  .status {
    background: #667eea;
    color: white;
  }

  .task-users {
    border-top: 1px solid #e2e8f0;
    padding-top: 0.5rem;
    font-size: 0.875rem;
  }

  .user-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
  }

  .user-info:last-child {
    margin-bottom: 0;
  }

  .user-label {
    color: #666;
    font-weight: 500;
  }

  .user-name {
    color: #333;
    font-weight: 600;
  }

  .empty-state {
    text-align: center;
    color: #999;
    padding: 2rem;
    font-style: italic;
  }

  .board-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    display: inline-block;
    border: none;
    cursor: pointer;
  }

  .btn-primary {
    background-color: #667eea;
    color: white;
    border: 2px solid #667eea;
  }

  .btn-primary:hover {
    background-color: #5a67d8;
    border-color: #5a67d8;
  }

  .btn-secondary {
    background-color: transparent;
    color: #667eea;
    border: 2px solid #667eea;
  }

  .btn-secondary:hover {
    background-color: #667eea;
    color: white;
  }

  .btn-success {
    background-color: #48bb78;
    color: white;
    border: 2px solid #48bb78;
  }

  .btn-success:hover {
    background-color: #38a169;
    border-color: #38a169;
  }
</style>
