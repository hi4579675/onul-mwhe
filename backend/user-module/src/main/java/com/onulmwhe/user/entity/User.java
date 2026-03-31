package com.onulmwhe.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;


import java.time.OffsetDateTime;

@Entity
@Table(
    name = "users",
    indexes = {
        @Index(name = "idx_users_provider_provider_id", columnList = "provider, provider_id")
    }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 비즈니스 키 — routes.user_id, favorite_places.user_id와 동일한 포맷.
     * "{provider}_{providerId}" 형태로 저장. (예: "kakao_123456789")
     * 두 테이블의 기존 FK 포맷을 맞추기 위해 별도 컬럼으로 저장.
     */
    @Column(name = "user_id", nullable = false, unique = true, length = 100)
    private String userId;

    /** 소문자 프로바이더명. 예: "kakao", "google" */
    @Column(name = "provider", nullable = false, length = 20)
    private String provider;

    /** 프로바이더가 부여한 고유 ID (숫자 혹은 문자열) */
    @Column(name = "provider_id", nullable = false, length = 100)
    private String providerId;

    /** Kakao 사용자가 account_email 스코프를 거부하면 null */
    @Column(name = "email", length = 200)
    private String email;

    @Column(name = "nickname", length = 100)
    private String nickname;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;

    /**
     * 신규 사용자 생성 팩토리.
     * userId는 "{provider}_{providerId}" 포맷으로 자동 조합.
     */
    public static User of(String provider, String providerId, String email, String nickname) {
        User u = new User();
        u.provider   = provider;
        u.providerId = providerId;
        u.userId     = provider + "_" + providerId;
        u.email      = email;
        u.nickname   = nickname;
        return u;
    }

    /**
     * 매 로그인 시 최신 이메일·닉네임으로 갱신.
     * Kakao 닉네임 변경 등을 반영하기 위해 upsert 시 항상 호출.
     */
    public void updateProfile(String email, String nickname) {
        this.email    = email;
        this.nickname = nickname;
        this.updatedAt = OffsetDateTime.now();
    }

    @PrePersist
    void prePersist() {
        OffsetDateTime now = OffsetDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    void preUpdate() {
        this.updatedAt = OffsetDateTime.now();
    }


}
