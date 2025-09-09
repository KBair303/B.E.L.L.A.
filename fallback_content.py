"""
Fallback content templates for B.E.L.L.A. when API is temporarily unavailable
"""

def get_fallback_content(niche, city, day):
    """
    Generate fallback content when OpenAI API is unavailable
    """
    
    # Universal templates that adapt to any niche
    def get_niche_templates(niche):
        # Generate niche-appropriate content
        base_activities = [
            f"{niche.title()} showcase", f"{niche.title()} tutorial", f"{niche.title()} process video", 
            f"Client {niche} experience", f"Behind-the-scenes {niche}", f"{niche.title()} transformation",
            f"Professional {niche} work", f"{niche.title()} techniques", f"Quality {niche} service",
            f"{niche.title()} consultation"
        ]
        
        base_scripts = [
            f"Experience exceptional {niche} quality and service",
            f"See our professional {niche} expertise in action",
            f"Your {niche} goals are our priority in {city}",
            f"Professional {niche} services that exceed expectations",
            f"Behind the scenes of our {niche} process",
            f"Transform your {niche} experience with our experts",
            f"Quality {niche} services you can trust",
            f"Watch our {niche} professionals at work",
            f"Exceptional {niche} results for {city} clients",
            f"Your satisfaction is our {niche} mission"
        ]
        
        base_visuals = [
            f"High-quality {niche} photography", f"Professional {niche} video content",
            f"Before and after {niche} results", f"Process documentation",
            f"Client satisfaction moments", f"Detail shots of {niche} work",
            f"Professional workspace", f"Quality {niche} equipment"
        ]
        
        base_captions = [
            f"Ready for exceptional {niche} service in {city}? We deliver quality results every time!",
            f"Your {niche} experience matters to us. Book your {city} appointment today!",
            f"Excellence in {niche} services, right here in {city}. Experience the difference!",
            f"Professional {niche} solutions tailored for you. Welcome to quality service!",
            f"Transform your {niche} needs with our expert team in {city}!"
        ]
        
        # Generate appropriate hashtags for any niche
        niche_clean = niche.replace(' ', '').title()
        city_clean = city.replace(' ', '').title()
        base_hashtags = [f"#{niche_clean}", f"#{city_clean}{niche_clean}", f"#Professional{niche_clean}", f"#{city_clean}Business"]
        
        return {
            "activities": base_activities,
            "scripts": base_scripts,
            "visuals": base_visuals,
            "captions": base_captions,
            "hashtags": base_hashtags
        }
    
    templates = get_niche_templates(niche)
    
    # Use the universal template system
    template = templates
    
    # Rotate content based on day to avoid repetition
    day_index = (day - 1) % len(template["activities"])
    
    activity = template["activities"][day_index]
    script = template["scripts"][day_index]
    visual = template["visuals"][day_index]
    caption = template["captions"][day_index % len(template["captions"])]
    hashtags = " ".join(template["hashtags"]) + f" #{city.replace(' ', '')}Local"
    
    # Enhanced time slots and CTAs for better variety
    times = ["Morning (9-11am)", "Afternoon (2-4pm)", "Evening (6-8pm)", "Peak hours (10am-2pm)", 
             "Weekend mornings", "Lunch break (12-1pm)", "After work (5-7pm)", "Early evening"]
    ctas = ["Book your appointment today!", "DM us to get started!", "Call now to schedule!", 
            "Visit our website to book!", "Limited slots available!", "Book your consultation!", 
            "Transform today!", "Schedule your session!"]
    
    time = times[day_index % len(times)]
    cta = ctas[day_index % len(ctas)]
    
    # Niche-appropriate AI prompt with location-specific branding
    if any(beauty_word in niche.lower() for beauty_word in ['hair', 'nail', 'beauty', 'salon', 'spa', 'microblading', 'lash', 'brow']):
        # Beauty-related niche
        prompt = f"Professional {niche} salon interior in {city} with modern aesthetic, natural lighting, premium equipment, and '@salonsuitedigitalstudio' subtly visible on signage, reflection, or background element"
        location_hashtags = f" #{city.replace(' ', '')}Salon #{city.replace(' ', '')}Beauty #Local{niche.replace(' ', '').title()}"
    else:
        # Non-beauty niche (like pizza, restaurant, retail, etc.)
        prompt = f"Professional {niche} business interior in {city} with modern aesthetic, natural lighting, quality setup, and '@salonsuitedigitalstudio' subtly visible on signage, reflection, or background element"
        location_hashtags = f" #{city.replace(' ', '')}Business #{city.replace(' ', '').title()}{niche.replace(' ', '').title()} #Local{niche.replace(' ', '').title()}"
    
    hashtags += location_hashtags
    
    return f"Day {day} | {activity} | {script} | {visual} | {caption} | {hashtags} | {time} | {cta} | {prompt}"