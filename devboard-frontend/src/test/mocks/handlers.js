import { http, HttpResponse } from 'msw'

const API_BASE = 'http://localhost:8080/api'

// Mock data
const mockTasks = [
  { 
    id: 1, 
    title: 'Test Task 1', 
    description: 'Description 1',
    status: 'TODO',
    priority: 'HIGH',
    creator: { id: 1, username: 'testuser' },
    assignee: null,
    createdAt: '2024-01-01T00:00:00',
    updatedAt: '2024-01-01T00:00:00'
  },
  { 
    id: 2, 
    title: 'Test Task 2', 
    description: 'Description 2',
    status: 'IN_PROGRESS',
    priority: 'MEDIUM',
    creator: { id: 1, username: 'testuser' },
    assignee: { id: 2, username: 'assignee' },
    createdAt: '2024-01-02T00:00:00',
    updatedAt: '2024-01-02T00:00:00'
  }
]

const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  role: 'USER',
  nickname: 'Test User',
  avatar: null
}

const mockComments = [
  {
    id: 1,
    content: 'Test comment 1',
    user: { id: 1, username: 'testuser', nickname: 'Test User' },
    createdAt: '2024-01-01T12:00:00',
    updatedAt: '2024-01-01T12:00:00'
  }
]

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const { username, password } = await request.json()
    
    if (username === 'testuser' && password === 'password123') {
      return HttpResponse.json({
        code: 0,
        message: 'success',
        data: {
          token: 'mock-jwt-token',
          type: 'Bearer',
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          role: 'USER',
          nickname: 'Test User'
        }
      })
    }
    
    return HttpResponse.json(
      { message: 'Invalid credentials' },
      { status: 401 }
    )
  }),

  http.post(`${API_BASE}/auth/register`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      id: 2,
      username: body.username,
      email: body.email,
      role: 'USER'
    }, { status: 201 })
  }),

  http.post(`${API_BASE}/auth/signup`, async ({ request }) => {
    const body = await request.json()
    
    // Simulate existing user error
    if (body.username === 'existinguser') {
      return HttpResponse.json(
        { message: 'Username already exists' },
        { status: 400 }
      )
    }
    
    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        id: 2,
        username: body.username,
        email: body.email,
        role: 'USER'
      }
    }, { status: 201 })
  }),

  // Task endpoints
  http.get(`${API_BASE}/tasks`, () => {
    return HttpResponse.json(mockTasks)
  }),

  http.get(`${API_BASE}/tasks/:id`, ({ params }) => {
    const task = mockTasks.find(t => t.id === parseInt(params.id))
    if (task) {
      return HttpResponse.json(task)
    }
    return HttpResponse.json(
      { message: 'Task not found' },
      { status: 404 }
    )
  }),

  http.post(`${API_BASE}/tasks`, async ({ request }) => {
    const body = await request.json()
    const newTask = {
      id: 3,
      ...body,
      creator: mockUser,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    return HttpResponse.json(newTask, { status: 201 })
  }),

  http.put(`${API_BASE}/tasks/:id`, async ({ request, params }) => {
    const body = await request.json()
    const taskId = parseInt(params.id)
    const task = mockTasks.find(t => t.id === taskId)
    
    if (task) {
      const updatedTask = { ...task, ...body, updatedAt: new Date().toISOString() }
      return HttpResponse.json(updatedTask)
    }
    
    return HttpResponse.json(
      { message: 'Task not found' },
      { status: 404 }
    )
  }),

  http.delete(`${API_BASE}/tasks/:id`, ({ params }) => {
    const taskId = parseInt(params.id)
    const task = mockTasks.find(t => t.id === taskId)
    
    if (task) {
      return new HttpResponse(null, { status: 204 })
    }
    
    return HttpResponse.json(
      { message: 'Task not found' },
      { status: 404 }
    )
  }),

  // Comment endpoints
  http.get(`${API_BASE}/tasks/:taskId/comments`, () => {
    return HttpResponse.json(mockComments)
  }),

  http.post(`${API_BASE}/tasks/:taskId/comments`, async ({ request }) => {
    const body = await request.json()
    const newComment = {
      id: 2,
      content: body.content,
      user: mockUser,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    return HttpResponse.json(newComment, { status: 201 })
  }),

  // User endpoints
  http.get(`${API_BASE}/users/profile`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (authHeader && authHeader.includes('mock-jwt-token')) {
      return HttpResponse.json(mockUser)
    }
    
    return HttpResponse.json(
      { message: 'Unauthorized' },
      { status: 401 }
    )
  }),

  http.put(`${API_BASE}/users/profile`, async ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (authHeader && authHeader.includes('mock-jwt-token')) {
      const body = await request.json()
      return HttpResponse.json({ ...mockUser, ...body })
    }
    
    return HttpResponse.json(
      { message: 'Unauthorized' },
      { status: 401 }
    )
  }),

  // Users list endpoint
  http.get(`${API_BASE}/users`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (authHeader && authHeader.includes('mock-jwt-token')) {
      return HttpResponse.json([
        mockUser,
        { id: 2, username: 'assignee', email: 'assignee@example.com', role: 'USER' },
        { id: 3, username: 'admin', email: 'admin@example.com', role: 'ADMIN' }
      ])
    }
    
    return HttpResponse.json(
      { message: 'Unauthorized' },
      { status: 401 }
    )
  }),

  // Current user endpoint
  http.get(`${API_BASE}/users/me`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (authHeader && authHeader.includes('mock-jwt-token')) {
      return HttpResponse.json(mockUser)
    }
    
    return HttpResponse.json(
      { message: 'Unauthorized' },
      { status: 401 }
    )
  }),

  // Admin endpoints
  http.get(`${API_BASE}/admin/dashboard`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (authHeader && authHeader.includes('mock-jwt-token')) {
      return HttpResponse.json({
        totalUsers: 10,
        totalTasks: 25,
        totalComments: 50,
        userRoleBreakdown: { admins: 2, users: 8 },
        taskStatusBreakdown: { todo: 10, inProgress: 8, done: 7 },
        taskPriorityBreakdown: { high: 5, medium: 15, low: 5 },
        unassignedTasks: 3,
        recentActivity: []
      })
    }
    
    return HttpResponse.json(
      { message: 'Forbidden' },
      { status: 403 }
    )
  })
]