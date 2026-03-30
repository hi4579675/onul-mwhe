package com.onulmwhe.route.entity;

import jakarta.persistence.*;

import java.time.OffsetDateTime;
import java.util.UUID;

import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
@Entity
@Table(name = "routes", indexes = {
    @Index(name = "idx_routes_user_id", columnList = "user_id"),
    @Index(name = "idx_routes_correlation_id", columnList = "correlation_id")
})
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Route {
    @Id
    private UUID id;
    @Column(name = "user_id", nullable = false, length = 100)
    private String userId;
    @Column(name = "region", nullable = false, length = 100)
    private String region;

    // RouteGenerateResponse 전체 JSON 저장
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "plan_json", nullable = false, columnDefinition = "jsonb")
    private String planJson;
    @Column(name = "fallback_used", nullable = false)
    private boolean fallbackUsed;
    @Column(name = "correlation_id", length = 36)
    private String correlationId;
    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;
    public static Route of(
        String userId,
        String region,
        String planJson,
        boolean fallbackUsed,
        String correlationId
    ) {
        Route r = new Route();
        r.userId = userId;
        r.region = region;
        r.planJson = planJson;
        r.fallbackUsed = fallbackUsed;
        r.correlationId = correlationId;
        return r;
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
