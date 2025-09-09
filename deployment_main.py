"""
Production deployment version of B.E.L.L.A. with strict memory management
Optimized for Replit Autoscale deployment environments
"""
import os
import sys
import time
import gc
import threading
import logging
from flask import Flask, request, render_template
import pandas as pd

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bella-production-key")

# Production-grade memory management
class ProductionSafety:
    def __init__(self):
        self.max_concurrent = 2  # Very conservative for deployment
        self.active_requests = 0
        self.lock = threading.Lock()
        self.last_cleanup = time.time()
        
    def can_process(self):
        with self.lock:
            return self.active_requests < self.max_concurrent
    
    def start_request(self):
        with self.lock:
            if self.active_requests >= self.max_concurrent:
                raise Exception("Server busy - too many concurrent requests")
            self.active_requests += 1
            logger.info(f"Started request {self.active_requests}/{self.max_concurrent}")
    
    def end_request(self):
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)
            logger.info(f"Ended request, now {self.active_requests}/{self.max_concurrent}")
            
        # Force cleanup after each request
        self.force_cleanup()
    
    def force_cleanup(self):
        """Aggressive memory cleanup for deployment"""
        try:
            # Multiple garbage collection passes
            for _ in range(3):
                collected = gc.collect()
            
            # Clear any cached modules
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
                
            self.last_cleanup = time.time()
            logger.info(f"Production cleanup completed, collected {collected} objects")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

safety = ProductionSafety()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check for deployment monitoring"""
    return {
        "status": "healthy",
        "active_requests": safety.active_requests,
        "max_concurrent": safety.max_concurrent,
        "last_cleanup": safety.last_cleanup
    }

@app.route("/generate", methods=["GET", "POST"])
def generate_calendar():
    """Production-safe calendar generation"""
    
    if request.method == "GET":
        return render_template("index.html")
    
    # Check if we can handle this request
    if not safety.can_process():
        error_message = "Server is currently busy processing other requests. Please try again in a moment."
        return render_template("index.html", error=error_message)
    
    table_html = None
    error_message = None
    calendar_data = []
    
    try:
        safety.start_request()
        logger.info("Production request started")
        
        # Get and validate form data
        selected_niches = request.form.getlist("niches") or []
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
        niche = ", ".join(selected_niches) if selected_niches else ""
        
        # Validation
        if not niche or not city:
            error_message = "Please select at least one niche and enter your city."
            return render_template("index.html", table=table_html, error=error_message)
        
        try:
            num_days = int(num_days)
            if num_days < 1 or num_days > 10:
                error_message = "Number of days must be between 1 and 10."
                return render_template("index.html", table=table_html, error=error_message)
        except ValueError:
            error_message = "Please enter a valid number of days."
            return render_template("index.html", table=table_html, error=error_message)
        
        logger.info(f"Production generation: {num_days} days for {niche} in {city}")
        
        # Production-safe content generation - NO AI calls for deployment stability
        # Use only predefined, guaranteed-safe content templates
        
        activities = [
            "Behind the Scenes", "Client Testimonial", "Before & After", 
            "Educational Tip", "Team Spotlight", "Product Feature", 
            "Service Highlight", "Client Review", "Process Video", "FAQ Post"
        ]
        
        scripts = [
            f"See what makes our {niche} special in {city}",
            f"Happy clients are our priority in {city}",
            f"Professional {niche} services you can trust in {city}",
            f"Quality {niche} experience awaits you in {city}",
            f"Your local {niche} experts in {city}",
            f"Excellence in {niche} services in {city}",
            f"Transform your experience with our {niche} in {city}",
            f"Discover why {city} chooses our {niche} services",
            f"Premium {niche} solutions in {city}",
            f"Book your {niche} appointment in {city} today"
        ]
        
        times = [
            "Morning (9-11am)", "Afternoon (2-4pm)", "Evening (6-8pm)", 
            "Peak hours", "Lunch break", "Weekend", "Early morning", 
            "Late afternoon", "Business hours", "After work"
        ]
        
        ctas = [
            "Book now", "Call today", "DM us", "Visit our website", 
            "Schedule consultation", "Get started", "Learn more", 
            "Contact us", "Reserve your spot", "Claim your appointment"
        ]
        
        # Generate safe content for each day
        for day in range(1, num_days + 1):
            try:
                logger.info(f"Production day {day}/{num_days}")
                
                # Use modulo to cycle through predefined content safely
                activity = activities[(day - 1) % len(activities)]
                script = scripts[(day - 1) % len(scripts)]
                time_slot = times[(day - 1) % len(times)]
                cta = ctas[(day - 1) % len(ctas)]
                
                # Create safe calendar entry
                calendar_entry = {
                    "Day": f"Day {day}",
                    "Activity": activity,
                    "Script": script,
                    "Visual": f"Professional {niche} content",
                    "Caption": f"{script} Book your appointment today!",
                    "Hashtags": f"#{niche.split(',')[0].replace(' ', '')} #{city.replace(' ', '')} #Professional #Local",
                    "Time": time_slot,
                    "CTA": cta,
                    "Prompt": f"Professional {niche} business in {city}, modern setup, '@salonsuitedigitalstudio' visible"
                }
                
                calendar_data.append(calendar_entry)
                logger.info(f"Production day {day} completed")
                
                # Micro cleanup after each day for deployment stability
                if day % 3 == 0:
                    gc.collect()
                    time.sleep(0.05)  # Tiny pause for stability
                
            except Exception as e:
                logger.error(f"Production error on day {day}: {e}")
                # Emergency fallback
                calendar_data.append({
                    "Day": f"Day {day}",
                    "Activity": "Social Media Post",
                    "Script": f"Professional {niche} services in {city}",
                    "Visual": "Professional business photo",
                    "Caption": f"Quality {niche} services in {city} - book today!",
                    "Hashtags": f"#{niche.split(',')[0].replace(' ', '')} #{city.replace(' ', '')} #Professional",
                    "Time": "Peak hours",
                    "CTA": "Book now",
                    "Prompt": f"Professional {niche} business in {city}"
                })
        
        # Create table with production error handling
        if calendar_data:
            try:
                df = pd.DataFrame(calendar_data)
                table_html = df.to_html(
                    classes="table table-striped table-hover styled-table", 
                    index=False, 
                    border=0,
                    escape=False,
                    table_id="calendar-table"
                )
                logger.info(f"Production success: {len(calendar_data)} days generated")
            except Exception as e:
                logger.error(f"Production table creation failed: {e}")
                error_message = "Content generated but display failed. Please refresh and try again."
        else:
            error_message = "No content was generated. Please try again."
            
    except Exception as e:
        logger.error(f"Production critical error: {e}")
        error_message = "Service temporarily unavailable. Please try again in a moment."
        
    finally:
        safety.end_request()
    
    return render_template("index.html", table=table_html, error=error_message, calendar_data=calendar_data)

@app.route("/image-generator")
def image_generator():
    return render_template("image_generator.html")

@app.route("/generate-images", methods=["POST"])
def generate_images_route():
    """Production-safe image generation with strict limits"""
    
    if not safety.can_process():
        error_message = "Server is currently busy. Please try again in a moment."
        return render_template("image_generator.html", error=error_message)
    
    try:
        safety.start_request()
        
        # For deployment stability, disable image generation temporarily
        error_message = "Image generation is temporarily disabled for deployment stability. Please use the content calendar prompts with external tools."
        
        return render_template("image_generator.html", error=error_message)
        
    finally:
        safety.end_request()

# Production error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Production 500 error: {error}")
    safety.force_cleanup()
    return render_template("500.html"), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    logger.info("Starting B.E.L.L.A. Production Deployment")
    app.run(host="0.0.0.0", port=5000, debug=False)