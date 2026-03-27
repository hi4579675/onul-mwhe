package com.onulmwhe.route.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record PlanItem(
    @JsonProperty("place_id")
    String placeId,

    @JsonProperty("slot")
    RouteGenerateRequest.TimeSlot slot,

    @JsonProperty("order")
    int order,

    @JsonProperty("reason")
    String reason,

    @JsonProperty("confidence")
    double confidence,

    @JsonProperty("ambience_tag")
    AmbienceTag ambienceTag
) {
    public enum AmbienceTag {
        quiet, lively, cozy, work_friendly, unknown
    }
}
