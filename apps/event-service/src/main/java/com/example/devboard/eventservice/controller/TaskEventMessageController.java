package com.example.devboard.eventservice.controller;

import com.example.devboard.eventservice.dto.TaskEventMessageResponse;
import com.example.devboard.eventservice.repository.TaskEventMessageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/events")
@RequiredArgsConstructor
public class TaskEventMessageController {

    private static final int DEFAULT_LIMIT = 100;
    private static final int MAX_LIMIT = 500;

    private final TaskEventMessageRepository repository;

    @GetMapping
    public List<TaskEventMessageResponse> listEvents(
            @RequestParam(defaultValue = "100") int limit
    ) {
        int boundedLimit = Math.max(1, Math.min(limit, MAX_LIMIT));
        PageRequest pageRequest = PageRequest.of(
                0,
                boundedLimit,
                Sort.by(Sort.Direction.DESC, "receivedAt")
        );

        return repository.findAllBy(pageRequest).stream()
                .map(TaskEventMessageResponse::from)
                .toList();
    }
}
