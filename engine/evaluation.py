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


def is_pawn_isolated(board, square, color):
    # No friendly pawn on either neighboring file = isolated
    file_index = chess.square_file(square)
    for neighbor_file in [file_index - 1, file_index + 1]:
        if neighbor_file < 0 or neighbor_file > 7:
            continue
        for rank_index in range(8):
            check_square = chess.square(neighbor_file, rank_index)
            piece = board.piece_at(check_square)
            if piece is not None and piece.piece_type == chess.PAWN and piece.color == color:
                return False
    return True


def is_pawn_doubled(board, square, color):
    # Two or more friendly pawns sharing the same file = doubled
    file_index = chess.square_file(square)
    pawn_count_on_file = 0
    for rank_index in range(8):
        check_square = chess.square(file_index, rank_index)
        piece = board.piece_at(check_square)
        if piece is not None and piece.piece_type == chess.PAWN and piece.color == color:
            pawn_count_on_file = pawn_count_on_file + 1
    return pawn_count_on_file >= 2


def evaluate_material(board):
    score = 0.0
    for square, piece in board.piece_map().items():
        if piece.piece_type == chess.PAWN:
            weak_pawn = is_pawn_isolated(board, square, piece.color) or is_pawn_doubled(board, square, piece.color)
            value = 0.8 if weak_pawn else PIECE_VALUES[chess.PAWN]
        else:
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


def evaluate_king_attack(board):
    # Rewards heavy attacking pieces (rook, queen) for being close to
    # the ENEMY king's file or rank - this is the basic idea behind
    # building a checkmate attack: line up your strongest pieces near
    # the opponent's king instead of leaving them far away.
    score = 0.0
    for color in [chess.WHITE, chess.BLACK]:
        enemy_king_square = board.king(not color)
        if enemy_king_square is None:
            continue

        king_file = chess.square_file(enemy_king_square)
        king_rank = chess.square_rank(enemy_king_square)

        for square, piece in board.piece_map().items():
            if piece.color != color:
                continue
            if piece.piece_type != chess.ROOK and piece.piece_type != chess.QUEEN:
                continue

            piece_file = chess.square_file(square)
            piece_rank = chess.square_rank(square)
            file_distance = abs(piece_file - king_file)
            rank_distance = abs(piece_rank - king_rank)

            if file_distance <= 2 or rank_distance <= 2:
                if color == chess.WHITE:
                    score = score + 0.15
                else:
                    score = score - 0.15
    return round(score, 2)


def evaluate_open_files(board):
    # Rewards a rook standing on a file with no pawn of its own color
    # on it - an "open" or "semi-open" file, where the rook can move
    # and attack freely instead of being blocked by its own pawns.
    score = 0.0
    for square, piece in board.piece_map().items():
        if piece.piece_type != chess.ROOK:
            continue

        file_index = chess.square_file(square)
        blocked_by_own_pawn = False
        for rank_index in range(8):
            other_square = chess.square(file_index, rank_index)
            other_piece = board.piece_at(other_square)
            if other_piece is not None and other_piece.piece_type == chess.PAWN and other_piece.color == piece.color:
                blocked_by_own_pawn = True

        if not blocked_by_own_pawn:
            if piece.color == chess.WHITE:
                score = score + 0.2
            else:
                score = score - 0.2
    return round(score, 2)


LONG_DIAGONAL_SQUARES = [
    chess.A1, chess.B2, chess.C3, chess.D4, chess.E5, chess.F6, chess.G7, chess.H8,
    chess.A8, chess.B7, chess.C6, chess.D5, chess.E4, chess.F3, chess.G2, chess.H1,
]


def evaluate_bishop_diagonals(board):
    # Rewards a bishop standing on one of the two long diagonals,
    # where it can see and control the most squares on the board.
    score = 0.0
    for square, piece in board.piece_map().items():
        if piece.piece_type != chess.BISHOP:
            continue
        if square in LONG_DIAGONAL_SQUARES:
            if piece.color == chess.WHITE:
                score = score + 0.15
            else:
                score = score - 0.15
    return round(score, 2)


def evaluate_board(board):
    material = evaluate_material(board)
    mobility = evaluate_mobility(board)
    king_safety = evaluate_king_safety(board)
    center_control = evaluate_center_control(board)
    king_attack = evaluate_king_attack(board)
    open_files = evaluate_open_files(board)
    bishop_diagonals = evaluate_bishop_diagonals(board)

    total = material + mobility + king_safety + center_control + king_attack + open_files + bishop_diagonals
    total = round(total, 2)

    return {
        "material": material,
        "mobility": mobility,
        "king_safety": king_safety,
        "center_control": center_control,
        "king_attack": king_attack,
        "open_files": open_files,
        "bishop_diagonals": bishop_diagonals,
        "total": total
    }