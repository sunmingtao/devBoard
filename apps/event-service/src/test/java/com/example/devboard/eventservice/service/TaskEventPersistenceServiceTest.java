package com.example.devboard.eventservice.service;

import com.example.devboard.eventservice.entity.TaskEventMessage;
import com.example.devboard.eventservice.repository.TaskEventMessageRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;

import java.time.Instant;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@Import({TaskEventPersistenceService.class, TaskEventPersistenceServiceTest.JsonConfig.class})
class TaskEventPersistenceServiceTest {

    @Autowired
    private TaskEventPersistenceService persistenceService;

    @Autowired
    private TaskEventMessageRepository repository;

    @Test
    void persistsKafkaRecordWithParsedTaskEventFields() {
        ConsumerRecord<String, String> record = new ConsumerRecord<>(
                "devboard.tasks",
                0,
                3L,
                "9",
                "{\"eventType\":\"TASK_CREATED\",\"taskId\":9,\"timestamp\":\"2026-05-04T20:26:29.879864818Z\",\"userId\":3}"
        );

        boolean persisted = persistenceService.persist(record);

        assertThat(persisted).isTrue();

        List<TaskEventMessage> messages = repository.findAll();
        assertThat(messages).hasSize(1);

        TaskEventMessage message = messages.getFirst();
        assertThat(message.getTopic()).isEqualTo("devboard.tasks");
        assertThat(message.getPartitionId()).isZero();
        assertThat(message.getMessageOffset()).isEqualTo(3L);
        assertThat(message.getMessageKey()).isEqualTo("9");
        assertThat(message.getEventType()).isEqualTo("TASK_CREATED");
        assertThat(message.getTaskId()).isEqualTo(9L);
        assertThat(message.getEventTimestamp()).isEqualTo(Instant.parse("2026-05-04T20:26:29.879864818Z"));
        assertThat(message.getUserId()).isEqualTo(3L);
        assertThat(message.getPayload()).contains("\"eventType\":\"TASK_CREATED\"");
        assertThat(message.getReceivedAt()).isNotNull();
    }

    @Test
    void ignoresDuplicateKafkaPosition() {
        ConsumerRecord<String, String> record = new ConsumerRecord<>(
                "devboard.tasks",
                0,
                3L,
                "9",
                "{\"eventType\":\"TASK_CREATED\",\"taskId\":9,\"timestamp\":1777926389.879864818,\"userId\":3}"
        );

        assertThat(persistenceService.persist(record)).isTrue();
        assertThat(persistenceService.persist(record)).isFalse();

        List<TaskEventMessage> messages = repository.findAll();
        assertThat(messages).hasSize(1);
        assertThat(messages.getFirst().getEventTimestamp())
                .isEqualTo(Instant.parse("2026-05-04T20:26:29.879864818Z"));
    }

    @TestConfiguration
    static class JsonConfig {
        @Bean
        ObjectMapper objectMapper() {
            return new ObjectMapper();
        }
    }
}
