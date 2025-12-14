# Chess ML Application - System Architecture

## Project Goal
Build a full-stack chess application where:
1. AI learns from historical chess games
2. Players can play against the AI
3. Human games feed back into training data
4. Model continuously improves

## System Components

### 1. Database Layer (PostgreSQL)
- games table: Store all chess games
- positions table: Store board states and moves
- model_training_games table: Track which games trained the model

### 2. Data Pipeline (Python + Jupyter)
- Parse PGN files from Lichess
- Clean and transform data
- Load into PostgreSQL
- Feature engineering for ML

### 3. ML Model (TensorFlow/Keras)
- Input: Board position (FEN notation)
- Output: Predicted best move
- Architecture: Neural network (to be determined)
- Training: Supervised learning on historical games

### 4. Backend API (Flask)
- POST /api/move - Get AI's move for a position
- POST /api/game - Save completed game
- GET /api/stats - Get model performance stats

### 5. Frontend (HTML/CSS/JavaScript)
- Interactive chess board
- Play against AI
- View game history

## Technology Stack
- Database: PostgreSQL 14
- Data Processing: Python 3.x, Pandas, python-chess
- ML Framework: TensorFlow/Keras
- API: Flask + SQLAlchemy
- Frontend: JavaScript + chess.js library
- Development: Jupyter Notebooks
- Version Control: Git + GitHub

## Development Phases
1. ✅ Environment setup
2. ⏳ Database schema & setup
3. ⏳ Data pipeline
4. ⏳ Model development
5. ⏳ API development
6. ⏳ Frontend development
7. ⏳ Integration & testing
