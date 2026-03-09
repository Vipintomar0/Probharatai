"""ProBharatAI - AI Desktop Automation Platform
Main entry point for the backend server.
"""
import logging
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import (
    HOST, PORT, DEBUG, SECRET_KEY, LOG_LEVEL, LOG_FILE, DATA_DIR
)
from database.models import init_db
from api.routes import api_bp

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("probharatai")


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    # CORS for React frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    app.socketio = socketio

    # Register API routes
    app.register_blueprint(api_bp, url_prefix="/api")

    # Initialize database
    init_db()

    # Health check
    @app.route("/")
    def index():
        return {
            "name": "ProBharatAI",
            "version": "1.0.0",
            "status": "running",
            "description": "Open-Source AI Desktop Automation Platform",
        }

    logger.info("🚀 ProBharatAI backend initialized successfully")
    return app, socketio


if __name__ == "__main__":
    app, socketio = create_app()
    logger.info(f"Starting ProBharatAI on {HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
