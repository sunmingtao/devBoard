package com.example.devboard.service;

import com.example.devboard.dto.UserSummaryResponse;
import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
import com.example.devboard.entity.User.UserRole;
import com.example.devboard.exception.BusinessException;
import com.example.devboard.common.ErrorCode;
import com.example.devboard.repository.CommentRepository;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AdminServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private CommentRepository commentRepository;

    @InjectMocks
    private AdminService adminService;

    private User adminUser;
    private User normalUser1;
    private User normalUser2;
    private List<Task> allTasks;

    @BeforeEach
    void setUp() {
        // Setup test users
        adminUser = new User();
        adminUser.setId(1L);
        adminUser.setUsername("admin");
        adminUser.setEmail("admin@example.com");
        adminUser.setRole(UserRole.ADMIN);
        adminUser.setCreatedAt(LocalDateTime.now().minusDays(30));

        normalUser1 = new User();
        normalUser1.setId(2L);
        normalUser1.setUsername("user1");
        normalUser1.setEmail("user1@example.com");
        normalUser1.setRole(UserRole.USER);
        normalUser1.setCreatedAt(LocalDateTime.now().minusDays(20));

        normalUser2 = new User();
        normalUser2.setId(3L);
        normalUser2.setUsername("user2");
        normalUser2.setEmail("user2@example.com");
        normalUser2.setRole(UserRole.USER);
        normalUser2.setCreatedAt(LocalDateTime.now().minusDays(10));

        // Setup test tasks
        Task task1 = createTask(1L, "Task 1", "TODO", normalUser1, normalUser1);
        Task task2 = createTask(2L, "Task 2", "IN_PROGRESS", normalUser1, normalUser2);
        Task task3 = createTask(3L, "Task 3", "DONE", normalUser2, normalUser2);
        Task task4 = createTask(4L, "Task 4", "TODO", normalUser2, null);
        
        allTasks = Arrays.asList(task1, task2, task3, task4);
    }

    private Task createTask(Long id, String title, String status, User creator, User assignee) {
        Task task = new Task();
        task.setId(id);
        task.setTitle(title);
        task.setStatus(Task.TaskStatus.valueOf(status));
        task.setCreator(creator);
        task.setAssignee(assignee);
        task.setCreatedAt(LocalDateTime.now().minusDays(5));
        return task;
    }

    @Test
    void getAllUsers_Success() {
        // Arrange
        List<User> users = Arrays.asList(adminUser, normalUser1, normalUser2);
        when(userRepository.findAll()).thenReturn(users);
        when(taskRepository.countByCreatorId(1L)).thenReturn(0L);
        when(taskRepository.countByCreatorId(2L)).thenReturn(2L);
        when(taskRepository.countByCreatorId(3L)).thenReturn(1L);
        when(taskRepository.countByAssigneeId(1L)).thenReturn(0L);
        when(commentRepository.countByUserId(1L)).thenReturn(0L);
        when(commentRepository.countByUserId(2L)).thenReturn(1L);
        when(commentRepository.countByUserId(3L)).thenReturn(2L);
        when(taskRepository.countByAssigneeId(2L)).thenReturn(2L);
        when(taskRepository.countByAssigneeId(3L)).thenReturn(1L);

        // Act
        List<UserSummaryResponse> responses = adminService.getAllUsers();

        // Assert
        assertThat(responses).hasSize(3);
        
        UserSummaryResponse adminResponse = responses.get(0);
        assertThat(adminResponse.getUsername()).isEqualTo("admin");
        assertThat(adminResponse.getRole()).isEqualTo("ADMIN");
        assertThat(adminResponse.getTasksCreated()).isEqualTo(0);
        assertThat(adminResponse.getTasksAssigned()).isEqualTo(0);
        
        UserSummaryResponse user1Response = responses.get(1);
        assertThat(user1Response.getUsername()).isEqualTo("user1");
        assertThat(user1Response.getRole()).isEqualTo("USER");
        assertThat(user1Response.getTasksCreated()).isEqualTo(2);
        assertThat(user1Response.getTasksAssigned()).isEqualTo(2);
        
        verify(userRepository).findAll();
        verify(taskRepository, times(3)).countByCreatorId(anyLong());
        verify(taskRepository, times(3)).countByAssigneeId(anyLong());
    }

    @Test
    void getAllUsers_EmptyList() {
        // Arrange
        when(userRepository.findAll()).thenReturn(Arrays.asList());

        // Act
        List<UserSummaryResponse> responses = adminService.getAllUsers();

        // Assert
        assertThat(responses).isEmpty();
    }

    @Test
    void getUserById_Success() {
        // Arrange
        when(userRepository.findById(2L)).thenReturn(Optional.of(normalUser1));
        when(taskRepository.countByCreatorId(2L)).thenReturn(5L);
        when(taskRepository.countByAssigneeId(2L)).thenReturn(3L);
        when(commentRepository.countByUserId(2L)).thenReturn(7L);

        // Act
        UserSummaryResponse response = adminService.getUserById(2L);

        // Assert
        assertThat(response).isNotNull();
        assertThat(response.getUsername()).isEqualTo("user1");
        assertThat(response.getEmail()).isEqualTo("user1@example.com");
        assertThat(response.getRole()).isEqualTo("USER");
        assertThat(response.getTasksCreated()).isEqualTo(5);
        assertThat(response.getTasksAssigned()).isEqualTo(3);
    }

    @Test
    void getUserById_NotFound_ThrowsException() {
        // Arrange
        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> adminService.getUserById(999L))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("User not found with id: 999");
    }

    @Test
    void getDashboardData_Success() {
        // Arrange
        when(userRepository.count()).thenReturn(3L);
        when(taskRepository.count()).thenReturn(4L);
        when(commentRepository.count()).thenReturn(5L);
        
        // User role breakdown
        when(userRepository.countByRole(UserRole.ADMIN)).thenReturn(1L);
        when(userRepository.countByRole(UserRole.USER)).thenReturn(2L);
        
        // Task status breakdown
        when(taskRepository.countByStatus(Task.TaskStatus.TODO)).thenReturn(2L);
        when(taskRepository.countByStatus(Task.TaskStatus.IN_PROGRESS)).thenReturn(1L);
        when(taskRepository.countByStatus(Task.TaskStatus.DONE)).thenReturn(1L);
        
        // Task priority breakdown
        when(taskRepository.countByPriority(Task.TaskPriority.HIGH)).thenReturn(1L);
        when(taskRepository.countByPriority(Task.TaskPriority.MEDIUM)).thenReturn(2L);
        when(taskRepository.countByPriority(Task.TaskPriority.LOW)).thenReturn(1L);
        
        // Unassigned tasks
        when(taskRepository.countByAssigneeIsNull()).thenReturn(1L);

        // Act
        Map<String, Object> response = adminService.getDashboardData();

        // Assert
        assertThat(response).isNotNull();
        
        // Basic counts
        assertThat(response.get("totalUsers")).isEqualTo(3L);
        assertThat(response.get("totalTasks")).isEqualTo(4L);
        assertThat(response.get("totalComments")).isEqualTo(5L);
        
        // User role breakdown
        Map<String, Long> userRoleBreakdown = (Map<String, Long>) response.get("userRoleBreakdown");
        assertThat(userRoleBreakdown).containsEntry("admins", 1L);
        assertThat(userRoleBreakdown).containsEntry("users", 2L);
        
        // Task status breakdown
        Map<String, Long> taskStatusBreakdown = (Map<String, Long>) response.get("taskStatusBreakdown");
        assertThat(taskStatusBreakdown).containsEntry("todo", 2L);
        assertThat(taskStatusBreakdown).containsEntry("inProgress", 1L);
        assertThat(taskStatusBreakdown).containsEntry("done", 1L);
        
        // Task priority breakdown
        Map<String, Long> taskPriorityBreakdown = (Map<String, Long>) response.get("taskPriorityBreakdown");
        assertThat(taskPriorityBreakdown).containsEntry("high", 1L);
        assertThat(taskPriorityBreakdown).containsEntry("medium", 2L);
        assertThat(taskPriorityBreakdown).containsEntry("low", 1L);
        
        // Unassigned tasks
        assertThat(response.get("unassignedTasks")).isEqualTo(1L);
        
        // Recent activity should exist
        assertThat(response).containsKey("recentActivity");
    }

    @Test
    void getDashboardData_EmptyData() {
        // Arrange
        when(userRepository.count()).thenReturn(0L);
        when(taskRepository.count()).thenReturn(0L);
        when(commentRepository.count()).thenReturn(0L);
        when(userRepository.countByRole(any(UserRole.class))).thenReturn(0L);
        when(taskRepository.countByStatus(any(Task.TaskStatus.class))).thenReturn(0L);
        when(taskRepository.countByPriority(any(Task.TaskPriority.class))).thenReturn(0L);
        when(taskRepository.countByAssigneeIsNull()).thenReturn(0L);

        // Act
        Map<String, Object> response = adminService.getDashboardData();

        // Assert
        assertThat(response).isNotNull();
        assertThat(response.get("totalUsers")).isEqualTo(0L);
        assertThat(response.get("totalTasks")).isEqualTo(0L);
        assertThat(response.get("totalComments")).isEqualTo(0L);
        assertThat(response.get("unassignedTasks")).isEqualTo(0L);
    }

    @Test
    void getDashboardData_WithMixedData() {
        // Arrange
        when(userRepository.count()).thenReturn(10L);
        when(taskRepository.count()).thenReturn(25L);
        when(commentRepository.count()).thenReturn(50L);
        
        // User role breakdown
        when(userRepository.countByRole(UserRole.ADMIN)).thenReturn(2L);
        when(userRepository.countByRole(UserRole.USER)).thenReturn(8L);
        
        // Task status breakdown
        when(taskRepository.countByStatus(Task.TaskStatus.TODO)).thenReturn(10L);
        when(taskRepository.countByStatus(Task.TaskStatus.IN_PROGRESS)).thenReturn(8L);
        when(taskRepository.countByStatus(Task.TaskStatus.DONE)).thenReturn(7L);
        
        // Task priority breakdown
        when(taskRepository.countByPriority(Task.TaskPriority.HIGH)).thenReturn(5L);
        when(taskRepository.countByPriority(Task.TaskPriority.MEDIUM)).thenReturn(15L);
        when(taskRepository.countByPriority(Task.TaskPriority.LOW)).thenReturn(5L);
        
        // Unassigned tasks
        when(taskRepository.countByAssigneeIsNull()).thenReturn(3L);

        // Act
        Map<String, Object> response = adminService.getDashboardData();

        // Assert
        assertThat(response.get("totalUsers")).isEqualTo(10L);
        assertThat(response.get("totalTasks")).isEqualTo(25L);
        assertThat(response.get("totalComments")).isEqualTo(50L);
        assertThat(response.get("unassignedTasks")).isEqualTo(3L);
        
        // Verify all sections are present
        assertThat(response).containsKeys("userRoleBreakdown", "taskStatusBreakdown", "taskPriorityBreakdown", "recentActivity");
    }
}