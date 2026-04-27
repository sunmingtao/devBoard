package com.example.devboard.eventservice.listener;

import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class TaskEventListener {
    @KafkaListener(topics = "${devboard.kafka.topics.task-events}", groupId = "${spring.kafka.consumer.group-id}")
    public void consumeTaskEvents(String eventPayload) {
        log.info("Consumed task event from topic devboard.tasks: {}", eventPayload);
        
    }
}
