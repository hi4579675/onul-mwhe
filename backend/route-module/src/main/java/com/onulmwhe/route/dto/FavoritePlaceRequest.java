package com.onulmwhe.route.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record FavoritePlaceRequest(
    @JsonProperty("place_id")
    String placeId,
    @JsonProperty("name")
    String name,
    @JsonProperty("category_name")
    String categoryName
) {}
