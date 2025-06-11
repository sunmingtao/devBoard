package com.example.devboard.controller;

import com.example.devboard.dto.CommentCreateRequest;
import com.example.devboard.dto.CommentResponse;
import com.example.devboard.service.CommentService;
import com.example.devboard.security.UserPrincipal;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
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
    public ResponseEntity<CommentResponse> createComment(
            @PathVariable Long taskId,
            @Valid @RequestBody CommentCreateRequest request,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        
        log.info("User {} creating comment on task {}", userPrincipal.getId(), taskId);
        CommentResponse comment = commentService.createComment(taskId, userPrincipal.getId(), request);
        return ResponseEntity.status(HttpStatus.CREATED).body(comment);
    }
    
    @GetMapping("/tasks/{taskId}/comments")
    public ResponseEntity<List<CommentResponse>> getTaskComments(@PathVariable Long taskId) {
        log.info("Fetching comments for task {}", taskId);
        List<CommentResponse> comments = commentService.getCommentsByTaskId(taskId);
        return ResponseEntity.ok(comments);
    }
    
    @DeleteMapping("/comments/{commentId}")
    public ResponseEntity<Void> deleteComment(
            @PathVariable Long commentId,
            @AuthenticationPrincipal UserPrincipal userPrincipal) {
        
        try {
            log.info("User {} deleting comment {}", userPrincipal.getId(), commentId);
            commentService.deleteComment(commentId, userPrincipal.getId());
            return ResponseEntity.noContent().build();
        } catch (RuntimeException e) {
            log.error("Failed to delete comment {}: {}", commentId, e.getMessage());
            if (e.getMessage().contains("not found")) {
                return ResponseEntity.notFound().build();
            } else if (e.getMessage().contains("permission")) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            return ResponseEntity.badRequest().build();
        }
    }
}