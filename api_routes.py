"""
Enterprise API routes for B.E.L.L.A. scaling
"""
from flask import Blueprint, request, jsonify, render_template
from models import db, User, ContentCalendar, ContentPost, ContentTemplate
from enterprise_features import EnterpriseFeatures, BatchProcessor
from ssds_ai import generate_social_post
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """System health endpoint for monitoring"""
    health_data = EnterpriseFeatures.get_system_health()
    return jsonify(health_data)

@api_bp.route('/generate/single', methods=['POST'])
@EnterpriseFeatures.track_api_usage('generate_single')
def generate_single_calendar():
    """Generate content calendar for single business"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['niche', 'city', 'days']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        niche = data['niche']
        city = data['city']
        days = min(int(data['days']), 30)  # Cap at 30 days for API
        user_id = data.get('user_id', 1)  # Default user for now
        
        # Check quotas and rate limits
        if not EnterpriseFeatures.quota_check(user_id):
            return jsonify({"error": "API quota exceeded"}), 429
        
        if not EnterpriseFeatures.rate_limit_check(user_id):
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        # Generate calendar
        start_time = datetime.utcnow()
        calendar_data = []
        
        for day in range(1, days + 1):
            try:
                post = generate_social_post(niche, city, day, calendar_data)
                if post:
                    # Parse the post data
                    fields = post.split('|')
                    if len(fields) >= 9:
                        post_data = {
                            'day': day,
                            'activity': fields[1].strip(),
                            'script': fields[2].strip(),
                            'visual': fields[3].strip(),
                            'caption': fields[4].strip(),
                            'hashtags': fields[5].strip(),
                            'time': fields[6].strip(),
                            'cta': fields[7].strip(),
                            'ai_prompt': fields[8].strip()
                        }
                        calendar_data.append(post_data)
            except Exception as e:
                logger.error(f"Failed to generate post for day {day}: {e}")
                continue
        
        # Save to database
        calendar = ContentCalendar(
            user_id=user_id,
            niche=niche,
            city=city,
            days_generated=len(calendar_data),
            generation_method='api',
            calendar_data=calendar_data,
            generation_time=(datetime.utcnow() - start_time).total_seconds(),
            success_rate=(len(calendar_data) / days) * 100 if days > 0 else 0
        )
        
        db.session.add(calendar)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "calendar_id": calendar.id,
            "posts_generated": len(calendar_data),
            "calendar_data": calendar_data
        })
        
    except Exception as e:
        logger.error(f"API generation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/generate/batch', methods=['POST'])
@EnterpriseFeatures.track_api_usage('generate_batch')
def generate_batch_calendars():
    """Generate content calendars for multiple businesses"""
    try:
        data = request.get_json()
        
        # Validate input
        if 'businesses' not in data or 'days' not in data:
            return jsonify({"error": "Missing businesses or days"}), 400
        
        businesses = data['businesses']
        days = min(int(data['days']), 30)
        user_id = data.get('user_id', 1)
        
        # Estimate processing time
        estimated_time = BatchProcessor.estimate_processing_time(days, len(businesses))
        
        # If large request, queue it
        if len(businesses) > 10 or estimated_time > 300:  # 5 minutes
            queue_id = EnterpriseFeatures.queue_large_request(
                user_id, 
                {"businesses": businesses, "days": days},
                priority=2
            )
            
            return jsonify({
                "status": "queued",
                "queue_id": queue_id,
                "estimated_time": estimated_time,
                "message": "Large request queued for processing"
            })
        
        # Process smaller requests immediately
        batches = BatchProcessor.split_large_request(businesses, days)
        all_results = []
        
        for batch in batches:
            batch_result = BatchProcessor.process_batch_async(batch, user_id)
            all_results.extend(batch_result.get('results', []))
        
        return jsonify({
            "status": "completed",
            "total_businesses": len(businesses),
            "total_calendars": len(all_results),
            "results": all_results
        })
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/queue/status/<int:queue_id>', methods=['GET'])
def check_queue_status(queue_id):
    """Check status of queued generation request"""
    from models import GenerationQueue
    
    queue_item = GenerationQueue.query.get(queue_id)
    if not queue_item:
        return jsonify({"error": "Queue item not found"}), 404
    
    response_data = {
        "queue_id": queue_id,
        "status": queue_item.status,
        "created_at": queue_item.created_at.isoformat(),
        "priority": queue_item.priority
    }
    
    if queue_item.started_at:
        response_data["started_at"] = queue_item.started_at.isoformat()
    
    if queue_item.completed_at:
        response_data["completed_at"] = queue_item.completed_at.isoformat()
        response_data["result"] = queue_item.result_data
    
    if queue_item.error_message:
        response_data["error"] = queue_item.error_message
    
    return jsonify(response_data)

@api_bp.route('/templates', methods=['GET', 'POST'])
@EnterpriseFeatures.track_api_usage('templates')
def manage_templates():
    """Manage content templates"""
    if request.method == 'GET':
        user_id = request.args.get('user_id', 1)
        templates = ContentTemplate.query.filter_by(user_id=user_id).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                "id": template.id,
                "name": template.template_name,
                "niche": template.niche,
                "usage_count": template.usage_count,
                "created_at": template.created_at.isoformat()
            })
        
        return jsonify({"templates": template_list})
    
    elif request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id', 1)
        
        template = ContentTemplate(
            user_id=user_id,
            template_name=data['name'],
            niche=data['niche'],
            template_data=data['template_data']
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "template_id": template.id,
            "message": "Template saved successfully"
        })

@api_bp.route('/analytics/usage', methods=['GET'])
def get_usage_analytics():
    """Get usage analytics for user"""
    user_id = request.args.get('user_id', 1)
    days = int(request.args.get('days', 30))
    
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get usage statistics
    from models import APIUsage
    usage_stats = db.session.query(
        db.func.date(APIUsage.timestamp).label('date'),
        db.func.count(APIUsage.id).label('requests'),
        db.func.avg(APIUsage.response_time).label('avg_response_time'),
        db.func.sum(db.cast(APIUsage.success, db.Integer)).label('successful_requests')
    ).filter(
        APIUsage.user_id == user_id,
        APIUsage.timestamp >= start_date
    ).group_by(
        db.func.date(APIUsage.timestamp)
    ).all()
    
    analytics_data = []
    for stat in usage_stats:
        analytics_data.append({
            "date": stat.date.isoformat(),
            "requests": stat.requests,
            "avg_response_time": float(stat.avg_response_time or 0),
            "success_rate": (stat.successful_requests / stat.requests * 100) if stat.requests > 0 else 0
        })
    
    return jsonify({
        "user_id": user_id,
        "period_days": days,
        "analytics": analytics_data
    })

@api_bp.route('/calendars', methods=['GET'])
def list_calendars():
    """List generated calendars for user"""
    user_id = request.args.get('user_id', 1)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    calendars = ContentCalendar.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    calendar_list = []
    for calendar in calendars.items:
        calendar_list.append({
            "id": calendar.id,
            "niche": calendar.niche,
            "city": calendar.city,
            "days_generated": calendar.days_generated,
            "generation_method": calendar.generation_method,
            "created_at": calendar.created_at.isoformat(),
            "success_rate": calendar.success_rate
        })
    
    return jsonify({
        "calendars": calendar_list,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": calendars.total,
            "pages": calendars.pages
        }
    })

def register_api_routes(app):
    """Register API routes with the Flask app"""
    app.register_blueprint(api_bp)
    logger.info("API routes registered successfully")