package com.example.devboard.service;

import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
@Order(2) // Run after DatabaseMigrationService
public class DataInitializer implements CommandLineRunner {
    
    private final TaskRepository taskRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    @Override
    public void run(String... args) {
        // Initialize users first
        if (userRepository.count() == 0) {
            log.info("Initializing sample user data...");
            
            User adminUser = User.builder()
                .username("admin")
                .email("admin@devboard.com")
                .password(passwordEncoder.encode("admin123"))
                .nickname("System Admin")
                .role(User.UserRole.ADMIN)
                .build();
                
            User developerUser = User.builder()
                .username("developer")
                .email("dev@devboard.com")
                .password(passwordEncoder.encode("dev123"))
                .nickname("Lead Developer")
                .role(User.UserRole.USER)
                .build();
                
            userRepository.save(adminUser);
            userRepository.save(developerUser);
            
            log.info("Sample users initialized successfully!");
        }
        
        // Then initialize tasks with creators
        if (taskRepository.count() == 0) {
            log.info("Initializing sample task data...");
            
            User admin = userRepository.findByUsername("admin").get();
            User developer = userRepository.findByUsername("developer").get();
            
            List<Task> sampleTasks = List.of(
                Task.builder()
                    .title("Set up project structure")
                    .description("Initialize Spring Boot and Vue.js projects with proper directory structure")
                    .status(Task.TaskStatus.DONE)
                    .priority(Task.TaskPriority.HIGH)
                    .creator(admin)
                    .build(),
                    
                Task.builder()
                    .title("Configure database")
                    .description("Set up MySQL with Docker and H2 for development environment")
                    .status(Task.TaskStatus.DONE)
                    .priority(Task.TaskPriority.MEDIUM)
                    .creator(admin)
                    .assignee(developer)
                    .build(),
                    
                Task.builder()
                    .title("Implement task CRUD API")
                    .description("Create REST endpoints for task management with full CRUD operations")
                    .status(Task.TaskStatus.DONE)
                    .priority(Task.TaskPriority.HIGH)
                    .creator(developer)
                    .build(),
                    
                Task.builder()
                    .title("Build Vue 3 frontend")
                    .description("Create Vue components for task board UI with router and navigation")
                    .status(Task.TaskStatus.IN_PROGRESS)
                    .priority(Task.TaskPriority.HIGH)
                    .creator(developer)
                    .assignee(developer)
                    .build(),
                    
                Task.builder()
                    .title("Add user authentication")
                    .description("Implement JWT-based authentication system for secure access")
                    .status(Task.TaskStatus.TODO)
                    .priority(Task.TaskPriority.MEDIUM)
                    .creator(admin)
                    .assignee(developer)
                    .build(),
                    
                Task.builder()
                    .title("Create admin dashboard")
                    .description("Build administrative interface for user and task management")
                    .status(Task.TaskStatus.TODO)
                    .priority(Task.TaskPriority.LOW)
                    .creator(admin)
                    .build(),
                    
                Task.builder()
                    .title("Deploy to production")
                    .description("Set up CI/CD pipeline and deploy application to cloud platform")
                    .status(Task.TaskStatus.TODO)
                    .priority(Task.TaskPriority.LOW)
                    .creator(admin)
                    .build(),
                    
                Task.builder()
                    .title("Write unit tests")
                    .description("Add comprehensive test coverage for backend services and controllers")
                    .status(Task.TaskStatus.IN_PROGRESS)
                    .priority(Task.TaskPriority.MEDIUM)
                    .creator(developer)
                    .assignee(developer)
                    .build()
            );
            
            taskRepository.saveAll(sampleTasks);
            log.info("Sample data initialized successfully! Created {} tasks.", sampleTasks.size());
        } else {
            log.info("Database already contains {} tasks. Skipping data initialization.", taskRepository.count());
        }
    }
}