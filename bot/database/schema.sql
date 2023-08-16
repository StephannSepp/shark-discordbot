CREATE TABLE IF NOT EXISTS warns (
  warn_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL, 
  server_id BIGINT NOT NULL,
  moderator_id BIGINT NOT NULL, 
  reason VARCHAR NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS fortune_records (
  user_id BIGINT NOT NULL,
  luck VARCHAR(4) NOT NULL,
  angel VARCHAR(20) NOT NULL,
  lucky_number INTEGER NOT NULL,
  colour VARCHAR(4) NOT NULL,
  draw_date timestamp NOT NULL
);
CREATE TABLE IF NOT EXISTS fortune_statistics (
  item_type VARCHAR NOT NULL,
  item VARCHAR NOT NULL,
  item_count BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS reminder (
  remind_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  server_id BIGINT NOT NULL,
  channel_id BIGINT NOT NULL,
  remind_text VARCHAR NOT NULL,
  remind_at timestamp NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);