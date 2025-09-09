# 🎯 B.E.L.L.A. - Beauty Engagement & Leads Launch Assistant

B.E.L.L.A. is an AI-powered social media content calendar generator for beauty businesses and any other business type. This enterprise-grade application now includes advanced streaming features for handling very large outputs reliably on Replit.

## 🚀 Features

### Core B.E.L.L.A. Features
- **Universal Content Generation**: Works for any business niche (beauty, restaurants, retail, services, etc.)
- **3-Word Simplicity**: Only requires niche, city, and days (maximum 10 days, 3 images)
- **AI-Powered Content**: Uses OpenAI GPT-4o for contextual, niche-specific content
- **Complete Calendar**: Generates scripts, visuals, captions, hashtags, timing, and CTAs
- **@salonsuitedigitalstudio Branding**: Maintains brand visibility across all content

### 🌊 New Streaming Features
- **Memory-Safe Processing**: Handle massive outputs without running out of RAM
- **Real-Time Streaming**: See results as they're generated
- **Reliable on Replit**: Optimized for Replit's resource constraints
- **Enterprise-Grade**: Production-ready with proper error handling

## 📡 Streaming Endpoints

### 1. Text Streaming (`/stream`)
Streams huge text responses in small memory-safe chunks.
```bash
curl http://localhost:5000/stream
```

### 2. NDJSON Streaming (`/ndjson`)
Newline-delimited JSON streaming for processing large datasets.
```bash
curl http://localhost:5000/ndjson | head -n 10
```

### 3. Interactive NDJSON Demo (`/ndjson-demo`)
Real-time web interface showing streaming JSON parsing as data arrives.

### 4. Pagination (`/paginate`)
Memory-efficient pagination that doesn't compute unnecessary data.
```bash
curl "http://localhost:5000/paginate?page=1&limit=50"
curl "http://localhost:5000/paginate?page=5&limit=25"
```

### 5. File Export (`/export`)
Export massive datasets to downloadable files without memory overload.
```bash
curl -O http://localhost:5000/export
```

### 6. Server-Sent Events (`/events`)
Real-time streaming with heartbeat for live updates.
```bash
curl http://localhost:5000/events
```

### 7. Demo Dashboard (`/demo`)
Interactive demo page with links to all streaming features and live examples.

## 🔧 Configuration

Control streaming behavior with environment variables:

```bash
export CHUNK_SIZE=1024          # Bytes per chunk
export NDJSON_ROWS=10000        # Rows in NDJSON stream
export EXPORT_ROWS=50000        # Rows in export file
export SSE_INTERVAL_MS=100      # SSE update interval
```

## 🚀 Running on Replit

### Development
```bash
# The app starts automatically with:
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Production Deployment
For crash-proof deployment, use the production-hardened version:
```bash
# Update .replit deployment run command to:
["gunicorn", "--bind", "0.0.0.0:5000", "deployment_main:app"]
```

## 🧪 Testing

### Quick Smoke Test
```bash
python smoke_test.py
```

### Manual Testing Examples

**Test text streaming:**
```bash
curl http://localhost:5000/stream | head -c 1000
```

**Test NDJSON parsing:**
```bash
curl http://localhost:5000/ndjson | head -n 5 | jq .
```

**Test pagination:**
```bash
curl "http://localhost:5000/paginate?page=1&limit=10" | jq '.results | length'
```

**Test file export:**
```bash
curl -O http://localhost:5000/export
ls -la *.json
```

**Test Server-Sent Events:**
```bash
curl http://localhost:5000/events | head -n 20
```

## 🎯 Use Cases

### Small Requests (≤5 days)
- Uses full AI generation with OpenAI
- Real-time content creation
- Perfect for quick campaigns

### Large Requests (6-10 days)
- Uses predefined safe templates
- Memory-efficient processing
- Guaranteed completion without crashes

### Enterprise Streaming
- **Content Auditing**: Stream thousands of posts for review
- **Bulk Export**: Download large content libraries
- **Real-Time Monitoring**: Track content generation progress
- **API Integration**: NDJSON endpoints for system integration

## 📊 Performance & Limits

### Memory Safety
- **Development**: ~8GB available, can use AI generation
- **Deployment**: 512MB-2GB limited, uses template generation
- **Streaming**: Processes data in small chunks, never loads full datasets

### Replit Optimizations
- **Chunk Size**: 1KB default (configurable)
- **Concurrent Requests**: Limited to prevent resource exhaustion
- **Cleanup**: Aggressive garbage collection after operations
- **Logging**: File-based to avoid console spam

### Request Limits
- **Content Calendar**: Maximum 10 days
- **Image Generation**: Maximum 3 images
- **NDJSON Stream**: 10,000 rows default
- **File Export**: 50,000 rows default

## 🛠 Architecture

### Files Structure
```
├── main.py                 # Original B.E.L.L.A. with crash prevention
├── deployment_main.py      # Production-hardened version (no AI calls)
├── streaming_routes.py     # All streaming endpoints
├── demo_page.py           # Interactive demo interface
├── smoke_test.py          # Testing script
├── ssds_ai.py            # AI content generation
├── image_ai.py           # Image generation
└── templates/            # HTML templates
```

### Streaming Technology
- **Flask Response Streaming**: Memory-safe generators
- **NDJSON**: Newline-delimited JSON for efficient parsing
- **Server-Sent Events**: Real-time browser updates
- **Gzip Compression**: Automatic compression for responses >500 bytes
- **File-based Logging**: Prevents console spam on Replit

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:5000/health
```

### Log Files
```bash
tail -f /tmp/app.log
```

### Browser DevTools
- Open `/demo` in browser
- Use Network tab to monitor streaming
- Watch SSE events in real-time

## 🚨 Troubleshooting

### Deployment Crashes
1. **Memory Issues**: Switch to `deployment_main.py`
2. **Timeout Issues**: Use Reserved VM deployment
3. **Resource Limits**: Reduce concurrent requests

### Streaming Issues
1. **Slow Streaming**: Increase `CHUNK_SIZE`
2. **Browser Timeout**: Check `SSE_INTERVAL_MS`
3. **Large Exports**: Monitor `/tmp/app.log`

### Development vs Production
- **Development**: Uses AI generation, more memory available
- **Production**: Uses template generation, limited memory
- **Both**: Streaming works reliably in either environment

## 📈 Enterprise Features

- **Multi-tenant Support**: Handle multiple businesses simultaneously
- **API Integration**: RESTful endpoints for system integration
- **Batch Processing**: Queue system for large operations
- **Performance Monitoring**: Real-time metrics and health checks
- **Crash Prevention**: Multiple fallback layers ensure reliability

---

**Made with 💜 by Salon Suite Digital Studio**  
*Where beauty meets brilliance in digital marketing*