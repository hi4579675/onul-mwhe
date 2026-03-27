package com.onulmwhe.route.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record RouteGenerateResponse(
    @JsonProperty("plan")
    List<PlanItem> plan,

    @JsonProperty("fallback_used")
    boolean fallbackUsed,

    @JsonProperty("unknown_count")
    int unknownCount,

    @JsonProperty("correlation_id")
    String correlationId
) {}
