package com.example.devboard.eventservice.dto;

import com.example.devboard.eventservice.entity.TaskEventMessage;

import java.time.Instant;

public record TaskEventMessageResponse(
        Long id,
        String topic,
        Integer partitionId,
        Long messageOffset,
        String messageKey,
        String eventType,
        Long taskId,
        Instant eventTimestamp,
        Long userId,
        String payload,
        Instant receivedAt
) {
    public static TaskEventMessageResponse from(TaskEventMessage message) {
        return new TaskEventMessageResponse(
                message.getId(),
                message.getTopic(),
                message.getPartitionId(),
                message.getMessageOffset(),
                message.getMessageKey(),
                message.getEventType(),
                message.getTaskId(),
                message.getEventTimestamp(),
                message.getUserId(),
                message.getPayload(),
                message.getReceivedAt()
        );
    }
}
