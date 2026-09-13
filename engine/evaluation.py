import chess

PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.2,
    chess.BISHOP: 3.3,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 0.0
}

CENTER_SQUARES = [chess.D4, chess.E4, chess.D5, chess.E5]


def evaluate_material(board):
    score = 0.0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        if piece.color == chess.WHITE:
            score = score + value
        else:
            score = score - value
    return round(score, 2)


def evaluate_center_control(board):
    score = 0.0
    for square in CENTER_SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            if piece.color == chess.WHITE:
                score = score + 0.3
            else:
                score = score - 0.3

        white_attackers = len(board.attackers(chess.WHITE, square))
        black_attackers = len(board.attackers(chess.BLACK, square))
        score = score + (white_attackers * 0.1)
        score = score - (black_attackers * 0.1)
    return round(score, 2)


def evaluate_mobility(board):
    if board.turn == chess.WHITE:
        white_move_count = len(list(board.legal_moves))
        board.push(chess.Move.null())
        black_move_count = len(list(board.legal_moves))
        board.pop()
    else:
        black_move_count = len(list(board.legal_moves))
        board.push(chess.Move.null())
        white_move_count = len(list(board.legal_moves))
        board.pop()

    difference = white_move_count - black_move_count
    return round(difference * 0.05, 2)


def evaluate_king_safety(board):
    score = 0.0
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if king_square is None:
            continue

        enemy_color = not color
        surrounding_squares = board.attacks(king_square)

        attacked_count = 0
        for square in surrounding_squares:
            if board.is_attacked_by(enemy_color, square):
                attacked_count = attacked_count + 1

        penalty = attacked_count * 0.25
        if color == chess.WHITE:
            score = score - penalty
        else:
            score = score + penalty
    return round(score, 2)


def evaluate_board(board):
    material = evaluate_material(board)
    mobility = evaluate_mobility(board)
    king_safety = evaluate_king_safety(board)
    center_control = evaluate_center_control(board)

    total = material + mobility + king_safety + center_control
    total = round(total, 2)

    return {
        "material": material,
        "mobility": mobility,
        "king_safety": king_safety,
        "center_control": center_control,
        "total": total
    }