CREATE TABLE IF NOT EXISTS warns (
  id BIGINT NOT NULL,
  user_id BIGINT NOT NULL, 
  server_id BIGINT NOT NULL,
  moderator_id BIGINT NOT NULL, 
  reason VARCHAR NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS players (
  user_id BIGINT NOT NULL, 
  crystal BIGINT NOT NULL, 
  mana BIGINT NOT NULL, 
  luck INTEGER NOT NULL,
  floor INTEGER NOT NULL, 
  kills BIGINT NOT NULL, 
  dead VARCHAR(1) NOT NULL, 
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, 
  CHECK (
    luck BETWEEN 0 
    AND 255
  )
);
CREATE TABLE IF NOT EXISTS players_skills (
  user_id BIGINT NOT NULL, 
  skill_id VARCHAR(5) NOT NULL, 
  skill_name VARCHAR(20) NOT NULL, 
  combo INTEGER NOT NULL, 
  damage_modifier REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS battle_log (
  user_id BIGINT NOT NULL, 
  target_id BIGINT NOT NULL, 
  dm VARCHAR(1) NOT NULL, 
  user_result VARCHAR(6) NOT NULL, 
  target_result VARCHAR(6) NOT NULL, 
  time_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS boss_fight_stats (
  boss_name VARCHAR(50) NOT NULL,
  wins INTEGER NOT NULL,
  loses INTEGER NOT NULL,
  kills INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS fortune_statistics (
  user_id BIGINT NOT NULL,
  luck VARCHAR(4) NOT NULL,
  angel VARCHAR(20) NOT NULL,
  number INTEGER NOT NULL,
  colour VARCHAR(4) NOT NULL,
  draw_date timestamp NOT NULL
);