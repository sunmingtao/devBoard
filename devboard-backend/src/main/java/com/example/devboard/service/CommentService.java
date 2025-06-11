package com.example.devboard.service;

import com.example.devboard.dto.CommentCreateRequest;
import com.example.devboard.dto.CommentResponse;
import com.example.devboard.entity.Comment;
import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
import com.example.devboard.repository.CommentRepository;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
@Slf4j
public class CommentService {
    
    private final CommentRepository commentRepository;
    private final TaskRepository taskRepository;
    private final UserRepository userRepository;
    
    public CommentResponse createComment(Long taskId, Long userId, CommentCreateRequest request) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> {
                    log.error("Task not found with id: {}", taskId);
                    return new RuntimeException("Task not found");
                });
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> {
                    log.error("User not found with id: {}", userId);
                    return new RuntimeException("User not found");
                });
        
        Comment comment = Comment.builder()
                .content(request.getContent())
                .task(task)
                .user(user)
                .build();
        
        Comment savedComment = commentRepository.save(comment);
        log.info("User {} created comment on task {}", userId, taskId);
        
        return convertToResponse(savedComment);
    }
    
    public List<CommentResponse> getCommentsByTaskId(Long taskId) {
        return commentRepository.findByTaskIdOrderByCreatedAtDesc(taskId)
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
    
    public void deleteComment(Long commentId, Long userId) {
        Comment comment = commentRepository.findById(commentId)
                .orElseThrow(() -> {
                    log.error("Comment not found with id: {}", commentId);
                    return new RuntimeException("Comment not found");
                });
        
        // Check if user is the comment owner or an admin
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        
        boolean isOwner = comment.getUser().getId().equals(userId);
        boolean isAdmin = user.getRole() == User.UserRole.ADMIN;
        
        if (!isOwner && !isAdmin) {
            log.warn("User {} attempted to delete comment {} without permission", userId, commentId);
            throw new RuntimeException("You don't have permission to delete this comment");
        }
        
        commentRepository.delete(comment);
        log.info("User {} deleted comment {}", userId, commentId);
    }
    
    public Long getCommentCountByTaskId(Long taskId) {
        return commentRepository.countByTaskId(taskId);
    }
    
    private CommentResponse convertToResponse(Comment comment) {
        CommentResponse.UserSummary userSummary = CommentResponse.UserSummary.builder()
                .id(comment.getUser().getId())
                .username(comment.getUser().getUsername())
                .nickname(comment.getUser().getNickname())
                .avatar(comment.getUser().getAvatar())
                .build();
        
        return CommentResponse.builder()
                .id(comment.getId())
                .content(comment.getContent())
                .user(userSummary)
                .createdAt(comment.getCreatedAt())
                .updatedAt(comment.getUpdatedAt())
                .build();
    }
}