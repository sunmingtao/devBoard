package com.example.devboard.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
@Tag(name = "Health Check", description = "API health check endpoints")
public class HelloController {
    
    @GetMapping("/hello")
    @Operation(summary = "Health check endpoint", description = "Returns a simple hello message with API status")
    @ApiResponse(responseCode = "200", description = "API is running successfully")
    public Map<String, String> hello() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "Hello from DevBoard API!");
        response.put("status", "running");
        response.put("timestamp", java.time.LocalDateTime.now().toString());
        return response;
    }
}