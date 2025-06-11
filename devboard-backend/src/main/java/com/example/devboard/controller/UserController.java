package com.example.devboard.controller;

import com.example.devboard.dto.MessageResponse;
import com.example.devboard.dto.UserProfileResponse;
import com.example.devboard.dto.UserProfileUpdateRequest;
import com.example.devboard.entity.User;
import com.example.devboard.security.UserPrincipal;
import com.example.devboard.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    
    private final UserService userService;
    
    @GetMapping("/me")
    public ResponseEntity<UserProfileResponse> getCurrentUserProfile(Authentication authentication) {
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
        User user = userService.findById(userPrincipal.getId())
                .orElseThrow(() -> new RuntimeException("User not found"));
        
        UserProfileResponse response = UserProfileResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .avatar(user.getAvatar())
                .role(user.getRole().name())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/me")
    public ResponseEntity<MessageResponse> updateCurrentUserProfile(
            @Valid @RequestBody UserProfileUpdateRequest request,
            Authentication authentication) {
        
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
        
        try {
            userService.updateUserProfile(userPrincipal.getId(), request);
            return ResponseEntity.ok(new MessageResponse("Profile updated successfully"));
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error updating profile: " + e.getMessage()));
        }
    }
    
    @GetMapping
    public ResponseEntity<List<UserProfileResponse>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        
        List<UserProfileResponse> userResponses = users.stream()
                .map(user -> UserProfileResponse.builder()
                        .id(user.getId())
                        .username(user.getUsername())
                        .email(user.getEmail())
                        .nickname(user.getNickname())
                        .avatar(user.getAvatar())
                        .role(user.getRole().name())
                        .createdAt(user.getCreatedAt())
                        .updatedAt(user.getUpdatedAt())
                        .build())
                .collect(Collectors.toList());
        
        return ResponseEntity.ok(userResponses);
    }
}