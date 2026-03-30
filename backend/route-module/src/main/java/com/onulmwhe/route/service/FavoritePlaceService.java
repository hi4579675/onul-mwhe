package com.onulmwhe.route.service;

import com.onulmwhe.route.dto.FavoritePlaceRequest;
import com.onulmwhe.route.dto.FavoritePlaceResponse;
import com.onulmwhe.route.entity.FavoritePlace;
import com.onulmwhe.route.repository.FavoritePlaceRepository;
import java.util.List;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@AllArgsConstructor
public class FavoritePlaceService {

    private final FavoritePlaceRepository favoritePlaceRepository;

    @Transactional
    public FavoritePlaceResponse create(String userId, FavoritePlaceRequest request) {
        if (!favoritePlaceRepository.existsByUserIdAndPlaceId(userId, request.placeId())) {
            FavoritePlace entity = FavoritePlace.of(
                userId,
                request.placeId(),
                request.name(),
                request.categoryName()
            );
            favoritePlaceRepository.save(entity);
            return toResponse(entity);
        }

        FavoritePlace existing = favoritePlaceRepository
            .findFirstByUserIdAndPlaceIdOrderByCreatedAtDesc(userId, request.placeId())
            .orElseGet(() -> {
                FavoritePlace fallback = FavoritePlace.of(
                    userId,
                    request.placeId(),
                    request.name(),
                    request.categoryName()
                );
                return favoritePlaceRepository.save(fallback);
            });
        return toResponse(existing);
    }

    @Transactional(readOnly = true)
    public List<FavoritePlaceResponse> list(String userId) {
        return favoritePlaceRepository.findByUserIdOrderByCreatedAtDesc(userId)
            .stream()
            .map(this::toResponse)
            .toList();
    }

    @Transactional
    public void delete(String userId, String placeId) {
        favoritePlaceRepository.deleteByUserIdAndPlaceId(userId, placeId);
    }

    private FavoritePlaceResponse toResponse(FavoritePlace row) {
        return new FavoritePlaceResponse(
            row.getId(),
            row.getUserId(),
            row.getPlaceId(),
            row.getName(),
            row.getCategoryName(),
            row.getCreatedAt()
        );
    }
}
