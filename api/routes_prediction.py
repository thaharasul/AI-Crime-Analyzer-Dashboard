
from flask import Blueprint, render_template, request, jsonify

from agents import prediction_agent
from ml.predictor import get_metrics
from api.routes_auth import login_required

prediction_bp = Blueprint("prediction", __name__)

ZONES = ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@prediction_bp.route("/prediction")
@login_required
def prediction_page():
    metrics = get_metrics()
    return render_template(
        "prediction.html",
        zones=ZONES, severities=SEVERITIES, days=DAYS, metrics=metrics,
    )


@prediction_bp.route("/api/prediction/run", methods=["POST"])
@login_required
def run_prediction():
    payload = request.get_json(force=True)

    scenario = {
        "zone": payload.get("zone", "Zone 1"),
        "severity": payload.get("severity", "Medium"),
        "day_of_week": payload.get("day_of_week", "Monday"),
        "weapon_involved": int(payload.get("weapon_involved", 0)),
        "hour_of_day": int(payload.get("hour_of_day", 12)),
        "victim_age": int(payload.get("victim_age", 30)),
    }

    try:
        result = prediction_agent.run(scenario)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


@prediction_bp.route("/api/prediction/metrics")
@login_required
def prediction_metrics():
    metrics = get_metrics()
    if metrics is None:
        return jsonify({"error": "Model has not been trained yet."}), 404
    return jsonify(metrics)
