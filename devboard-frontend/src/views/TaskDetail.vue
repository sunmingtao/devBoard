<template>
  <div class="task-detail">
    <div class="task-detail-header">
      <button @click="goBack" class="back-button">← Back to Tasks</button>
      <h1>Task Details</h1>
    </div>

    <div v-if="loading" class="loading">Loading task details...</div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="task" class="task-content">
      <!-- Task Information -->
      <div class="task-info">
        <div class="task-header">
          <h2>{{ task.title }}</h2>
          <div class="task-meta">
            <span class="status" :class="`status-${task.status.toLowerCase()}`">
              {{ formatStatus(task.status) }}
            </span>
            <span class="priority" :class="`priority-${task.priority.toLowerCase()}`">
              {{ task.priority }}
            </span>
          </div>
        </div>
        
        <div class="task-description">
          <h3>Description</h3>
          <p>{{ task.description || 'No description provided' }}</p>
        </div>
        
        <div class="task-details">
          <div class="detail-item">
            <strong>Creator:</strong> 
            {{ task.creator?.nickname || task.creator?.username || 'Unknown' }}
          </div>
          <div class="detail-item" v-if="task.assignee">
            <strong>Assignee:</strong> 
            {{ task.assignee.nickname || task.assignee.username }}
          </div>
          <div class="detail-item">
            <strong>Created:</strong> 
            {{ formatDate(task.createdAt) }}
          </div>
          <div class="detail-item" v-if="task.updatedAt !== task.createdAt">
            <strong>Updated:</strong> 
            {{ formatDate(task.updatedAt) }}
          </div>
        </div>
      </div>

      <!-- Comments Section -->
      <div class="comments-section">
        <div class="comments-header">
          <h3>Comments ({{ comments.length }})</h3>
        </div>
        
        <!-- Add Comment Form -->
        <div class="add-comment">
          <textarea 
            v-model="newComment" 
            placeholder="Add a comment..."
            rows="3"
            class="comment-input"
          ></textarea>
          <button 
            @click="addComment" 
            :disabled="!newComment.trim() || addingComment"
            class="add-comment-btn"
          >
            {{ addingComment ? 'Adding...' : 'Add Comment' }}
          </button>
        </div>
        
        <!-- Comments List -->
        <div class="comments-list">
          <div v-if="comments.length === 0" class="no-comments">
            No comments yet. Be the first to comment!
          </div>
          
          <div v-for="comment in comments" :key="comment.id" class="comment">
            <div class="comment-header">
              <div class="comment-author">
                <strong>{{ comment.user.nickname || comment.user.username }}</strong>
                <span class="comment-date">{{ formatDate(comment.createdAt) }}</span>
              </div>
              <button 
                v-if="canDeleteComment(comment)"
                @click="deleteComment(comment.id)"
                class="delete-comment-btn"
                title="Delete comment"
              >
                ×
              </button>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { taskService } from '../services/taskService'

const route = useRoute()
const router = useRouter()

const task = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')
const newComment = ref('')
const addingComment = ref(false)

const currentUser = computed(() => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
})

const goBack = () => {
  router.push('/tasks')
}

const formatStatus = (status) => {
  return status.replace('_', ' ')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const canDeleteComment = (comment) => {
  if (!currentUser.value) return false
  return comment.user.id === currentUser.value.id || currentUser.value.role === 'ADMIN'
}

const fetchTaskDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const taskId = route.params.id
    const response = await taskService.getTaskDetail(taskId)
    
    task.value = response.task
    comments.value = response.comments || []
  } catch (err) {
    console.error('Error fetching task detail:', err)
    error.value = 'Failed to load task details'
  } finally {
    loading.value = false
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    addingComment.value = true
    const taskId = route.params.id
    
    const commentData = {
      content: newComment.value.trim()
    }
    
    await taskService.addComment(taskId, commentData)
    newComment.value = ''
    
    // Refresh comments
    await fetchTaskDetail()
  } catch (err) {
    console.error('Error adding comment:', err)
    error.value = 'Failed to add comment'
  } finally {
    addingComment.value = false
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) return
  
  try {
    await taskService.deleteComment(commentId)
    // Refresh comments
    await fetchTaskDetail()
  } catch (err) {
    console.error('Error deleting comment:', err)
    error.value = 'Failed to delete comment'
  }
}

onMounted(() => {
  fetchTaskDetail()
})
</script>

<style scoped>
.task-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.task-detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.back-button {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  color: #6c757d;
}

.back-button:hover {
  background: #e9ecef;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #dc3545;
}

.task-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.task-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.task-header h2 {
  margin: 0;
  color: #2c3e50;
}

.task-meta {
  display: flex;
  gap: 10px;
}

.status, .priority {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-todo {
  background: #ffc107;
  color: #856404;
}

.status-in_progress {
  background: #17a2b8;
  color: white;
}

.status-done {
  background: #28a745;
  color: white;
}

.priority-high {
  background: #dc3545;
  color: white;
}

.priority-medium {
  background: #fd7e14;
  color: white;
}

.priority-low {
  background: #6c757d;
  color: white;
}

.task-description h3 {
  margin-bottom: 10px;
  color: #495057;
}

.task-description p {
  line-height: 1.6;
  color: #6c757d;
}

.task-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.detail-item {
  color: #495057;
}

.comments-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.comments-header h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.add-comment {
  margin-bottom: 20px;
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 10px;
}

.comment-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.add-comment-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.add-comment-btn:hover:not(:disabled) {
  background: #0056b3;
}

.add-comment-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.no-comments {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 20px;
}

.comment {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 15px;
  padding: 15px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-author strong {
  color: #2c3e50;
}

.comment-date {
  color: #6c757d;
  font-size: 12px;
}

.delete-comment-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 18px;
  padding: 2px 6px;
  border-radius: 3px;
}

.delete-comment-btn:hover {
  background: #f8d7da;
}

.comment-content {
  color: #495057;
  line-height: 1.5;
  white-space: pre-wrap;
}
</style>