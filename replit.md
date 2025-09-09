# Overview

Salon Suite Digital Studio's B.E.L.L.A. (Beauty Engagement & Leads Launch Assistant) is an AI-powered Flask web application that generates social media content calendars for beauty businesses. Where beauty meets brilliance in digital marketing, B.E.L.L.A. helps small business owners confidently market themselves without the overwhelm using just three simple inputs: niche, city, and days. Unlike generic ChatGPT, B.E.L.L.A. is specifically trained with beauty & local marketing trends in mind and uses multiple AI sources (OpenAI, RiteTag, TrendTok) for comprehensive content generation. B.E.L.L.A. is a flagship tool developed by Salon Suite Digital Studio.

## Recent Updates (August 2025)
- **Guaranteed Branding System**: Every image automatically includes @salonsuitedigitalstudio branding regardless of user prompt
- **Content-Image Integration**: Calendar prompts automatically suggest image generation with one-click insertion
- **Image Refinement Feature**: Users can add details to improve generated images iteratively
- **Enterprise Streaming Features**: Added comprehensive large-output handling with memory-safe processing
- **Production-Grade Reliability**: Multiple deployment versions for different resource constraints  
- **Real-Time Streaming**: Text streams, NDJSON, Server-Sent Events, and file exports for enterprise use
- **Memory-Safe Architecture**: Process massive datasets without RAM overflow on Replit
- **Deployment Crash Prevention**: Ultra-safe deployment version eliminates all crash sources
- **Interactive Demo System**: Complete testing and demo interface for all streaming features
- **File-Based Logging**: Prevents console spam while maintaining proper monitoring
- **Comprehensive Testing**: Automated smoke tests verify all endpoints and streaming functionality

# User Preferences

Preferred communication style: Simple, everyday language.
Final resource limits: Maximum 3 photos and 30 days output with intelligent processing (AI for ≤7 days, templates for 8+ days).

# System Architecture

## Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **UI Components**: Bootstrap 5 for responsive design with custom CSS styling
- **JavaScript**: Vanilla JavaScript for form validation, smooth scrolling, and interactive features
- **Styling**: Custom CSS with CSS variables for theming, Google Fonts (Poppins), and Font Awesome icons
- **Design Pattern**: Template inheritance using base.html for consistent layout across pages

## Backend Architecture
- **Multi-Environment Flask**: Three versions for different use cases (development, deployment, ultra-safe)
- **Memory-Safe Streaming**: Process unlimited data without RAM constraints using generators
- **Real-Time Capabilities**: Server-Sent Events, NDJSON streaming, and chunked text processing
- **Enterprise Export System**: Handle 50,000+ row exports with temporary file management
- **Intelligent Pagination**: Memory-efficient pagination that generates only requested data slices
- **Production Deployment Safety**: deployment_main.py eliminates AI calls for crash-proof operation
- **Comprehensive Error Handling**: Multi-layer fallbacks with guaranteed content delivery
- **File-Based Logging**: Structured logging to /tmp/app.log prevents console overflow
- **Automatic Compression**: Gzip compression for responses >500 bytes

## Content Generation System
- **Universal AI Module**: `ssds_ai.py` now handles any business type with niche-specific prompts and content
- **Multi-Source Integration**: OpenAI, RiteTag, and TrendTok for comprehensive content across all industries
- **3-Word Simplicity**: Only requires niche, city, and days input (works for pizza, retail, services, beauty, etc.)
- **Niche-Agnostic Training**: Dynamically adapts to any business type while maintaining quality
- **Response Parsing**: Structured parsing of pipe-delimited GPT responses into calendar components
- **Content Structure**: Each post includes Day, Activity, Script, Visual, Caption, Hashtags, Time, CTA, and AI Image Prompt
- **Smart Image Generation**: Business-appropriate prompts (salon interior vs restaurant vs retail space)
- **Guaranteed Branding**: EVERY generated image automatically includes @salonsuitedigitalstudio branding regardless of user prompt
- **Enterprise Batch Processing**: Handle multiple businesses simultaneously with queue management
- **Database Persistence**: All generated content saved to PostgreSQL for tracking and analytics
- **Resource Management**: Enterprise-grade limits with automatic scaling for high-volume operations
- **Multi-layer Reliability**: 4-tier fallback system ensures zero-failure content generation

## Session Management
- **Security**: Flask secret key configuration with environment variable fallback
- **State Management**: Form data persistence through POST requests with validation

# External Dependencies

## AI Services
- **OpenAI API**: GPT-4o model for beauty-focused content generation requiring OPENAI_API_KEY environment variable
- **RiteKit API** (Optional): Live hashtag trending analysis with RITEKIT_TOKEN environment variable
- **TrendTok Integration** (Future): Social media trend analysis for current audio and hashtag suggestions

## Python Libraries
- **Flask**: Web framework for application routing and templating
- **pandas**: Data manipulation and HTML table generation
- **openai**: Official OpenAI Python client library
- **requests**: HTTP client for external API calls
- **python-dotenv**: Environment variable management

## Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **Google Fonts**: Custom typography (Poppins font family)

## Environment Configuration
- **Required**: OPENAI_API_KEY for content generation
- **Optional**: RITEKIT_TOKEN for enhanced hashtag trends, SESSION_SECRET for custom session security