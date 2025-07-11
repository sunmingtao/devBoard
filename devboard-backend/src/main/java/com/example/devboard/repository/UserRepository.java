package com.example.devboard.repository;

import com.example.devboard.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByUsername(String username);
    
    Optional<User> findByEmail(String email);
    
    boolean existsByUsername(String username);
    
    boolean existsByEmail(String email);
    
    // Migration helper method
    Optional<User> findByRole(User.UserRole role);
    
    // Admin service methods
    long countByRole(User.UserRole role);
}