package com.example.devboard.service;

import com.example.devboard.dto.JwtResponse;
import com.example.devboard.dto.LoginRequest;
import com.example.devboard.dto.SignupRequest;
import com.example.devboard.dto.UserProfileUpdateRequest;
import com.example.devboard.entity.User;
import com.example.devboard.entity.User.UserRole;
import com.example.devboard.exception.BusinessException;
import com.example.devboard.common.ErrorCode;
import com.example.devboard.repository.UserRepository;
import com.example.devboard.security.JwtUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtUtils jwtUtils;

    @InjectMocks
    private UserService userService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");
        testUser.setPassword("encoded_password");
        testUser.setRole(UserRole.USER);
        testUser.setCreatedAt(LocalDateTime.now());
    }

    @Test
    void registerUser_Success() {
        // Arrange
        SignupRequest signupRequest = new SignupRequest();
        signupRequest.setUsername("newuser");
        signupRequest.setEmail("newuser@example.com");
        signupRequest.setPassword("password123");

        when(userRepository.existsByUsername("newuser")).thenReturn(false);
        when(userRepository.existsByEmail("newuser@example.com")).thenReturn(false);
        when(passwordEncoder.encode("password123")).thenReturn("encoded_password");
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            user.setId(2L);
            user.setCreatedAt(LocalDateTime.now());
            return user;
        });

        // Act
        User result = userService.registerUser(signupRequest);

        // Assert
        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo("newuser");
        assertThat(result.getEmail()).isEqualTo("newuser@example.com");
        assertThat(result.getRole()).isEqualTo(UserRole.USER);
        
        verify(userRepository).save(any(User.class));
        verify(passwordEncoder).encode("password123");
    }

    @Test
    void authenticateUser_Success() {
        // Arrange
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("testuser");
        loginRequest.setPassword("password123");

        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(passwordEncoder.matches("password123", "encoded_password")).thenReturn(true);
        when(jwtUtils.generateJwtToken("testuser")).thenReturn("jwt_token_123");

        // Act
        JwtResponse response = userService.authenticateUser(loginRequest);

        // Assert
        assertThat(response).isNotNull();
        assertThat(response.getToken()).isEqualTo("jwt_token_123");
        assertThat(response.getUsername()).isEqualTo("testuser");
        assertThat(response.getEmail()).isEqualTo("test@example.com");
        assertThat(response.getRole()).isEqualTo("USER");
        assertThat(response.getId()).isEqualTo(1L);
        assertThat(response.getType()).isEqualTo("Bearer");
    }

    @Test
    void authenticateUser_InvalidPassword_ThrowsException() {
        // Arrange
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("testuser");
        loginRequest.setPassword("wrongpassword");

        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(passwordEncoder.matches("wrongpassword", "encoded_password")).thenReturn(false);

        // Act & Assert
        assertThatThrownBy(() -> userService.authenticateUser(loginRequest))
                .isInstanceOf(BusinessException.class)
                .hasFieldOrPropertyWithValue("code", ErrorCode.INVALID_CREDENTIALS.getCode());
        
        verify(jwtUtils, never()).generateJwtToken(anyString());
    }

    @Test
    void findById_Success() {
        // Arrange
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));

        // Act
        Optional<User> result = userService.findById(1L);

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(1L);
    }

    @Test
    void findById_NotFound_ReturnsEmpty() {
        // Arrange
        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // Act
        Optional<User> result = userService.findById(999L);

        // Assert
        assertThat(result).isEmpty();
    }

    @Test
    void updateUserProfile_Success() {
        // Arrange
        UserProfileUpdateRequest updateRequest = new UserProfileUpdateRequest();
        updateRequest.setEmail("newemail@example.com");
        updateRequest.setNickname("newnickname");
        updateRequest.setAvatar("http://example.com/avatar.jpg");

        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(userRepository.existsByEmail("newemail@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> invocation.getArgument(0));

        // Act
        User result = userService.updateUserProfile(1L, updateRequest);

        // Assert
        assertThat(result).isNotNull();
        assertThat(result.getEmail()).isEqualTo("newemail@example.com");
        assertThat(result.getNickname()).isEqualTo("newnickname");
        assertThat(result.getAvatar()).isEqualTo("http://example.com/avatar.jpg");
        
        verify(userRepository).save(testUser);
    }

    @Test
    void updateUserProfile_EmailAlreadyExists_ThrowsException() {
        // Arrange
        UserProfileUpdateRequest updateRequest = new UserProfileUpdateRequest();
        updateRequest.setEmail("existing@example.com");

        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(userRepository.existsByEmail("existing@example.com")).thenReturn(true);

        // Act & Assert
        assertThatThrownBy(() -> userService.updateUserProfile(1L, updateRequest))
                .isInstanceOf(BusinessException.class)
                .hasFieldOrPropertyWithValue("code", ErrorCode.USER_ALREADY_EXISTS.getCode());
    }

    @Test
    void getAllUsers_Success() {
        // Arrange
        User user2 = new User();
        user2.setId(2L);
        user2.setUsername("user2");
        user2.setEmail("user2@example.com");
        user2.setRole(UserRole.USER);

        List<User> users = Arrays.asList(testUser, user2);
        when(userRepository.findAll()).thenReturn(users);

        // Act
        List<User> result = userService.getAllUsers();

        // Assert
        assertThat(result).hasSize(2);
        assertThat(result.get(0).getUsername()).isEqualTo("testuser");
        assertThat(result.get(1).getUsername()).isEqualTo("user2");
    }
}