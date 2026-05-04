package com.example.devboard.eventservice.repository;

import com.example.devboard.eventservice.entity.TaskEventMessage;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TaskEventMessageRepository extends JpaRepository<TaskEventMessage, Long> {

    boolean existsByTopicAndPartitionIdAndMessageOffset(String topic, Integer partitionId, Long messageOffset);

    List<TaskEventMessage> findAllBy(Pageable pageable);
}
