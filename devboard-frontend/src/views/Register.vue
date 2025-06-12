<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h2>Create a new account</h2>
          <p>
            Or
            <router-link to="/login" class="link">
              sign in to your existing account
            </router-link>
          </p>
        </div>

        <form class="register-form" @submit.prevent="handleSubmit">
          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>
          <div v-if="success" class="alert alert-success">
            {{ success }}
          </div>

          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="formData.username"
              name="username"
              type="text"
              required
              placeholder="Choose a username"
            />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="formData.email"
              name="email"
              type="email"
              required
              placeholder="your@email.com"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="formData.password"
              name="password"
              type="password"
              required
              minlength="6"
              placeholder="At least 6 characters"
            />
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="formData.confirmPassword"
              name="confirmPassword"
              type="password"
              required
              placeholder="Confirm your password"
            />
          </div>

          <button
            type="submit"
            class="btn btn-primary btn-block"
            :disabled="loading"
          >
            {{ loading ? 'Creating account...' : 'Create account' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/authService'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  
  // Validate passwords match
  if (formData.value.password !== formData.value.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true

  try {
    const response = await authService.register({
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password
    })
    
    success.value = 'Account created successfully! Redirecting to login...'
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to create account'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.register-container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  justify-content: center;
}

.register-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
  max-width: 450px;
}

.register-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.register-header h2 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.75rem;
  font-weight: 600;
}

.register-header p {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.link:hover {
  color: #5a67d8;
  text-decoration: underline;
}

.register-form {
  padding: 2rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  text-align: center;
}

.alert-error {
  background-color: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.alert-success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.2s ease;
  background-color: #f9fafb;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input::placeholder {
  color: #9ca3af;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  display: inline-block;
  text-align: center;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
  display: block;
}

/* Responsive Design */
@media (max-width: 480px) {
  .register-container {
    max-width: 100%;
  }
  
  .register-card {
    border-radius: 0;
    box-shadow: none;
  }
  
  .register-page {
    padding: 0;
  }
  
  .register-form {
    padding: 1.5rem;
  }
  
  .register-header {
    padding: 1.5rem 1.5rem 1rem;
  }
  
  .register-header h2 {
    font-size: 1.5rem;
  }
}</style>