package com.example.devboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskDetailResponse {
    private TaskResponse task;
    private List<CommentResponse> comments;
    
    public static TaskDetailResponse fromTaskResponse(TaskResponse taskResponse, List<CommentResponse> comments) {
        return TaskDetailResponse.builder()
                .task(taskResponse)
                .comments(comments)
                .build();
    }
}