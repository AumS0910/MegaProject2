package com.brochure.controller;

import com.brochure.model.BrochureHistory;
import com.brochure.service.BrochureHistoryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/brochures")
@CrossOrigin(origins = "http://localhost:3000", allowCredentials = "true")
public class BrochureHistoryController {
    private static final Logger logger = LoggerFactory.getLogger(BrochureHistoryController.class);
    
    @Autowired
    private BrochureHistoryService service;

    @GetMapping("/recent")
    public ResponseEntity<List<BrochureHistory>> getRecentBrochures(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestParam(defaultValue = "10") int limit) {
        try {
            logger.info("Fetching recent brochures with limit: {}", limit);
            Long userId = getUserIdFromUserDetails(userDetails);
            logger.info("User ID: {}", userId);
            List<BrochureHistory> brochures = service.getRecentBrochures(userId, limit);
            logger.info("Found {} brochures", brochures.size());
            return ResponseEntity.ok(brochures);
        } catch (Exception e) {
            logger.error("Error fetching recent brochures", e);
            throw e;
        }
    }

    @PostMapping("/save")
    public ResponseEntity<BrochureHistory> saveBrochure(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestBody BrochureRequest request) {
        try {
            logger.info("Saving brochure for hotel: {}", request.getHotelName());
            Long userId = getUserIdFromUserDetails(userDetails);
            logger.info("User ID: {}", userId);
            BrochureHistory brochure = service.createBrochure(
                userId,
                request.getHotelName(),
                request.getLocation(),
                request.getFilePath(),
                request.getExteriorImage(),
                request.getRoomImage(),
                request.getRestaurantImage(),
                request.getPrompt()
            );
            logger.info("Successfully saved brochure with ID: {}", brochure.getId());
            return ResponseEntity.ok(brochure);
        } catch (Exception e) {
            logger.error("Error saving brochure", e);
            throw e;
        }
    }

    // Helper method to get userId from UserDetails
    private Long getUserIdFromUserDetails(UserDetails userDetails) {
        if (userDetails == null) {
            logger.error("UserDetails is null");
            throw new IllegalStateException("User not authenticated");
        }
        try {
            String username = userDetails.getUsername();
            // Extract user ID from the username (email)
            return service.getUserIdByEmail(username);
        } catch (Exception e) {
            logger.error("Error getting user ID from UserDetails", e);
            throw new IllegalStateException("Could not retrieve user ID", e);
        }
    }
}

// Request class for saving brochure
class BrochureRequest {
    private String hotelName;
    private String location;
    private String filePath;
    private String exteriorImage;
    private String roomImage;
    private String restaurantImage;
    private String prompt;

    // Getters and setters
    public String getHotelName() { return hotelName; }
    public void setHotelName(String hotelName) { this.hotelName = hotelName; }
    
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    
    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) { this.filePath = filePath; }
    
    public String getExteriorImage() { return exteriorImage; }
    public void setExteriorImage(String exteriorImage) { this.exteriorImage = exteriorImage; }
    
    public String getRoomImage() { return roomImage; }
    public void setRoomImage(String roomImage) { this.roomImage = roomImage; }
    
    public String getRestaurantImage() { return restaurantImage; }
    public void setRestaurantImage(String restaurantImage) { this.restaurantImage = restaurantImage; }
    
    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }
}
