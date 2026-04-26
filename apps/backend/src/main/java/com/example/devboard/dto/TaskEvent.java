package com.example.devboard.dto;

import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

@Getter
@Builder
public class TaskEvent {
    private String eventType;
    private Long taskId;
    private Instant timestamp;
    private Long userId;
}
