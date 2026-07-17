

from ml.predictor import predict, get_metrics


def run(scenario: dict) -> dict:
    result = predict(scenario)
    result["model_metrics"] = get_metrics()
    return result
