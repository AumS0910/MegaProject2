package com.brochure.service;

import com.brochure.dto.AuthResponse;
import com.brochure.dto.LoginRequest;
import com.brochure.dto.SignupRequest;
import com.brochure.model.User;
import com.brochure.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtService jwtService;

    public AuthResponse signup(SignupRequest request) {
        // Check if user already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        // Create new user
        User user = new User();
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        // Save user
        user = userRepository.save(user);

        // Generate JWT token
        String token = jwtService.generateToken(user.getEmail());

        // Return response
        return new AuthResponse(
            token,
            user.getId().toString(),
            user.getFirstName() + " " + user.getLastName(),
            user.getEmail()
        );
    }

    public AuthResponse login(LoginRequest request) {
        // Find user by email
        User user = userRepository.findByEmail(request.getEmail())
            .orElseThrow(() -> new RuntimeException("User not found"));

        // Verify password
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid password");
        }

        // Generate JWT token
        String token = jwtService.generateToken(user.getEmail());

        // Return response
        return new AuthResponse(
            token,
            user.getId().toString(),
            user.getFirstName() + " " + user.getLastName(),
            user.getEmail()
        );
    }
}
