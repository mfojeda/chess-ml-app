-- V1: Initial schema for chess application
-- Created: 2024-12-13

CREATE TABLE IF NOT EXISTS games (
    game_id SERIAL PRIMARY KEY,
    white_player VARCHAR(100),
    black_player VARCHAR(100),
    white_elo INTEGER,
    black_elo INTEGER,
    result VARCHAR(10) CHECK (result IN ('1-0', '0-1', '1/2-1/2', '*')),
    game_date DATE,
    opening_name VARCHAR(200),
    pgn_moves TEXT NOT NULL,
    source VARCHAR(50) DEFAULT 'lichess',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(game_id) ON DELETE CASCADE,
    move_number INTEGER NOT NULL,
    fen VARCHAR(100) NOT NULL,
    move_played VARCHAR(10) NOT NULL,
    evaluation FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, move_number)
);

CREATE TABLE IF NOT EXISTS model_training_games (
    training_id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(game_id) ON DELETE CASCADE,
    player_username VARCHAR(100),
    is_human_game BOOLEAN DEFAULT TRUE,
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fen ON positions(fen);
CREATE INDEX IF NOT EXISTS idx_game_id ON positions(game_id);
CREATE INDEX IF NOT EXISTS idx_game_date ON games(game_date);
CREATE INDEX IF NOT EXISTS idx_result ON games(result);

-- Comments for documentation
COMMENT ON TABLE games IS 'Stores complete chess games in PGN format';
COMMENT ON TABLE positions IS 'Stores individual positions and moves from games';
COMMENT ON TABLE model_training_games IS 'Tracks which games were used for model training';
