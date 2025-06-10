import api from './api'

export const userService = {
  // Get current user's detailed profile
  async getProfile() {
    const response = await api.get('/users/me')
    return response.data
  },

  // Update user profile
  async updateProfile(profileData) {
    const response = await api.put('/users/me', profileData)
    return response.data
  },

  // Upload avatar (for future implementation)
  async uploadAvatar(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/users/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}