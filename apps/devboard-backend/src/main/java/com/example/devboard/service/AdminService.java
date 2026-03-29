package com.example.devboard.service;

import com.example.devboard.dto.UserSummaryResponse;
import com.example.devboard.entity.User;
import com.example.devboard.repository.CommentRepository;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class AdminService {
    
    private final UserRepository userRepository;
    private final TaskRepository taskRepository;
    private final CommentRepository commentRepository;
    
    public List<UserSummaryResponse> getAllUsers() {
        List<User> users = userRepository.findAll();
        
        return users.stream()
                .map(this::convertToUserSummary)
                .collect(Collectors.toList());
    }
    
    public UserSummaryResponse getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + id));
        
        return convertToUserSummary(user);
    }
    
    public Map<String, Object> getDashboardData() {
        Map<String, Object> dashboardData = new HashMap<>();
        
        // Basic counts
        long totalUsers = userRepository.count();
        long totalTasks = taskRepository.count();
        long totalComments = commentRepository.count();
        
        // User role breakdown
        long adminUsers = userRepository.countByRole(User.UserRole.ADMIN);
        long regularUsers = userRepository.countByRole(User.UserRole.USER);
        
        // Task status breakdown
        long todoTasks = taskRepository.countByStatus(com.example.devboard.entity.Task.TaskStatus.TODO);
        long inProgressTasks = taskRepository.countByStatus(com.example.devboard.entity.Task.TaskStatus.IN_PROGRESS);
        long doneTasks = taskRepository.countByStatus(com.example.devboard.entity.Task.TaskStatus.DONE);
        
        // Task priority breakdown
        long highPriorityTasks = taskRepository.countByPriority(com.example.devboard.entity.Task.TaskPriority.HIGH);
        long mediumPriorityTasks = taskRepository.countByPriority(com.example.devboard.entity.Task.TaskPriority.MEDIUM);
        long lowPriorityTasks = taskRepository.countByPriority(com.example.devboard.entity.Task.TaskPriority.LOW);
        
        // Unassigned tasks
        long unassignedTasks = taskRepository.countByAssigneeIsNull();
        
        dashboardData.put("totalUsers", totalUsers);
        dashboardData.put("totalTasks", totalTasks);
        dashboardData.put("totalComments", totalComments);
        
        dashboardData.put("userRoleBreakdown", Map.of(
            "admins", adminUsers,
            "users", regularUsers
        ));
        
        dashboardData.put("taskStatusBreakdown", Map.of(
            "todo", todoTasks,
            "inProgress", inProgressTasks,
            "done", doneTasks
        ));
        
        dashboardData.put("taskPriorityBreakdown", Map.of(
            "high", highPriorityTasks,
            "medium", mediumPriorityTasks,
            "low", lowPriorityTasks
        ));
        
        dashboardData.put("unassignedTasks", unassignedTasks);
        
        // Recent activity (placeholder for now)
        dashboardData.put("recentActivity", List.of(
            Map.of("type", "user_registered", "message", "New user registration", "count", 0),
            Map.of("type", "task_created", "message", "Tasks created today", "count", 0),
            Map.of("type", "comments_added", "message", "Comments added today", "count", 0)
        ));
        
        log.info("Generated dashboard data: {} users, {} tasks, {} comments", 
                totalUsers, totalTasks, totalComments);
        
        return dashboardData;
    }
    
    private UserSummaryResponse convertToUserSummary(User user) {
        // Get user statistics
        long tasksCreated = taskRepository.countByCreatorId(user.getId());
        long tasksAssigned = taskRepository.countByAssigneeId(user.getId());
        long commentsCount = commentRepository.countByUserId(user.getId());
        
        return UserSummaryResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .avatar(user.getAvatar())
                .role(user.getRole().name())
                .createdAt(user.getCreatedAt())
                .lastActiveAt(user.getUpdatedAt()) // Using updatedAt as proxy for last active
                .tasksCreated(tasksCreated)
                .tasksAssigned(tasksAssigned)
                .commentsCount(commentsCount)
                .isActive(true) // Placeholder - could implement actual activity tracking
                .build();
    }
}