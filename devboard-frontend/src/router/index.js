import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import TaskBoard from '../views/TaskBoard.vue'
import TaskDetail from '../views/TaskDetail.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Profile from '../views/Profile.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import authService from '../services/authService'

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
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: 'DevBoard - Page Not Found',
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
    if (!authService.isAuthenticated()) {
      // Redirect to login with return URL
      next({
        path: '/login',
        query: { returnUrl: to.fullPath }
      })
      return
    }
    
    // Check if route requires admin role
    if (to.meta.requiresAdmin) {
      if (!authService.isAdmin()) {
        // Redirect to home if not admin
        alert('Access denied: Admin role required')
        next('/')
        return
      }
    }
    
    next()
  } else {
    // Handle guest routes (login/register)
    if ((to.path === '/login' || to.path === '/register') && authService.isAuthenticated()) {
      // Redirect authenticated users away from login/register
      next('/')
      return
    }
    
    next()
  }
})

export { routes }
export default router
