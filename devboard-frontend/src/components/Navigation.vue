<template>
  <nav class="navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <h1>DevBoard</h1>
        </router-link>
      </div>

      <div class="nav-menu" :class="{ active: isMenuOpen }">
        <router-link
          to="/"
          class="nav-link"
          :class="{ active: $route.name === 'Home' }"
          @click="closeMenu"
        >
          🏠 Home
        </router-link>
        <router-link
          v-if="isAuthenticated"
          to="/tasks"
          class="nav-link"
          :class="{ active: $route.name === 'TaskBoard' }"
          @click="closeMenu"
        >
          📋 Tasks
        </router-link>
        <router-link
          v-if="isAuthenticated"
          to="/profile"
          class="nav-link"
          :class="{ active: $route.name === 'Profile' }"
          @click="closeMenu"
        >
          👤 Profile
        </router-link>
        <router-link
          to="/about"
          class="nav-link"
          :class="{ active: $route.name === 'About' }"
          @click="closeMenu"
        >
          ℹ️ About
        </router-link>
        
        <div class="nav-auth">
          <template v-if="!isAuthenticated">
            <router-link
              to="/login"
              class="nav-link auth-link"
              :class="{ active: $route.name === 'Login' }"
              @click="closeMenu"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              class="nav-link auth-link register-btn"
              :class="{ active: $route.name === 'Register' }"
              @click="closeMenu"
            >
              Register
            </router-link>
          </template>
          <template v-else>
            <router-link
              to="/profile"
              class="nav-link auth-link"
              :class="{ active: $route.name === 'Profile' }"
              @click="closeMenu"
            >
              👤 {{ username }}
            </router-link>
            <button @click="handleLogout" class="nav-link auth-link logout-btn">
              Logout
            </button>
          </template>
        </div>
      </div>

      <button
        class="nav-toggle"
        @click="toggleMenu"
        :class="{ active: isMenuOpen }"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
  </nav>
</template>

<script>
  import { ref, computed, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { authService } from '../services/authService'

  export default {
    name: 'Navigation',
    setup() {
      const router = useRouter()
      const route = useRoute()
      const isMenuOpen = ref(false)
      
      // Authentication state
      const isAuthenticated = ref(authService.isAuthenticated())
      const username = ref('')
      
      // Update username when authenticated
      const updateUserInfo = () => {
        if (isAuthenticated.value) {
          const user = authService.getUser()
          username.value = user?.username || ''
        }
      }
      
      // Watch for route changes to update auth state
      watch(() => route.path, () => {
        isAuthenticated.value = authService.isAuthenticated()
        updateUserInfo()
      })
      
      // Initialize user info
      updateUserInfo()

      const toggleMenu = () => {
        isMenuOpen.value = !isMenuOpen.value
      }

      const closeMenu = () => {
        isMenuOpen.value = false
      }
      
      const handleLogout = () => {
        authService.logout()
        isAuthenticated.value = false
        username.value = ''
        closeMenu()
        router.push('/')
      }

      return {
        isMenuOpen,
        isAuthenticated,
        username,
        toggleMenu,
        closeMenu,
        handleLogout,
      }
    },
  }
</script>

<style scoped>
  .navigation {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    height: 4rem;
  }

  .nav-brand {
    flex-shrink: 0;
  }

  .brand-link {
    text-decoration: none;
    color: white;
  }

  .brand-link h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: bold;
  }

  .nav-menu {
    display: flex;
    gap: 2rem;
    align-items: center;
  }

  .nav-link {
    color: rgba(255, 255, 255, 0.9);
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .nav-link:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .nav-link.active {
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
  }

  .nav-auth {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-left: auto;
  }

  .user-info {
    color: white;
    font-weight: 500;
    padding: 0.5rem 1rem;
  }

  .auth-link {
    padding: 0.5rem 1rem;
  }

  .register-btn {
    background-color: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
  }

  .register-btn:hover {
    background-color: rgba(255, 255, 255, 0.3);
  }

  .logout-btn {
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
    cursor: pointer;
    font-size: inherit;
    font-family: inherit;
  }

  .logout-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .nav-toggle {
    display: none;
    flex-direction: column;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
  }

  .nav-toggle span {
    width: 25px;
    height: 3px;
    background: white;
    margin: 3px 0;
    transition: 0.3s;
    border-radius: 2px;
  }

  .nav-toggle.active span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
  }

  .nav-toggle.active span:nth-child(2) {
    opacity: 0;
  }

  .nav-toggle.active span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -6px);
  }

  @media (max-width: 768px) {
    .nav-container {
      padding: 0 1rem;
    }

    .nav-menu {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      flex-direction: column;
      padding: 1rem;
      gap: 0;
      transform: translateY(-100%);
      opacity: 0;
      visibility: hidden;
      transition: all 0.3s ease;
    }

    .nav-menu.active {
      transform: translateY(0);
      opacity: 1;
      visibility: visible;
    }

    .nav-link {
      width: 100%;
      padding: 1rem;
      text-align: center;
      border-radius: 0.5rem;
      margin-bottom: 0.5rem;
    }

    .nav-auth {
      width: 100%;
      flex-direction: column;
      gap: 0.5rem;
      margin-left: 0;
      margin-top: 1rem;
    }

    .auth-link {
      width: 100%;
      text-align: center;
    }

    .user-info {
      text-align: center;
      margin-bottom: 0.5rem;
    }

    .nav-toggle {
      display: flex;
    }
  }
</style>
