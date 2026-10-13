
import chess

from engine.evaluation import PIECE_VALUES

def piece_is_hanging(board, square, color):
    enemy_color = not color
    attackers = board.attackers(enemy_color, square)
    defenders = board.attackers(color, square)
    return len(attackers) > 0 and len(defenders) == 0


def detect_tactics(board, move):
    motifs = []

    board.push(move)
    moved_piece = board.piece_at(move.to_square)

    if moved_piece is not None:
        mover_color = moved_piece.color
        mover_value = PIECE_VALUES[moved_piece.piece_type]
        mover_is_hanging = piece_is_hanging(board, move.to_square, mover_color)
        attacked_squares = board.attacks(move.to_square)
        if not mover_is_hanging:
            qualifying_targets = 0
            for square in attacked_squares:
                target = board.piece_at(square)
                if target is not None and target.color != mover_color:
                    if target.piece_type == chess.KING:
                        qualifying_targets = qualifying_targets + 1
                        continue
                    target_value = PIECE_VALUES[target.piece_type]
                    target_is_undefended = piece_is_hanging(board, square, target.color)
                    attacker_is_cheaper = mover_value < target_value
                    if target_is_undefended or attacker_is_cheaper:
                        qualifying_targets = qualifying_targets + 1

            if qualifying_targets >= 2:
                motifs.append("FORK")
        if not mover_is_hanging:
            for square in attacked_squares:
                target = board.piece_at(square)
                if target is not None and target.color != mover_color and target.piece_type != chess.KING:
                    target_value = PIECE_VALUES[target.piece_type]
                    if mover_value < target_value:
                        motifs.append("TEMPO")
                        break

    if board.is_check():
        motifs.append("CHECK")

    board.pop()

    return motifs