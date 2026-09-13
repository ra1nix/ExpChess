import chess

# Note: pin detection, discovered-attack detection ,even tempo and various concepts might be implemented in the future
def detect_tactics(board, move):
    motifs = []

    board.push(move)
    moved_piece = board.piece_at(move.to_square)

    if moved_piece is not None:
        attacked_squares = board.attacks(move.to_square)
        valuable_targets_hit = 0
        for square in attacked_squares:
            target = board.piece_at(square)
            if target is not None and target.color != moved_piece.color:
                if target.piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
                    valuable_targets_hit = valuable_targets_hit + 1

        if valuable_targets_hit >= 2:
            motifs.append("FORK")

    if board.is_check():
        motifs.append("CHECK")

    board.pop()

    return motifs