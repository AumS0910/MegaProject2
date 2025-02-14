package com.brochure.repository;

import com.brochure.model.BrochureHistory;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface BrochureHistoryRepository extends JpaRepository<BrochureHistory, String> {
    List<BrochureHistory> findByUserIdOrderByCreatedAtDesc(Long userId, Pageable pageable);
}
