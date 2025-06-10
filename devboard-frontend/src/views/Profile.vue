<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>My Profile</h1>
      <p class="subtitle">Manage your account information</p>
    </div>

    <div class="profile-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading profile...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-message">
          <h3>Error Loading Profile</h3>
          <p>{{ error }}</p>
          <button @click="loadProfile" class="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>

      <!-- Profile Form -->
      <div v-else class="profile-form-container">
        <!-- Avatar Section -->
        <div class="avatar-section">
          <div class="avatar-container">
            <img 
              :src="profile.avatar || '/default-avatar.svg'" 
              :alt="profile.nickname || profile.username"
              class="avatar-image"
              @error="handleImageError"
            />
            <div class="avatar-overlay">
              <button @click="triggerFileUpload" class="avatar-upload-btn">
                📷 Change
              </button>
              <input 
                ref="fileInput"
                type="file"
                accept="image/*"
                @change="handleAvatarUpload"
                style="display: none"
              />
            </div>
          </div>
          <div class="avatar-info">
            <h2>{{ profile.nickname || profile.username }}</h2>
            <p class="user-role">{{ profile.role }}</p>
            <p class="join-date">
              Joined {{ formatDate(profile.createdAt) }}
            </p>
          </div>
        </div>

        <!-- Edit Form -->
        <form @submit.prevent="handleSubmit" class="profile-form">
          <div v-if="submitError" class="alert alert-error">
            {{ submitError }}
          </div>
          
          <div v-if="submitSuccess" class="alert alert-success">
            Profile updated successfully!
          </div>

          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="profile.username"
              type="text"
              class="form-input"
              readonly
              disabled
            />
            <small class="help-text">Username cannot be changed</small>
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label for="nickname">Display Name</label>
            <input
              id="nickname"
              v-model="formData.nickname"
              type="text"
              class="form-input"
              maxlength="50"
              placeholder="Enter your display name"
            />
            <small class="help-text">This name will be shown to other users</small>
          </div>

          <div class="form-group">
            <label for="avatar">Avatar URL</label>
            <input
              id="avatar"
              v-model="formData.avatar"
              type="url"
              class="form-input"
              placeholder="https://example.com/avatar.jpg"
            />
            <small class="help-text">Or upload an image using the button above</small>
          </div>

          <div class="form-actions">
            <button 
              type="button" 
              @click="resetForm" 
              class="btn btn-secondary"
              :disabled="submitting"
            >
              Reset
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="submitting || !hasChanges"
            >
              <span v-if="submitting">Saving...</span>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { userService } from '../services/userService'
import { authService } from '../services/authService'

// Reactive data
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)
const fileInput = ref(null)

const profile = reactive({
  id: null,
  username: '',
  email: '',
  nickname: '',
  avatar: '',
  role: '',
  createdAt: null,
  updatedAt: null
})

const formData = reactive({
  email: '',
  nickname: '',
  avatar: ''
})

// Computed properties
const hasChanges = computed(() => {
  return formData.email !== profile.email ||
         formData.nickname !== (profile.nickname || '') ||
         formData.avatar !== (profile.avatar || '')
})

// Methods
const loadProfile = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const profileData = await userService.getProfile()
    
    // Update profile object
    Object.assign(profile, profileData)
    
    // Initialize form data
    resetForm()
    
  } catch (err) {
    console.error('Error loading profile:', err)
    error.value = err.response?.data?.message || 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.email = profile.email || ''
  formData.nickname = profile.nickname || ''
  formData.avatar = profile.avatar || ''
  submitError.value = ''
  submitSuccess.value = false
}

const handleSubmit = async () => {
  if (!hasChanges.value) return
  
  try {
    submitting.value = true
    submitError.value = ''
    submitSuccess.value = false
    
    // Prepare update data (only send changed fields)
    const updateData = {}
    if (formData.email !== profile.email) {
      updateData.email = formData.email
    }
    if (formData.nickname !== (profile.nickname || '')) {
      updateData.nickname = formData.nickname
    }
    if (formData.avatar !== (profile.avatar || '')) {
      updateData.avatar = formData.avatar
    }
    
    await userService.updateProfile(updateData)
    
    // Update local profile data
    Object.assign(profile, updateData)
    
    // Update localStorage user data
    const currentUser = authService.getUser()
    if (currentUser) {
      const updatedUser = { ...currentUser, ...updateData }
      localStorage.setItem('user', JSON.stringify(updatedUser))
    }
    
    submitSuccess.value = true
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      submitSuccess.value = false
    }, 3000)
    
  } catch (err) {
    console.error('Error updating profile:', err)
    submitError.value = err.response?.data?.message || 'Failed to update profile'
  } finally {
    submitting.value = false
  }
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file
  if (!file.type.startsWith('image/')) {
    submitError.value = 'Please select a valid image file'
    return
  }
  
  if (file.size > 5 * 1024 * 1024) { // 5MB limit
    submitError.value = 'File size must be less than 5MB'
    return
  }
  
  try {
    submitting.value = true
    submitError.value = ''
    
    // For now, we'll create a data URL for preview
    // In a real app, you'd upload to a server/cloud storage
    const reader = new FileReader()
    reader.onload = (e) => {
      formData.avatar = e.target.result
      profile.avatar = e.target.result
    }
    reader.readAsDataURL(file)
    
    // TODO: Implement actual file upload to server
    // const uploadResult = await userService.uploadAvatar(file)
    // formData.avatar = uploadResult.avatarUrl
    
  } catch (err) {
    console.error('Error uploading avatar:', err)
    submitError.value = 'Failed to upload avatar'
  } finally {
    submitting.value = false
  }
}

const handleImageError = (event) => {
  event.target.src = '/default-avatar.svg'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Watch for avatar changes to update preview
watch(() => formData.avatar, (newAvatar) => {
  if (newAvatar && newAvatar !== profile.avatar) {
    profile.avatar = newAvatar
  }
})

// Initialize
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  text-align: center;
  margin-bottom: 3rem;
}

.profile-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 3rem;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 2rem;
  color: #c33;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.avatar-container {
  position: relative;
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(255, 255, 255, 0.3);
  transition: transform 0.3s ease;
}

.avatar-image:hover {
  transform: scale(1.05);
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  right: 0;
}

.avatar-upload-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-upload-btn:hover {
  background: white;
  transform: translateY(-2px);
}

.avatar-info h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.user-role {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  display: inline-block;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.join-date {
  opacity: 0.8;
  font-size: 0.9rem;
  margin: 0;
}

.profile-form {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background-color: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #666;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.alert-error {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.alert-success {
  background: #efe;
  color: #363;
  border: 1px solid #cfc;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
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
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 2px solid #e1e5e9;
}

.btn-secondary:hover:not(:disabled) {
  background: #e9ecef;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 1rem;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>