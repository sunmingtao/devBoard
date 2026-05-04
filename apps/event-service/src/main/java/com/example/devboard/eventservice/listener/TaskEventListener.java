package com.example.devboard.eventservice.listener;

import com.example.devboard.eventservice.service.TaskEventPersistenceService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class TaskEventListener {
    private final TaskEventPersistenceService persistenceService;

    @KafkaListener(topics = "${devboard.kafka.topics.task-events}", groupId = "${spring.kafka.consumer.group-id}")
    public void consumeTaskEvents(ConsumerRecord<String, String> record) {
        boolean persisted = persistenceService.persist(record);
        log.info(
                "Consumed task event from {}-{}@{} persisted={}: {}",
                record.topic(),
                record.partition(),
                record.offset(),
                persisted,
                record.value()
        );
    }
}
