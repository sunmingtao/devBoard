package com.example.devboard.security;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {
    
    private static final Logger logger = LoggerFactory.getLogger(JwtAuthenticationEntryPoint.class);
    
    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException authException) throws IOException {
        String requestUrl = request.getRequestURL().toString();
        String method = request.getMethod();
        String userAgent = request.getHeader("User-Agent");
        
        logger.error("Unauthorized access attempt - Method: {}, URL: {}, User-Agent: {}, Error: {}", 
                    method, requestUrl, userAgent, authException.getMessage());
        
        response.setContentType("application/json");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.getOutputStream().println(
            "{ \"error\": \"Unauthorized\", \"message\": \"" + authException.getMessage() + "\" }"
        );
    }
}