package com.example.devboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserProfileUpdateRequest {
    
    @Email(message = "Please provide a valid email address")
    private String email;
    
    @Size(max = 50, message = "Nickname must be at most 50 characters")
    private String nickname;
    
    @Size(max = 255, message = "Avatar URL must be at most 255 characters")
    private String avatar;
}