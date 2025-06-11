import api from './api'

export const taskService = {
  // Get all tasks
  getAllTasks: async () => {
    try {
      const response = await api.get('/tasks')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch tasks: ${error.message}`)
    }
  },

  // Get tasks with filters
  getTasksWithFilters: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      
      if (filters.assigneeId) params.append('assigneeId', filters.assigneeId)
      if (filters.priority) params.append('priority', filters.priority)
      if (filters.status) params.append('status', filters.status)
      if (filters.search) params.append('search', filters.search)
      if (filters.creatorId) params.append('creatorId', filters.creatorId)
      
      const url = params.toString() ? `/tasks?${params.toString()}` : '/tasks'
      const response = await api.get(url)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch filtered tasks: ${error.message}`)
    }
  },

  // Get task by ID
  getTaskById: async (id) => {
    try {
      const response = await api.get(`/tasks/${id}`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch task ${id}: ${error.message}`)
    }
  },

  // Create new task
  createTask: async (task) => {
    try {
      const response = await api.post('/tasks', task)
      return response.data
    } catch (error) {
      throw new Error(`Failed to create task: ${error.message}`)
    }
  },

  // Update task
  updateTask: async (id, task) => {
    try {
      const response = await api.put(`/tasks/${id}`, task)
      return response.data
    } catch (error) {
      throw new Error(`Failed to update task ${id}: ${error.message}`)
    }
  },

  // Delete task
  deleteTask: async (id) => {
    try {
      await api.delete(`/tasks/${id}`)
      return true
    } catch (error) {
      throw new Error(`Failed to delete task ${id}: ${error.message}`)
    }
  },

  // Get tasks by status
  getTasksByStatus: async (status) => {
    try {
      const response = await api.get(`/tasks/status/${status}`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch tasks with status ${status}: ${error.message}`)
    }
  },

  // Get tasks by priority
  getTasksByPriority: async (priority) => {
    try {
      const response = await api.get(`/tasks/priority/${priority}`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch tasks with priority ${priority}: ${error.message}`)
    }
  },

  // Get task detail with comments
  getTaskDetail: async (id) => {
    try {
      const response = await api.get(`/tasks/${id}/detail`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch task detail ${id}: ${error.message}`)
    }
  },

  // Add comment to task
  addComment: async (taskId, comment) => {
    try {
      const response = await api.post(`/tasks/${taskId}/comments`, comment)
      return response.data
    } catch (error) {
      throw new Error(`Failed to add comment to task ${taskId}: ${error.message}`)
    }
  },

  // Get comments for task
  getTaskComments: async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}/comments`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch comments for task ${taskId}: ${error.message}`)
    }
  },

  // Delete comment
  deleteComment: async (commentId) => {
    try {
      await api.delete(`/comments/${commentId}`)
      return true
    } catch (error) {
      throw new Error(`Failed to delete comment ${commentId}: ${error.message}`)
    }
  },

  // Test API connection
  testConnection: async () => {
    try {
      const response = await api.get('/hello')
      return response.data
    } catch (error) {
      throw new Error(`Failed to connect to API: ${error.message}`)
    }
  }
}

export default taskService