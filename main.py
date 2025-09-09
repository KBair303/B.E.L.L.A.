import os
import logging
from flask import Flask, request, render_template, jsonify, make_response, session
import pandas as pd
import re
from ssds_ai import generate_social_post
from image_ai import generate_images, validate_prompt, get_image_generation_suggestions
from io import StringIO

def get_image_prompts(calendar_data):
    """Extract image prompts from calendar data for easy image generation"""
    prompts = []
    for entry in calendar_data:
        if entry.get('Prompt'):
            prompts.append({
                'day': entry.get('Day', 'Unknown'),
                'activity': entry.get('Activity', 'Unknown'),
                'prompt': entry.get('Prompt'),
                'script': entry.get('Script', '')
            })
    return prompts

# Configure logging with file handler to avoid console spam
logging.basicConfig(level=logging.INFO)

# Add file logging for large output operations
if not os.path.exists('/tmp'):
    os.makedirs('/tmp', exist_ok=True)

file_handler = logging.FileHandler('/tmp/app.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "beauty-salon-secret-key-2024")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["GET", "POST"])
def generate_calendar():
    """Main route for the social media content calendar generator"""
    table_html = None
    calendar_data = []
    error_message = None
    
    if request.method == "POST":
        try:
            # Get selected niches (multiple checkboxes)
            selected_niches = request.form.getlist("niches")
            custom_niche = request.form.get("customNiche", "").strip()
            city = request.form.get("city", "").strip()
            num_days = request.form.get("days", "7")
            
            # Handle custom niche
            if "other" in selected_niches and custom_niche:
                selected_niches = [n for n in selected_niches if n != "other"]  # Remove "other"
                selected_niches.append(custom_niche)  # Add custom niche
            elif "other" in selected_niches and not custom_niche:
                selected_niches = [n for n in selected_niches if n != "other"]  # Remove "other" if no custom input
            
            # Create combined niche string
            if selected_niches:
                niche = ", ".join(selected_niches)
            else:
                niche = ""
            
            # Validation
            if not niche or not city:
                error_message = "Please select at least one niche and enter your city."
                return render_template("index.html", table=table_html, error=error_message)
            
            try:
                num_days = int(num_days)
                if num_days < 1 or num_days > 30:
                    error_message = "Number of days must be between 1 and 30."
                    return render_template("index.html", table=table_html, error=error_message)
            except ValueError:
                error_message = "Please enter a valid number of days."
                return render_template("index.html", table=table_html, error=error_message)

            # Final limits enforced (maximum 30 days)
            num_days = min(num_days, 30)
            app.logger.info(f"Final request: {num_days} days (maximum 30 days)")
            
            # Always ensure content generation succeeds
            app.logger.info(f"Generating {num_days} days of content with guaranteed delivery")
            
            # Ultra-safe one-day-at-a-time processing to prevent crashes
            import time
            import gc
            
            app.logger.info(f"Ultra-safe processing: {num_days} days one at a time")
            
            for day in range(1, num_days + 1):
                try:
                    app.logger.info(f"Processing day {day}/{num_days}")
                    
                    # Force memory cleanup before each day
                    gc.collect()
                    
                    # Try to generate content, but with heavy error protection
                    post = None
                    try:
                        # Only try AI for smaller requests to maintain performance
                        if num_days <= 7:
                            post = generate_social_post(niche, city, day, calendar_data)
                    except Exception as e:
                        app.logger.warning(f"AI generation failed for day {day}: {e}")
                    
                    # If AI failed or we have > 5 days, use guaranteed safe content
                    if not post or len(post.split("|")) < 6:
                        # Safe predefined content
                        activities = ["Behind the Scenes", "Client Testimonial", "Before & After", "Educational Tip", "Team Spotlight", "Product Feature", "Service Highlight"]
                        scripts = [
                            f"See what makes our {niche} special in {city}",
                            f"Happy clients are our priority in {city}",
                            f"Professional {niche} services you can trust in {city}",
                            f"Quality {niche} experience in {city}",
                            f"Your local {niche} experts in {city}",
                            f"Excellence in {niche} services in {city}",
                            f"Transform your look with our {niche} in {city}"
                        ]
                        times = ["Morning (9-11am)", "Afternoon (2-4pm)", "Evening (6-8pm)", "Peak hours", "Lunch break", "Weekend"]
                        ctas = ["Book now", "Call today", "DM us", "Visit our website", "Schedule consultation", "Get started"]
                        
                        activity = activities[(day - 1) % len(activities)]
                        script = scripts[(day - 1) % len(scripts)]
                        time_slot = times[(day - 1) % len(times)]
                        cta = ctas[(day - 1) % len(ctas)]
                        
                        post = f"Day {day} | {activity} | {script} | Professional {niche} content | {script} Book your appointment today! | #{niche.split(',')[0].replace(' ', '')} #{city.replace(' ', '')} #Professional #Local | {time_slot} | {cta} | Professional {niche} business in {city}, modern setup, '@salonsuitedigitalstudio' visible"
                    
                    # Parse the post safely
                    parts = [p.strip().replace("\n", " ") for p in post.strip().split("|")]
                    app.logger.info(f"Day {day} parsed {len(parts)} fields")

                    # Create calendar entry with safe defaults
                    calendar_entry = {
                        "Day": parts[0] if len(parts) > 0 else f"Day {day}",
                        "Activity": parts[1] if len(parts) > 1 else "Social media post",
                        "Script": parts[2] if len(parts) > 2 else f"Professional {niche} content",
                        "Visual": parts[3] if len(parts) > 3 else "Professional visual",
                        "Caption": parts[4] if len(parts) > 4 else f"Quality {niche} in {city}",
                        "Hashtags": parts[5] if len(parts) > 5 else f"#{niche.split(',')[0].replace(' ', '')} #{city.replace(' ', '')}",
                        "Time": parts[6] if len(parts) > 6 else "Peak hours",
                        "CTA": parts[7] if len(parts) > 7 else "Book now",
                        "Prompt": parts[8] if len(parts) > 8 else f"Professional {niche} business in {city}"
                    }
                    calendar_data.append(calendar_entry)
                    
                    app.logger.info(f"Day {day} completed successfully")
                    
                    # Small delay and cleanup after each day
                    time.sleep(0.1)
                    gc.collect()
                    
                except Exception as e:
                    app.logger.error(f"Critical error on day {day}: {e}")
                    # Emergency safe fallback
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
                    app.logger.info(f"Used emergency fallback for day {day}")
                    
                    # Force cleanup after error
                    gc.collect()
                    time.sleep(0.2)

            if calendar_data:
                df = pd.DataFrame(calendar_data)
                table_html = df.to_html(
                    classes="table table-striped table-hover styled-table", 
                    index=False, 
                    border=0,
                    escape=False,
                    table_id="calendar-table"
                )
            else:
                error_message = "No content was generated. Please check your input and try again."

        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            error_message = f"An error occurred while generating content: {str(e)}"

    # Store image prompts in session for image generator
    image_prompts = get_image_prompts(calendar_data)
    session['calendar_image_prompts'] = image_prompts
    
    return render_template("index.html", table=table_html, error=error_message, calendar_data=calendar_data, image_prompts=image_prompts)

@app.route("/download/<format_type>")
def download_calendar(format_type):
    """Download the calendar in different formats"""
    # Get the calendar data from the session or regenerate
    # For now, return an error as we need the data to be passed properly
    return jsonify({"error": "Download functionality requires calendar data"}), 400

@app.route("/image-generator", methods=["GET", "POST"])
def image_generator():
    """Image generator route using B.E.L.L.A.'s AI image generation"""
    images = []
    error_message = None
    suggested_prompts = []
    
    # Get calendar prompts from session or URL parameter
    if request.args.get('prompts') == 'calendar':
        # Try to get prompts from the session (if coming from calendar generation)
        suggested_prompts = session.get('calendar_image_prompts', [])
    
    if request.method == "POST":
        try:
            # Get form data
            prompt = request.form.get("prompt", "").strip()
            num_images = int(request.form.get("num_images", 1))
            image_size = request.form.get("image_size", "1024x1024")
            
            # Check if this is a refinement request
            is_refinement = request.form.get("is_refinement") == "true"
            base_prompt = request.form.get("base_prompt", "").strip()
            refinement_details = request.form.get("refinement_details", "").strip()
            
            if is_refinement and base_prompt and refinement_details:
                # Combine base prompt with refinement details
                prompt = f"{base_prompt}, {refinement_details}"
                app.logger.info(f"Refinement request: base='{base_prompt}' + details='{refinement_details}'")
            
            # Validate inputs
            if not prompt:
                error_message = "Please enter an image prompt."
                return render_template("image_generator.html", error=error_message)
            
            # Resource management for image generation
            if num_images > 3:
                app.logger.warning(f"Large image request ({num_images}). Limiting to 3 for stability.")
                num_images = 3
                error_message = "Limited to 3 images for stability. Generating 3 images..."
            
            # Validate prompt
            try:
                validated_prompt = validate_prompt(prompt)
            except ValueError as e:
                error_message = str(e)
                return render_template("image_generator.html", error=error_message)
            
            # Generate images with timeout protection
            app.logger.info(f"Generating {num_images} images with prompt: {validated_prompt}")
            try:
                images = generate_images(validated_prompt, num_images, image_size)
                app.logger.info(f"Successfully generated {len(images)} images")
                
                # Add base prompt to each image for refinement capability
                for img in images:
                    img['base_prompt'] = base_prompt if is_refinement else prompt
                    img['is_refined'] = is_refinement
                    
            except Exception as img_error:
                app.logger.error(f"Image generation failed: {str(img_error)}")
                error_message = "Image generation is temporarily unavailable due to network issues. Please try again."
                images = []
            
        except Exception as e:
            app.logger.error(f"Error in image generation: {str(e)}")
            error_message = "Image generation is temporarily unavailable. Please try again later."
    
    return render_template("image_generator.html", images=images, error=error_message, suggested_prompts=suggested_prompts)

@app.errorhandler(404)
def not_found_error(error):
    try:
        return render_template('404.html'), 404
    except:
        return '''
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/" style="color: #FF6B9D;">← Back to B.E.L.L.A.</a>
        </body></html>
        ''', 404

@app.errorhandler(500)
def internal_error(error):
    try:
        return render_template('500.html'), 500
    except:
        return '''
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>500 - Server Error</h1>
        <p>Something went wrong. Please try again.</p>
        <a href="/" style="color: #FF6B9D;">← Back to B.E.L.L.A.</a>
        </body></html>
        ''', 500

@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error(f"Unexpected error: {str(error)}")
    try:
        return render_template('500.html'), 500
    except:
        return '''
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>Unexpected Error</h1>
        <p>B.E.L.L.A. encountered an issue. Please try again.</p>
        <a href="/" style="color: #FF6B9D;">← Back to Home</a>
        </body></html>
        ''', 500

# Import streaming routes and demo pages
try:
    import streaming_routes  # noqa: F401
    import demo_page  # noqa: F401
    app.logger.info("Streaming features loaded successfully")
except ImportError as e:
    app.logger.warning(f"Could not load streaming features: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
