package com.onulmwhe.route.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Table(
    name = "favorite_places",
    indexes = {
        @Index(name = "idx_favorite_places_user_id", columnList = "user_id"),
        @Index(name = "idx_favorite_places_place_id", columnList = "place_id")
    }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class FavoritePlace {
    @Id
    private UUID id;

    @Column(name = "user_id", nullable = false, length = 100)
    private String userId;

    @Column(name = "place_id", nullable = false, length = 100)
    private String placeId;

    @Column(name = "name", nullable = false, length = 200)
    private String name;

    @Column(name = "category_name", length = 200)
    private String categoryName;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    public static FavoritePlace of(String userId, String placeId, String name, String categoryName) {
        FavoritePlace favoritePlace = new FavoritePlace();
        favoritePlace.userId = userId;
        favoritePlace.placeId = placeId;
        favoritePlace.name = name;
        favoritePlace.categoryName = categoryName;
        return favoritePlace;
    }

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID();
        }
        if (createdAt == null) {
            createdAt = OffsetDateTime.now();
        }
    }
}
