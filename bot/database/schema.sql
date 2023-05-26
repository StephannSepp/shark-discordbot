CREATE TABLE IF NOT EXISTS warns (
  id BIGINT NOT NULL,
  user_id BIGINT NOT NULL, 
  server_id BIGINT NOT NULL,
  moderator_id BIGINT NOT NULL, 
  reason VARCHAR NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS fortune_statistics (
  user_id BIGINT NOT NULL,
  luck VARCHAR(4) NOT NULL,
  angel VARCHAR(20) NOT NULL,
  number INTEGER NOT NULL,
  colour VARCHAR(4) NOT NULL,
  draw_date timestamp NOT NULL
);