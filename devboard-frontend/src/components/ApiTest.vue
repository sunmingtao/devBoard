<template>
  <div class="api-test">
    <div class="test-container">
      <h2>🔗 API Connection Test</h2>
      
      <!-- Connection Status -->
      <div class="status-section">
        <h3>Connection Status</h3>
        <div class="status-indicator" :class="connectionStatus">
          <div class="status-dot"></div>
          <span>{{ connectionMessage }}</span>
        </div>
        <button @click="testConnection" class="btn btn-primary" :disabled="loading">
          {{ loading ? '⏳ Testing...' : '🔄 Test Connection' }}
        </button>
      </div>

      <!-- Hello API Test -->
      <div class="hello-section" v-if="connectionStatus === 'connected'">
        <h3>/api/hello Response</h3>
        <div class="api-response" v-if="helloResponse">
          <pre>{{ JSON.stringify(helloResponse, null, 2) }}</pre>
        </div>
      </div>

      <!-- Tasks API Test -->
      <div class="tasks-section" v-if="connectionStatus === 'connected'">
        <h3>📋 Tasks from API</h3>
        <div class="tasks-controls">
          <button @click="loadTasks" class="btn btn-secondary" :disabled="loadingTasks">
            {{ loadingTasks ? '⏳ Loading...' : '📥 Load Tasks' }}
          </button>
          <span class="task-count" v-if="tasks.length > 0">
            Found {{ tasks.length }} tasks
          </span>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          ❌ {{ error }}
        </div>

        <!-- Tasks Display -->
        <div v-if="tasks.length > 0" class="tasks-grid">
          <div 
            v-for="task in tasks" 
            :key="task.id"
            class="task-card"
            :class="task.priority?.toLowerCase()"
          >
            <div class="task-header">
              <h4>{{ task.title }}</h4>
              <span class="task-id">#{{ task.id }}</span>
            </div>
            <p class="task-description">{{ task.description }}</p>
            <div class="task-meta">
              <span class="status" :class="task.status?.toLowerCase()">
                {{ task.status }}
              </span>
              <span class="priority" :class="task.priority?.toLowerCase()">
                {{ task.priority }}
              </span>
            </div>
            <div class="task-dates" v-if="task.createdAt">
              <small>Created: {{ formatDate(task.createdAt) }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted } from 'vue'
  import taskService from '../services/taskService'

  export default {
    name: 'ApiTest',
    setup() {
      const connectionStatus = ref('disconnected') // disconnected, connecting, connected, error
      const connectionMessage = ref('Not connected')
      const loading = ref(false)
      const loadingTasks = ref(false)
      const helloResponse = ref(null)
      const tasks = ref([])
      const error = ref('')

      const testConnection = async () => {
        loading.value = true
        connectionStatus.value = 'connecting'
        connectionMessage.value = 'Testing connection...'
        error.value = ''

        try {
          const response = await taskService.testConnection()
          helloResponse.value = response
          connectionStatus.value = 'connected'
          connectionMessage.value = 'Connected to backend API ✅'
        } catch (err) {
          connectionStatus.value = 'error'
          connectionMessage.value = 'Connection failed ❌'
          error.value = err.message
          console.error('Connection test failed:', err)
        } finally {
          loading.value = false
        }
      }

      const loadTasks = async () => {
        loadingTasks.value = true
        error.value = ''

        try {
          const fetchedTasks = await taskService.getAllTasks()
          tasks.value = fetchedTasks
          console.log('Tasks loaded successfully:', fetchedTasks)
        } catch (err) {
          error.value = err.message
          console.error('Failed to load tasks:', err)
        } finally {
          loadingTasks.value = false
        }
      }

      const formatDate = (dateString) => {
        if (!dateString) return 'N/A'
        return new Date(dateString).toLocaleDateString()
      }

      // Test connection on component mount
      onMounted(() => {
        testConnection()
      })

      return {
        connectionStatus,
        connectionMessage,
        loading,
        loadingTasks,
        helloResponse,
        tasks,
        error,
        testConnection,
        loadTasks,
        formatDate
      }
    }
  }
</script>

<style scoped>
  .api-test {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .test-container {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .test-container h2 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin: 0;
    padding: 1.5rem;
    font-size: 1.5rem;
  }

  .status-section,
  .hello-section,
  .tasks-section {
    padding: 1.5rem;
    border-bottom: 1px solid #e1e5e9;
  }

  .tasks-section {
    border-bottom: none;
  }

  .status-section h3,
  .hello-section h3,
  .tasks-section h3 {
    margin: 0 0 1rem 0;
    color: #333;
    font-size: 1.25rem;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-weight: 500;
  }

  .status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  .status-indicator.disconnected .status-dot {
    background-color: #6b7280;
  }

  .status-indicator.connecting .status-dot {
    background-color: #f59e0b;
  }

  .status-indicator.connected .status-dot {
    background-color: #10b981;
  }

  .status-indicator.error .status-dot {
    background-color: #ef4444;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .api-response {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #667eea;
    overflow-x: auto;
  }

  .api-response pre {
    margin: 0;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 0.875rem;
    color: #333;
  }

  .tasks-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .task-count {
    color: #666;
    font-weight: 500;
  }

  .error-message {
    background: #fee2e2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #dc2626;
  }

  .tasks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .task-card {
    background: #f8f9fa;
    border-radius: 0.5rem;
    padding: 1rem;
    border-left: 4px solid #ddd;
    transition: all 0.3s ease;
  }

  .task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  .task-card.high {
    border-left-color: #ef4444;
  }

  .task-card.medium {
    border-left-color: #f59e0b;
  }

  .task-card.low {
    border-left-color: #10b981;
  }

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .task-header h4 {
    margin: 0;
    color: #333;
    font-size: 1rem;
  }

  .task-id {
    background: #e5e7eb;
    color: #6b7280;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: bold;
  }

  .task-description {
    color: #666;
    margin: 0.5rem 0;
    line-height: 1.4;
    font-size: 0.875rem;
  }

  .task-meta {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .status,
  .priority {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }

  .status.todo {
    background: #fee2e2;
    color: #dc2626;
  }

  .status.in_progress {
    background: #fef3c7;
    color: #d97706;
  }

  .status.done {
    background: #d1fae5;
    color: #065f46;
  }

  .priority.high {
    background: #fee2e2;
    color: #dc2626;
  }

  .priority.medium {
    background: #fef3c7;
    color: #d97706;
  }

  .priority.low {
    background: #d1fae5;
    color: #065f46;
  }

  .task-dates {
    color: #9ca3af;
    font-size: 0.75rem;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-primary {
    background-color: #667eea;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #5a67d8;
  }

  .btn-secondary {
    background-color: #6b7280;
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background-color: #4b5563;
  }
</style>