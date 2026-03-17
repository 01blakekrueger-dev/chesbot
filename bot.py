# ============================================================
#  bot.py  —  YOUR CHESS BOT
#  Edit this file to make your bot smarter!
# ============================================================

import chess
import random

PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   20000,
}

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]
TABLES = {
    chess.PAWN: PAWN_TABLE, chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE, chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE, chess.KING: KING_TABLE,
}

def piece_square_bonus(piece_type, square, color):
    table = TABLES.get(piece_type, [])
    if not table: return 0
    if color == chess.WHITE:
        idx = (7 - chess.square_rank(square)) * 8 + chess.square_file(square)
    else:
        idx = chess.square_rank(square) * 8 + chess.square_file(square)
    return table[idx]

def evaluate(board):
    if board.is_checkmate(): return -99999
    if board.is_stalemate() or board.is_insufficient_material(): return 0
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None: continue
        v = PIECE_VALUES[piece.piece_type] + piece_square_bonus(piece.piece_type, sq, piece.color)
        score += v if piece.color == chess.WHITE else -v
    return score if board.turn == chess.WHITE else -score

def order_moves(board):
    def score(move):
        s = 0
        if board.gives_check(move): s += 500
        if board.is_capture(move):
            victim   = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                s += PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type] // 10
        if move.promotion: s += 900
        return s
    return sorted(board.legal_moves, key=score, reverse=True)

def minimax(board, depth, alpha, beta):
    if depth == 0 or board.is_game_over(): return evaluate(board)
    best = -float('inf')
    for move in order_moves(board):
        board.push(move)
        score = -minimax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score > best: best = score
        alpha = max(alpha, best)
        if alpha >= beta: break
    return best

SEARCH_DEPTH = 3  # increase for stronger play (3=fast, 4=slow)

def your_bot(board: chess.Board) -> chess.Move:
    legal = list(board.legal_moves)
    if not legal: return None
    best_move, best_score = None, -float('inf')
    alpha, beta = -float('inf'), float('inf')
    for move in order_moves(board):
        board.push(move)
        score = -minimax(board, SEARCH_DEPTH - 1, -beta, -alpha)
        board.pop()
        if score > best_score:
            best_score = score
            best_move  = move
        alpha = max(alpha, score)
    return best_move or random.choice(legal)
