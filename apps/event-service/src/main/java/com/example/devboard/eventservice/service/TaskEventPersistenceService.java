package com.example.devboard.eventservice.service;

import com.example.devboard.eventservice.entity.TaskEventMessage;
import com.example.devboard.eventservice.repository.TaskEventMessageRepository;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;

@Service
@RequiredArgsConstructor
@Slf4j
public class TaskEventPersistenceService {

    private final TaskEventMessageRepository repository;
    private final ObjectMapper objectMapper;

    @Transactional
    public boolean persist(ConsumerRecord<String, String> record) {
        if (repository.existsByTopicAndPartitionIdAndMessageOffset(record.topic(), record.partition(), record.offset())) {
            log.info(
                    "Task event already persisted for {}-{}@{}",
                    record.topic(),
                    record.partition(),
                    record.offset()
            );
            return false;
        }

        TaskEventMessage message = buildMessage(record);

        repository.saveAndFlush(message);
        return true;
    }

    private TaskEventMessage buildMessage(ConsumerRecord<String, String> record) {
        ParsedTaskEvent parsed = parsePayload(record.value());

        return TaskEventMessage.builder()
                .topic(record.topic())
                .partitionId(record.partition())
                .messageOffset(record.offset())
                .messageKey(record.key())
                .eventType(parsed.eventType())
                .taskId(parsed.taskId())
                .eventTimestamp(parsed.eventTimestamp())
                .userId(parsed.userId())
                .payload(record.value())
                .receivedAt(Instant.now())
                .build();
    }

    private ParsedTaskEvent parsePayload(String payload) {
        try {
            JsonNode root = objectMapper.reader()
                    .with(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS)
                    .readTree(payload);
            return new ParsedTaskEvent(
                    textValue(root, "eventType"),
                    longValue(root, "taskId"),
                    instantValue(root, "timestamp"),
                    longValue(root, "userId")
            );
        } catch (Exception ex) {
            log.warn("Unable to parse task event payload; persisting raw payload only", ex);
            return new ParsedTaskEvent(null, null, null, null);
        }
    }

    private String textValue(JsonNode root, String fieldName) {
        JsonNode node = root.get(fieldName);
        return node == null || node.isNull() ? null : node.asText();
    }

    private Long longValue(JsonNode root, String fieldName) {
        JsonNode node = root.get(fieldName);
        return node == null || node.isNull() ? null : node.asLong();
    }

    private Instant instantValue(JsonNode root, String fieldName) {
        JsonNode node = root.get(fieldName);
        if (node == null || node.isNull()) {
            return null;
        }
        if (node.isTextual()) {
            return Instant.parse(node.asText());
        }

        BigDecimal epochSeconds = node.decimalValue();
        long seconds = epochSeconds.longValue();
        int nanos = epochSeconds.subtract(BigDecimal.valueOf(seconds))
                .movePointRight(9)
                .intValue();
        return Instant.ofEpochSecond(seconds, nanos);
    }

    private record ParsedTaskEvent(String eventType, Long taskId, Instant eventTimestamp, Long userId) {
    }
}
