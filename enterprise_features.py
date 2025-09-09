"""
Enterprise scaling features for B.E.L.L.A.
"""
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from models import db, User, APIUsage, GenerationQueue, SystemMetrics
import logging

logger = logging.getLogger(__name__)

class EnterpriseFeatures:
    """Enterprise features for scaling B.E.L.L.A."""
    
    @staticmethod
    def track_api_usage(endpoint_name):
        """Decorator to track API usage and performance"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                start_time = time.time()
                user_id = getattr(g, 'user_id', None)
                success = True
                error_msg = None
                
                try:
                    result = f(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    logger.error(f"API Error in {endpoint_name}: {error_msg}")
                    raise
                finally:
                    # Record usage
                    response_time = time.time() - start_time
                    usage = APIUsage(
                        user_id=user_id,
                        endpoint=endpoint_name,
                        request_data=request.get_json() if request.is_json else None,
                        response_time=response_time,
                        success=success,
                        error_message=error_msg,
                        credits_used=1
                    )
                    try:
                        db.session.add(usage)
                        db.session.commit()
                    except Exception as db_error:
                        logger.error(f"Failed to record API usage: {db_error}")
                        db.session.rollback()
            
            return decorated_function
        return decorator
    
    @staticmethod
    def rate_limit_check(user_id, requests_per_hour=100):
        """Check if user has exceeded rate limit"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_requests = APIUsage.query.filter(
            APIUsage.user_id == user_id,
            APIUsage.timestamp >= one_hour_ago
        ).count()
        
        return recent_requests < requests_per_hour
    
    @staticmethod
    def quota_check(user_id):
        """Check if user has API quota remaining"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        return user.api_quota_used < user.api_quota_limit
    
    @staticmethod
    def queue_large_request(user_id, request_data, priority=1):
        """Queue large requests for background processing"""
        queue_item = GenerationQueue(
            user_id=user_id,
            request_data=request_data,
            priority=priority
        )
        db.session.add(queue_item)
        db.session.commit()
        
        logger.info(f"Queued large request for user {user_id}")
        return queue_item.id
    
    @staticmethod
    def process_queue_item(queue_id):
        """Process a queued generation request"""
        queue_item = GenerationQueue.query.get(queue_id)
        if not queue_item or queue_item.status != 'pending':
            return False
        
        # Update status
        queue_item.status = 'processing'
        queue_item.started_at = datetime.utcnow()
        db.session.commit()
        
        try:
            # Process the request (integrate with existing generation logic)
            request_data = queue_item.request_data
            
            # This would call your existing content generation functions
            # result = generate_large_calendar(request_data)
            
            # For now, simulate processing
            time.sleep(2)  # Simulate work
            result = {"status": "completed", "calendar_id": "sample_id"}
            
            # Update completion
            queue_item.status = 'completed'
            queue_item.completed_at = datetime.utcnow()
            queue_item.result_data = result
            db.session.commit()
            
            logger.info(f"Completed queue item {queue_id}")
            return True
            
        except Exception as e:
            queue_item.status = 'failed'
            queue_item.error_message = str(e)
            queue_item.completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.error(f"Failed to process queue item {queue_id}: {e}")
            return False
    
    @staticmethod
    def record_system_metric(metric_name, value, additional_data=None):
        """Record system performance metrics"""
        metric = SystemMetrics(
            metric_name=metric_name,
            metric_value=value,
            additional_data=additional_data
        )
        try:
            db.session.add(metric)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")
            db.session.rollback()
    
    @staticmethod
    def get_system_health():
        """Get current system health metrics"""
        try:
            # Get recent metrics
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            metrics = db.session.query(SystemMetrics).filter(
                SystemMetrics.timestamp >= one_hour_ago
            ).all()
            
            # Calculate health indicators
            avg_response_time = db.session.query(db.func.avg(APIUsage.response_time)).filter(
                APIUsage.timestamp >= one_hour_ago
            ).scalar() or 0
            
            success_rate = db.session.query(
                db.func.avg(db.cast(APIUsage.success, db.Float))
            ).filter(
                APIUsage.timestamp >= one_hour_ago
            ).scalar() or 1.0
            
            active_users = User.query.filter(User.is_active == True).count()
            pending_queue = GenerationQueue.query.filter(
                GenerationQueue.status == 'pending'
            ).count()
            
            return {
                "status": "healthy" if success_rate > 0.95 else "degraded",
                "avg_response_time": avg_response_time,
                "success_rate": success_rate * 100,
                "active_users": active_users,
                "queue_backlog": pending_queue,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {"status": "error", "message": str(e)}

class BatchProcessor:
    """Handle large batch content generation requests"""
    
    @staticmethod
    def estimate_processing_time(num_days, num_businesses):
        """Estimate processing time for batch requests"""
        # Base processing time per day per business (in seconds)
        base_time = 2.0
        return num_days * num_businesses * base_time
    
    @staticmethod
    def split_large_request(businesses, days, max_batch_size=50):
        """Split large requests into manageable batches"""
        total_items = len(businesses) * days
        
        if total_items <= max_batch_size:
            return [{"businesses": businesses, "days": days}]
        
        # Split by businesses first, then by days if needed
        batches = []
        items_per_batch = max_batch_size // days if days > 0 else max_batch_size
        
        for i in range(0, len(businesses), items_per_batch):
            batch_businesses = businesses[i:i + items_per_batch]
            batches.append({
                "businesses": batch_businesses,
                "days": days
            })
        
        return batches
    
    @staticmethod
    def process_batch_async(batch_data, user_id):
        """Process a batch asynchronously (would integrate with Celery/Redis in production)"""
        try:
            # This would be implemented with proper async task queue
            # For now, simulate batch processing
            businesses = batch_data["businesses"]
            days = batch_data["days"]
            
            results = []
            for business in businesses:
                # Generate calendar for this business
                # result = generate_content_calendar(business["niche"], business["city"], days)
                result = {
                    "business": business,
                    "calendar_generated": True,
                    "posts_count": days
                }
                results.append(result)
            
            return {
                "status": "completed",
                "results": results,
                "total_businesses": len(businesses),
                "total_posts": len(businesses) * days
            }
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

def initialize_enterprise_features(app):
    """Initialize enterprise features with the Flask app"""
    
    @app.before_request
    def track_request_metrics():
        """Track request metrics for monitoring"""
        g.request_start_time = time.time()
    
    @app.after_request
    def log_request_metrics(response):
        """Log request completion metrics"""
        if hasattr(g, 'request_start_time'):
            response_time = time.time() - g.request_start_time
            
            # Record metric asynchronously to avoid blocking requests
            try:
                EnterpriseFeatures.record_system_metric(
                    "response_time",
                    response_time,
                    {"endpoint": request.endpoint, "method": request.method}
                )
            except Exception as e:
                logger.warning(f"Failed to record request metric: {e}")
        
        return response
    
    logger.info("Enterprise features initialized")