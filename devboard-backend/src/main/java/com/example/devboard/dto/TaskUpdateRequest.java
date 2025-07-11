package com.example.devboard.dto;

import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskUpdateRequest {
    
    @Size(max = 255, message = "Title must be at most 255 characters")
    private String title;
    
    @Size(max = 1000, message = "Description must be at most 1000 characters")
    private String description;
    
    private String status;
    
    private String priority;
    
    private Long assigneeId;
}