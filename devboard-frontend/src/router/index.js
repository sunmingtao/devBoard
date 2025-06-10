import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import TaskBoard from '../views/TaskBoard.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = to.meta.title || 'DevBoard'
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      // Redirect to login if not authenticated
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
