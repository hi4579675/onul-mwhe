CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE routes (
                      id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                      user_id         VARCHAR(100) NOT NULL,
                      region          VARCHAR(100) NOT NULL,
                      plan_json       JSONB        NOT NULL,
                      fallback_used   BOOLEAN      NOT NULL DEFAULT FALSE,
                      correlation_id  VARCHAR(36),
                      created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX idx_routes_user_id_created_at_desc
  ON routes(user_id, created_at DESC);
