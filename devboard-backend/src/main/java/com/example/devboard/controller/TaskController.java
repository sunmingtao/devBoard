package com.example.devboard.controller;

import com.example.devboard.dto.TaskCreateRequest;
import com.example.devboard.dto.TaskResponse;
import com.example.devboard.dto.TaskUpdateRequest;
import com.example.devboard.dto.TaskDetailResponse;
import com.example.devboard.service.TaskService;
import com.example.devboard.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;

import java.util.List;

@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Task Management", description = "APIs for managing development tasks")
public class TaskController {
    
    private final TaskService taskService;
    
    @GetMapping
    @Operation(summary = "Get all tasks with optional filtering", description = "Retrieve tasks with optional filters")
    @ApiResponse(responseCode = "200", description = "Successfully retrieved filtered tasks")
    public List<TaskResponse> getAllTasks(
            @Parameter(description = "Filter by assignee user ID")
            @RequestParam(required = false) Long assigneeId,
            @Parameter(description = "Filter by task priority (HIGH, MEDIUM, LOW)")
            @RequestParam(required = false) String priority,
            @Parameter(description = "Filter by task status (TODO, IN_PROGRESS, DONE)")
            @RequestParam(required = false) String status,
            @Parameter(description = "Search in task title and description")
            @RequestParam(required = false) String search,
            @Parameter(description = "Filter by creator user ID")
            @RequestParam(required = false) Long creatorId) {
        return taskService.getAllTasksWithFilters(assigneeId, priority, status, search, creatorId);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get task by ID", description = "Retrieve a specific task by its ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Task found"),
        @ApiResponse(responseCode = "404", description = "Task not found")
    })
    public ResponseEntity<TaskResponse> getTaskById(
            @Parameter(description = "ID of the task to retrieve", required = true)
            @PathVariable Long id) {
        try {
            TaskResponse task = taskService.getTaskById(id);
            return ResponseEntity.ok(task);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    @GetMapping("/{id}/detail")
    @Operation(summary = "Get task detail with comments", description = "Retrieve a task with all its comments")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Task detail found"),
        @ApiResponse(responseCode = "404", description = "Task not found")
    })
    public ResponseEntity<TaskDetailResponse> getTaskDetail(
            @Parameter(description = "ID of the task to retrieve", required = true)
            @PathVariable Long id) {
        try {
            TaskDetailResponse taskDetail = taskService.getTaskDetail(id);
            return ResponseEntity.ok(taskDetail);
        } catch (RuntimeException e) {
            log.error("Failed to get task detail {}: {}", id, e.getMessage());
            return ResponseEntity.notFound().build();
        }
    }
    
    @PostMapping
    @Operation(summary = "Create a new task", description = "Create a new task with the provided details")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Task created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid task data")
    })
    public ResponseEntity<TaskResponse> createTask(
            @Parameter(description = "Task details to create", required = true)
            @Valid @RequestBody TaskCreateRequest request,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        TaskResponse createdTask = taskService.createTask(request, userPrincipal.getId());
        return ResponseEntity.status(HttpStatus.CREATED).body(createdTask);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update an existing task", description = "Update a task with new details")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Task updated successfully"),
        @ApiResponse(responseCode = "404", description = "Task not found"),
        @ApiResponse(responseCode = "403", description = "Forbidden - insufficient permissions")
    })
    public ResponseEntity<TaskResponse> updateTask(
            @Parameter(description = "ID of the task to update", required = true)
            @PathVariable Long id,
            @Parameter(description = "Updated task details", required = true)
            @Valid @RequestBody TaskUpdateRequest request,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        try {
            TaskResponse updatedTask = taskService.updateTask(id, request, userPrincipal.getId());
            return ResponseEntity.ok(updatedTask);
        } catch (RuntimeException e) {
            log.error("Failed to update task {}: {}", id, e.getMessage(), e);
            if (e.getMessage().contains("not found")) {
                return ResponseEntity.notFound().build();
            } else if (e.getMessage().contains("permission")) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            return ResponseEntity.badRequest().build();
        }
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a task", description = "Delete a task by its ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "204", description = "Task deleted successfully"),
        @ApiResponse(responseCode = "404", description = "Task not found"),
        @ApiResponse(responseCode = "403", description = "Forbidden - only creator can delete")
    })
    public ResponseEntity<Void> deleteTask(
            @Parameter(description = "ID of the task to delete", required = true)
            @PathVariable Long id,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        try {
            taskService.deleteTask(id, userPrincipal.getId());
            return ResponseEntity.noContent().build();
        } catch (RuntimeException e) {
            log.error("Failed to delete task {}: {}", id, e.getMessage(), e);
            if (e.getMessage().contains("not found")) {
                return ResponseEntity.notFound().build();
            } else if (e.getMessage().contains("creator") || e.getMessage().contains("admin")) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            return ResponseEntity.badRequest().build();
        }
    }
    
    @GetMapping("/status/{status}")
    @Operation(summary = "Get tasks by status", description = "Retrieve all tasks with a specific status")
    @ApiResponse(responseCode = "200", description = "Successfully retrieved tasks")
    public List<TaskResponse> getTasksByStatus(
            @Parameter(description = "Task status to filter by (TODO, IN_PROGRESS, DONE)", required = true)
            @PathVariable String status) {
        return taskService.getTasksByStatus(status);
    }
    
    @GetMapping("/my")
    @Operation(summary = "Get my tasks", description = "Retrieve all tasks where user is creator or assignee")
    @ApiResponse(responseCode = "200", description = "Successfully retrieved user's tasks")
    public List<TaskResponse> getMyTasks(
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        return taskService.getMyTasks(userPrincipal.getId());
    }
}