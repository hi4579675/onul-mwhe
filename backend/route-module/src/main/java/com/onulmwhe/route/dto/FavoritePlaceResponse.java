package com.onulmwhe.route.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;
import java.util.UUID;

public record FavoritePlaceResponse(
    @JsonProperty("id")
    UUID id,
    @JsonProperty("user_id")
    String userId,
    @JsonProperty("place_id")
    String placeId,
    @JsonProperty("name")
    String name,
    @JsonProperty("category_name")
    String categoryName,
    @JsonProperty("created_at")
    OffsetDateTime createdAt
) {}
