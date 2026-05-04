package com.example.devboard.eventservice.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Entity
@Table(
        name = "task_event_messages",
        uniqueConstraints = @UniqueConstraint(
                name = "uq_task_event_messages_kafka_position",
                columnNames = {"topic", "partition_id", "message_offset"}
        )
)
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class TaskEventMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String topic;

    @Column(name = "partition_id", nullable = false)
    private Integer partitionId;

    @Column(name = "message_offset", nullable = false)
    private Long messageOffset;

    @Column(name = "message_key")
    private String messageKey;

    @Column(name = "event_type")
    private String eventType;

    @Column(name = "task_id")
    private Long taskId;

    @Column(name = "event_timestamp")
    private Instant eventTimestamp;

    @Column(name = "user_id")
    private Long userId;

    @Lob
    @Column(nullable = false, columnDefinition = "CLOB")
    private String payload;

    @Column(name = "received_at", nullable = false)
    private Instant receivedAt;
}
