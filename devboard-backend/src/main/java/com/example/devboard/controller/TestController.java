package com.example.devboard.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/test")
public class TestController {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @GetMapping("/redis")
    public ResponseEntity<Map<String, Object>> testRedis() {
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Test Redis connection
            String testKey = "test:connection";
            String testValue = "Redis is working! " + System.currentTimeMillis();
            
            // Write to Redis
            redisTemplate.opsForValue().set(testKey, testValue);
            
            // Read from Redis
            Object retrievedValue = redisTemplate.opsForValue().get(testKey);
            
            response.put("success", true);
            response.put("written", testValue);
            response.put("retrieved", retrievedValue);
            response.put("redisHost", System.getenv("REDIS_HOST"));
            response.put("redisPort", System.getenv("REDIS_PORT"));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("error", e.getMessage());
            response.put("redisHost", System.getenv("REDIS_HOST"));
            response.put("redisPort", System.getenv("REDIS_PORT"));
            
            return ResponseEntity.ok(response);
        }
    }
}