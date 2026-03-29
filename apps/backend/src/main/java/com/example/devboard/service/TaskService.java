package com.example.devboard.service;

import com.example.devboard.common.ErrorCode;
import com.example.devboard.dto.TaskCreateRequest;
import com.example.devboard.dto.TaskResponse;
import com.example.devboard.dto.TaskUpdateRequest;
import com.example.devboard.dto.TaskDetailResponse;
import com.example.devboard.dto.CommentResponse;
import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
import com.example.devboard.exception.BusinessException;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import com.example.devboard.repository.CommentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
@Slf4j
public class TaskService {
    
    private final TaskRepository taskRepository;
    private final UserRepository userRepository;
    private final CommentRepository commentRepository;
    
    public List<TaskResponse> getAllTasks() {
        return taskRepository.findAll().stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public List<TaskResponse> getAllTasksWithFilters(Long assigneeId, String priority, String status, String search, Long creatorId) {
        return taskRepository.findAll().stream()
                .filter(task -> {
                    // Filter by assignee - only filter if assigneeId is specified
                    if (assigneeId != null) {
                        // If task has no assignee, exclude it when looking for specific assignee
                        if (task.getAssignee() == null) {
                            return false;
                        }
                        // If task has assignee but doesn't match the filter, exclude it
                        if (!task.getAssignee().getId().equals(assigneeId)) {
                            return false;
                        }
                    }
                    
                    // Filter by creator - only filter if creatorId is specified
                    if (creatorId != null) {
                        if (task.getCreator() == null || !task.getCreator().getId().equals(creatorId)) {
                            return false;
                        }
                    }
                    
                    // Filter by priority - only filter if priority is specified
                    if (priority != null && !priority.isEmpty()) {
                        try {
                            Task.TaskPriority taskPriority = Task.TaskPriority.valueOf(priority.toUpperCase());
                            if (!task.getPriority().equals(taskPriority)) {
                                return false;
                            }
                        } catch (IllegalArgumentException e) {
                            log.warn("Invalid priority filter: {}", priority);
                            return false;
                        }
                    }
                    
                    // Filter by status - only filter if status is specified
                    if (status != null && !status.isEmpty()) {
                        try {
                            Task.TaskStatus taskStatus = Task.TaskStatus.valueOf(status.toUpperCase());
                            if (!task.getStatus().equals(taskStatus)) {
                                return false;
                            }
                        } catch (IllegalArgumentException e) {
                            log.warn("Invalid status filter: {}", status);
                            return false;
                        }
                    }
                    
                    // Search in title and description - only filter if search is specified
                    if (search != null && !search.trim().isEmpty()) {
                        String searchLower = search.toLowerCase().trim();
                        boolean titleMatch = task.getTitle() != null && 
                                           task.getTitle().toLowerCase().contains(searchLower);
                        boolean descMatch = task.getDescription() != null && 
                                          task.getDescription().toLowerCase().contains(searchLower);
                        if (!titleMatch && !descMatch) {
                            return false;
                        }
                    }
                    
                    return true;
                })
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public TaskResponse getTaskById(Long id) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.TASK_NOT_FOUND, "Task not found with id: " + id));
        return convertToResponse(task);
    }
    
    public TaskDetailResponse getTaskDetail(Long id) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> {
                    log.error("Task not found with id: {}", id);
                    return new BusinessException(ErrorCode.TASK_NOT_FOUND, "Task not found with id: " + id);
                });
        
        TaskResponse taskResponse = convertToResponse(task);
        List<CommentResponse> comments = commentRepository.findByTaskIdOrderByCreatedAtDesc(id)
                .stream()
                .map(comment -> {
                    CommentResponse.UserSummary userSummary = CommentResponse.UserSummary.builder()
                            .id(comment.getUser().getId())
                            .username(comment.getUser().getUsername())
                            .nickname(comment.getUser().getNickname())
                            .avatar(comment.getUser().getAvatar())
                            .build();
                    
                    return CommentResponse.builder()
                            .id(comment.getId())
                            .content(comment.getContent())
                            .user(userSummary)
                            .createdAt(comment.getCreatedAt())
                            .updatedAt(comment.getUpdatedAt())
                            .build();
                })
                .collect(Collectors.toList());
        
        return TaskDetailResponse.fromTaskResponse(taskResponse, comments);
    }
    
    public TaskResponse createTask(TaskCreateRequest request, Long creatorId) {
        User creator = userRepository.findById(creatorId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND, "Creator not found"));
        
        Task task = Task.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .status(Task.TaskStatus.valueOf(request.getStatus()))
                .priority(Task.TaskPriority.valueOf(request.getPriority()))
                .creator(creator)
                .build();
        
        // Set assignee if provided
        if (request.getAssigneeId() != null) {
            User assignee = userRepository.findById(request.getAssigneeId())
                    .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND, "Assignee not found"));
            task.setAssignee(assignee);
        }
        
        Task savedTask = taskRepository.save(task);
        return convertToResponse(savedTask);
    }
    
    public TaskResponse updateTask(Long id, TaskUpdateRequest request, Long userId) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> {
                    log.error("Task not found with id: {}", id);
                    return new BusinessException(ErrorCode.TASK_NOT_FOUND, "Task not found with id: " + id);
                });
        
        log.info("User {} updating task {} - '{}'", userId, id, task.getTitle());
        
        // New permission logic: Any authenticated user can update any task
        
        // Update fields if provided
        if (request.getTitle() != null) {
            task.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            task.setDescription(request.getDescription());
        }
        if (request.getStatus() != null) {
            task.setStatus(Task.TaskStatus.valueOf(request.getStatus()));
        }
        if (request.getPriority() != null) {
            task.setPriority(Task.TaskPriority.valueOf(request.getPriority()));
        }
        if (request.getAssigneeId() != null) {
            User assignee = userRepository.findById(request.getAssigneeId())
                    .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND, "Assignee not found"));
            task.setAssignee(assignee);
        }
        
        Task updatedTask = taskRepository.save(task);
        return convertToResponse(updatedTask);
    }
    
    public void deleteTask(Long id, Long userId) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> {
                    log.error("Task not found with id: {}", id);
                    return new BusinessException(ErrorCode.TASK_NOT_FOUND, "Task not found with id: " + id);
                });
        
        // Get user to check if admin
        User user = userRepository.findById(userId)
                .orElseThrow(() -> {
                    log.error("User not found with id: {}", userId);
                    return new BusinessException(ErrorCode.USER_NOT_FOUND, "User not found");
                });
        
        // Only creator or admin can delete
        boolean isCreator = task.getCreator() != null && task.getCreator().getId().equals(userId);
        boolean isAdmin = user.getRole() == User.UserRole.ADMIN;
        
        if (!isCreator && !isAdmin) {
            log.warn("User {} attempted to delete task {} - permission denied. Creator: {}, User role: {}", 
                    userId, id, 
                    task.getCreator() != null ? task.getCreator().getId() : "null", 
                    user.getRole());
            throw new BusinessException(ErrorCode.TASK_ACCESS_DENIED, "Only the creator or admin can delete this task");
        }
        
        log.info("User {} deleting task {} - '{}'", userId, id, task.getTitle());
        taskRepository.delete(task);
    }
    
    public List<TaskResponse> getTasksByStatus(String status) {
        Task.TaskStatus taskStatus = Task.TaskStatus.valueOf(status);
        return taskRepository.findByStatus(taskStatus).stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public List<TaskResponse> getMyTasks(Long userId) {
        List<Task> tasks = taskRepository.findAll().stream()
                .filter(task -> (task.getCreator() != null && task.getCreator().getId().equals(userId)) || 
                               (task.getAssignee() != null && task.getAssignee().getId().equals(userId)))
                .collect(Collectors.toList());
        
        return tasks.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    private TaskResponse convertToResponse(Task task) {
        TaskResponse.UserSummary creator = null;
        if (task.getCreator() != null) {
            creator = TaskResponse.UserSummary.builder()
                    .id(task.getCreator().getId())
                    .username(task.getCreator().getUsername())
                    .nickname(task.getCreator().getNickname())
                    .avatar(task.getCreator().getAvatar())
                    .build();
        }
        
        TaskResponse.UserSummary assignee = null;
        if (task.getAssignee() != null) {
            assignee = TaskResponse.UserSummary.builder()
                    .id(task.getAssignee().getId())
                    .username(task.getAssignee().getUsername())
                    .nickname(task.getAssignee().getNickname())
                    .avatar(task.getAssignee().getAvatar())
                    .build();
        }
        
        return TaskResponse.builder()
                .id(task.getId())
                .title(task.getTitle())
                .description(task.getDescription())
                .status(task.getStatus().name())
                .priority(task.getPriority().name())
                .creator(creator)
                .assignee(assignee)
                .createdAt(task.getCreatedAt())
                .updatedAt(task.getUpdatedAt())
                .commentCount(commentRepository.countByTaskId(task.getId()))
                .build();
    }
    
    // Permission checking method for @PreAuthorize
    public boolean isTaskCreator(Long taskId, String username) {
        return taskRepository.findById(taskId)
                .map(task -> task.getCreator().getUsername().equals(username))
                .orElse(false);
    }
    
    // Admin-only task deletion
    public void adminDeleteTask(Long taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new BusinessException(ErrorCode.TASK_NOT_FOUND, "Task not found"));
        
        log.info("Admin deleting task: {} ({})", task.getId(), task.getTitle());
        taskRepository.delete(task);
    }
}