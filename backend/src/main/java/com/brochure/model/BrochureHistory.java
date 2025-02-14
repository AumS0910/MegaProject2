package com.brochure.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "brochure_history")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class BrochureHistory {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(columnDefinition = "UUID")
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "hotel_name", nullable = false)
    private String hotelName;

    @Column(name = "location", nullable = false)
    private String location;

    @Column(name = "file_path", nullable = false)
    private String filePath;

    @Column(name = "exterior_image")
    private String exteriorImage;

    @Column(name = "room_image")
    private String roomImage;

    @Column(name = "restaurant_image")
    private String restaurantImage;

    @Column(name = "prompt")
    private String prompt;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
}
