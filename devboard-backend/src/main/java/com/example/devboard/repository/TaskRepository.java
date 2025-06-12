package com.example.devboard.repository;

import com.example.devboard.entity.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TaskRepository extends JpaRepository<Task, Long> {
    
    List<Task> findByStatus(Task.TaskStatus status);
    
    List<Task> findByPriority(Task.TaskPriority priority);
    
    List<Task> findByStatusOrderByPriorityDescCreatedAtDesc(Task.TaskStatus status);
    
    // Admin service methods
    long countByStatus(Task.TaskStatus status);
    long countByPriority(Task.TaskPriority priority);
    long countByCreatorId(Long creatorId);
    long countByAssigneeId(Long assigneeId);
    long countByAssigneeIsNull();
}