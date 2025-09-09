"""
Database models for B.E.L.L.A. enterprise scaling
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    """User accounts for multi-tenant B.E.L.L.A."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    subscription_tier = db.Column(db.String(50), default='free')  # free, pro, enterprise
    api_quota_used = db.Column(db.Integer, default=0)
    api_quota_limit = db.Column(db.Integer, default=100)  # per month
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    calendars = db.relationship('ContentCalendar', backref='user', lazy=True)
    templates = db.relationship('ContentTemplate', backref='user', lazy=True)

class ContentCalendar(db.Model):
    """Generated content calendars for tracking and management"""
    __tablename__ = 'content_calendars'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    niche = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    days_generated = db.Column(db.Integer, nullable=False)
    generation_method = db.Column(db.String(50))  # 'ai', 'fallback', 'template'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    calendar_data = db.Column(db.JSON)  # Store the actual calendar content
    
    # Performance tracking
    generation_time = db.Column(db.Float)  # seconds
    success_rate = db.Column(db.Float)  # percentage of successful posts

class ContentPost(db.Model):
    """Individual posts within calendars for detailed analytics"""
    __tablename__ = 'content_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('content_calendars.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.String(200))
    script = db.Column(db.Text)
    visual = db.Column(db.Text)
    caption = db.Column(db.Text)
    hashtags = db.Column(db.String(500))
    post_time = db.Column(db.String(50))
    cta = db.Column(db.String(200))
    ai_prompt = db.Column(db.Text)
    generation_source = db.Column(db.String(50))  # 'openai', 'fallback', 'template'
    
    # Analytics
    engagement_score = db.Column(db.Float)  # if connected to social platforms
    performance_rating = db.Column(db.Integer)  # 1-5 rating

class ContentTemplate(db.Model):
    """Custom templates for users to save and reuse"""
    __tablename__ = 'content_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_name = db.Column(db.String(200), nullable=False)
    niche = db.Column(db.String(200), nullable=False)
    template_data = db.Column(db.JSON)  # Structured template content
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)  # Allow sharing templates

class APIUsage(db.Model):
    """Track API usage for billing and analytics"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    request_data = db.Column(db.JSON)
    response_time = db.Column(db.Float)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    credits_used = db.Column(db.Integer, default=1)

class GenerationQueue(db.Model):
    """Queue system for handling large batch requests"""
    __tablename__ = 'generation_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_data = db.Column(db.JSON)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    priority = db.Column(db.Integer, default=1)  # Higher number = higher priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    result_data = db.Column(db.JSON)
    error_message = db.Column(db.Text)

class SystemMetrics(db.Model):
    """System performance and health metrics"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    additional_data = db.Column(db.JSON)