package com.example.devboard.common;

import lombok.Getter;

@Getter
public enum ErrorCode {
    SUCCESS(0, "Success"),
    BAD_REQUEST(400, "Bad request"),
    UNAUTHORIZED(401, "Unauthorized"),
    FORBIDDEN(403, "Forbidden"),
    NOT_FOUND(404, "Resource not found"),
    CONFLICT(409, "Resource conflict"),
    VALIDATION_FAILED(422, "Validation failed"),
    INTERNAL_SERVER_ERROR(500, "Internal server error"),
    
    // Business specific errors
    USER_NOT_FOUND(1001, "User not found"),
    USER_ALREADY_EXISTS(1002, "User already exists"),
    INVALID_CREDENTIALS(1003, "Invalid username or password"),
    TOKEN_EXPIRED(1004, "Token has expired"),
    INVALID_TOKEN(1005, "Invalid token"),
    
    TASK_NOT_FOUND(2001, "Task not found"),
    TASK_ACCESS_DENIED(2002, "No permission to access this task"),
    
    COMMENT_NOT_FOUND(3001, "Comment not found");
    
    private final int code;
    private final String message;
    
    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}