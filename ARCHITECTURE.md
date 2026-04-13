# Chess AI — System Architecture

## Project Goal

A full-stack chess application where:
1. The AI learns from 112,000+ historical Lichess games
2. Players play against the AI in a mobile-first web interface
3. Human games are saved back to the database for future training
4. The model continuously improves with new data

---

## System Components

### 1. Database Layer — PostgreSQL

| Table | Purpose |
|---|---|
| `games` | Stores all chess games (Lichess + human-played) |
| `positions` | Stores individual board states (FEN + move played) |
| `model_training_games` | Tracks which games were used for each training run |

**Scale:** 2,200 games · 112,466 positions

### 2. Data Pipeline — Python + Jupyter

- Downloads PGN files from Lichess Open Database
- Parses game metadata (players, ELO, result, opening)
- Replays each game move-by-move to extract FEN positions
- Loads into PostgreSQL via SQLAlchemy
- ELO filter: only positions from games where white ELO > 1,400

### 3. ML Model — TensorFlow / Keras (V2)

**Input:** 781-element float32 feature vector per board position

```
[  0 – 767 ]  12 binary planes (64 squares × 6 piece types × 2 colors)
[       768 ]  Side to move (1 = White, 0 = Black)
[ 769 – 772 ]  Castling rights (WK, WQ, BK, BQ)
[ 773 – 780 ]  En passant file (one-hot, files a–h)
```

**Architecture:**
```
Input (781)
  → Dense(1024) + BatchNorm + ReLU + Dropout(0.3)
  → Dense(512)  + BatchNorm + ReLU + Dropout(0.3)
  → Dense(256)  + BatchNorm + ReLU + Dropout(0.2)
  → Dense(1841, softmax)   ← 1,841 unique SAN moves
```

**Training:** Early stopping (patience=5) · Adam optimizer · 112,466 positions

**Inference:** Legal move masking via python-chess — model never suggests an illegal move

**Performance:**
- Top-1: 89.05% · Top-3: 93.65% · Top-5: 95.00%
- Fallback rate: 0.0% · Overfitting gap: +0.69pp

### 4. Backend API — Flask

| Endpoint | Method | Description |
|---|---|---|
| `/api/move` | POST | Returns model's best move for a FEN position |
| `/api/game` | POST | Saves a completed game to PostgreSQL |
| `/api/stats` | GET | Returns model metadata and DB counts |

**Stack:** Flask · SQLAlchemy · python-chess · TensorFlow

### 5. Frontend — HTML / CSS / JavaScript

- Mobile-first SVG chess board (scales to any screen width)
- Tap-to-select + tap-to-move with legal move dot indicators
- Animated AI thinking indicator · smooth status transitions
- Player indicator cards with active pulse animation
- Move history in `# White Black` grid layout
- Calls `/api/move` for AI response after each human move
- Saves game on completion via `/api/game`

**Stack:** chess.js (move validation) · vanilla JS · SVG

### 6. Deployment — Capacitor (planned)

The web frontend will be wrapped in a Capacitor native shell to produce:
- Android APK (distributable directly for testing)
- iOS IPA (via TestFlight with Apple Developer account)

The Flask backend will be hosted on a cloud provider (Render/Railway).

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Database | PostgreSQL | 14 |
| ORM | SQLAlchemy | 2.0 |
| Data processing | Python, Pandas, python-chess | 3.11 |
| ML framework | TensorFlow / Keras | 2.20 |
| API | Flask | 3.1 |
| Frontend | JavaScript, chess.js | — |
| Notebooks | JupyterLab | 4.5 |
| Mobile | Capacitor | planned |
| Version control | Git + GitHub | — |

---

## Development Phases

1. ✅ Environment setup
2. ✅ Database schema & ETL pipeline (2,200 games, 112,466 positions)
3. ✅ Exploratory data analysis
4. ✅ ML modeling — V2 (89.05% top-1 accuracy)
5. ✅ Model evaluation (held-out test set, overfitting check, fallback rate)
6. ✅ Flask REST API
7. ✅ Mobile-first frontend
8. ⏳ Capacitor mobile app + cloud deployment
