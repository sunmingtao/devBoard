package com.example.devboard.controller;

import com.example.devboard.common.ApiResponse;
import com.example.devboard.dto.CommentCreateRequest;
import com.example.devboard.dto.CommentResponse;
import com.example.devboard.service.CommentService;
import com.example.devboard.security.UserPrincipal;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@Slf4j
public class CommentController {
    
    private final CommentService commentService;
    
    @PostMapping("/tasks/{taskId}/comments")
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<CommentResponse> createComment(
            @PathVariable Long taskId,
            @Valid @RequestBody CommentCreateRequest request,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        
        log.info("User {} creating comment on task {}", userPrincipal.getId(), taskId);
        CommentResponse comment = commentService.createComment(taskId, userPrincipal.getId(), request);
        return ApiResponse.success("Comment created successfully", comment);
    }
    
    @GetMapping("/tasks/{taskId}/comments")
    public ApiResponse<List<CommentResponse>> getTaskComments(@PathVariable Long taskId) {
        log.info("Fetching comments for task {}", taskId);
        List<CommentResponse> comments = commentService.getCommentsByTaskId(taskId);
        return ApiResponse.success(comments);
    }
    
    @DeleteMapping("/comments/{commentId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public ApiResponse<?> deleteComment(
            @PathVariable Long commentId,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        
        log.info("User {} deleting comment {}", userPrincipal.getId(), commentId);
        commentService.deleteComment(commentId, userPrincipal.getId());
        return ApiResponse.success("Comment deleted successfully");
    }
}