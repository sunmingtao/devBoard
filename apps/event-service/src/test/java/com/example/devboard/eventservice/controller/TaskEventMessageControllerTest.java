package com.example.devboard.eventservice.controller;

import com.example.devboard.eventservice.entity.TaskEventMessage;
import com.example.devboard.eventservice.repository.TaskEventMessageRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.data.domain.Pageable;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(TaskEventMessageController.class)
class TaskEventMessageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private TaskEventMessageRepository repository;

    @Test
    void listsPersistedTaskEvents() throws Exception {
        when(repository.findAllBy(any(Pageable.class))).thenReturn(List.of(
                TaskEventMessage.builder()
                        .id(7L)
                        .topic("devboard.tasks")
                        .partitionId(0)
                        .messageOffset(42L)
                        .messageKey("9")
                        .eventType("TASK_CREATED")
                        .taskId(9L)
                        .eventTimestamp(Instant.parse("2026-05-04T20:26:29.879864818Z"))
                        .userId(3L)
                        .payload("{\"eventType\":\"TASK_CREATED\"}")
                        .receivedAt(Instant.parse("2026-05-04T20:26:30Z"))
                        .build()
        ));

        mockMvc.perform(get("/api/events").param("limit", "20"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(7))
                .andExpect(jsonPath("$[0].topic").value("devboard.tasks"))
                .andExpect(jsonPath("$[0].partitionId").value(0))
                .andExpect(jsonPath("$[0].messageOffset").value(42))
                .andExpect(jsonPath("$[0].eventType").value("TASK_CREATED"))
                .andExpect(jsonPath("$[0].taskId").value(9))
                .andExpect(jsonPath("$[0].userId").value(3))
                .andExpect(jsonPath("$[0].payload").value("{\"eventType\":\"TASK_CREATED\"}"));

        verify(repository).findAllBy(org.mockito.ArgumentMatchers.argThat(pageable -> {
            assertThat(pageable.getPageSize()).isEqualTo(20);
            assertThat(pageable.getSort().getOrderFor("receivedAt")).isNotNull();
            assertThat(pageable.getSort().getOrderFor("receivedAt").isDescending()).isTrue();
            return true;
        }));
    }

    @Test
    void capsRequestedLimit() throws Exception {
        when(repository.findAllBy(any(Pageable.class))).thenReturn(List.of());

        mockMvc.perform(get("/api/events").param("limit", "5000"))
                .andExpect(status().isOk());

        verify(repository).findAllBy(org.mockito.ArgumentMatchers.argThat(pageable -> {
            assertThat(pageable.getPageSize()).isEqualTo(500);
            return true;
        }));
    }
}
