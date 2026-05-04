package com.example.devboard.eventservice.listener;

import com.example.devboard.eventservice.service.TaskEventPersistenceService;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class TaskEventListenerTest {

    @Test
    void persistsConsumedRecordBeforeListenerReturns() {
        CapturingPersistenceService persistenceService = new CapturingPersistenceService();
        TaskEventListener listener = new TaskEventListener(persistenceService);
        ConsumerRecord<String, String> record = new ConsumerRecord<>(
                "devboard.tasks",
                0,
                42L,
                "9",
                "{\"eventType\":\"TASK_CREATED\",\"taskId\":9,\"userId\":3}"
        );

        listener.consumeTaskEvents(record);

        assertThat(persistenceService.persistedRecord).isSameAs(record);
    }

    private static class CapturingPersistenceService extends TaskEventPersistenceService {
        private ConsumerRecord<String, String> persistedRecord;

        private CapturingPersistenceService() {
            super(null, null);
        }

        @Override
        public boolean persist(ConsumerRecord<String, String> record) {
            this.persistedRecord = record;
            return true;
        }
    }
}
