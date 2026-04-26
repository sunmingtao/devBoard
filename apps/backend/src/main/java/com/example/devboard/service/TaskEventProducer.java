package com.example.devboard.service;

import com.example.devboard.dto.TaskEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
@RequiredArgsConstructor
@Slf4j
public class TaskEventProducer {

    private final KafkaTemplate<String, TaskEvent> kafkaTemplate;

    @Value("${devboard.kafka.topics.task-events}")
    private String taskEventsTopic;

    public void publishTaskCreatedEvent(Long taskId, Long userId) {
        publishEvent("TASK_CREATED", taskId, userId);
    }

    public void publishTaskUpdatedEvent(Long taskId, Long userId) {
        publishEvent("TASK_UPDATED", taskId, userId);
    }

    private void publishEvent(String eventType, Long taskId, Long userId) {
        TaskEvent event = TaskEvent.builder()
                .eventType(eventType)
                .taskId(taskId)
                .timestamp(Instant.now())
                .userId(userId)
                .build();

        kafkaTemplate.send(taskEventsTopic, String.valueOf(taskId), event)
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        log.error("Failed to publish {} event for task {}", eventType, taskId, ex);
                    } else {
                        log.info("Published {} event for task {} to topic {}", eventType, taskId, taskEventsTopic);
                    }
                });
    }
}
