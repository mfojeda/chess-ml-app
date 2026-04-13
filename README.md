# Chess AI — Full-Stack ML Application

A full-stack chess application powered by a neural network trained on 112,000+ real games from Lichess. Play against the AI in your browser, with a mobile-first UI designed for deployment as a native app.

## Model Performance

| Metric | V1 | V2 |
|---|---|---|
| Training positions | 10,000 | 112,466 |
| Feature size | 65 | 781 |
| Top-1 accuracy | 6.95% | **89.05%** |
| Top-3 accuracy | — | **93.65%** |
| Top-5 accuracy | — | **95.00%** |
| Fallback rate | — | **0.0%** |
| Overfitting gap | — | +0.69pp ✅ |

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL |
| Data pipeline | Python, Pandas, python-chess |
| ML framework | TensorFlow / Keras |
| Backend API | Flask, SQLAlchemy |
| Frontend | HTML, CSS, JavaScript, chess.js |
| Notebooks | Jupyter |

## Project Structure

```
chess_project/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── model.py             # Model loading and inference
│   ├── routes.py            # API endpoints
│   └── templates/
│       └── index.html       # Mobile-first frontend (SVG board)
├── data/
│   ├── processed/           # Evaluation charts
│   ├── raw/                 # PGN source files (gitignored)
│   └── scripts/
│       └── db_connection.py # PostgreSQL connection helper
├── docs/
│   └── diagrams/            # Mermaid architecture diagrams
├── models/
│   ├── chess_move_predictor_v1.keras
│   └── chess_move_predictor_v2.keras  # ← active model
├── notebooks/
│   ├── 01_parse_pgn_to_database.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_training_v2.ipynb
│   └── 05_model_evaluation.ipynb
├── sql/
│   └── V1__initial_schema.sql
├── evaluate_model.py        # Reproducible evaluation script
├── run.py                   # Flask entry point
├── requirements.txt         # Dependencies
└── CRISP_DM_LOG.md          # Full development log (CRISP-DM methodology)
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/move` | Get AI's best move for a FEN position |
| `POST` | `/api/game` | Save a completed game to the database |
| `GET` | `/api/stats` | Model metadata and database counts |

### Example — get AI move
```bash
curl -X POST http://localhost:5000/api/move \
  -H "Content-Type: application/json" \
  -d '{"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", "top_k": 3}'
```

## Running Locally

```bash
# 1. Create and activate virtual environment
python -m venv chess_env
source chess_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up PostgreSQL database
# Ensure PostgreSQL is running and create the chess_app database
psql -c "CREATE DATABASE chess_app;"
psql chess_app < sql/V1__initial_schema.sql

# 4. Start the Flask server
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

## Development Phases (CRISP-DM)

1. ✅ Business understanding & project setup
2. ✅ Data collection — 2,200 Lichess games, 112,466 positions
3. ✅ Exploratory data analysis
4. ✅ Modeling — V2 neural network (1024→512→256, BatchNorm, legal move masking)
5. ✅ Evaluation — 89.05% top-1 accuracy, 0% fallback rate
6. ✅ API development — Flask REST API
7. ✅ Frontend — Mobile-first SVG chess board
8. ⏳ Deployment — Capacitor mobile app (iOS + Android)

See [CRISP_DM_LOG.md](CRISP_DM_LOG.md) for the full development log.

## Architecture Diagrams

All diagrams use Mermaid and render on GitHub:

- [Workflow](docs/diagrams/01_workflow.md) — Full project pipeline
- [Data Flow](docs/diagrams/02_dataflow.md) — ETL pipeline
- [Database ERD](docs/diagrams/03_database_erd.md) — Schema
- [ETL Process](docs/diagrams/04_etl_process.md) — Extract-Transform-Load detail
- [Gameplay Flow](docs/diagrams/05_gameplay_flow.md) — Runtime data flow during a game
