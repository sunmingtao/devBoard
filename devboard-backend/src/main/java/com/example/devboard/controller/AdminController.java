package com.example.devboard.controller;

import com.example.devboard.dto.UserSummaryResponse;
import com.example.devboard.service.AdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Admin Management", description = "Admin-only endpoints for user and system management")
@SecurityRequirement(name = "bearer-key")
public class AdminController {
    
    private final AdminService adminService;
    
    @GetMapping("/users")
    @Operation(summary = "Get all users (Admin only)", description = "Retrieve list of all users in the system with statistics")
    @ApiResponse(responseCode = "200", description = "Successfully retrieved user list")
    @ApiResponse(responseCode = "403", description = "Access denied - Admin role required")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<UserSummaryResponse>> getAllUsers(Authentication authentication) {
        log.info("Admin {} requesting all users list", authentication.getName());
        List<UserSummaryResponse> users = adminService.getAllUsers();
        return ResponseEntity.ok(users);
    }
    
    @GetMapping("/dashboard")
    @Operation(summary = "Get admin dashboard data", description = "Retrieve system statistics and metrics for admin dashboard")
    @ApiResponse(responseCode = "200", description = "Successfully retrieved dashboard data")
    @ApiResponse(responseCode = "403", description = "Access denied - Admin role required")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> getDashboardData(Authentication authentication) {
        log.info("Admin {} requesting dashboard data", authentication.getName());
        Map<String, Object> dashboardData = adminService.getDashboardData();
        return ResponseEntity.ok(dashboardData);
    }
    
    @GetMapping("/users/{id}")
    @Operation(summary = "Get user details (Admin only)", description = "Retrieve detailed information about a specific user")
    @ApiResponse(responseCode = "200", description = "Successfully retrieved user details")
    @ApiResponse(responseCode = "404", description = "User not found")
    @ApiResponse(responseCode = "403", description = "Access denied - Admin role required")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<UserSummaryResponse> getUserById(@PathVariable Long id, Authentication authentication) {
        log.info("Admin {} requesting details for user {}", authentication.getName(), id);
        UserSummaryResponse user = adminService.getUserById(id);
        return ResponseEntity.ok(user);
    }
    
    // Placeholder endpoints for future user management features
    
    @PutMapping("/users/{id}/disable")
    @Operation(summary = "Disable user account (Placeholder)", description = "Disable a user account - Not implemented yet")
    @ApiResponse(responseCode = "501", description = "Not implemented yet")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> disableUser(@PathVariable Long id, Authentication authentication) {
        log.info("Admin {} attempted to disable user {} - Feature not implemented", authentication.getName(), id);
        return ResponseEntity.status(501).body(Map.of(
            "message", "User disable functionality not implemented yet",
            "feature", "Coming in future release"
        ));
    }
    
    @PutMapping("/users/{id}/enable")
    @Operation(summary = "Enable user account (Placeholder)", description = "Enable a user account - Not implemented yet")
    @ApiResponse(responseCode = "501", description = "Not implemented yet")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> enableUser(@PathVariable Long id, Authentication authentication) {
        log.info("Admin {} attempted to enable user {} - Feature not implemented", authentication.getName(), id);
        return ResponseEntity.status(501).body(Map.of(
            "message", "User enable functionality not implemented yet",
            "feature", "Coming in future release"
        ));
    }
    
    @PostMapping("/users/{id}/reset-password")
    @Operation(summary = "Reset user password (Placeholder)", description = "Reset a user's password - Not implemented yet")
    @ApiResponse(responseCode = "501", description = "Not implemented yet")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> resetUserPassword(@PathVariable Long id, Authentication authentication) {
        log.info("Admin {} attempted to reset password for user {} - Feature not implemented", authentication.getName(), id);
        return ResponseEntity.status(501).body(Map.of(
            "message", "Password reset functionality not implemented yet",
            "feature", "Coming in future release"
        ));
    }
}