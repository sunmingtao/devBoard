package com.example.devboard.controller;

import com.example.devboard.common.ApiResponse;
import com.example.devboard.common.ErrorCode;
import com.example.devboard.dto.MessageResponse;
import com.example.devboard.dto.UserProfileResponse;
import com.example.devboard.dto.UserProfileUpdateRequest;
import com.example.devboard.entity.User;
import com.example.devboard.exception.BusinessException;
import com.example.devboard.security.UserPrincipal;
import com.example.devboard.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
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
    public ApiResponse<UserProfileResponse> getCurrentUserProfile(Authentication authentication) {
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
        User user = userService.findById(userPrincipal.getId())
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND, "User not found"));
        
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
        
        return ApiResponse.success(response);
    }
    
    @PutMapping("/me")
    public ApiResponse<MessageResponse> updateCurrentUserProfile(
            @Valid @RequestBody UserProfileUpdateRequest request,
            Authentication authentication) {
        
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
        userService.updateUserProfile(userPrincipal.getId(), request);
        return ApiResponse.success(new MessageResponse("Profile updated successfully"));
    }
    
    @GetMapping
    public ApiResponse<List<UserProfileResponse>> getAllUsers() {
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
        
        return ApiResponse.success(userResponses);
    }
}