package com.example.devboard.controller;

import com.example.devboard.common.ApiResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
@Tag(name = "Health Check", description = "API health check endpoints")
public class HelloController {

    private final String appVersion;

    public HelloController(@Value("${devboard.app.version:unknown}") String appVersion) {
        this.appVersion = appVersion;
    }
    
    @GetMapping("/hello")
    @Operation(summary = "Health check endpoint", description = "Returns a simple hello message with API status")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "API is running successfully")
    public ApiResponse<Map<String, String>> hello() {
        Map<String, String> data = new HashMap<>();
        data.put("message", "Hello from DevBoard API!");
        data.put("status", "running");
        data.put("timestamp", java.time.LocalDateTime.now().toString());
        return ApiResponse.success(data);
    }
    
    @GetMapping("/health")
    @Operation(summary = "Simple health check", description = "Returns basic health status for load balancer")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Service is healthy")
    public ApiResponse<String> health() {
        return ApiResponse.success("OK");
    }

    @GetMapping("/version")
    @Operation(summary = "Application version", description = "Returns the deployed backend image tag")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Version information returned")
    public ApiResponse<Map<String, String>> version() {
        Map<String, String> data = new HashMap<>();
        data.put("service", "devboard-backend");
        data.put("version", appVersion);
        return ApiResponse.success(data);
    }
}
