"""
Streaming and large output handling routes for B.E.L.L.A.
Enterprise-grade endpoints for handling very large outputs reliably on Replit
"""
import os
import json
import time
import tempfile
import logging
from datetime import datetime
from flask import Response, request, jsonify, send_file, render_template_string
from main import app
import gc

# Configure file logging to avoid console spam
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('/tmp/app.log')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

stream_logger = logging.getLogger('streaming')
stream_logger.addHandler(file_handler)
stream_logger.setLevel(logging.INFO)

# Environment configuration with safe defaults
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '1024'))  # bytes
NDJSON_ROWS = int(os.environ.get('NDJSON_ROWS', '10000'))  # rows
EXPORT_ROWS = int(os.environ.get('EXPORT_ROWS', '50000'))  # rows
SSE_INTERVAL_MS = int(os.environ.get('SSE_INTERVAL_MS', '100'))  # milliseconds

def generate_large_content(rows=1000):
    """Memory-safe generator for large content without building full data in RAM"""
    for i in range(rows):
        # Generate B.E.L.L.A. content row by row
        content = {
            "id": i + 1,
            "business_type": ["nail salon", "hair salon", "spa", "barbershop", "beauty clinic"][i % 5],
            "city": ["Miami", "Dallas", "Phoenix", "Seattle", "Denver"][i % 5],
            "day": (i % 30) + 1,
            "activity": ["Behind the Scenes", "Client Testimonial", "Before & After", "Educational Tip"][i % 4],
            "script": f"Professional beauty services in your city - Day {(i % 30) + 1}",
            "hashtags": f"#beauty #salon #professional #local #day{(i % 30) + 1}",
            "generated_at": datetime.now().isoformat(),
            "@salonsuitedigitalstudio": "Powered by Salon Suite Digital Studio"
        }
        yield content
        
        # Memory cleanup every 100 rows
        if i % 100 == 0:
            gc.collect()

@app.route('/stream')
def stream_large_text():
    """Stream huge text response in small chunks for memory safety"""
    def generate_text_stream():
        stream_logger.info("Starting large text stream")
        
        # Generate content in small chunks
        chunk_count = 0
        for content_row in generate_large_content(NDJSON_ROWS):
            # Convert to text format
            text_chunk = f"Day {content_row['day']}: {content_row['script']} {content_row['hashtags']}\n"
            
            # Yield chunk if it reaches target size or every 50 rows
            if len(text_chunk) >= CHUNK_SIZE or chunk_count % 50 == 0:
                yield text_chunk
                chunk_count += 1
                
                # Memory safety: force cleanup periodically
                if chunk_count % 200 == 0:
                    gc.collect()
                    stream_logger.info(f"Streamed {chunk_count} chunks")
        
        stream_logger.info(f"Text stream completed: {chunk_count} chunks")
    
    return Response(
        generate_text_stream(),
        content_type='text/plain; charset=utf-8',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

@app.route('/ndjson')
def stream_ndjson():
    """Stream newline-delimited JSON rows without holding them all in memory"""
    def generate_ndjson_stream():
        stream_logger.info("Starting NDJSON stream")
        
        row_count = 0
        for content_row in generate_large_content(NDJSON_ROWS):
            # Each row as JSON + newline
            json_line = json.dumps(content_row) + '\n'
            yield json_line
            row_count += 1
            
            # Memory cleanup every 500 rows
            if row_count % 500 == 0:
                gc.collect()
                stream_logger.info(f"Streamed {row_count} NDJSON rows")
        
        stream_logger.info(f"NDJSON stream completed: {row_count} rows")
    
    return Response(
        generate_ndjson_stream(),
        content_type='application/x-ndjson',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

@app.route('/ndjson-demo')
def ndjson_demo():
    """HTML demo page that fetches NDJSON with ReadableStream"""
    demo_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>B.E.L.L.A. NDJSON Streaming Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #output { background: #f5f5f5; padding: 10px; height: 400px; overflow-y: scroll; }
            .row { margin: 5px 0; padding: 5px; background: white; border-radius: 3px; }
            .status { color: #666; font-style: italic; }
            button { background: #007bff; color: white; border: none; padding: 10px 15px; cursor: pointer; }
            button:disabled { background: #ccc; cursor: not-allowed; }
        </style>
    </head>
    <body>
        <h1>🎯 B.E.L.L.A. NDJSON Streaming Demo</h1>
        <p>This demonstrates streaming large datasets without loading everything into memory.</p>
        
        <button id="startBtn" onclick="startStreaming()">Start Streaming</button>
        <button id="stopBtn" onclick="stopStreaming()" disabled>Stop Streaming</button>
        
        <div id="status" class="status">Ready to stream...</div>
        <div id="output"></div>
        
        <script>
            let controller = null;
            let rowCount = 0;
            
            async function startStreaming() {
                const startBtn = document.getElementById('startBtn');
                const stopBtn = document.getElementById('stopBtn');
                const status = document.getElementById('status');
                const output = document.getElementById('output');
                
                startBtn.disabled = true;
                stopBtn.disabled = false;
                rowCount = 0;
                output.innerHTML = '';
                status.textContent = 'Streaming started...';
                
                try {
                    const response = await fetch('/ndjson');
                    const reader = response.body.getReader();
                    controller = new AbortController();
                    
                    let buffer = '';
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        
                        if (done) break;
                        
                        // Decode chunk and add to buffer
                        buffer += new TextDecoder().decode(value);
                        
                        // Process complete lines
                        const lines = buffer.split('\\n');
                        buffer = lines.pop(); // Keep incomplete line in buffer
                        
                        for (const line of lines) {
                            if (line.trim()) {
                                try {
                                    const data = JSON.parse(line);
                                    rowCount++;
                                    
                                    // Add row to display (limit to last 100 for performance)
                                    const rowDiv = document.createElement('div');
                                    rowDiv.className = 'row';
                                    rowDiv.innerHTML = `
                                        <strong>Row ${rowCount}:</strong> 
                                        ${data.business_type} in ${data.city} - 
                                        Day ${data.day}: ${data.activity}
                                        <small>(${data.generated_at})</small>
                                    `;
                                    
                                    output.appendChild(rowDiv);
                                    
                                    // Keep only last 100 rows for performance
                                    if (output.children.length > 100) {
                                        output.removeChild(output.firstChild);
                                    }
                                    
                                    // Auto-scroll to bottom
                                    output.scrollTop = output.scrollHeight;
                                    
                                    // Update status every 100 rows
                                    if (rowCount % 100 === 0) {
                                        status.textContent = `Streamed ${rowCount} rows...`;
                                    }
                                } catch (e) {
                                    console.error('JSON parse error:', e, line);
                                }
                            }
                        }
                    }
                    
                    status.textContent = `Streaming completed! Total rows: ${rowCount}`;
                } catch (error) {
                    status.textContent = `Error: ${error.message}`;
                    console.error('Streaming error:', error);
                } finally {
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    controller = null;
                }
            }
            
            function stopStreaming() {
                if (controller) {
                    controller.abort();
                    document.getElementById('status').textContent = `Streaming stopped at ${rowCount} rows`;
                }
            }
        </script>
    </body>
    </html>
    """
    return demo_html

@app.route('/paginate')
def paginate_results():
    """Pagination endpoint that returns only a slice of results"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        
        # Validate inputs
        if page < 1 or limit < 1 or limit > 1000:
            return jsonify({"error": "Invalid page or limit parameters"}), 400
        
        # Calculate offset
        offset = (page - 1) * limit
        
        stream_logger.info(f"Paginate request: page={page}, limit={limit}, offset={offset}")
        
        # Generate only the requested slice without computing full data
        results = []
        for i, content_row in enumerate(generate_large_content(EXPORT_ROWS)):
            if i < offset:
                continue
            if len(results) >= limit:
                break
                
            results.append(content_row)
        
        # Calculate total pages (estimate)
        total_pages = (EXPORT_ROWS + limit - 1) // limit
        
        response = {
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "results": results
        }
        
        return jsonify(response)
        
    except ValueError:
        return jsonify({"error": "Page and limit must be integers"}), 400

@app.route('/export')
def export_large_file():
    """Export very large result to temporary file and return as download"""
    stream_logger.info("Starting large file export")
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json', prefix='bella_export_')
    
    try:
        # Write data to temp file without loading all into memory
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write('[\n')  # JSON array start
            
            for i, content_row in enumerate(generate_large_content(EXPORT_ROWS)):
                if i > 0:
                    f.write(',\n')
                json.dump(content_row, f, ensure_ascii=False)
                
                # Memory cleanup every 1000 rows
                if i % 1000 == 0:
                    f.flush()
                    gc.collect()
                    stream_logger.info(f"Exported {i} rows to file")
            
            f.write('\n]')  # JSON array end
        
        stream_logger.info(f"Export completed: {EXPORT_ROWS} rows written to {temp_path}")
        
        # Return file as download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'bella_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            mimetype='application/json'
        )
        
    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except:
            pass
        stream_logger.error(f"Export error: {e}")
        return jsonify({"error": "Export failed"}), 500

@app.route('/events')
def server_sent_events():
    """Server-Sent Events endpoint for live streaming with heartbeat"""
    def generate_sse():
        stream_logger.info("Starting SSE stream")
        
        try:
            counter = 0
            start_time = time.time()
            
            # Send initial connection event
            yield f"data: {{\"type\": \"connection\", \"message\": \"Connected to B.E.L.L.A. live stream\"}}\n\n"
            
            while counter < 100:  # Limit to prevent infinite streams
                counter += 1
                elapsed = time.time() - start_time
                
                # Send data event
                event_data = {
                    "type": "counter",
                    "counter": counter,
                    "elapsed_time": round(elapsed, 2),
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Live update #{counter} from B.E.L.L.A."
                }
                
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # Heartbeat comment to keep connection alive
                if counter % 10 == 0:
                    yield f": heartbeat at {datetime.now().isoformat()}\n\n"
                    stream_logger.info(f"SSE heartbeat: {counter} events sent")
                
                time.sleep(SSE_INTERVAL_MS / 1000.0)
            
            # Send completion event
            yield f"data: {{\"type\": \"complete\", \"total_events\": {counter}}}\n\n"
            stream_logger.info(f"SSE stream completed: {counter} events")
            
        except Exception as e:
            stream_logger.error(f"SSE error: {e}")
            yield f"data: {{\"type\": \"error\", \"message\": \"Stream error: {str(e)}\"}}\n\n"
    
    return Response(
        generate_sse(),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # Disable nginx buffering
        }
    )

# Add compression middleware (disabled for streaming responses to avoid conflicts)
@app.after_request
def compress_response(response):
    """Enable gzip compression for responses larger than 500 bytes (non-streaming only)"""
    # Skip compression for streaming responses to avoid conflicts
    if (response.headers.get('Content-Type', '').startswith(('text/event-stream', 'application/x-ndjson', 'text/plain')) and
        'stream' in str(response.response)):
        return response
    
    if (response.content_length and response.content_length > 500 and
        'gzip' in request.headers.get('Accept-Encoding', '') and
        response.headers.get('Content-Encoding') is None and
        not getattr(response, 'direct_passthrough', False)):
        
        try:
            import gzip
            import io
            
            # Compress response data
            gzip_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as f:
                f.write(response.get_data())
            
            response.set_data(gzip_buffer.getvalue())
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.get_data())
            
        except Exception as e:
            # Silently skip compression on streaming responses
            if "direct passthrough mode" not in str(e):
                stream_logger.error(f"Compression error: {e}")
            pass
    
    return response