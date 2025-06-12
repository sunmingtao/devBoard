import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import TaskBoard from '../views/TaskBoard.vue'
import TaskDetail from '../views/TaskDetail.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Profile from '../views/Profile.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'DevBoard - Home',
    },
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      title: 'DevBoard - About',
    },
  },
  {
    path: '/tasks',
    name: 'TaskBoard',
    component: TaskBoard,
    meta: {
      title: 'DevBoard - Task Board',
      requiresAuth: true,
    },
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: TaskDetail,
    meta: {
      title: 'DevBoard - Task Detail',
      requiresAuth: true,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: 'DevBoard - Login',
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: 'DevBoard - Register',
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      title: 'DevBoard - Profile',
      requiresAuth: true,
    },
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: {
      title: 'DevBoard - Admin Dashboard',
      requiresAuth: true,
      requiresAdmin: true,
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard for authentication and authorization
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = to.meta.title || 'DevBoard'
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      // Redirect to login if not authenticated
      next('/login')
      return
    }
    
    // Check if route requires admin role
    if (to.meta.requiresAdmin) {
      const userStr = localStorage.getItem('user')
      if (!userStr) {
        next('/login')
        return
      }
      
      try {
        const user = JSON.parse(userStr)
        if (user.role !== 'ADMIN') {
          // Redirect to home if not admin
          alert('Access denied: Admin role required')
          next('/')
          return
        }
      } catch (error) {
        console.error('Failed to parse user data:', error)
        next('/login')
        return
      }
    }
    
    next()
  } else {
    next()
  }
})

export default router
