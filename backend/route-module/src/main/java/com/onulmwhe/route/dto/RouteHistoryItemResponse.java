package com.onulmwhe.route.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;
import java.util.UUID;

public record RouteHistoryItemResponse(
    @JsonProperty("id")
    UUID id,

    @JsonProperty("user_id")
    String userId,

    @JsonProperty("region")
    String region,

    @JsonProperty("response")
    RouteGenerateResponse response,

    @JsonProperty("created_at")
    OffsetDateTime createdAt
) {}
