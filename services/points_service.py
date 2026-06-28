DOUBLE_POINTS_STAGES = {
    "Dieciseisavos",
    "Octavos de final",
    "Cuartos de final",
    "Semifinales",
    "Tercer puesto",
    "Final",
}


def calcular_puntos(pred_local, pred_visitante, real_local, real_visitante, stage=None):
    if real_local is None or real_visitante is None:
        return 0

    exact_points = 6 if stage in DOUBLE_POINTS_STAGES else 3
    result_points = 4 if stage in DOUBLE_POINTS_STAGES else 2

    if pred_local == real_local and pred_visitante == real_visitante:
        return exact_points

    pred_resultado = pred_local - pred_visitante
    real_resultado = real_local - real_visitante

    if pred_resultado > 0 and real_resultado > 0:
        return result_points
    if pred_resultado < 0 and real_resultado < 0:
        return result_points
    if pred_resultado == 0 and real_resultado == 0:
        return result_points

    return 0


def update_prediction_points(prediction):
    prediction.points = calcular_puntos(
        prediction.pred_home_score,
        prediction.pred_away_score,
        prediction.match.home_score,
        prediction.match.away_score,
        prediction.match.stage,
    )
    return prediction.points
