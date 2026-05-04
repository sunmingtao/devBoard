package com.example.devboard.eventservice.repository;

import com.example.devboard.eventservice.entity.TaskEventMessage;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaskEventMessageRepository extends JpaRepository<TaskEventMessage, Long> {

    boolean existsByTopicAndPartitionIdAndMessageOffset(String topic, Integer partitionId, Long messageOffset);
}
