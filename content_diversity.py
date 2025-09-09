"""
Advanced content diversity system for B.E.L.L.A.
Ensures unique, non-repetitive content generation
"""

def generate_diverse_content(niche, city, day, used_content):
    """Generate diverse content ensuring no duplicates"""
    
    # Advanced content templates with high variety
    content_themes = {
        "transformation": {
            "activities": ["Amazing Transformation Tuesday", "Makeover Magic", "Before & After Reveal", 
                         "Client Glow-Up Story", "Confidence Transformation"],
            "scripts": [f"Watch this incredible {niche} transformation in {city}",
                       f"From ordinary to extraordinary - {niche} magic happens here",
                       f"This {city} client's transformation will inspire you"]
        },
        "education": {
            "activities": ["Tutorial Thursday", "Technique Breakdown", "Pro Tips Friday", 
                         "Educational Content", "How-To Guide"],
            "scripts": [f"Learn professional {niche} techniques from our {city} experts",
                       f"Master these {niche} tips for amazing results",
                       f"Behind-the-scenes {niche} education"]
        },
        "behind_scenes": {
            "activities": ["Behind the Scenes", "Day in the Life", "Process Video", 
                         "Studio Tour", "Artist at Work"],
            "scripts": [f"See what happens behind the scenes at our {city} studio",
                       f"A day in the life of {niche} professionals",
                       f"The artistry behind every {niche} service"]
        },
        "client_focus": {
            "activities": ["Client Spotlight", "Success Story", "Testimonial Feature", 
                         "Happy Client Friday", "Client Love"],
            "scripts": [f"Meet our amazing {city} clients and their {niche} journey",
                       f"Nothing makes us happier than satisfied {niche} clients",
                       f"Client love from the heart of {city}"]
        },
        "trends": {
            "activities": ["Trending Now", "Style Forecast", "What's Hot", 
                         "Season's Best", "Latest Looks"],
            "scripts": [f"The hottest {niche} trends taking over {city}",
                       f"Stay ahead with these {niche} style predictions",
                       f"What's trending in {niche} this season"]
        }
    }
    
    # Select theme based on day to ensure variety
    theme_keys = list(content_themes.keys())
    theme = content_themes[theme_keys[day % len(theme_keys)]]
    
    # Generate unique content signature
    activity_index = (day - 1) % len(theme["activities"])
    script_index = (day - 1) % len(theme["scripts"])
    
    activity = theme["activities"][activity_index]
    script = theme["scripts"][script_index]
    
    # Ensure uniqueness by checking against used content
    content_signature = f"{activity.lower()}_{script[:30].lower()}"
    counter = 0
    while content_signature in used_content and counter < 10:
        counter += 1
        activity_index = (activity_index + 1) % len(theme["activities"])
        script_index = (script_index + 1) % len(theme["scripts"])
        activity = theme["activities"][activity_index]
        script = theme["scripts"][script_index]
        content_signature = f"{activity.lower()}_{script[:30].lower()}"
    
    # Generate supporting content elements
    visuals = [
        f"High-quality {niche} photography",
        f"Professional {niche} video content",
        f"Before and after {niche} shots",
        f"Process documentation",
        f"Client reaction captures",
        f"Detail shots of {niche} work",
        f"Studio atmosphere photos",
        f"Tool and technique displays"
    ]
    
    captions = [
        f"Ready to elevate your {niche} game in {city}? We're here to make it happen!",
        f"Your {niche} journey starts with the right professionals. Book your {city} appointment today!",
        f"Excellence in {niche} services, right here in {city}. Experience the difference!",
        f"Transform your look, boost your confidence. That's the {niche} magic we create in {city}!",
        f"Professional {niche} services that exceed expectations. Welcome to your {city} beauty destination!"
    ]
    
    hashtags_sets = [
        f"#{niche.replace(' ', '')} #{city.replace(' ', '')}Beauty #Transform #BookNow",
        f"#{niche.replace(' ', '')}Goals #{city.replace(' ', '')}Salon #Professional #BeautyVibes",
        f"#{niche.replace(' ', '')}Expert #{city.replace(' ', '')}Style #Confidence #GlowUp",
        f"#{niche.replace(' ', '')}Art #{city.replace(' ', '')}Beauty #Precision #Results",
        f"#{niche.replace(' ', '')}Magic #{city.replace(' ', '')}Professionals #Excellence #SalonLife"
    ]
    
    times = ["Peak hours", "Morning sessions", "Afternoon appointments", "Evening slots", 
             "Weekend availability", "Flexible scheduling"]
    
    ctas = ["Book your transformation!", "Schedule today!", "Call now!", "DM to book!", 
            "Limited availability!", "Transform with us!", "Your appointment awaits!", "Book consultation!"]
    
    # Select elements with day-based rotation
    visual = visuals[day % len(visuals)]
    caption = captions[day % len(captions)]
    hashtags = hashtags_sets[day % len(hashtags_sets)]
    time = times[day % len(times)]
    cta = ctas[day % len(ctas)]
    
    # Niche-appropriate AI image prompt
    if any(beauty_word in niche.lower() for beauty_word in ['hair', 'nail', 'beauty', 'salon', 'spa', 'microblading', 'lash', 'brow']):
        # Beauty-related niche
        prompt = f"Professional {niche} salon in {city}, modern interior design, natural lighting, happy clients, premium equipment, '@salonsuitedigitalstudio' subtly visible in background or signage"
    else:
        # Non-beauty niche
        prompt = f"Professional {niche} business in {city}, modern interior design, natural lighting, satisfied customers, quality equipment, '@salonsuitedigitalstudio' subtly visible in background or signage"
    
    return f"Day {day} | {activity} | {script} | {visual} | {caption} | {hashtags} | {time} | {cta} | {prompt}"