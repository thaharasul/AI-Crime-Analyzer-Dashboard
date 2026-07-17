

from flask import Blueprint, render_template, request, send_file, jsonify

from agents import coordinator
from utils import report_generator
from database.db import db_cursor
from api.routes_auth import login_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports_page():
    with db_cursor() as cur:
        cur.execute("SELECT DISTINCT zone FROM crimes ORDER BY zone")
        zones = [r["zone"] for r in cur.fetchall()]
        cur.execute("SELECT DISTINCT category FROM crimes ORDER BY category")
        categories = [r["category"] for r in cur.fetchall()]
    return render_template("reports.html", zones=zones, categories=categories)


@reports_bp.route("/api/reports/export/csv")
@login_required
def export_csv():
    filters = {
        "zone": request.args.get("zone") or None,
        "category": request.args.get("category") or None,
        "status": request.args.get("status") or None,
    }
    buffer = report_generator.generate_csv_export(filters)
    return send_file(
        buffer, mimetype="text/csv", as_attachment=True,
        download_name="crime_report.csv",
    )


@reports_bp.route("/api/reports/export/pdf")
@login_required
def export_pdf():
    briefing = coordinator.handle_request("full_briefing")
    buffer = report_generator.generate_pdf_briefing(briefing)
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True,
        download_name="crime_executive_briefing.pdf",
    )


@reports_bp.route("/api/reports/briefing")
@login_required
def briefing_preview():
    """Lets the front end show the briefing content before the user downloads it."""
    briefing = coordinator.handle_request("full_briefing")
    return jsonify(briefing)
