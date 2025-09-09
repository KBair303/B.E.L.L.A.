"""
Enterprise Flask application setup for B.E.L.L.A.
"""
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern for better scaling"""
    app = Flask(__name__)
    
    # Security and session configuration
    app.secret_key = os.environ.get("SESSION_SECRET") or "bella-production-secret"
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration with connection pooling
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,  # Increased for scaling
        'max_overflow': 30,  # Handle traffic spikes
        'pool_timeout': 30
    }
    
    # Enterprise configuration
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload
    app.config["RATELIMIT_STORAGE_URL"] = os.environ.get("REDIS_URL")  # For rate limiting
    
    # Initialize extensions
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")
    
    return app

# Create the application instance
app = create_app()