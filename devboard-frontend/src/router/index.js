import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import TaskBoard from '../views/TaskBoard.vue'

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
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Update page title based on route
router.beforeEach(to => {
  document.title = to.meta.title || 'DevBoard'
})

export default router
