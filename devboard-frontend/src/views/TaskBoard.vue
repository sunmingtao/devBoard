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
            >
              <h3>{{ task.title }}</h3>
              <p>{{ task.description }}</p>
              <div class="task-meta">
                <span class="priority">{{ task.priority }}</span>
                <span class="status">{{ task.status }}</span>
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
            >
              <h3>{{ task.title }}</h3>
              <p>{{ task.description }}</p>
              <div class="task-meta">
                <span class="priority">{{ task.priority }}</span>
                <span class="status">{{ task.status }}</span>
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
            >
              <h3>{{ task.title }}</h3>
              <p>{{ task.description }}</p>
              <div class="task-meta">
                <span class="priority">{{ task.priority }}</span>
                <span class="status">{{ task.status }}</span>
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
        <button class="btn btn-primary" @click="loadTasks" :disabled="loading">
          {{ loading ? '⏳ Loading...' : '🔄 Refresh Tasks' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted } from 'vue'
  import taskService from '../services/taskService'

  export default {
    name: 'TaskBoard',
    setup() {
      const tasks = ref([])
      const loading = ref(false)
      const error = ref('')

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
            }
          ]
        } finally {
          loading.value = false
        }
      }

      onMounted(() => {
        loadTasks()
      })

      return {
        tasks,
        todoTasks,
        inProgressTasks,
        doneTasks,
        loadTasks,
        loading,
        error,
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
  }

  .task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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
</style>
