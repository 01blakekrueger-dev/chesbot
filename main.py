# ============================================================
#  main.py  —  Chess Bot Website  |  Flask Server
#  Run locally:  python main.py
#  Then open:    http://localhost:8080
# ============================================================

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import os, sys

from bot import your_bot

app = Flask(__name__)
CORS(app)

# ── Stockfish path ────────────────────────────────────────────
# Windows: download from https://stockfishchess.org/download/
# Put stockfish.exe in the same folder as this file
if sys.platform == "win32":
    SF_PATH = os.path.join(os.path.dirname(__file__), "stockfish.exe")
else:
    SF_PATH = "/usr/games/stockfish"   # Linux (Render)

# ── Game state ────────────────────────────────────────────────
game_board = chess.Board()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new-game", methods=["POST"])
def new_game():
    global game_board
    game_board = chess.Board()
    return jsonify({"fen": game_board.fen()})

@app.route("/player-move", methods=["POST"])
def player_move():
    global game_board
    uci = request.json.get("move", "")
    try:
        move = chess.Move.from_uci(uci)
        if move not in game_board.legal_moves:
            return jsonify({"error": "Illegal move"}), 400
        san = game_board.san(move)
        game_board.push(move)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "fen":       game_board.fen(),
        "last_move": uci,
        "move_san":  san,
        "game_over": check_game_over(game_board),
    })

@app.route("/bot-move", methods=["POST"])
def bot_move():
    global game_board
    if game_board.is_game_over():
        return jsonify({"error": "Game over"}), 400
    move = your_bot(game_board.copy())
    if move not in game_board.legal_moves:
        import random
        move = random.choice(list(game_board.legal_moves))
    uci = move.uci()
    san = game_board.san(move)
    game_board.push(move)
    return jsonify({
        "fen":       game_board.fen(),
        "last_move": uci,
        "move_san":  san,
        "game_over": check_game_over(game_board),
    })

@app.route("/stockfish-move", methods=["POST"])
def stockfish_move():
    global game_board
    data   = request.json
    skill  = int(data.get("skill", 20))
    time_s = float(data.get("time", 1.0))

    if game_board.is_game_over():
        return jsonify({"error": "Game over"}), 400
    if not os.path.exists(SF_PATH):
        return jsonify({"error": f"Stockfish not found at: {SF_PATH}"}), 500

    with chess.engine.SimpleEngine.popen_uci(SF_PATH) as engine:
        engine.configure({"Skill Level": skill, "UCI_LimitStrength": False})
        result = engine.play(game_board, chess.engine.Limit(time=time_s))
        move   = result.move

    uci = move.uci()
    san = game_board.san(move)
    game_board.push(move)
    return jsonify({
        "fen":       game_board.fen(),
        "last_move": uci,
        "move_san":  san,
        "game_over": check_game_over(game_board),
    })

@app.route("/analyse-move", methods=["POST"])
def analyse_move():
    """Stockfish evaluates a position and returns centipawn score."""
    data = request.json
    fen  = data.get("fen", chess.STARTING_FEN)
    time_s = float(data.get("time", 0.3))

    if not os.path.exists(SF_PATH):
        return jsonify({"cp": 0, "mate": None})

    board = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci(SF_PATH) as engine:
        info  = engine.analyse(board, chess.engine.Limit(time=time_s))
        score = info["score"].white()
        best  = info.get("pv", [None])[0]

    if score.is_mate():
        return jsonify({"cp": None, "mate": score.mate(), "best_move": best.uci() if best else None})
    return jsonify({"cp": score.score(), "mate": None, "best_move": best.uci() if best else None})

@app.route("/legal-moves", methods=["POST"])
def legal_moves():
    sq = request.json.get("square", "")
    try:
        s = chess.parse_square(sq)
        moves = [m.uci() for m in game_board.legal_moves if m.from_square == s]
        return jsonify({"moves": moves})
    except Exception:
        return jsonify({"moves": []})

def check_game_over(board):
    if not board.is_game_over():
        return None
    o = board.outcome()
    if o.winner == chess.WHITE:  return {"result": "White wins", "reason": o.termination.name}
    if o.winner == chess.BLACK:  return {"result": "Black wins", "reason": o.termination.name}
    return {"result": "Draw", "reason": o.termination.name}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
