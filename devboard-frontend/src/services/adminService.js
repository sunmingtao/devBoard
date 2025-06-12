import api from './api'

export const adminService = {
  // Get all users (admin only)
  getAllUsers: async () => {
    try {
      const response = await api.get('/admin/users')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch users: ${error.message}`)
    }
  },

  // Get dashboard data (admin only)
  getDashboardData: async () => {
    try {
      const response = await api.get('/admin/dashboard')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch dashboard data: ${error.message}`)
    }
  },

  // Get user details (admin only)
  getUserById: async (id) => {
    try {
      const response = await api.get(`/admin/users/${id}`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch user ${id}: ${error.message}`)
    }
  },

  // Placeholder methods for future features
  disableUser: async (id) => {
    try {
      const response = await api.put(`/admin/users/${id}/disable`)
      return response.data
    } catch (error) {
      if (error.response?.status === 501) {
        throw new Error('User disable functionality not implemented yet')
      }
      throw new Error(`Failed to disable user ${id}: ${error.message}`)
    }
  },

  enableUser: async (id) => {
    try {
      const response = await api.put(`/admin/users/${id}/enable`)
      return response.data
    } catch (error) {
      if (error.response?.status === 501) {
        throw new Error('User enable functionality not implemented yet')
      }
      throw new Error(`Failed to enable user ${id}: ${error.message}`)
    }
  },

  resetUserPassword: async (id) => {
    try {
      const response = await api.post(`/admin/users/${id}/reset-password`)
      return response.data
    } catch (error) {
      if (error.response?.status === 501) {
        throw new Error('Password reset functionality not implemented yet')
      }
      throw new Error(`Failed to reset password for user ${id}: ${error.message}`)
    }
  }
}