import chess

from engine.evaluation import evaluate_board


def order_moves(board, moves):
    capturing_moves = []
    other_moves = []
    for move in moves:
        if board.is_capture(move):
            capturing_moves.append(move)
        else:
            other_moves.append(move)
    return capturing_moves + other_moves


def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        result = evaluate_board(board)
        return result["total"]

    ordered_moves = order_moves(board, list(board.legal_moves))

    if maximizing:
        best_value = -9999.0
        for move in ordered_moves:
            board.push(move)
            value = minimax(board, depth - 1, alpha, beta, False)
            board.pop()

            if value > best_value:
                best_value = value
            if value > alpha:
                alpha = value
            if beta <= alpha:
                break
        return best_value
    else:
        best_value = 9999.0
        for move in ordered_moves:
            board.push(move)
            value = minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            if value < best_value:
                best_value = value
            if value < beta:
                beta = value
            if beta <= alpha:
                break
        return best_value


def get_best_move_with_analysis(board, depth=2):
    is_white_turn = (board.turn == chess.WHITE)
    candidate_list = []

    ordered_moves = order_moves(board, list(board.legal_moves))

    for move in ordered_moves:
        board.push(move)
        score = minimax(board, depth - 1, -9999.0, 9999.0, not is_white_turn)
        board.pop()
        candidate_list.append((move, score))

    if is_white_turn:
        candidate_list.sort(key=lambda pair: pair[1], reverse=True)
    else:
        candidate_list.sort(key=lambda pair: pair[1])

    best_move, best_score = candidate_list[0]

    if len(candidate_list) > 1:
        alternative_move, alt_score = candidate_list[1]
    else:
        alternative_move, alt_score = None, None

    return {
        "best_move": best_move,
        "best_score": best_score,
        "alternative_move": alternative_move,
        "alt_score": alt_score,
        "all_candidates": candidate_list
    }