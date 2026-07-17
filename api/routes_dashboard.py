

from datetime import datetime, timedelta

from flask import Blueprint, render_template, jsonify

from database.db import db_cursor
from api.routes_auth import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html")


@dashboard_bp.route("/api/dashboard/summary")
@login_required
def summary():
    today = datetime.now().strftime("%Y-%m-%d")

    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM crimes")
        total = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) AS c FROM crimes WHERE status = 'Solved'")
        solved = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) AS c FROM crimes WHERE status != 'Solved'")
        pending = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) AS c FROM crimes WHERE date_reported = ?", (today,))
        today_count = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(DISTINCT category) AS c FROM crimes")
        category_count = cur.fetchone()["c"]

    return jsonify({
        "total_crimes": total,
        "solved_cases": solved,
        "pending_cases": pending,
        "today_cases": today_count,
        "crime_categories": category_count,
    })


@dashboard_bp.route("/api/dashboard/category-distribution")
@login_required
def category_distribution():
    with db_cursor() as cur:
        cur.execute("""
            SELECT category, COUNT(*) AS count
            FROM crimes GROUP BY category ORDER BY count DESC
        """)
        rows = cur.fetchall()
    return jsonify([{"category": r["category"], "count": r["count"]} for r in rows])


@dashboard_bp.route("/api/dashboard/zone-distribution")
@login_required
def zone_distribution():
    with db_cursor() as cur:
        cur.execute("""
            SELECT zone, COUNT(*) AS count
            FROM crimes GROUP BY zone ORDER BY count DESC
        """)
        rows = cur.fetchall()
    return jsonify([{"zone": r["zone"], "count": r["count"]} for r in rows])


@dashboard_bp.route("/api/dashboard/monthly-trend")
@login_required
def monthly_trend():
    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    with db_cursor() as cur:
        cur.execute("""
            SELECT strftime('%Y-%m', date_reported) AS month, COUNT(*) AS count
            FROM crimes
            WHERE date_reported >= ?
            GROUP BY month ORDER BY month ASC
        """, (cutoff,))
        rows = cur.fetchall()
    return jsonify([{"month": r["month"], "count": r["count"]} for r in rows])


@dashboard_bp.route("/api/dashboard/status-breakdown")
@login_required
def status_breakdown():
    with db_cursor() as cur:
        cur.execute("""
            SELECT status, COUNT(*) AS count
            FROM crimes GROUP BY status ORDER BY count DESC
        """)
        rows = cur.fetchall()
    return jsonify([{"status": r["status"], "count": r["count"]} for r in rows])


@dashboard_bp.route("/api/dashboard/map-points")
@login_required
def map_points():
    with db_cursor() as cur:
        cur.execute("""
            SELECT crime_type, category, latitude, longitude, severity,
                   zone, location_name, date_reported, status
            FROM crimes
            ORDER BY date_reported DESC
            LIMIT 500
        """)
        rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


@dashboard_bp.route("/api/dashboard/dangerous-locations")
@login_required
def dangerous_locations():
    with db_cursor() as cur:
        cur.execute("""
            SELECT location_name, COUNT(*) AS count,
                   SUM(CASE WHEN severity IN ('High', 'Critical') THEN 1 ELSE 0 END) AS severe_count
            FROM crimes
            GROUP BY location_name
            ORDER BY severe_count DESC, count DESC
            LIMIT 8
        """)
        rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])
