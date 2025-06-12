package com.example.devboard.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class UserSummaryResponse {
    private Long id;
    private String username;
    private String email;
    private String nickname;
    private String avatar;
    private String role;
    private LocalDateTime createdAt;
    private LocalDateTime lastActiveAt;
    
    // Statistics
    private Long tasksCreated;
    private Long tasksAssigned;
    private Long commentsCount;
    private Boolean isActive;
}