package com.onulmwhe.route.repository;

import com.onulmwhe.route.entity.FavoritePlace;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FavoritePlaceRepository extends JpaRepository<FavoritePlace, UUID> {
    boolean existsByUserIdAndPlaceId(String userId, String placeId);

    Optional<FavoritePlace> findFirstByUserIdAndPlaceIdOrderByCreatedAtDesc(String userId, String placeId);

    List<FavoritePlace> findByUserIdOrderByCreatedAtDesc(String userId);

    void deleteByUserIdAndPlaceId(String userId, String placeId);
}
