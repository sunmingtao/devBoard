package com.example.devboard.service;

import com.example.devboard.dto.TaskResponse;
import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
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

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TaskServiceTest {

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private CommentRepository commentRepository;

    @InjectMocks
    private TaskService taskService;

    private User user1;
    private User user2;
    private Task taskWithAssignee;
    private Task taskWithoutAssignee;
    private Task taskHighPriority;
    private Task taskLowPriority;
    private Task taskTodo;
    private Task taskInProgress;

    @BeforeEach
    void setUp() {
        // Create test users
        user1 = User.builder()
                .id(1L)
                .username("user1")
                .email("user1@test.com")
                .password("password")
                .nickname("User One")
                .role(User.UserRole.USER)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        user2 = User.builder()
                .id(2L)
                .username("user2")
                .email("user2@test.com")
                .password("password")
                .nickname("User Two")
                .role(User.UserRole.USER)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        // Create test tasks
        taskWithAssignee = Task.builder()
                .id(1L)
                .title("Task with Assignee")
                .description("This task has an assignee")
                .status(Task.TaskStatus.TODO)
                .priority(Task.TaskPriority.HIGH)
                .creator(user1)
                .assignee(user2)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        taskWithoutAssignee = Task.builder()
                .id(2L)
                .title("Task without Assignee")
                .description("This task has no assignee")
                .status(Task.TaskStatus.TODO)
                .priority(Task.TaskPriority.MEDIUM)
                .creator(user1)
                .assignee(null)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        taskHighPriority = Task.builder()
                .id(3L)
                .title("High Priority Task")
                .description("Important task")
                .status(Task.TaskStatus.IN_PROGRESS)
                .priority(Task.TaskPriority.HIGH)
                .creator(user2)
                .assignee(user1)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        taskLowPriority = Task.builder()
                .id(4L)
                .title("Low Priority Task")
                .description("Not urgent")
                .status(Task.TaskStatus.DONE)
                .priority(Task.TaskPriority.LOW)
                .creator(user2)
                .assignee(user2)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        taskTodo = Task.builder()
                .id(5L)
                .title("Todo Task")
                .description("Task to do")
                .status(Task.TaskStatus.TODO)
                .priority(Task.TaskPriority.MEDIUM)
                .creator(user1)
                .assignee(null)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        taskInProgress = Task.builder()
                .id(6L)
                .title("In Progress Task")
                .description("Currently working on this")
                .status(Task.TaskStatus.IN_PROGRESS)
                .priority(Task.TaskPriority.MEDIUM)
                .creator(user1)
                .assignee(user1)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
    }

    @Test
    void getAllTasksWithFilters_NoFilters_ReturnsAllTasks() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority, taskLowPriority, taskTodo, taskInProgress);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);
        when(commentRepository.countByTaskId(2L)).thenReturn(0L);
        when(commentRepository.countByTaskId(3L)).thenReturn(0L);
        when(commentRepository.countByTaskId(4L)).thenReturn(0L);
        when(commentRepository.countByTaskId(5L)).thenReturn(0L);
        when(commentRepository.countByTaskId(6L)).thenReturn(0L);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, null, null);

        // Assert
        assertThat(result).hasSize(6);
        assertThat(result.stream().map(TaskResponse::getId)).containsExactlyInAnyOrder(1L, 2L, 3L, 4L, 5L, 6L);
    }

    @Test
    void getAllTasksWithFilters_FilterByAssignee_ReturnsOnlyTasksWithSpecificAssignee() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority, taskLowPriority, taskTodo, taskInProgress);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);
        when(commentRepository.countByTaskId(4L)).thenReturn(0L);

        // Act - Filter by user2 as assignee
        List<TaskResponse> result = taskService.getAllTasksWithFilters(2L, null, null, null, null);

        // Assert - Should return taskWithAssignee and taskLowPriority (both assigned to user2)
        assertThat(result).hasSize(2);
        assertThat(result.stream().map(TaskResponse::getId)).containsExactlyInAnyOrder(1L, 4L);
    }

    @Test
    void getAllTasksWithFilters_FilterByAssignee_ExcludesTasksWithoutAssignee() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskTodo);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);

        // Act - Filter by user2 as assignee
        List<TaskResponse> result = taskService.getAllTasksWithFilters(2L, null, null, null, null);

        // Assert - Should only return taskWithAssignee, excluding tasks without assignee
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getId()).isEqualTo(1L);
    }

    @Test
    void getAllTasksWithFilters_FilterByPriority_ReturnsOnlyHighPriorityTasks() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority, taskLowPriority);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);
        when(commentRepository.countByTaskId(3L)).thenReturn(0L);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, "HIGH", null, null, null);

        // Assert - Should return taskWithAssignee and taskHighPriority (both HIGH priority)
        assertThat(result).hasSize(2);
        assertThat(result.stream().map(TaskResponse::getId)).containsExactlyInAnyOrder(1L, 3L);
    }

    @Test
    void getAllTasksWithFilters_FilterByStatus_ReturnsOnlyTodoTasks() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority, taskTodo);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);
        when(commentRepository.countByTaskId(2L)).thenReturn(0L);
        when(commentRepository.countByTaskId(5L)).thenReturn(0L);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, "TODO", null, null);

        // Assert - Should return tasks with TODO status
        assertThat(result).hasSize(3);
        assertThat(result.stream().map(TaskResponse::getId)).containsExactlyInAnyOrder(1L, 2L, 5L);
    }

    @Test
    void getAllTasksWithFilters_FilterByCreator_ReturnsOnlyTasksFromSpecificCreator() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority, taskLowPriority);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);
        when(commentRepository.countByTaskId(2L)).thenReturn(0L);

        // Act - Filter by user1 as creator
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, null, 1L);

        // Assert - Should return taskWithAssignee and taskWithoutAssignee (both created by user1)
        assertThat(result).hasSize(2);
        assertThat(result.stream().map(TaskResponse::getId)).containsExactlyInAnyOrder(1L, 2L);
    }

    @Test
    void getAllTasksWithFilters_SearchInTitle_ReturnsMatchingTasks() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(3L)).thenReturn(0L);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, "High Priority", null);

        // Assert - Should return only taskHighPriority
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getId()).isEqualTo(3L);
    }

    @Test
    void getAllTasksWithFilters_SearchInDescription_ReturnsMatchingTasks() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(3L)).thenReturn(0L);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, "Important", null);

        // Assert - Should return only taskHighPriority (description contains "Important")
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getId()).isEqualTo(3L);
    }

    @Test
    void getAllTasksWithFilters_CombinedFilters_ReturnsCorrectResults() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee, taskHighPriority, taskLowPriority, taskInProgress);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(6L)).thenReturn(0L);

        // Act - Filter by assignee=user1 AND priority=MEDIUM
        List<TaskResponse> result = taskService.getAllTasksWithFilters(1L, "MEDIUM", null, null, null);

        // Assert - Should return only taskInProgress (assigned to user1 AND MEDIUM priority)
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getId()).isEqualTo(6L);
    }

    @Test
    void getAllTasksWithFilters_InvalidPriority_ReturnsNoResults() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee);
        when(taskRepository.findAll()).thenReturn(allTasks);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, "INVALID_PRIORITY", null, null, null);

        // Assert - Should return empty list due to invalid priority
        assertThat(result).isEmpty();
    }

    @Test
    void getAllTasksWithFilters_InvalidStatus_ReturnsNoResults() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee);
        when(taskRepository.findAll()).thenReturn(allTasks);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, "INVALID_STATUS", null, null);

        // Assert - Should return empty list due to invalid status
        assertThat(result).isEmpty();
    }

    @Test
    void getAllTasksWithFilters_EmptySearch_ReturnsNoResults() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee);
        when(taskRepository.findAll()).thenReturn(allTasks);

        // Act
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, "NonExistentSearchTerm", null);

        // Assert - Should return empty list as no tasks match the search term
        assertThat(result).isEmpty();
    }

    @Test
    void getAllTasksWithFilters_CaseInsensitiveSearch_ReturnsMatchingTasks() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskHighPriority);
        when(taskRepository.findAll()).thenReturn(allTasks);
        when(commentRepository.countByTaskId(3L)).thenReturn(0L);

        // Act - Search with different case
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, "high priority", null);

        // Assert - Should return taskHighPriority (case insensitive match)
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getId()).isEqualTo(3L);
    }

    @Test
    void getAllTasksWithFilters_WhitespaceSearch_HandlesCorrectly() {
        // Arrange
        List<Task> allTasks = Arrays.asList(taskWithAssignee, taskWithoutAssignee);
        when(taskRepository.findAll()).thenReturn(allTasks);

        // Act - Search with only whitespace
        List<TaskResponse> result = taskService.getAllTasksWithFilters(null, null, null, "   ", null);

        // Assert - Should return all tasks as whitespace search is ignored
        assertThat(result).hasSize(2);
    }
}