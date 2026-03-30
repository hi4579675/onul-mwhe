CREATE TABLE favorite_places (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         VARCHAR(100) NOT NULL,
    place_id        VARCHAR(100) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    category_name   VARCHAR(200),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uk_favorite_places_user_place
  ON favorite_places(user_id, place_id);

CREATE INDEX idx_favorite_places_user_id_created_at_desc
  ON favorite_places(user_id, created_at DESC);
