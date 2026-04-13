# CRISP-DM Process Log - Chess ML Project

## Phase 1: Business Understanding ✅ COMPLETE

### Business Objectives
- **Goal:** Build a chess AI that learns from historical games
- **Success Criteria:** 
  - Model can predict moves with >60% accuracy
  - Playable web interface
  - Continuous learning from user games
- **Project Sponsor:** Self-directed learning project

### Situation Assessment
- **Resources:** MacBook Pro, PostgreSQL, Python, Jupyter
- **Requirements:** 
  - Free chess game data (Lichess)
  - ML framework (TensorFlow)
  - Web framework (Flask)
- **Constraints:** 
  - Local development only (initially)
  - Storage limitations (managed)
  - No budget

### Data Mining Goals
- Extract patterns from 1,000+ chess games
- Identify strong move choices in various positions
- Build predictive model for move selection

### Project Plan
- **Phase A-C:** ✅ Complete (Setup, Database, Data Pipeline)
- **Phase D:** ✅ Complete (Exploratory Data Analysis)
- **Phase E:** ✅ Complete (Modeling — V1 & V2)
- **Phase F-I:** ⏳ Next (Evaluation, API, Frontend, Deployment)

---

## Phase 2: Data Understanding ⏳ IN PROGRESS

### Initial Data Collection ✅
- **Source:** Lichess Open Database (January 2024)
- **Volume:** 1,000 games sampled from 4M games
- **Format:** PGN (Portable Game Notation)
- **Size:** 2.2 MB
- **Date:** 2025-12-13

### Data Description ✅
**Games Dataset:**
- 100 games loaded
- ELO range: 635 - 2658
- Average ELO: ~1,655
- Result distribution: 51% white wins, 47% black wins, 2% draws

**Positions Dataset:**
- 673 individual board positions
- Average 67 positions per game
- Each position contains FEN (board state) and move played

### Data Quality ✅
- ✅ No corrupt PGN files
- ✅ Valid ELO ratings
- ✅ Legal moves validated
- ⚠️ Some duplicate games (ran load twice - to clean)

### Data Exploration 📊 NEXT STEPS
- [x] ELO distribution analysis (bell curve, 568-3003 range)
- [x] Opening success rates (392 unique openings)
- [x] Move frequency analysis (e4 most popular: 431 games)
- [x] Win correlation with ELO difference (confirmed strong correlation)
- [x] Game length statistics (avg 69 moves, range 2-242)
- [x] Visualizations created (8+ charts including distributions, win rates, openings) [ ] Position evaluation patterns

---

## Phase 3: Data Preparation ✅ COMPLETE (V2)

### Data Selection
- ✅ Used all available positions (112,466 from 2,200 games) — no ELO filter applied
- ✅ All 392 openings included

### Data Cleaning
- ✅ Duplicate positions handled via full dataset reload
- ✅ FEN notations validated through python-chess library

### Feature Engineering ✅
- ✅ 12 binary planes per piece type (6 piece types × 2 colors × 64 squares = 768 values)
- ✅ Additional features: castling rights (4), side-to-move (1) → **781 total features**
- ✅ Legal move masking at inference time (filters illegal moves from predictions)

### Data Transformation ✅
- ✅ Train/validation split applied during model training
- ✅ LabelEncoder for 1,841 unique target moves (saved as label_encoder_v2.pkl)

---

## Phase 4: Modeling ✅ COMPLETE

### V1 Model — 2025-12-21
- Model type: Dense neural network (256→128→64 layers, 135K parameters)
- Features: 65 (64 board squares + turn indicator)
- Target: 1,188 unique chess moves
- Training data: 10,000 positions
- Performance: **6.95% top-1 accuracy (87x better than random baseline)**
- Saved: `chess_move_predictor_v1.keras`

### V2 Model — 2026-03-01
- Model type: Dense neural network with batch normalization (1024→512→256 layers)
- Features: **781** (12 binary planes per piece type + castling rights + side-to-move)
- Target: 1,841 unique chess moves
- Training data: 112,466 positions (full dataset)
- Performance: **~55% top-1 accuracy, top-3 and top-5 metrics tracked**
- Legal move masking applied at inference time
- Saved: `chess_move_predictor_v2.keras`

---

## Phase 5: Evaluation ✅ COMPLETE

### Methodology
- Deterministic hold-out test set (20% of data, `ORDER BY position_id`, `random_state=42`)
- Evaluated on 22,494 test positions; 100% vocab coverage (all moves known to encoder)

### Results
| Metric | V1 | V2 |
|---|---|---|
| Top-1 accuracy | 6.95% | **89.05%** |
| Top-3 accuracy | — | **93.65%** |
| Top-5 accuracy | — | **95.00%** |
| Fallback rate | — | **0.0%** |

### Overfitting check
- Train top-1: 89.74% · Test top-1: 89.05% · Gap: +0.69pp ✅ No significant overfitting

### Accuracy by move frequency
| Move frequency | Top-1 accuracy |
|---|---|
| Rare (≤10 occurrences) | 90.0% |
| Uncommon (11–50) | 92.9% |
| Common (51–200) | 92.7% |
| Very common (>200) | 86.2% |

Note: very common moves score slightly lower — likely because they appear in more diverse positions, making them harder to predict in context.

### Artefacts
- `evaluate_model.py` — reproducible evaluation script
- `data/processed/evaluation_by_freq.png` — accuracy by move frequency chart

---

## Phase 6: API Development ✅ COMPLETE

### Endpoints
- `POST /api/move` — returns model's best move for a FEN position (top_k supported)
- `POST /api/game` — saves a completed human game to PostgreSQL
- `GET /api/stats` — returns model metadata + live DB counts

### Implementation
- Flask Blueprint (`app/routes.py`)
- Model inference in `app/model.py` (singleton load, legal move masking)
- FEN validation + game-over guard before calling model

---

## Phase 7: Frontend Development ✅ COMPLETE

### Implementation
- SVG chess board (400×400 viewBox, scales to mobile width)
- Touch-friendly tap-to-select + tap-to-move interaction
- Legal move dots + capture rings on selection
- Last-move highlight
- AI thinking state + status bar
- Move history panel (scrollable)
- New Game / Flip Board controls
- Calls `/api/move` for AI response

---

## Phase 8: Deployment ⏳ TODO

---

## Iteration Log

| Date | Phase | Activity | Outcome |
|------|-------|----------|---------|
| 2025-12-12 | Phase 1 | Project setup | Environment ready |
| 2025-12-12 | Phase 1 | Database design | Schema created |
| 2025-12-13 | Phase 2 | Data collection | 1,000 games downloaded |
| 2025-12-13 | Phase 2 | Initial load | 100 games, 673 positions |
| 2025-12-13 | Phase 2 | Data quality check | Passed with minor issues |
| 2025-12-17 | Phase C | Data pipeline scaled up | 2,200 games, 148k positions |
| 2025-12-18 | Phase D |Exploratory Data Analysis | Visualizations, patterns identified, ready for ML |
| 2025-12-21 | Phase E | ML Model Training (V1) | Neural network built, 6.95% accuracy, model saved |
| 2026-03-01 | Phase E | ML Model Training (V2) | 781-feature binary planes, ~55% accuracy, legal move masking |
| 2026-04-12 | Phase 5 | Model evaluation | Top-1: 89.05%, Top-3: 93.65%, Top-5: 95.00%, 0% fallback — no overfitting |
| 2026-04-12 | Phase 6 | API development | Flask routes: /api/move, /api/game, /api/stats — complete |
| 2026-04-12 | Phase 7 | Frontend development | SVG board, touch interaction, move history, AI integration — complete |
---

## Key Decisions

### Decision 1: Database Choice
- **Date:** 2025-12-12
- **Options:** PostgreSQL vs SQLite vs MongoDB
- **Decision:** PostgreSQL
- **Rationale:** Production-ready, great for ML pipelines, SQL expertise transferable

### Decision 2: Data Volume
- **Date:** 2025-12-13
- **Options:** 1K, 10K, or 100K games
- **Decision:** Start with 1K games
- **Rationale:** Faster iteration, validate pipeline, scale later

### Decision 3: Position Extraction
- **Date:** 2025-12-13
- **Options:** Store only game results vs store all positions
- **Decision:** Store all positions
- **Rationale:** Needed for supervised learning, enables position-level analysis

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Insufficient data | High | Low | Can scale to 100K+ games |
| Model overfitting | Medium | Medium | Use validation set, regularization |
| Storage limitations | Low | Low | Managed (cleaned 245GB) |
| Performance issues | Medium | Low | Start simple, optimize later |
