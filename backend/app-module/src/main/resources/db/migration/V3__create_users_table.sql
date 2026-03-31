-- users 테이블 생성
-- user_id는 "{provider}_{providerId}" 포맷 (예: kakao_123456789)
-- routes.user_id, favorite_places.user_id와 동일한 포맷으로 설계되어 FK 정합성 유지
CREATE TABLE users (
                     id          BIGSERIAL    PRIMARY KEY,
                     user_id     VARCHAR(100) NOT NULL,
                     provider    VARCHAR(20)  NOT NULL,
                     provider_id VARCHAR(100) NOT NULL,
                     email       VARCHAR(200),                    -- account_email 스코프 거부 시 NULL
                     nickname    VARCHAR(100),
                     created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                     updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),

                     CONSTRAINT uk_users_user_id            UNIQUE (user_id),
                     CONSTRAINT uk_users_provider_provider  UNIQUE (provider, provider_id)
);

-- JwtAuthenticationFilter에서 user_id 조회 성능 보장
CREATE INDEX idx_users_user_id ON users (user_id);
