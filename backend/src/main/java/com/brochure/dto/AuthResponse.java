package com.brochure.dto;

import lombok.Data;

@Data
public class AuthResponse {
    private String accessToken;
    private String userId;
    private String name;
    private String email;

    public AuthResponse(String accessToken, String userId, String name, String email) {
        this.accessToken = accessToken;
        this.userId = userId;
        this.name = name;
        this.email = email;
    }
}
