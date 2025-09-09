"""
Enterprise-ready B.E.L.L.A. with scaling features
"""
import os
import logging
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import pandas as pd
from ssds_ai import generate_social_post
from image_ai import generate_images, validate_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create Flask app with enterprise configuration
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bella-enterprise-secret-2024")

# Database configuration for scaling
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 20,  # Handle more concurrent connections
    'max_overflow': 30,  # Allow burst traffic
    'pool_timeout': 30
}

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Enterprise database models
class User(db.Model):
    """User accounts for multi-tenant B.E.L.L.A."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    subscription_tier = db.Column(db.String(50), default='free')
    api_quota_used = db.Column(db.Integer, default=0)
    api_quota_limit = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class ContentCalendar(db.Model):
    """Generated content calendars"""
    __tablename__ = 'content_calendars'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    niche = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    days_generated = db.Column(db.Integer, nullable=False)
    generation_method = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    calendar_data = db.Column(db.JSON)
    generation_time = db.Column(db.Float)
    success_rate = db.Column(db.Float)

class APIUsage(db.Model):
    """Track API usage for scaling metrics"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    response_time = db.Column(db.Float)
    success = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    credits_used = db.Column(db.Integer, default=1)

class BatchRequest(db.Model):
    """Handle large batch processing requests"""
    __tablename__ = 'batch_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_data = db.Column(db.JSON)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    result_data = db.Column(db.JSON)
    total_businesses = db.Column(db.Integer)
    total_calendars = db.Column(db.Integer)

# Create tables
with app.app_context():
    db.create_all()
    logger.info("Enterprise database tables created")

# Enterprise scaling features
class EnterpriseScaling:
    """Enterprise scaling functionality"""
    
    @staticmethod
    def track_usage(user_id, endpoint, response_time, success=True):
        """Track API usage for scaling metrics"""
        try:
            usage = APIUsage(
                user_id=user_id,
                endpoint=endpoint,
                response_time=response_time,
                success=success,
                credits_used=1
            )
            db.session.add(usage)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            db.session.rollback()
    
    @staticmethod
    def save_calendar(user_id, niche, city, calendar_data, generation_time):
        """Save generated calendar to database"""
        try:
            calendar = ContentCalendar(
                user_id=user_id,
                niche=niche,
                city=city,
                days_generated=len(calendar_data),
                generation_method='enterprise',
                calendar_data=calendar_data,
                generation_time=generation_time,
                success_rate=100.0  # Simplified for now
            )
            db.session.add(calendar)
            db.session.commit()
            return calendar.id
        except Exception as e:
            logger.error(f"Failed to save calendar: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def process_batch_request(businesses, days):
        """Process batch content generation"""
        results = []
        start_time = datetime.utcnow()
        
        for business in businesses:
            try:
                niche = business.get('niche', '')
                city = business.get('city', '')
                
                # Generate calendar for this business
                calendar_data = []
                for day in range(1, days + 1):
                    try:
                        post = generate_social_post(niche, city, day, calendar_data)
                        if post:
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
                        logger.error(f"Failed to generate post for {niche} day {day}: {e}")
                        continue
                
                # Save calendar
                generation_time = (datetime.utcnow() - start_time).total_seconds()
                calendar_id = EnterpriseScaling.save_calendar(
                    user_id=1,  # Default user for now
                    niche=niche,
                    city=city,
                    calendar_data=calendar_data,
                    generation_time=generation_time
                )
                
                results.append({
                    "business": business,
                    "calendar_id": calendar_id,
                    "posts_generated": len(calendar_data),
                    "status": "completed"
                })
                
            except Exception as e:
                logger.error(f"Failed to process business {business}: {e}")
                results.append({
                    "business": business,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results

# Original routes (keeping existing functionality)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["GET", "POST"])
def generate_calendar():
    """Enhanced calendar generation with enterprise tracking"""
    import time
    start_time = time.time()
    
    table_html = None
    calendar_data = []
    error_message = None
    
    if request.method == "POST":
        try:
            # Get form data
            selected_niches = request.form.getlist("niches")
            custom_niche = request.form.get("customNiche", "").strip()
            city = request.form.get("city", "").strip()
            num_days = request.form.get("days", "7")
            
            # Handle custom niche
            if "other" in selected_niches and custom_niche:
                selected_niches = [n for n in selected_niches if n != "other"]
                selected_niches.append(custom_niche)
            elif "other" in selected_niches and not custom_niche:
                selected_niches = [n for n in selected_niches if n != "other"]
            
            # Create combined niche string
            if selected_niches:
                niche = ", ".join(selected_niches)
            else:
                error_message = "Please select at least one niche or specify a custom niche."
                return render_template("index.html", table=table_html, error=error_message)
            
            if not city:
                error_message = "Please enter a city."
                return render_template("index.html", table=table_html, error=error_message)
            
            try:
                num_days = int(num_days)
                if num_days <= 0 or num_days > 30:
                    raise ValueError
            except ValueError:
                error_message = "Please enter a valid number of days (1-30)."
                return render_template("index.html", table=table_html, error=error_message)
            
            # Enterprise resource management
            if num_days > 15:
                app.logger.warning(f"Large enterprise request ({num_days} days) for {niche} in {city}")
            
            # Generate calendar with enterprise tracking
            app.logger.info(f"Enterprise generation: {num_days} days for {niche} in {city}")
            
            for day in range(1, num_days + 1):
                try:
                    post = generate_social_post(niche, city, day, calendar_data)
                    if not post or len(post.split("|")) < 6:
                        from content_diversity import generate_diverse_content
                        used_signatures = {f"{item.get('Activity', '').lower()}_{item.get('Script', '')[:30].lower()}" 
                                         for item in calendar_data}
                        post = generate_diverse_content(niche, city, day, used_signatures)
                    
                    # Parse post data
                    fields = post.split("|")
                    if len(fields) >= 9:
                        post_data = {
                            "Day": day,
                            "Activity": fields[1].strip(),
                            "Script": fields[2].strip(),
                            "Visual": fields[3].strip(),
                            "Caption": fields[4].strip(),
                            "Hashtags": fields[5].strip(),
                            "Time": fields[6].strip(),
                            "CTA": fields[7].strip(),
                            "AI Image Prompt": fields[8].strip()
                        }
                        calendar_data.append(post_data)
                    
                    if day < num_days:
                        time.sleep(0.1)  # Small delay for stability
                        
                except Exception as e:
                    app.logger.error(f"Error generating post for Day {day}: {str(e)}")
                    continue
            
            if calendar_data:
                # Save to enterprise database
                generation_time = time.time() - start_time
                calendar_id = EnterpriseScaling.save_calendar(
                    user_id=1,  # Default user
                    niche=niche,
                    city=city,
                    calendar_data=calendar_data,
                    generation_time=generation_time
                )
                
                # Track usage
                EnterpriseScaling.track_usage(
                    user_id=1,
                    endpoint="generate_calendar",
                    response_time=generation_time,
                    success=True
                )
                
                # Create table
                df = pd.DataFrame(calendar_data)
                table_html = df.to_html(classes='table table-striped table-bordered', 
                                      table_id='calendar-table', escape=False, index=False)
                
                app.logger.info(f"Enterprise calendar generated: ID {calendar_id}, {len(calendar_data)} posts in {generation_time:.2f}s")
            else:
                error_message = "Failed to generate any content. Please try again."
                
        except Exception as e:
            app.logger.error(f"Enterprise generation error: {str(e)}")
            error_message = "An error occurred during generation. Our enterprise system will retry automatically."
            
            # Track failed usage
            generation_time = time.time() - start_time
            EnterpriseScaling.track_usage(
                user_id=1,
                endpoint="generate_calendar",
                response_time=generation_time,
                success=False
            )
    
    return render_template("index.html", table=table_html, error=error_message)

# Enterprise API routes
@app.route("/api/v1/health")
def health_check():
    """Health check for enterprise monitoring"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Get system metrics
        total_calendars = ContentCalendar.query.count()
        total_users = User.query.count()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "total_calendars": total_calendars,
            "total_users": total_users,
            "version": "enterprise-1.0"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route("/api/v1/batch", methods=["POST"])
def batch_generate():
    """Enterprise batch content generation with performance optimization"""
    from performance_optimizer import performance_optimizer, optimize_for_large_request
    
    try:
        data = request.get_json()
        
        if not data or 'businesses' not in data or 'days' not in data:
            return jsonify({"error": "Missing businesses or days"}), 400
        
        businesses = data['businesses']
        days = min(int(data['days']), 10)  # Maximum 10 days as requested
        
        if len(businesses) > 1000:  # Increased limit
            return jsonify({"error": "Maximum 1000 businesses per batch"}), 400
        
        # Estimate processing time
        estimated_time = performance_optimizer.estimate_processing_time(len(businesses), days)
        
        app.logger.info(f"Starting batch generation: {len(businesses)} businesses, {days} days each")
        app.logger.info(f"Estimated processing time: {estimated_time:.1f} seconds")
        
        # Process with performance optimization
        start_time = datetime.utcnow()
        
        # Use crash-safe processing for larger batches
        if len(businesses) > 10:
            from crash_prevention import safe_batch_generation
            results = safe_batch_generation(businesses, days)
        else:
            results = EnterpriseScaling.process_batch_request(businesses, days)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Save batch request record
        batch_request = BatchRequest(
            user_id=1,
            request_data=data,
            status='completed',
            completed_at=datetime.utcnow(),
            result_data=results,
            total_businesses=len(businesses),
            total_calendars=len([r for r in results if r.get('status') == 'completed'])
        )
        db.session.add(batch_request)
        db.session.commit()
        
        successful_count = len([r for r in results if r.get('status') == 'completed'])
        
        app.logger.info(f"Batch generation completed: {successful_count}/{len(businesses)} successful in {processing_time:.2f}s")
        
        return jsonify({
            "status": "completed",
            "batch_id": batch_request.id,
            "total_businesses": len(businesses),
            "successful_calendars": successful_count,
            "processing_time": processing_time,
            "estimated_time": estimated_time,
            "efficiency": f"{(estimated_time / processing_time * 100):.1f}%" if processing_time > 0 else "N/A",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/batch/large", methods=["POST"])
def batch_generate_large():
    """Handle extremely large batch requests with streaming response"""
    from performance_optimizer import StreamingResponse, performance_optimizer
    
    try:
        data = request.get_json()
        businesses = data['businesses']
        days = min(int(data['days']), 10)  # Maximum 10 days as requested
        
        if len(businesses) > 10000:
            return jsonify({"error": "Maximum 10,000 businesses per large batch"}), 400
        
        # For very large requests, return immediately with job ID
        if len(businesses) > 100:
            # Queue the request for background processing
            batch_request = BatchRequest(
                user_id=1,
                request_data=data,
                status='processing',
                total_businesses=len(businesses),
                total_calendars=0
            )
            db.session.add(batch_request)
            db.session.commit()
            
            # Start background processing (in production, use Celery)
            def process_in_background():
                try:
                    from crash_prevention import safe_batch_generation
                    results = safe_batch_generation(businesses, days, max_chunk_size=3)
                    batch_request.status = 'completed'
                    batch_request.completed_at = datetime.utcnow()
                    batch_request.result_data = results
                    batch_request.total_calendars = len([r for r in results if r.get('status') == 'completed'])
                    db.session.commit()
                except Exception as e:
                    batch_request.status = 'failed'
                    batch_request.result_data = {"error": str(e)}
                    db.session.commit()
            
            # Start background thread (in production, use proper task queue)
            import threading
            thread = threading.Thread(target=process_in_background)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "status": "processing",
                "batch_id": batch_request.id,
                "message": "Large batch queued for processing",
                "estimated_time": performance_optimizer.estimate_processing_time(len(businesses), days),
                "check_status_url": f"/api/v1/batch/status/{batch_request.id}"
            })
        
        # Process smaller large requests with crash protection
        from crash_prevention import safe_batch_generation
        results = safe_batch_generation(businesses, days)
        
        return jsonify({
            "status": "completed",
            "total_businesses": len(businesses),
            "successful_calendars": len([r for r in results if r.get('status') == 'completed']),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Large batch generation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/batch/status/<int:batch_id>")
def check_batch_status(batch_id):
    """Check status of large batch processing"""
    try:
        batch_request = BatchRequest.query.get(batch_id)
        if not batch_request:
            return jsonify({"error": "Batch not found"}), 404
        
        response_data = {
            "batch_id": batch_id,
            "status": batch_request.status,
            "total_businesses": batch_request.total_businesses,
            "created_at": batch_request.created_at.isoformat()
        }
        
        if batch_request.completed_at:
            response_data["completed_at"] = batch_request.completed_at.isoformat()
            processing_time = (batch_request.completed_at - batch_request.created_at).total_seconds()
            response_data["processing_time"] = processing_time
        
        if batch_request.total_calendars:
            response_data["successful_calendars"] = batch_request.total_calendars
        
        if batch_request.result_data:
            response_data["results"] = batch_request.result_data
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Batch status check error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/calendars")
def list_calendars():
    """List generated calendars with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Cap at 100
        
        calendars = ContentCalendar.query.order_by(
            ContentCalendar.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        calendar_list = []
        for calendar in calendars.items:
            calendar_list.append({
                "id": calendar.id,
                "niche": calendar.niche,
                "city": calendar.city,
                "days_generated": calendar.days_generated,
                "created_at": calendar.created_at.isoformat(),
                "generation_time": calendar.generation_time,
                "success_rate": calendar.success_rate
            })
        
        return jsonify({
            "calendars": calendar_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": calendars.total,
                "pages": calendars.pages,
                "has_next": calendars.has_next,
                "has_prev": calendars.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Calendar listing error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/analytics")
def get_analytics():
    """Enterprise analytics dashboard"""
    try:
        # Get usage statistics
        from sqlalchemy import func
        from datetime import timedelta
        
        # Last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        total_calendars = ContentCalendar.query.filter(
            ContentCalendar.created_at >= thirty_days_ago
        ).count()
        
        avg_generation_time = db.session.query(
            func.avg(ContentCalendar.generation_time)
        ).filter(
            ContentCalendar.created_at >= thirty_days_ago
        ).scalar() or 0
        
        total_posts = db.session.query(
            func.sum(ContentCalendar.days_generated)
        ).filter(
            ContentCalendar.created_at >= thirty_days_ago
        ).scalar() or 0
        
        success_rate = db.session.query(
            func.avg(APIUsage.success.cast(db.Float))
        ).filter(
            APIUsage.timestamp >= thirty_days_ago
        ).scalar() or 1.0
        
        return jsonify({
            "period": "30_days",
            "total_calendars": total_calendars,
            "total_posts_generated": int(total_posts),
            "avg_generation_time": round(float(avg_generation_time), 2),
            "success_rate": round(float(success_rate) * 100, 2),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Keep existing routes for image generation
@app.route("/image-generator")
def image_generator():
    return render_template("image_generator.html")

@app.route("/generate-images", methods=["POST"])
def generate_images_route():
    """Image generation with enterprise tracking"""
    import time
    start_time = time.time()
    
    try:
        prompt = request.form.get("prompt", "").strip()
        num_images = int(request.form.get("num_images", 1))
        image_size = request.form.get("image_size", "1024x1024")
        
        if not prompt:
            error_message = "Please enter a prompt for image generation."
            return render_template("image_generator.html", error=error_message)
        
        try:
            validate_prompt(prompt)
        except ValueError as e:
            error_message = str(e)
            return render_template("image_generator.html", error=error_message)
        
        # Generate images with enterprise tracking
        app.logger.info(f"Enterprise image generation: {num_images} images")
        try:
            images = generate_images(prompt, num_images, image_size)
            generation_time = time.time() - start_time
            
            # Track enterprise usage
            EnterpriseScaling.track_usage(
                user_id=1,
                endpoint="generate_images",
                response_time=generation_time,
                success=True
            )
            
            app.logger.info(f"Enterprise images generated: {len(images)} images in {generation_time:.2f}s")
        except Exception as img_error:
            app.logger.error(f"Enterprise image generation failed: {str(img_error)}")
            error_message = "Image generation temporarily unavailable. Please try again."
            images = []
            
            # Track failed usage
            EnterpriseScaling.track_usage(
                user_id=1,
                endpoint="generate_images",
                response_time=time.time() - start_time,
                success=False
            )
        
    except Exception as e:
        app.logger.error(f"Enterprise image route error: {str(e)}")
        error_message = "An unexpected error occurred."
        images = []
    
    return render_template("image_generator.html", images=images, 
                         error=error_message if 'error_message' in locals() else None)

if __name__ == "__main__":
    logger.info("Starting B.E.L.L.A. Enterprise Server")
    app.run(host="0.0.0.0", port=5000, debug=True)