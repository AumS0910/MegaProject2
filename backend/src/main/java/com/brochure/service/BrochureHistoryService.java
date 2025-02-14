package com.brochure.service;

import com.brochure.model.BrochureHistory;
import com.brochure.repository.BrochureHistoryRepository;
import com.brochure.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional
public class BrochureHistoryService {
    private static final Logger logger = LoggerFactory.getLogger(BrochureHistoryService.class);

    @Autowired
    private BrochureHistoryRepository repository;

    @Autowired
    private UserRepository userRepository;

    public Long getUserIdByEmail(String email) {
        logger.info("Getting user ID for email: {}", email);
        return userRepository.findByEmail(email)
                .orElseThrow(() -> {
                    logger.error("User not found for email: {}", email);
                    return new IllegalStateException("User not found");
                })
                .getId();
    }

    public List<BrochureHistory> getRecentBrochures(Long userId, int limit) {
        try {
            logger.info("Fetching recent brochures for user {} with limit {}", userId, limit);
            List<BrochureHistory> brochures = repository.findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(0, limit));
            logger.info("Found {} brochures", brochures.size());
            return brochures;
        } catch (Exception e) {
            logger.error("Error fetching recent brochures for user {}", userId, e);
            throw new RuntimeException("Failed to fetch recent brochures", e);
        }
    }

    public BrochureHistory saveBrochure(BrochureHistory brochure) {
        try {
            logger.info("Saving brochure: {}", brochure);
            brochure.setCreatedAt(LocalDateTime.now());
            BrochureHistory saved = repository.save(brochure);
            logger.info("Successfully saved brochure with ID: {}", saved.getId());
            return saved;
        } catch (Exception e) {
            logger.error("Error saving brochure", e);
            throw new RuntimeException("Failed to save brochure", e);
        }
    }

    public BrochureHistory createBrochure(Long userId, String hotelName, String location, 
                                        String filePath, String exteriorImage, 
                                        String roomImage, String restaurantImage, 
                                        String prompt) {
        try {
            logger.info("Creating brochure for user {} and hotel {}", userId, hotelName);
            BrochureHistory brochure = new BrochureHistory();
            brochure.setUserId(userId);
            brochure.setHotelName(hotelName);
            brochure.setLocation(location);
            brochure.setFilePath(filePath);
            brochure.setExteriorImage(exteriorImage);
            brochure.setRoomImage(roomImage);
            brochure.setRestaurantImage(restaurantImage);
            brochure.setPrompt(prompt);
            brochure.setCreatedAt(LocalDateTime.now());
            return saveBrochure(brochure);
        } catch (Exception e) {
            logger.error("Error creating brochure for user {} and hotel {}", userId, hotelName, e);
            throw new RuntimeException("Failed to create brochure", e);
        }
    }
}
