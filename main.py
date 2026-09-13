from flask import Flask, render_template, request, jsonify
import chess
from engine.search import get_best_move_with_analysis
from engine.evaluation import evaluate_board
from explanation.generator import generate_explanation

app = Flask(__name__)


class GameState:
    def __init__(self):
        self.reset(player_color="white")

    def reset(self, player_color="white"):
        self.board = chess.Board()
        self.player_color = player_color
        self.bot_color = "black" if player_color == "white" else "white"
        self.last_explanation = "أهلاً ! اختر لونك ثم ابدأ اللعب."
        self.last_eval = 0.0

        if self.player_color == "black":
            self.make_bot_move()

    def get_san_history(self):
        temp_board = chess.Board()
        san_moves = []
        for move in self.board.move_stack:
            san_moves.append(temp_board.san(move))
            temp_board.push(move)
        return san_moves

    def make_bot_move(self):
        if self.board.is_game_over():
            return None

        analysis = get_best_move_with_analysis(self.board, depth=2)
        bot_move = analysis["best_move"]

        explanation_text = generate_explanation(self.board, analysis)
        self.last_explanation = explanation_text
        self.last_eval = analysis["best_score"]

        self.board.push(bot_move)
        return bot_move.uci()


game = GameState()


def parse_move_with_promotion(board, move_uci):
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            return move
    except ValueError:
        pass

    try:
        move_with_queen = chess.Move.from_uci(move_uci + "q")
        if move_with_queen in board.legal_moves:
            return move_with_queen
    except ValueError:
        pass

    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/state', methods=['GET'])
def get_state():
    eval_breakdown = evaluate_board(game.board)
    return jsonify({
        "fen": game.board.fen(),
        "is_game_over": game.board.is_game_over(),
        "turn": "white" if game.board.turn == chess.WHITE else "black",
        "player_color": game.player_color,
        "explanation": game.last_explanation,
        "eval": eval_breakdown["total"] if game.player_color == "white" else game.last_eval,
        "san_history": game.get_san_history()
    })


@app.route('/api/legal_moves', methods=['POST'])
def legal_moves():
    data = request.json or {}
    square = data.get("square")

    moves = []
    if square:
        try:
            sq_index = chess.parse_square(square)
            for m in game.board.legal_moves:
                if m.from_square == sq_index:
                    moves.append(chess.square_name(m.to_square))
        except ValueError:
            pass
    return jsonify({"legal_moves": moves})


@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json or {}
    move_uci = data.get("move")

    current_turn = "white" if game.board.turn == chess.WHITE else "black"
    if current_turn != game.player_color:
        return jsonify({"status": "error", "message": "انتظر دور البوت!"}), 400

    user_move = parse_move_with_promotion(game.board, move_uci)

    if user_move is None:
        return jsonify({"status": "invalid_move", "message": "حركة غير قانونية"}), 400

    game.board.push(user_move)

    if game.board.is_game_over():
        eval_breakdown = evaluate_board(game.board)
        return jsonify({
            "status": "game_over",
            "fen": game.board.fen(),
            "eval": eval_breakdown["total"],
            "explanation": "انتهت اللعبة!",
            "san_history": game.get_san_history()
        })

    game.make_bot_move()

    return jsonify({
        "status": "success",
        "fen": game.board.fen(),
        "explanation": game.last_explanation,
        "eval": game.last_eval,
        "san_history": game.get_san_history(),
        "is_game_over": game.board.is_game_over()
    })


@app.route('/api/undo', methods=['POST'])
def undo_move():
    moves_count = len(game.board.move_stack)
    if moves_count == 0:
        return jsonify({"status": "error", "message": "لا توجد حركات للتراجع عنها"}), 400

    current_turn = "white" if game.board.turn == chess.WHITE else "black"

    if current_turn == game.player_color:
        if moves_count >= 2:
            game.board.pop()
            game.board.pop()
        elif moves_count == 1 and game.player_color == "black":
            game.reset(player_color="black")
    else:
        game.board.pop()

    eval_breakdown = evaluate_board(game.board)
    game.last_eval = eval_breakdown["total"]
    game.last_explanation = "تم التراجع عن الحركة الأخيرة."

    return jsonify({
        "status": "success",
        "fen": game.board.fen(),
        "explanation": game.last_explanation,
        "eval": game.last_eval,
        "san_history": game.get_san_history()
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.json or {}
    player_color = data.get("player_color", "white")
    game.reset(player_color=player_color)
    eval_breakdown = evaluate_board(game.board)
    return jsonify({
        "status": "reset",
        "fen": game.board.fen(),
        "explanation": game.last_explanation,
        "eval": game.last_eval,
        "san_history": game.get_san_history(),
        "player_color": game.player_color
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)