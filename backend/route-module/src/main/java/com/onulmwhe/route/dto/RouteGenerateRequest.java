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
    @JsonProperty("budget_level")
    BudgetLevel budgetLevel,
    @JsonProperty("companion")
    Companion companion,
    @JsonProperty("activity")
    Activity activity,
    @JsonProperty("allergies")
    List<Allergy> allergies,
    @JsonProperty("vegan")
    boolean vegan
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
        public enum Companion {
            ALONE, COUPLE, FRIENDS
        }
        public enum Activity {
            CAFE, ACTIVITY, SHOPPING
        }
        public enum Allergy {
            PEANUT, SHELLFISH, DAIRY, NONE
        }
    }
