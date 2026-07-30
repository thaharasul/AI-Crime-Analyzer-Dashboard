
from api.routes_assistant import assistant_bp

app.register_blueprint(assistant_bp)
from flask import Flask, redirect, url_for

from config import Config
from database.db import init_db, table_has_rows
from database.seed_data import seed

from api.routes_auth import auth_bp, login_required
from api.routes_dashboard import dashboard_bp
from api.routes_prediction import prediction_bp
from api.routes_assistant import assistant_bp
from api.routes_reports import reports_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure the DB exists and has data before the app starts serving
    # requests - avoids a confusing empty-dashboard first run.
    init_db()
    if not table_has_rows():
        seed()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prediction_bp)
   # app.register_blueprint(assistant_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("dashboard.dashboard_page"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
