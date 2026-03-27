package com.onulmwhe.route.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import java.util.List;

public record RouteGenerateRequest(
    @JsonProperty("region")
    String region,
    @JsonProperty("timeslots")
    List<TimeSlot> timeslots,
    @JsonProperty("preferred_ambience")
    List<Ambience> preferredAmbience,
    @JsonProperty("food_type")
    List<String> foodType,
    @JsonProperty("budget_level")
    BudgetLevel budgetLevel
) {
        public enum TimeSlot {
            breakfast, lunch, cafe, activity, dinner, dessert
        }
        public enum Ambience {
            quiet, lively, cozy, work_friendly
        }
        public enum BudgetLevel {
            low, normal, high
        }
    }
