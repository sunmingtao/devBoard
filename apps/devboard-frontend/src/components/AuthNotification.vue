<template>
  <div v-if="notification" class="auth-notification" :class="notification.type">
    <div class="notification-content">
      <span class="message">{{ notification.message }}</span>
      <button @click="closeNotification" class="close-btn">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const notification = ref(null)

const showNotification = (event) => {
  const { status, message } = event.detail
  
  let type = 'info'
  let autoHideDelay = 5000
  
  if (status === 401) {
    type = 'error'
    autoHideDelay = 3000 // Shorter for auth errors since we redirect
  } else if (status === 403) {
    type = 'warning'
    autoHideDelay = 6000
  } else if (status === 'warning') {
    type = 'warning'
    autoHideDelay = 8000 // Longer for session expiry warnings
  }
  
  notification.value = {
    message,
    type
  }
  
  // Auto-hide after specified delay
  setTimeout(() => {
    notification.value = null
  }, autoHideDelay)
}

const closeNotification = () => {
  notification.value = null
}

onMounted(() => {
  window.addEventListener('auth-error', showNotification)
})

onUnmounted(() => {
  window.removeEventListener('auth-error', showNotification)
})
</script>

<style scoped>
.auth-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  z-index: 1000;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

.notification-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.auth-notification.error {
  border-left: 4px solid #ef4444;
}

.auth-notification.error .notification-content {
  background: #fef2f2;
  color: #991b1b;
}

.auth-notification.warning {
  border-left: 4px solid #f59e0b;
}

.auth-notification.warning .notification-content {
  background: #fffbeb;
  color: #92400e;
}

.message {
  flex: 1;
  font-weight: 500;
  margin-right: 12px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  transition: opacity 0.2s ease;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  opacity: 1;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>