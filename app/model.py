"""
Chess model inference module.
Loads the V2 model and label encoder once at startup, exposes predict_move().
"""

import os
import pickle
import random

import chess
import numpy as np
import tensorflow as tf

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'chess_move_predictor_v2.h5')
_ENCODER_PATH = os.path.join(_BASE_DIR, 'models', 'label_encoder_v2.pkl')

# Module-level singletons — loaded once on first call
_model = None
_label_encoder = None

PIECE_TYPES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
COLORS = [chess.WHITE, chess.BLACK]


def _load():
    global _model, _label_encoder
    if _model is None:
        _model = tf.keras.models.load_model(_MODEL_PATH)
    if _label_encoder is None:
        with open(_ENCODER_PATH, 'rb') as f:
            _label_encoder = pickle.load(f)


def fen_to_features(fen: str) -> np.ndarray:
    """Convert a FEN string to a 781-element float32 feature vector.

    Layout:
      [0:768]   12-plane binary board (piece type x color x square)
      [768]     side to move (1=white, 0=black)
      [769:773] castling rights (WK, WQ, BK, BQ)
      [773:781] en passant file, one-hot (files a-h)
    """
    board = chess.Board(fen)

    planes = np.zeros(768, dtype=np.float32)
    for color_idx, color in enumerate(COLORS):
        for piece_idx, piece_type in enumerate(PIECE_TYPES):
            plane = color_idx * 6 + piece_idx
            for sq in board.pieces(piece_type, color):
                planes[plane * 64 + sq] = 1.0

    side = np.array([1.0 if board.turn == chess.WHITE else 0.0], dtype=np.float32)

    castling = np.array([
        float(board.has_kingside_castling_rights(chess.WHITE)),
        float(board.has_queenside_castling_rights(chess.WHITE)),
        float(board.has_kingside_castling_rights(chess.BLACK)),
        float(board.has_queenside_castling_rights(chess.BLACK)),
    ], dtype=np.float32)

    ep = np.zeros(8, dtype=np.float32)
    if board.ep_square is not None:
        ep[chess.square_file(board.ep_square)] = 1.0

    return np.concatenate([planes, side, castling, ep])


def predict_move(fen: str, top_k: int = 3) -> list:
    """Predict the best move(s) for a FEN position, restricted to legal moves.

    Returns a list of dicts [{"move": "e5", "probability": 0.42}, ...],
    sorted by probability descending.
    Falls back to a random legal move if the model knows none of the legal moves.
    """
    _load()

    board = chess.Board(fen)
    legal_moves_san = {board.san(m) for m in board.legal_moves}

    features = fen_to_features(fen).reshape(1, -1)
    probs = _model.predict(features, verbose=0)[0]

    known_classes = set(_label_encoder.classes_)
    candidates = []
    for move_san in legal_moves_san:
        if move_san in known_classes:
            idx = int(_label_encoder.transform([move_san])[0])
            candidates.append({'move': move_san, 'probability': float(probs[idx])})

    if not candidates:
        fallback = board.san(random.choice(list(board.legal_moves)))
        return [{'move': fallback, 'probability': 0.0}]

    candidates.sort(key=lambda x: x['probability'], reverse=True)
    return candidates[:top_k]
