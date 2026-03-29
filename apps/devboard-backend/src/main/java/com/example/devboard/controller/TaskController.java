package com.example.devboard.controller;

import com.example.devboard.common.ApiResponse;
import com.example.devboard.common.ErrorCode;
import com.example.devboard.dto.TaskCreateRequest;
import com.example.devboard.dto.TaskResponse;
import com.example.devboard.dto.TaskUpdateRequest;
import com.example.devboard.dto.TaskDetailResponse;
import com.example.devboard.exception.BusinessException;
import com.example.devboard.service.TaskService;
import com.example.devboard.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
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
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Successfully retrieved filtered tasks")
    public ApiResponse<List<TaskResponse>> getAllTasks(
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
        List<TaskResponse> tasks = taskService.getAllTasksWithFilters(assigneeId, priority, status, search, creatorId);
        return ApiResponse.success(tasks);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get task by ID", description = "Retrieve a specific task by its ID")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Task found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Task not found")
    })
    public ApiResponse<TaskResponse> getTaskById(
            @Parameter(description = "ID of the task to retrieve", required = true)
            @PathVariable Long id) {
        TaskResponse task = taskService.getTaskById(id);
        return ApiResponse.success(task);
    }
    
    @GetMapping("/{id}/detail")
    @Operation(summary = "Get task detail with comments", description = "Retrieve a task with all its comments")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Task detail found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Task not found")
    })
    public ApiResponse<TaskDetailResponse> getTaskDetail(
            @Parameter(description = "ID of the task to retrieve", required = true)
            @PathVariable Long id) {
        TaskDetailResponse taskDetail = taskService.getTaskDetail(id);
        return ApiResponse.success(taskDetail);
    }
    
    @PostMapping
    @Operation(summary = "Create a new task", description = "Create a new task with the provided details")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Task created successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Invalid task data")
    })
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<TaskResponse> createTask(
            @Parameter(description = "Task details to create", required = true)
            @Valid @RequestBody TaskCreateRequest request,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        TaskResponse createdTask = taskService.createTask(request, userPrincipal.getId());
        return ApiResponse.success("Task created successfully", createdTask);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update an existing task", description = "Update a task with new details")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Task updated successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Task not found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Forbidden - insufficient permissions")
    })
    public ApiResponse<TaskResponse> updateTask(
            @Parameter(description = "ID of the task to update", required = true)
            @PathVariable Long id,
            @Parameter(description = "Updated task details", required = true)
            @Valid @RequestBody TaskUpdateRequest request,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        TaskResponse updatedTask = taskService.updateTask(id, request, userPrincipal.getId());
        return ApiResponse.success("Task updated successfully", updatedTask);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a task", description = "Delete a task by its ID (creator or admin only)")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "204", description = "Task deleted successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Task not found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Forbidden - only creator or admin can delete")
    })
    @PreAuthorize("hasRole('ADMIN') or @taskService.isTaskCreator(#id, authentication.name)")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public ApiResponse<?> deleteTask(
            @Parameter(description = "ID of the task to delete", required = true)
            @PathVariable Long id,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        taskService.deleteTask(id, userPrincipal.getId());
        return ApiResponse.success("Task deleted successfully");
    }
    
    @DeleteMapping("/admin/{id}")
    @Operation(summary = "Admin delete any task", description = "Admin can delete any task regardless of creator")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "204", description = "Task deleted successfully by admin"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Task not found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Forbidden - admin access required")
    })
    @PreAuthorize("hasRole('ADMIN')")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public ApiResponse<?> adminDeleteTask(
            @Parameter(description = "ID of the task to delete", required = true)
            @PathVariable Long id) {
        taskService.adminDeleteTask(id);
        return ApiResponse.success("Task deleted successfully by admin");
    }
    
    @GetMapping("/status/{status}")
    @Operation(summary = "Get tasks by status", description = "Retrieve all tasks with a specific status")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Successfully retrieved tasks")
    public ApiResponse<List<TaskResponse>> getTasksByStatus(
            @Parameter(description = "Task status to filter by (TODO, IN_PROGRESS, DONE)", required = true)
            @PathVariable String status) {
        List<TaskResponse> tasks = taskService.getTasksByStatus(status);
        return ApiResponse.success(tasks);
    }
    
    @GetMapping("/my")
    @Operation(summary = "Get my tasks", description = "Retrieve all tasks where user is creator or assignee")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Successfully retrieved user's tasks")
    public ApiResponse<List<TaskResponse>> getMyTasks(
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        List<TaskResponse> tasks = taskService.getMyTasks(userPrincipal.getId());
        return ApiResponse.success(tasks);
    }
}