<template>
  <div class="home">
    <header class="hero">
      <h1 v-if="isAuthenticated">Welcome back, {{ username }}! 👋</h1>
      <h1 v-else>Welcome to DevBoard</h1>
      <p class="hero-subtitle">
        A modern task management system for developers
      </p>
      <div class="hero-actions">
        <router-link v-if="isAuthenticated" to="/tasks" class="btn btn-primary">
          View Your Tasks
        </router-link>
        <router-link v-else to="/login" class="btn btn-primary">
          Get Started
        </router-link>
        <router-link to="/about" class="btn btn-secondary">
          Learn More
        </router-link>
      </div>
    </header>

    <!-- Vue 3 Composition API Demo -->
    <section class="composition-api-demo">
      <Counter />
    </section>

    <!-- API Testing Section -->
    <section class="api-test-section">
      <ApiTest />
    </section>

    <section class="features">
      <h2>Features</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <h3>🎯 Task Management</h3>
          <p>Create, update, and organize your tasks efficiently</p>
        </div>
        <div class="feature-card">
          <h3>📊 Kanban Board</h3>
          <p>
            Visualize your workflow with Todo, In Progress, and Done columns
          </p>
        </div>
        <div class="feature-card">
          <h3>🚀 Modern Tech Stack</h3>
          <p>Built with Vue 3, Spring Boot, and MySQL</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
  import { ref, onMounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import ApiTest from '../components/ApiTest.vue'
  import Counter from '../components/Counter.vue'
  import { authService } from '../services/authService'

  export default {
    name: 'Home',
    components: {
      ApiTest,
      Counter,
    },
    setup() {
      const route = useRoute()
      const isAuthenticated = ref(authService.isAuthenticated())
      const username = ref('')

      const updateAuthInfo = () => {
        isAuthenticated.value = authService.isAuthenticated()
        if (isAuthenticated.value) {
          const user = authService.getUser()
          username.value = user?.username || ''
        } else {
          username.value = ''
        }
      }

      // Watch for route changes to update auth state
      watch(() => route.path, updateAuthInfo)

      // Initialize auth info on mount
      onMounted(updateAuthInfo)

      return {
        isAuthenticated,
        username
      }
    }
  }
</script>

<style scoped>
  .home {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .composition-api-demo {
    margin-bottom: 3rem;
  }

  .api-test-section {
    margin-bottom: 3rem;
  }

  .hero {
    text-align: center;
    padding: 4rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 1rem;
    margin-bottom: 3rem;
  }

  .hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: bold;
  }

  .hero-subtitle {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
  }

  .hero-actions {
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
  }

  .btn-primary {
    background-color: #fff;
    color: #667eea;
    border: 2px solid #fff;
  }

  .btn-primary:hover {
    background-color: transparent;
    color: #fff;
  }

  .btn-secondary {
    background-color: transparent;
    color: #fff;
    border: 2px solid #fff;
  }

  .btn-secondary:hover {
    background-color: #fff;
    color: #667eea;
  }

  .features {
    text-align: center;
  }

  .features h2 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    color: #333;
  }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
  }

  .feature-card {
    padding: 2rem;
    border: 1px solid #e1e5e9;
    border-radius: 0.5rem;
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;
  }

  .feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  .feature-card h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #333;
  }

  .feature-card p {
    color: #666;
    line-height: 1.6;
  }
</style>
