package com.example.devboard.service;

import com.example.devboard.dto.JwtResponse;
import com.example.devboard.dto.LoginRequest;
import com.example.devboard.dto.SignupRequest;
import com.example.devboard.dto.UserProfileUpdateRequest;
import com.example.devboard.entity.User;
import com.example.devboard.repository.UserRepository;
import com.example.devboard.security.JwtUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;
    
    @Transactional
    public User registerUser(SignupRequest signupRequest) {
        // Check if username exists
        if (userRepository.existsByUsername(signupRequest.getUsername())) {
            throw new RuntimeException("Error: Username is already taken!");
        }
        
        // Check if email exists
        if (userRepository.existsByEmail(signupRequest.getEmail())) {
            throw new RuntimeException("Error: Email is already in use!");
        }
        
        // Create new user account
        User user = User.builder()
                .username(signupRequest.getUsername())
                .email(signupRequest.getEmail())
                .password(passwordEncoder.encode(signupRequest.getPassword()))
                .role(User.UserRole.USER)
                .build();
        
        return userRepository.save(user);
    }
    
    public JwtResponse authenticateUser(LoginRequest loginRequest) {
        // Find user by username
        User user = userRepository.findByUsername(loginRequest.getUsername())
                .orElseThrow(() -> new RuntimeException("Error: User not found!"));
        
        // Check password
        if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
            throw new RuntimeException("Error: Invalid password!");
        }
        
        // Generate JWT token
        String jwt = jwtUtils.generateJwtToken(user.getUsername());
        
        return JwtResponse.builder()
                .token(jwt)
                .type("Bearer")
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .avatar(user.getAvatar())
                .role(user.getRole().name())
                .build();
    }
    
    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found with username: " + username));
    }
    
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }
    
    @Transactional
    public User updateUserProfile(Long userId, UserProfileUpdateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        // Check if email is being changed and if it's already taken by another user
        if (request.getEmail() != null && !request.getEmail().equals(user.getEmail())) {
            if (userRepository.existsByEmail(request.getEmail())) {
                throw new RuntimeException("Error: Email is already in use!");
            }
            user.setEmail(request.getEmail());
        }
        
        // Update nickname if provided
        if (request.getNickname() != null) {
            user.setNickname(request.getNickname());
        }
        
        // Update avatar if provided
        if (request.getAvatar() != null) {
            user.setAvatar(request.getAvatar());
        }
        
        return userRepository.save(user);
    }
}