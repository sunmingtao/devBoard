<template>
  <div class="admin-dashboard">
    <div class="container">
      <header class="dashboard-header">
        <div class="header-content">
          <div>
            <h1>🛠️ Admin Dashboard</h1>
            <p>System management and user overview</p>
          </div>
          <div class="admin-actions">
            <button class="btn btn-outline" @click="refreshData" :disabled="loading">
              {{ loading ? '⏳ Loading...' : '🔄 Refresh' }}
            </button>
          </div>
        </div>
      </header>

      <!-- Error Display -->
      <div v-if="error" class="error-banner">
        ⚠️ {{ error }}
      </div>

      <!-- Dashboard Statistics -->
      <div class="stats-grid" v-if="dashboardData">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <h3>{{ dashboardData.totalUsers }}</h3>
            <p>Total Users</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📋</div>
          <div class="stat-content">
            <h3>{{ dashboardData.totalTasks }}</h3>
            <p>Total Tasks</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">💬</div>
          <div class="stat-content">
            <h3>{{ dashboardData.totalComments }}</h3>
            <p>Total Comments</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">🚫</div>
          <div class="stat-content">
            <h3>{{ dashboardData.unassignedTasks }}</h3>
            <p>Unassigned Tasks</p>
          </div>
        </div>
      </div>

      <!-- Detailed Breakdowns -->
      <div class="breakdown-grid" v-if="dashboardData">
        <!-- User Role Breakdown -->
        <div class="breakdown-card">
          <h3>👥 User Roles</h3>
          <div class="breakdown-items">
            <div class="breakdown-item">
              <span class="label">🔐 Admins</span>
              <span class="value">{{ dashboardData.userRoleBreakdown.admins }}</span>
            </div>
            <div class="breakdown-item">
              <span class="label">👤 Users</span>
              <span class="value">{{ dashboardData.userRoleBreakdown.users }}</span>
            </div>
          </div>
        </div>

        <!-- Task Status Breakdown -->
        <div class="breakdown-card">
          <h3>📋 Task Status</h3>
          <div class="breakdown-items">
            <div class="breakdown-item">
              <span class="label">📝 To Do</span>
              <span class="value">{{ dashboardData.taskStatusBreakdown.todo }}</span>
            </div>
            <div class="breakdown-item">
              <span class="label">🔄 In Progress</span>
              <span class="value">{{ dashboardData.taskStatusBreakdown.inProgress }}</span>
            </div>
            <div class="breakdown-item">
              <span class="label">✅ Done</span>
              <span class="value">{{ dashboardData.taskStatusBreakdown.done }}</span>
            </div>
          </div>
        </div>

        <!-- Task Priority Breakdown -->
        <div class="breakdown-card">
          <h3>⭐ Task Priority</h3>
          <div class="breakdown-items">
            <div class="breakdown-item">
              <span class="label">🔴 High</span>
              <span class="value">{{ dashboardData.taskPriorityBreakdown.high }}</span>
            </div>
            <div class="breakdown-item">
              <span class="label">🟡 Medium</span>
              <span class="value">{{ dashboardData.taskPriorityBreakdown.medium }}</span>
            </div>
            <div class="breakdown-item">
              <span class="label">🟢 Low</span>
              <span class="value">{{ dashboardData.taskPriorityBreakdown.low }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Management Section -->
      <div class="users-section">
        <div class="section-header">
          <h2>👥 User Management</h2>
          <p>Manage system users and their permissions</p>
        </div>

        <div class="users-table-container">
          <table class="users-table" v-if="users.length > 0">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Stats</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="user-row">
                <td class="user-info">
                  <div class="user-avatar">
                    <img v-if="user.avatar" :src="user.avatar" :alt="user.username" />
                    <div v-else class="avatar-placeholder">
                      {{ user.username.charAt(0).toUpperCase() }}
                    </div>
                  </div>
                  <div class="user-details">
                    <div class="username">{{ user.nickname || user.username }}</div>
                    <div class="user-handle">@{{ user.username }}</div>
                  </div>
                </td>
                <td class="user-email">{{ user.email }}</td>
                <td class="user-role">
                  <span :class="['role-badge', user.role.toLowerCase()]">
                    {{ user.role === 'ADMIN' ? '🔐 Admin' : '👤 User' }}
                  </span>
                </td>
                <td class="user-stats">
                  <div class="stat-item">📝 {{ user.tasksCreated }} created</div>
                  <div class="stat-item">📋 {{ user.tasksAssigned }} assigned</div>
                  <div class="stat-item">💬 {{ user.commentsCount }} comments</div>
                </td>
                <td class="user-joined">
                  {{ formatDate(user.createdAt) }}
                </td>
                <td class="user-actions">
                  <div class="action-buttons">
                    <button 
                      class="action-btn view" 
                      @click="viewUser(user)" 
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      class="action-btn disable" 
                      @click="toggleUserStatus(user)"
                      title="Disable User (Not Implemented)"
                      disabled
                    >
                      🚫
                    </button>
                    <button 
                      class="action-btn reset" 
                      @click="resetPassword(user)"
                      title="Reset Password (Not Implemented)"
                      disabled
                    >
                      🔑
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else-if="loading" class="loading-state">
            ⏳ Loading users...
          </div>
          
          <div v-else class="empty-state">
            No users found
          </div>
        </div>
      </div>

      <!-- Quick Navigation -->
      <div class="quick-nav">
        <router-link to="/tasks" class="btn btn-secondary">
          📋 View Tasks
        </router-link>
        <router-link to="/" class="btn btn-secondary">
          🏠 Back to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminService } from '../services/adminService'
import { authService } from '../services/authService'

export default {
  name: 'AdminDashboard',
  setup() {
    const dashboardData = ref(null)
    const users = ref([])
    const loading = ref(false)
    const error = ref('')

    const loadDashboardData = async () => {
      try {
        console.log('🔄 Loading dashboard data...')
        const data = await adminService.getDashboardData()
        dashboardData.value = data
        console.log('✅ Dashboard data loaded:', data)
      } catch (err) {
        console.error('❌ Failed to load dashboard data:', err)
        error.value = `Failed to load dashboard data: ${err.message}`
      }
    }

    const loadUsers = async () => {
      try {
        console.log('🔄 Loading users...')
        const usersData = await adminService.getAllUsers()
        users.value = usersData
        console.log('✅ Users loaded:', usersData.length, 'users')
      } catch (err) {
        console.error('❌ Failed to load users:', err)
        error.value = `Failed to load users: ${err.message}`
      }
    }

    const refreshData = async () => {
      loading.value = true
      error.value = ''
      
      try {
        await Promise.all([
          loadDashboardData(),
          loadUsers()
        ])
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const viewUser = (user) => {
      alert(`User Details:\n\nID: ${user.id}\nUsername: ${user.username}\nEmail: ${user.email}\nRole: ${user.role}\nTasks Created: ${user.tasksCreated}\nTasks Assigned: ${user.tasksAssigned}\nComments: ${user.commentsCount}\nJoined: ${formatDate(user.createdAt)}`)
    }

    const toggleUserStatus = async (user) => {
      try {
        await adminService.disableUser(user.id)
      } catch (err) {
        alert(err.message)
      }
    }

    const resetPassword = async (user) => {
      try {
        await adminService.resetUserPassword(user.id)
      } catch (err) {
        alert(err.message)
      }
    }

    // Check if user is admin
    const checkAdminAccess = () => {
      const user = authService.getUser()
      if (!user || user.role !== 'ADMIN') {
        error.value = 'Access denied: Admin role required'
        return false
      }
      return true
    }

    onMounted(() => {
      if (checkAdminAccess()) {
        refreshData()
      }
    })

    return {
      dashboardData,
      users,
      loading,
      error,
      refreshData,
      formatDate,
      viewUser,
      toggleUserStatus,
      resetPassword
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  font-size: 1.125rem;
  color: #666;
  margin: 0;
}

.admin-actions {
  display: flex;
  gap: 1rem;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0 0 0.25rem 0;
  color: #333;
}

.stat-content p {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.breakdown-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.breakdown-card h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
}

.breakdown-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.breakdown-item:last-child {
  border-bottom: none;
}

.breakdown-item .label {
  color: #666;
  font-size: 0.875rem;
}

.breakdown-item .value {
  font-weight: bold;
  color: #333;
  font-size: 1.125rem;
}

.users-section {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  padding: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h2 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.section-header p {
  margin: 0;
  color: #666;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.user-row {
  border-bottom: 1px solid #e5e7eb;
  transition: background-color 0.2s ease;
}

.user-row:hover {
  background: #f9fafb;
}

.users-table td {
  padding: 1rem;
  vertical-align: middle;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.25rem;
}

.user-details {
  min-width: 0;
}

.username {
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.125rem;
}

.user-handle {
  font-size: 0.875rem;
  color: #6b7280;
}

.user-email {
  color: #374151;
  font-size: 0.875rem;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.admin {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.user {
  background: #e0e7ff;
  color: #3730a3;
}

.user-stats {
  font-size: 0.75rem;
  color: #6b7280;
}

.stat-item {
  margin-bottom: 0.25rem;
}

.user-joined {
  color: #6b7280;
  font-size: 0.875rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: 1px solid #d1d5db;
  padding: 0.375rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state, .empty-state {
  padding: 3rem;
  text-align: center;
  color: #6b7280;
  font-size: 1.125rem;
}

.quick-nav {
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
  text-align: center;
}

.btn-outline {
  background: transparent;
  color: #333;
  border: 2px solid #333;
}

.btn-outline:hover {
  background: #333;
  color: white;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: transparent;
  color: white;
  border-color: white;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .dashboard-header h1 {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .breakdown-grid {
    grid-template-columns: 1fr;
  }

  .users-table {
    font-size: 0.875rem;
  }

  .users-table th,
  .users-table td {
    padding: 0.75rem 0.5rem;
  }
}
</style>