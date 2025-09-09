"""
Ultra-safe B.E.L.L.A. implementation with maximum crash prevention
"""
import os
import sys
import time
import gc
import threading
import signal
from contextlib import contextmanager
from flask import Flask, request, render_template
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bella-safe-key")

# Global crash prevention
class UltraSafety:
    def __init__(self):
        self.active_requests = 0
        self.max_requests = 5
        self.lock = threading.Lock()
    
    @contextmanager
    def safe_request(self):
        with self.lock:
            if self.active_requests >= self.max_requests:
                raise Exception("System busy, try again in a moment")
            self.active_requests += 1
        
        try:
            yield
        finally:
            with self.lock:
                self.active_requests -= 1
                gc.collect()

safety = UltraSafety()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["GET", "POST"])
def generate_calendar():
    """Ultra-safe calendar generation"""
    
    if request.method == "GET":
        return render_template("index.html")
    
    table_html = None
    error_message = None
    calendar_data = []
    
    try:
        with safety.safe_request():
            # Get form data with validation
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
            
            logger.info(f"Ultra-safe generation: {num_days} days for {niche} in {city}")
            
            # Ultra-conservative processing - one day at a time
            for day in range(1, num_days + 1):
                try:
                    logger.info(f"Processing day {day}/{num_days}")
                    
                    # Extremely simple fallback content - no AI calls that can crash
                    day_content = create_safe_content(niche, city, day)
                    
                    # Add to calendar immediately
                    calendar_data.append(day_content)
                    
                    # Aggressive cleanup after each day
                    gc.collect()
                    
                    # Small delay for stability
                    time.sleep(0.1)
                    
                    logger.info(f"Day {day} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error on day {day}: {e}")
                    # Add emergency content
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
            
            # Create table if we have data
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
                    logger.info(f"Successfully generated {len(calendar_data)} days of content")
                except Exception as e:
                    logger.error(f"Table creation failed: {e}")
                    error_message = "Content generated but display failed. Please try again."
            else:
                error_message = "No content was generated. Please try again."
                
    except Exception as e:
        logger.error(f"Critical error: {e}")
        error_message = "System temporarily unavailable. Please try again in a moment."
        # Force cleanup
        gc.collect()
    
    return render_template("index.html", table=table_html, error=error_message, calendar_data=calendar_data)

def create_safe_content(niche, city, day):
    """Create guaranteed safe content without any AI calls that could crash"""
    
    # Safe niche handling
    safe_niche = niche.split(',')[0].strip() if niche else "business"
    safe_city = city.strip() if city else "local"
    
    # Predefined safe activities
    activities = [
        "Behind the Scenes",
        "Client Testimonial", 
        "Before & After",
        "Educational Tip",
        "Team Spotlight",
        "Product Feature",
        "Service Highlight"
    ]
    
    # Predefined safe scripts
    scripts = [
        f"See what makes our {safe_niche} special in {safe_city}",
        f"Happy clients are our priority at our {safe_niche} in {safe_city}",
        f"Professional {safe_niche} services you can trust in {safe_city}",
        f"Quality {safe_niche} experience in {safe_city}",
        f"Your local {safe_niche} experts in {safe_city}",
        f"Excellence in {safe_niche} services in {safe_city}",
        f"Transform your look with our {safe_niche} in {safe_city}"
    ]
    
    # Predefined safe times
    times = ["Morning (9-11am)", "Afternoon (2-4pm)", "Evening (6-8pm)", "Peak hours", "Lunch break", "Weekend"]
    
    # Predefined safe CTAs
    ctas = ["Book now", "Call today", "DM us", "Visit our website", "Schedule consultation", "Get started"]
    
    # Use modulo to cycle through options safely
    activity = activities[(day - 1) % len(activities)]
    script = scripts[(day - 1) % len(scripts)]
    time_slot = times[(day - 1) % len(times)]
    cta = ctas[(day - 1) % len(ctas)]
    
    return {
        "Day": f"Day {day}",
        "Activity": activity,
        "Script": script,
        "Visual": f"Professional {safe_niche} content",
        "Caption": f"{script} Book your appointment today!",
        "Hashtags": f"#{safe_niche.replace(' ', '')} #{safe_city.replace(' ', '')} #Professional #Local",
        "Time": time_slot,
        "CTA": cta,
        "Prompt": f"Professional {safe_niche} business in {safe_city}, modern setup, '@salonsuitedigitalstudio' visible"
    }

@app.route("/image-generator")
def image_generator():
    return render_template("image_generator.html")

@app.route("/health")
def health():
    """Simple health check"""
    return {"status": "ok", "active_requests": safety.active_requests}

if __name__ == "__main__":
    logger.info("Starting Ultra-Safe B.E.L.L.A.")
    app.run(host="0.0.0.0", port=5000, debug=False)  # Debug off for stability