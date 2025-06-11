package com.example.devboard.service;

import com.example.devboard.dto.TaskCreateRequest;
import com.example.devboard.dto.TaskResponse;
import com.example.devboard.dto.TaskUpdateRequest;
import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class TaskService {
    
    private final TaskRepository taskRepository;
    private final UserRepository userRepository;
    
    public List<TaskResponse> getAllTasks() {
        return taskRepository.findAll().stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public TaskResponse getTaskById(Long id) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Task not found with id: " + id));
        return convertToResponse(task);
    }
    
    public TaskResponse createTask(TaskCreateRequest request, Long creatorId) {
        User creator = userRepository.findById(creatorId)
                .orElseThrow(() -> new RuntimeException("Creator not found"));
        
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
                    .orElseThrow(() -> new RuntimeException("Assignee not found"));
            task.setAssignee(assignee);
        }
        
        Task savedTask = taskRepository.save(task);
        return convertToResponse(savedTask);
    }
    
    public TaskResponse updateTask(Long id, TaskUpdateRequest request, Long userId) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Task not found with id: " + id));
        
        // Check if user has permission to update (creator or assignee)
        boolean isCreator = task.getCreator() != null && task.getCreator().getId().equals(userId);
        boolean isAssignee = task.getAssignee() != null && task.getAssignee().getId().equals(userId);
        
        if (!isCreator && !isAssignee) {
            throw new RuntimeException("You don't have permission to update this task");
        }
        
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
                    .orElseThrow(() -> new RuntimeException("Assignee not found"));
            task.setAssignee(assignee);
        }
        
        Task updatedTask = taskRepository.save(task);
        return convertToResponse(updatedTask);
    }
    
    public void deleteTask(Long id, Long userId) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Task not found with id: " + id));
        
        // Only creator can delete
        if (task.getCreator() == null || !task.getCreator().getId().equals(userId)) {
            throw new RuntimeException("Only the creator can delete this task");
        }
        
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
                .build();
    }
}