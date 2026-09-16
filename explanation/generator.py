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
    king_attack_change = after_eval["king_attack"] - before_eval["king_attack"]
    open_file_change = after_eval["open_files"] - before_eval["open_files"]
    bishop_diagonal_change = after_eval["bishop_diagonals"] - before_eval["bishop_diagonals"]

    if not mover_is_white:
        material_change = -material_change
        mobility_change = -mobility_change
        king_safety_change = -king_safety_change
        center_change = -center_change
        king_attack_change = -king_attack_change
        open_file_change = -open_file_change
        bishop_diagonal_change = -bishop_diagonal_change

    reasons = []

    if "FORK" in tactics_found:
        reasons.append("(Fork) تهاجم بها قطعتين مهمتين في آن واحد، ما يجبر الخصم على خسارة إحداهما")
    if "CHECK" in tactics_found:
        reasons.append("تضع ملك الخصم في كش مباشر، فتجبره على الرد الفوري وتمنحني دورا (Tempo)")

    measurable_reasons = []
    if material_change > 0.05:
        measurable_reasons.append(("تكسب تفوق قطع واضحا، وهو عامل تزداد قيمته كلما اقتربت اللعبة من نهايتها", material_change))
    if king_safety_change > 0.05:
        measurable_reasons.append(("تُضعف الغطاء الدفاعي حول ملك الخصم، وتفتح خطوطا نحوه", king_safety_change))
    if center_change > 0.05:
        measurable_reasons.append(("تعزز سيطرتي على مربعات الوسط الحيوية، نقطة الانطلاق الرئيسية لأي هجوم", center_change))
    if mobility_change > 0.05:
        measurable_reasons.append(("تزيد من حرية حركة قطعي، وتحوّلها من قطع خاملة إلى قطع اكثر فاعلية", mobility_change))
    if king_attack_change > 0.05:
        measurable_reasons.append(("تقرّب قطعي الثقيلة (الرخ/الوزير) من ملك الخصم استعداداً لهجوم حاسم", king_attack_change))
    if open_file_change > 0.05:
        measurable_reasons.append(("تضع رخّي على عمود مفتوح، فيتحرك بحرية بلا عوائق من بيادقي", open_file_change))
    if bishop_diagonal_change > 0.05:
        measurable_reasons.append(("تضع فيلي على القطر الطويل، حيث تتسع رؤيته لأقصى عدد من المربعات", bishop_diagonal_change))

    measurable_reasons.sort(key=lambda pair: pair[1], reverse=True)
    for label, value in measurable_reasons:
        reasons.append(label)

    if len(reasons) == 0:
        reasons.append("تحسّن ميزان القوى الاستراتيجي على الرقعة بشكل عام")

    text = "اخترت " + move_san + " لأنها " + reasons[0] + "."

    if len(reasons) > 1:
        text = text + " إضافة إلى ذلك، فهي " + reasons[1] + "."

    if alt_move is not None:
        alt_san = board.san(alt_move)
        gap = abs(best_score - alt_score)
        if gap > 1.0:
            text = text + " فكّرت أيضاً في " + alt_san + "، لكنها أضعف بفارق واضح في ميزان القوى."
        else:
            text = text + " كانت " + alt_san + " بديلاً قريباً من حيث القوة، لكن " + move_san + " ترجّحت بفارق طفيف."

    text = text + " (تقييم الرقعة الآن: " + format(best_score, "+g") + ")"

    return text