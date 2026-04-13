# Gameplay Data Flow

How data moves through the system during a live game.

## Runtime Flow (per move)

```mermaid
sequenceDiagram
    actor User
    participant Board as Frontend<br/>(SVG Board + chess.js)
    participant API as Flask API<br/>(/api/move)
    participant Model as Model Inference<br/>(app/model.py)
    participant TF as TensorFlow V2<br/>(chess_move_predictor_v2.h5)
    participant DB as PostgreSQL<br/>(chess_app)

    User->>Board: Tap piece → tap destination
    Board->>Board: chess.js validates move locally<br/>updates FEN string

    Board->>API: POST /api/move<br/>{ fen: "rnbq...", top_k: 1 }

    API->>API: Validate FEN with python-chess<br/>Check game not already over

    API->>Model: predict_move(fen, top_k=1)

    Model->>Model: fen_to_features(fen)<br/>→ 781-element float32 vector<br/>(768 board planes + 13 game-state)

    Model->>TF: model.predict(features)
    TF-->>Model: softmax probs<br/>over 1,841 moves

    Model->>Model: Legal move masking<br/>filter to python-chess legal moves<br/>sort by probability

    Model-->>API: [{ move: "e5", probability: 0.73 }]

    API-->>Board: { move: "e5", top_moves: [...], fen: "..." }

    Board->>Board: chess.js applies AI move<br/>re-renders SVG board

    Note over User,Board: Game continues until checkmate / draw / stalemate

    User->>API: POST /api/game<br/>{ white, black, result, moves, ... }
    API->>DB: INSERT INTO games (pgn_moves, result, ...)<br/>RETURNING game_id
    DB-->>API: game_id
    API-->>User: { game_id: 42 }
```

---

## Component Architecture

```mermaid
flowchart TB
    subgraph Client["📱 Mobile Browser"]
        UI["SVG Chess Board<br/>chess.js · touch events"]
    end

    subgraph Server["🐍 Flask Backend"]
        direction TB
        R["/api/move<br/>/api/game<br/>/api/stats"]
        M["Model Inference<br/>fen_to_features()<br/>legal move masking"]
        R --> M
    end

    subgraph ML["🧠 ML Layer"]
        direction TB
        TF["TensorFlow V2 Model<br/>1024→512→256→1841<br/>BatchNorm + Dropout"]
        LE["Label Encoder<br/>1,841 SAN moves"]
        TF --- LE
    end

    subgraph Data["🗄️ Data Layer"]
        direction TB
        PG[("PostgreSQL<br/>chess_app")]
        PGN["Lichess PGN Pipeline<br/>2,200 games<br/>112,466 positions"]
        PGN -->|"parse + load"| PG
        PG -->|"training data"| TF
    end

    UI -->|"POST /api/move { fen }"| R
    M -->|"features (781)"| TF
    TF -->|"probabilities (1841)"| M
    M -->|"best legal move"| R
    R -->|"{ move, top_moves }"| UI
    UI -->|"POST /api/game"| R
    R -->|"INSERT game"| PG
```

---

## Feature Engineering Detail

Each board position is encoded as a **781-element float32 vector**:

```
[  0 – 767 ]  12 binary planes (64 squares each)
               Plane  0: White pawns       Plane  6: Black pawns
               Plane  1: White knights     Plane  7: Black knights
               Plane  2: White bishops     Plane  8: Black bishops
               Plane  3: White rooks       Plane  9: Black rooks
               Plane  4: White queens      Plane 10: Black queens
               Plane  5: White king        Plane 11: Black king

[       768 ]  Side to move  (1 = White, 0 = Black)

[ 769 – 772 ]  Castling rights  (WK, WQ, BK, BQ)

[ 773 – 780 ]  En passant file  (one-hot, files a–h)
```

---

## Model Performance

| Metric | V1 | V2 |
|---|---|---|
| Training positions | 10,000 | 112,466 |
| Feature size | 65 | **781** |
| Top-1 accuracy | 6.95% | **89.05%** |
| Top-3 accuracy | — | **93.65%** |
| Top-5 accuracy | — | **95.00%** |
| Fallback rate | — | **0.0%** |
| Overfitting gap | — | **+0.69pp ✅** |
