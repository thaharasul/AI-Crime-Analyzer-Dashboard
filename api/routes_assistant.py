

from flask import Blueprint, render_template, request, jsonify

from services import assistant_service
from api.routes_auth import login_required

assistant_bp = Blueprint("assistant", __name__)

SUGGESTED_QUERIES = [
    "Why has robbery increased in Zone 4?",
    "Compare cybercrime trends year over year.",
    "What legal sections apply to burglary?",
    "What IPC section applies to online fraud?",
]


@assistant_bp.route("/assistant")
@login_required
def assistant_page():
    return render_template("assistant.html", suggested_queries=SUGGESTED_QUERIES)


@assistant_bp.route("/api/assistant/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(force=True)
    question = (payload.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    try:
        result = assistant_service.answer_question(question)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)
