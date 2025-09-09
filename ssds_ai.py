import os
import re
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client with API key from environment
OPENAI_API_KEY = os.getenv("BELLAS_OPEN_AI_KEY") or os.getenv("OPENAI_API_KEY2") or os.getenv("OPENAI_API_KEY")
RITEKIT_TOKEN = os.getenv("RITEKIT_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=8,  # Very short timeout to prevent crashes
    max_retries=0  # Disable internal retries, we handle our own
)

def get_live_trends(niche):
    """Get current trending audio and hashtags for different niches"""
    trends = {
        "hair": {
            "audio": "Trending hair transformation audio with before/after transitions",
            "hashtags": "#HairTransformation #HairGoals #SalonLife #HairTrends #BeautyTok"
        },
        "nails": {
            "audio": "Nail art process audio with satisfying ASMR sounds",
            "hashtags": "#NailArt #NailGoals #SalonNails #NailTrends #BeautyVibes"
        },
        "lashes": {
            "audio": "Lash extension process with dramatic reveal audio",
            "hashtags": "#LashGoals #LashExtensions #BeautyTrends #EyeLashes #SalonLife"
        },
        "makeup": {
            "audio": "Makeup transformation with trending beauty audio",
            "hashtags": "#MakeupArtist #MakeupGoals #BeautyMakeup #GlamSquad #MakeupTrends"
        },
        "skincare": {
            "audio": "Skincare routine audio with calming background music",
            "hashtags": "#SkinCare #GlowUp #HealthySkin #SkinGoals #BeautyRoutine"
        },
        "eyebrows": {
            "audio": "Eyebrow shaping process with precision audio",
            "hashtags": "#BrowGoals #EyebrowShaping #BrowArt #BeautyBrows #SalonBrows"
        },
        "microblading": {
            "audio": "Precision microblading process with satisfying technique audio",
            "hashtags": "#Microblading #BrowArt #PermanentMakeup #BeautyProfessional #BrowGoals"
        },
        "massage": {
            "audio": "Relaxing spa music with peaceful ambience",
            "hashtags": "#MassageTherapy #SelfCare #Wellness #Relaxation #SpaLife"
        },
        "fitness": {
            "audio": "Motivational workout music with high energy beats",
            "hashtags": "#FitnessMotivation #WorkoutGoals #HealthyLifestyle #FitLife #Wellness"
        },
        "photography": {
            "audio": "Behind-the-scenes creative process audio",
            "hashtags": "#Photography #CreativeProcess #PhotoShoot #ArtisticVision #BehindTheScenes"
        },
        "consulting": {
            "audio": "Professional business development audio",
            "hashtags": "#BusinessConsulting #ProfessionalDevelopment #Success #Strategy #Growth"
        }
    }
    
    return trends.get(niche.lower(), {
        "audio": "Trending transformation audio with engaging reveals",
        "hashtags": "#SmallBusiness #Entrepreneur #LocalBusiness #Success #Growth"
    })

def get_live_hashtags(keyword):
    """Fetch live trending hashtags from RiteKit API"""
    if not RITEKIT_TOKEN:
        print("⚠️ No RiteKit token found, using fallback hashtags")
        return "#BeautyTrends #SalonLife #BeautyGoals"

    url = f"https://api.ritekit.com/v1/stats/auto-hashtag"
    params = {
        "text": keyword,
        "client_id": RITEKIT_TOKEN
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'hashtags' in data and data['hashtags']:
                tags = [tag['tag'] for tag in data['hashtags'][:8]]  # Get top 8 hashtags
                return ' '.join(f"#{tag}" for tag in tags)
            else:
                print("⚠️ No hashtags returned from RiteKit API")
        else:
            print(f"⚠️ RiteKit API Error: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⚠️ RiteKit API timeout")
    except Exception as e:
        print(f"⚠️ RiteKit API Exception: {e}")
    
    # Fallback hashtags
    return "#BeautyTrends #SalonLife #BeautyGoals"

def generate_social_post(niche, city, day, previous_posts=None):
    """Generate a social media post using OpenAI GPT-4o with duplicate prevention"""
    if previous_posts is None:
        previous_posts = []
    
    # Handle multiple niches - split by comma and get trends for the primary niche
    primary_niche = niche.split(',')[0].strip() if ',' in niche else niche
    
    trend_data = get_live_trends(primary_niche)
    audio = trend_data["audio"]
    fallback_hashtags = trend_data["hashtags"]
    live_hashtags = get_live_hashtags(f"{niche} {city}") or fallback_hashtags

    # Create description based on single or multiple niches
    if ',' in niche:
        niche_description = f"multiple specialties ({niche})"
        focus_instruction = f"Create content that can appeal to clients interested in any of these services: {niche}"
    else:
        niche_description = f"{niche} services"
        focus_instruction = f"Focus on {niche} expertise while showcasing personality"

    # Build context about previous posts to avoid repetition
    previous_context = ""
    if previous_posts:
        used_activities = [post.get('Activity', '') for post in previous_posts if post.get('Activity')]
        used_concepts = [post.get('Visual', '') for post in previous_posts if post.get('Visual')]
        
        if used_activities:
            previous_context += f"\n\nPREVIOUS ACTIVITIES USED (DO NOT REPEAT): {', '.join(used_activities)}"
        if used_concepts:
            # Extract key concepts from visual descriptions
            key_concepts = []
            for visual in used_concepts:
                if visual and len(visual) > 10:
                    key_concepts.append(visual[:50] + "...")
            if key_concepts:
                previous_context += f"\n\nPREVIOUS VISUAL CONCEPTS USED (CREATE SOMETHING DIFFERENT): {'; '.join(key_concepts)}"

    prompt = f"""
You are an expert AI social media strategist helping a {niche} professional in {city}.

Your task is to generate a single Instagram or TikTok post idea for Day {day} focused specifically on {niche}.

CONTENT STRATEGY:
- Mix content types: reels (2-3x/week), carousels, stories, client features, behind-scenes
- Each day should be UNIQUE and engaging - avoid repeating previous concepts
- {focus_instruction}
- Include local {city} appeal when relevant
- Current trend to incorporate: {audio}
{previous_context}

UNIQUENESS REQUIREMENTS:
- Create completely different activity types from previous days
- Use fresh visual concepts and angles
- Vary the content format (video vs photo, indoor vs outdoor, etc.)
- Ensure each day offers unique value to followers

OUTPUT FORMAT: Use exactly 9 fields separated by pipes (|), no extra text or labels:
Day | Activity | Script | Visual | Caption | Hashtags | Time | CTA | Prompt

GUIDELINES:
- Day: Write "Day {day}"
- Activity: Type of post (transformation reel, tutorial, client feature, behind-scenes, etc.) - MUST BE DIFFERENT from previous days
- Script: What they would say/text overlay (keep concise, 1-2 sentences)
- Visual: Describe the video/image concept in detail - MUST BE UNIQUE from previous posts
- Caption: Engaging caption with personality, no hashtags here (2-3 sentences)
- Hashtags: Mix of niche, location, trending tags: {live_hashtags}
- Time: Best posting time (morning/afternoon/evening)
- CTA: Clear call-to-action
- Prompt: AI image generation prompt for creating marketing background images. Always include "@salonsuitedigitalstudio" subtly hidden in the image (on a sign, reflection, or background element). Make it photorealistic and professional.

Focus on authentic, engaging content that drives bookings and builds community while ensuring each day is completely unique.
"""

    # Prioritize fallback content for reliability, try OpenAI as enhancement
    import time
    
    # Start with reliable fallback content
    try:
        from fallback_content import get_fallback_content
        fallback_post = get_fallback_content(niche, city, day)
        print(f"✅ Generated reliable fallback content for Day {day}")
        
        # Quick attempt at OpenAI enhancement (fail fast if network issues)
        try:
            print(f"Attempting OpenAI enhancement for Day {day}")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
                timeout=3  # Ultra-short timeout for enhancement attempt
            )
            
            if response.choices[0].message.content:
                print(f"✅ OpenAI enhancement successful for Day {day}")
                return response.choices[0].message.content.strip()
            else:
                print(f"Using fallback content for Day {day}")
                return fallback_post
                
        except Exception as ai_error:
            print(f"OpenAI enhancement failed, using fallback for Day {day}")
            return fallback_post
            
    except Exception as fallback_error:
        print(f"Fallback content failed: {fallback_error}")
        # Ultimate emergency content
        return f"Day {day} | Professional Content | Engaging {niche} content | High-quality visuals | Professional {niche} content for {city} | {fallback_hashtags} | Peak hours | Book today | Professional marketing image with @salonsuitedigitalstudio visible"
