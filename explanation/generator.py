import chess

from engine.evaluation import evaluate_board
from engine.tactics import detect_tactics


def generate_explanation(board, search_result):
    move = search_result["best_move"]
    best_score = search_result["best_score"]
    alt_move = search_result["alternative_move"]
    alt_score = search_result["alt_score"]

    mover_is_white = (board.turn == chess.WHITE)

    before_eval = evaluate_board(board)
    tactics_found = detect_tactics(board, move)

    board.push(move)
    after_eval = evaluate_board(board)
    board.pop()

    move_san = board.san(move)

   
    material_change = after_eval["material"] - before_eval["material"]
    mobility_change = after_eval["mobility"] - before_eval["mobility"]
    king_safety_change = after_eval["king_safety"] - before_eval["king_safety"]
    center_change = after_eval["center_control"] - before_eval["center_control"]

    if not mover_is_white:
        material_change = -material_change
        mobility_change = -mobility_change
        king_safety_change = -king_safety_change
        center_change = -center_change

    reasons = []

    if "FORK" in tactics_found:
        reasons.append("تهاجم قطعتين مهمتين للخصم في نفس الوقت (شوكة)")
    if "CHECK" in tactics_found:
        reasons.append("تضع ملك الخصم في وضع كش ")

    measurable_reasons = []
    if material_change > 0.05:
        measurable_reasons.append(("تكسب عتاد إضافي", material_change))
    if center_change > 0.05:
        measurable_reasons.append(("تزيد السيطرة على المركز", center_change))
    if mobility_change > 0.05:
        measurable_reasons.append(("تمنح القطع حرية حركة أكبر", mobility_change))
    if king_safety_change > 0.05:
        measurable_reasons.append(("تحسن أمان الملك", king_safety_change))

    measurable_reasons.sort(key=lambda pair: pair[1], reverse=True)
    for label, value in measurable_reasons:
        reasons.append(label)

    if len(reasons) == 0:
        reasons.append("تحسن الوضع العام للرقعة بشكل عام")

    text = "لعبت " + move_san + " لأنها " + reasons[0] + "."

    if len(reasons) > 1:
        text = text + " كما أنها " + reasons[1] + "."

    if alt_move is not None:
        alt_san = board.san(alt_move)
        gap = abs(best_score - alt_score)
        if gap > 1.0:
            text = text + " كانت هناك حركة بديلة (" + alt_san + ") لكنها أضعف بفارق واضح."
        else:
            text = text + " الحركة البديلة (" + alt_san + ") كانت قريبة من حيث القوة، لكن " + move_san + " أفضل قليلاً."

    text = text + " (تقييم الرقعة الآن: " + format(best_score, "+g") + ")"

    return text
