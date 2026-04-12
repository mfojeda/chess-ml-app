"""
Flask API routes for the chess ML application.
"""

import sys
import os

import chess
from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import text

# Allow importing from data/scripts at the project root
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'scripts'))
from db_connection import get_engine

from app.model import predict_move

api = Blueprint('api', __name__, template_folder='templates')


@api.route('/')
def index():
    return render_template('index.html')


@api.route('/api/move', methods=['POST'])
def get_move():
    """
    POST /api/move
    Body: {"fen": "<FEN string>", "top_k": 1}
    Returns the model's best move(s) for the given position.
    """
    data = request.get_json(silent=True)
    if not data or 'fen' not in data:
        return jsonify({'error': 'Missing required field: fen'}), 400

    fen = data['fen']
    top_k = max(1, min(int(data.get('top_k', 1)), 10))

    try:
        board = chess.Board(fen)
    except ValueError:
        return jsonify({'error': 'Invalid FEN string'}), 400

    if board.is_game_over():
        return jsonify({'error': 'Game is already over'}), 400

    top_moves = predict_move(fen, top_k=top_k)

    return jsonify({
        'move': top_moves[0]['move'],
        'top_moves': top_moves,
        'fen': fen,
    })


@api.route('/api/game', methods=['POST'])
def save_game():
    """
    POST /api/game
    Body: {"white": "Player1", "black": "Player2", "result": "1-0",
           "moves": "<PGN move text>", "white_elo": 1500, "black_elo": 1500,
           "opening_name": "Sicilian Defense"}
    Saves a completed game to the database.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    required = ['white', 'black', 'result', 'moves']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    valid_results = {'1-0', '0-1', '1/2-1/2', '*'}
    if data['result'] not in valid_results:
        return jsonify({'error': f'Invalid result. Must be one of: {sorted(valid_results)}'}), 400

    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                INSERT INTO games
                    (white_player, black_player, result,
                     white_elo, black_elo, opening_name, pgn_moves, source)
                VALUES
                    (:white, :black, :result,
                     :white_elo, :black_elo, :opening_name, :pgn_moves, 'human')
                RETURNING game_id
            """),
            {
                'white': data['white'],
                'black': data['black'],
                'result': data['result'],
                'white_elo': data.get('white_elo'),
                'black_elo': data.get('black_elo'),
                'opening_name': data.get('opening_name', ''),
                'pgn_moves': data['moves'],
            }
        )
        game_id = row.fetchone()[0]

    return jsonify({'game_id': game_id}), 201


@api.route('/api/stats', methods=['GET'])
def get_stats():
    """
    GET /api/stats
    Returns model metadata and live database counts.
    """
    engine = get_engine()
    with engine.connect() as conn:
        game_count = conn.execute(text('SELECT COUNT(*) FROM games')).scalar()
        position_count = conn.execute(text('SELECT COUNT(*) FROM positions')).scalar()

    return jsonify({
        'model_version': 'v2',
        'top1_accuracy': 0.55,
        'top3_accuracy': None,
        'top5_accuracy': None,
        'feature_size': 781,
        'unique_moves': 1841,
        'total_games': game_count,
        'total_positions': position_count,
    })
