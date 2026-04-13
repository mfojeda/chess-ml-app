"""
Model Evaluation — Chess ML V2
Phase 5: Evaluation

Computes top-1, top-3, top-5 accuracy on a deterministic held-out test set,
checks for overfitting, and measures the legal-move fallback rate.
"""

import os
import sys
import pickle

import chess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for script use
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.model_selection import train_test_split

# Project root is this script's directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'data', 'scripts'))
from db_connection import get_engine

MODEL_PATH   = os.path.join(PROJECT_ROOT, 'models', 'chess_move_predictor_v2.h5')
ENCODER_PATH = os.path.join(PROJECT_ROOT, 'models', 'label_encoder_v2.pkl')
PLOT_PATH    = os.path.join(PROJECT_ROOT, 'data', 'processed', 'evaluation_by_freq.png')

# ── 1. Load model & encoder ────────────────────────────────────────────────
print(f'TensorFlow: {tf.__version__}')
print(f'Loading model from {MODEL_PATH}...')
model = tf.keras.models.load_model(MODEL_PATH)

with open(ENCODER_PATH, 'rb') as f:
    label_encoder = pickle.load(f)

print(f'Known moves: {len(label_encoder.classes_):,}')

# ── 2. Load positions (deterministic order) ────────────────────────────────
engine = get_engine()
print('\nLoading positions from database...')
df = pd.read_sql("""
    SELECT
        p.position_id,
        p.fen,
        p.move_played
    FROM positions p
    JOIN games g ON p.game_id = g.game_id
    WHERE g.white_elo > 1400
    ORDER BY p.position_id
""", engine)
print(f'Loaded {len(df):,} positions  ({df["move_played"].nunique():,} unique moves)')

# ── 3. Feature engineering ─────────────────────────────────────────────────
PIECE_TYPES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
COLORS      = [chess.WHITE, chess.BLACK]

def fen_to_features(fen):
    board = chess.Board(fen)
    planes = np.zeros(768, dtype=np.float32)
    for ci, color in enumerate(COLORS):
        for pi, piece_type in enumerate(PIECE_TYPES):
            plane = ci * 6 + pi
            for sq in board.pieces(piece_type, color):
                planes[plane * 64 + sq] = 1.0
    side     = np.array([1.0 if board.turn == chess.WHITE else 0.0], dtype=np.float32)
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

print(f'\nConverting {len(df):,} positions to feature vectors (~60-90s)...')
X          = np.array([fen_to_features(fen) for fen in df['fen']])
known_mask = df['move_played'].isin(label_encoder.classes_).values
y          = label_encoder.transform(
    df['move_played'].where(known_mask, other=label_encoder.classes_[0])
)
print(f'Done. X shape: {X.shape}')
print(f'Vocab coverage: {known_mask.sum():,}/{len(known_mask):,} ({known_mask.mean()*100:.1f}%)')

# ── 4. Deterministic 80/20 split ───────────────────────────────────────────
X_train, X_test, y_train, y_test, mask_train, mask_test = train_test_split(
    X, y, known_mask, test_size=0.2, random_state=42
)
print(f'\nTrain: {len(X_train):,}   Test: {len(X_test):,}')

# ── 5. Top-k accuracy ─────────────────────────────────────────────────────
print('\nRunning inference on test set...')
y_pred_probs = model.predict(X_test, batch_size=512, verbose=1)

def topk_accuracy(y_true, y_probs, k, mask=None):
    if mask is not None:
        y_true, y_probs = y_true[mask], y_probs[mask]
    top_k = np.argsort(y_probs, axis=1)[:, -k:]
    return np.any(top_k == y_true[:, None], axis=1).mean()

top1 = topk_accuracy(y_test, y_pred_probs, 1, mask=mask_test)
top3 = topk_accuracy(y_test, y_pred_probs, 3, mask=mask_test)
top5 = topk_accuracy(y_test, y_pred_probs, 5, mask=mask_test)

print()
print('=' * 55)
print('MODEL V2 EVALUATION RESULTS')
print('=' * 55)
print(f'  Test positions (move in vocab): {mask_test.sum():,}')
print()
print(f'  Top-1 accuracy:  {top1*100:.2f}%   (V1: 6.95%)')
print(f'  Top-3 accuracy:  {top3*100:.2f}%')
print(f'  Top-5 accuracy:  {top5*100:.2f}%')
print(f'\n  vs V1:  {(top1-0.0695)*100:+.2f}pp  ({top1/0.0695:.1f}x improvement)')
print('=' * 55)

# ── 6. Overfitting check ───────────────────────────────────────────────────
print('\nOverfitting check (5K train sample)...')
idx = np.random.default_rng(0).choice(len(X_train), size=5000, replace=False)
train_probs  = model.predict(X_train[idx], batch_size=512, verbose=0)
train_top1   = topk_accuracy(y_train[idx], train_probs, 1, mask=mask_train[idx])
gap          = train_top1 - top1

print(f'  Train top-1: {train_top1*100:.2f}%')
print(f'  Test  top-1: {top1*100:.2f}%')
print(f'  Gap:         {gap*100:+.2f}pp  ', end='')
if gap < 0.03:   print('✅ No significant overfitting')
elif gap < 0.08: print('⚠️  Mild overfitting')
else:            print('❌ Significant overfitting')

# ── 7. Fallback rate ───────────────────────────────────────────────────────
print('\nMeasuring legal-move fallback rate (500 positions)...')
known_classes  = set(label_encoder.classes_)
sample_fens    = df['fen'].sample(500, random_state=99)
fallback_count = 0
for fen in sample_fens:
    try:
        board     = chess.Board(fen)
        legal_san = {board.san(m) for m in board.legal_moves}
        if not any(m in known_classes for m in legal_san):
            fallback_count += 1
    except Exception:
        fallback_count += 1

fallback_rate = fallback_count / 500
print(f'  Fallback rate: {fallback_count}/500 = {fallback_rate*100:.1f}%  ', end='')
if fallback_rate < 0.05:   print('✅ Very low')
elif fallback_rate < 0.15: print('⚠️  Moderate')
else:                      print('❌ High')

# ── 8. Accuracy by move frequency ─────────────────────────────────────────
print('\nAccuracy by move frequency...')
move_counts  = df['move_played'].value_counts()
test_indices = train_test_split(range(len(df)), test_size=0.2, random_state=42)[1]
test_df      = df.iloc[test_indices].copy()
test_df      = test_df[test_df['move_played'].isin(known_classes)].copy()
test_df['move_freq'] = test_df['move_played'].map(move_counts)

bins   = [0, 10, 50, 200, float('inf')]
labels = ['Rare (≤10)', 'Uncommon (11-50)', 'Common (51-200)', 'Very common (>200)']
test_df['freq_bin'] = pd.cut(test_df['move_freq'], bins=bins, labels=labels)

X_freq    = np.array([fen_to_features(fen) for fen in test_df['fen']])
y_freq    = label_encoder.transform(test_df['move_played'])
pred_freq = model.predict(X_freq, batch_size=512, verbose=0)
test_df['correct'] = (np.argmax(pred_freq, axis=1) == y_freq)

acc_by_freq = test_df.groupby('freq_bin', observed=True)['correct'].agg(['mean', 'count'])
acc_by_freq.columns = ['Top-1 Accuracy', 'Count']
acc_by_freq['Top-1 Accuracy'] = acc_by_freq['Top-1 Accuracy'].map('{:.1%}'.format)
print()
print(acc_by_freq.to_string())

# ── 9. Plot ────────────────────────────────────────────────────────────────
grp  = test_df.groupby('freq_bin', observed=True)['correct'].mean()
fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(grp.index.astype(str), grp.values * 100, color='steelblue', edgecolor='white')
for bar, val in zip(bars, grp.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val*100:.1f}%', ha='center', va='bottom', fontsize=10)
ax.set_ylabel('Top-1 Accuracy (%)')
ax.set_title('V2 Model Accuracy by Move Frequency')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150)
print(f'\nPlot saved to {PLOT_PATH}')

# ── 10. Copy-paste for routes.py ───────────────────────────────────────────
print()
print('─' * 55)
print('Paste into app/routes.py → get_stats():')
print(f"    'top1_accuracy': {top1:.4f},")
print(f"    'top3_accuracy': {top3:.4f},")
print(f"    'top5_accuracy': {top5:.4f},")
print(f"    'fallback_rate': {fallback_rate:.4f},")
print('─' * 55)
