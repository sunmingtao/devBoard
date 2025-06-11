package com.example.devboard.repository;

import com.example.devboard.entity.Comment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {
    
    List<Comment> findByTaskIdOrderByCreatedAtDesc(Long taskId);
    
    List<Comment> findByUserIdOrderByCreatedAtDesc(Long userId);
    
    Long countByTaskId(Long taskId);
}