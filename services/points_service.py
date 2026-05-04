def calcular_puntos(pred_local, pred_visitante, real_local, real_visitante):
    if real_local is None or real_visitante is None:
        return 0

    if pred_local == real_local and pred_visitante == real_visitante:
        return 3

    pred_resultado = pred_local - pred_visitante
    real_resultado = real_local - real_visitante

    if pred_resultado > 0 and real_resultado > 0:
        return 2
    if pred_resultado < 0 and real_resultado < 0:
        return 2
    if pred_resultado == 0 and real_resultado == 0:
        return 2

    return 0


def update_prediction_points(prediction):
    prediction.points = calcular_puntos(
        prediction.pred_home_score,
        prediction.pred_away_score,
        prediction.match.home_score,
        prediction.match.away_score,
    )
    return prediction.points
