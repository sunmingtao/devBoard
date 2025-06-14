package com.example.devboard.service;

import com.example.devboard.dto.CommentCreateRequest;
import com.example.devboard.dto.CommentResponse;
import com.example.devboard.entity.Comment;
import com.example.devboard.entity.Task;
import com.example.devboard.entity.User;
import com.example.devboard.repository.CommentRepository;
import com.example.devboard.repository.TaskRepository;
import com.example.devboard.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CommentServiceTest {

    @Mock
    private CommentRepository commentRepository;

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private CommentService commentService;

    private User testUser;
    private User otherUser;
    private Task testTask;
    private Comment testComment;

    @BeforeEach
    void setUp() {
        // Setup test data
        testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");

        otherUser = new User();
        otherUser.setId(2L);
        otherUser.setUsername("otheruser");
        otherUser.setEmail("other@example.com");

        testTask = new Task();
        testTask.setId(1L);
        testTask.setTitle("Test Task");
        testTask.setDescription("Test Description");
        testTask.setStatus(Task.TaskStatus.TODO);
        testTask.setCreator(testUser);

        testComment = new Comment();
        testComment.setId(1L);
        testComment.setContent("Test comment");
        testComment.setTask(testTask);
        testComment.setUser(testUser);
        testComment.setCreatedAt(LocalDateTime.now());
    }

    @Test
    void createComment_Success() {
        // Arrange
        CommentCreateRequest request = new CommentCreateRequest();
        request.setContent("New comment");

        when(taskRepository.findById(1L)).thenReturn(Optional.of(testTask));
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(commentRepository.save(any(Comment.class))).thenAnswer(invocation -> {
            Comment comment = invocation.getArgument(0);
            comment.setId(2L);
            comment.setCreatedAt(LocalDateTime.now());
            return comment;
        });

        // Act
        CommentResponse response = commentService.createComment(1L, 1L, request);

        // Assert
        assertThat(response).isNotNull();
        assertThat(response.getContent()).isEqualTo("New comment");
        assertThat(response.getUser().getUsername()).isEqualTo("testuser");
        assertThat(response.getId()).isEqualTo(2L);
        
        verify(commentRepository).save(any(Comment.class));
    }

    @Test
    void createComment_TaskNotFound_ThrowsException() {
        // Arrange
        CommentCreateRequest request = new CommentCreateRequest();
        request.setContent("New comment");

        when(taskRepository.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> commentService.createComment(999L, 1L, request))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Task not found");
    }

    @Test
    void createComment_UserNotFound_ThrowsException() {
        // Arrange
        CommentCreateRequest request = new CommentCreateRequest();
        request.setContent("New comment");

        when(taskRepository.findById(1L)).thenReturn(Optional.of(testTask));
        when(userRepository.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> commentService.createComment(1L, 999L, request))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("User not found");
    }

    @Test
    void getCommentsByTaskId_Success() {
        // Arrange
        Comment comment2 = new Comment();
        comment2.setId(2L);
        comment2.setContent("Second comment");
        comment2.setTask(testTask);
        comment2.setUser(otherUser);
        comment2.setCreatedAt(LocalDateTime.now());

        List<Comment> comments = Arrays.asList(testComment, comment2);
        when(commentRepository.findByTaskIdOrderByCreatedAtDesc(1L)).thenReturn(comments);

        // Act
        List<CommentResponse> responses = commentService.getCommentsByTaskId(1L);

        // Assert
        assertThat(responses).hasSize(2);
        assertThat(responses.get(0).getContent()).isEqualTo("Test comment");
        assertThat(responses.get(0).getUser().getUsername()).isEqualTo("testuser");
        assertThat(responses.get(1).getContent()).isEqualTo("Second comment");
        assertThat(responses.get(1).getUser().getUsername()).isEqualTo("otheruser");
    }

    @Test
    void getCommentsByTaskId_EmptyList() {
        // Arrange
        when(commentRepository.findByTaskIdOrderByCreatedAtDesc(1L)).thenReturn(Arrays.asList());

        // Act
        List<CommentResponse> responses = commentService.getCommentsByTaskId(1L);

        // Assert
        assertThat(responses).isEmpty();
    }

    @Test
    void deleteComment_ByCommentOwner_Success() {
        // Arrange
        when(commentRepository.findById(1L)).thenReturn(Optional.of(testComment));
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));

        // Act
        commentService.deleteComment(1L, 1L);

        // Assert
        verify(commentRepository).delete(testComment);
    }

    @Test
    void deleteComment_ByAdmin_Success() {
        // Arrange
        testUser.setRole(User.UserRole.ADMIN); // Make testUser an admin
        testComment.setUser(otherUser); // Comment by other user
        when(commentRepository.findById(1L)).thenReturn(Optional.of(testComment));
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));

        // Act
        commentService.deleteComment(1L, 1L); // Admin deleting comment

        // Assert
        verify(commentRepository).delete(testComment);
    }

    @Test
    void deleteComment_NotFound_ThrowsException() {
        // Arrange
        when(commentRepository.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> commentService.deleteComment(999L, 1L))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Comment not found");
    }

    @Test
    void deleteComment_Unauthorized_ThrowsException() {
        // Arrange
        testComment.setUser(otherUser); // Comment by other user
        when(commentRepository.findById(1L)).thenReturn(Optional.of(testComment));
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser)); // Regular user, not admin

        // Act & Assert
        assertThatThrownBy(() -> commentService.deleteComment(1L, 1L))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("permission to delete");
    }

    @Test
    void getCommentCountByTaskId_Success() {
        // Arrange
        when(commentRepository.countByTaskId(1L)).thenReturn(5L);

        // Act
        Long count = commentService.getCommentCountByTaskId(1L);

        // Assert
        assertThat(count).isEqualTo(5L);
    }

    @Test
    void getCommentCountByTaskId_NoComments() {
        // Arrange
        when(commentRepository.countByTaskId(1L)).thenReturn(0L);

        // Act
        Long count = commentService.getCommentCountByTaskId(1L);

        // Assert
        assertThat(count).isEqualTo(0L);
    }
}