"""
Demo page routes for B.E.L.L.A. streaming features
"""
from flask import render_template_string
from main import app

@app.route('/demo')
def streaming_demo():
    """Main demo page with links to all streaming endpoints"""
    demo_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎯 B.E.L.L.A. Large Output Demo</title>
        <style>
            body { 
                font-family: 'Poppins', Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            h1 { 
                text-align: center; 
                margin-bottom: 10px; 
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle { 
                text-align: center; 
                margin-bottom: 30px; 
                opacity: 0.9;
                font-size: 1.1em;
            }
            .endpoint { 
                background: rgba(255,255,255,0.15); 
                margin: 15px 0; 
                padding: 20px; 
                border-radius: 10px;
                border-left: 4px solid #fff;
            }
            .endpoint h3 { 
                margin-top: 0; 
                color: #fff;
                font-size: 1.3em;
            }
            .endpoint p { 
                margin: 10px 0; 
                opacity: 0.9;
                line-height: 1.5;
            }
            .links { 
                margin-top: 15px;
            }
            .links a { 
                display: inline-block; 
                background: rgba(255,255,255,0.2); 
                color: white; 
                text-decoration: none; 
                padding: 8px 16px; 
                margin: 5px 10px 5px 0; 
                border-radius: 25px;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.3);
            }
            .links a:hover { 
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .code { 
                background: rgba(0,0,0,0.3); 
                padding: 10px; 
                border-radius: 5px; 
                font-family: monospace; 
                margin: 10px 0;
                font-size: 0.9em;
                overflow-x: auto;
            }
            .warning { 
                background: rgba(255, 193, 7, 0.2); 
                border: 1px solid rgba(255, 193, 7, 0.5); 
                padding: 15px; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .config { 
                background: rgba(40, 167, 69, 0.2); 
                border: 1px solid rgba(40, 167, 69, 0.5); 
                padding: 15px; 
                border-radius: 5px; 
                margin: 20px 0;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>🎯 B.E.L.L.A.</h1>
            <div class="subtitle">Large Output Streaming Demo</div>
            
            <div class="warning">
                <strong>⚠️ Memory Safety:</strong> These endpoints demonstrate handling very large outputs without loading everything into memory. Perfect for Replit's resource constraints.
            </div>
            
            <div class="config">
                <strong>📊 Current Configuration:</strong><br>
                • Chunk Size: 1KB per chunk<br>
                • NDJSON Rows: 10,000 rows<br>
                • Export Rows: 50,000 rows<br>
                • SSE Interval: 100ms
            </div>

            <div class="endpoint">
                <h3>📡 Text Streaming</h3>
                <p>Stream huge text responses in small memory-safe chunks. Perfect for large content generation that would normally crash on Replit.</p>
                <div class="links">
                    <a href="/stream" target="_blank">View Stream</a>
                </div>
                <div class="code">curl {{ request.url_root }}stream</div>
            </div>

            <div class="endpoint">
                <h3>📊 NDJSON Streaming</h3>
                <p>Newline-delimited JSON streaming with real-time parsing demo. Each row is processed as it arrives without waiting for the complete response.</p>
                <div class="links">
                    <a href="/ndjson" target="_blank">Raw NDJSON</a>
                    <a href="/ndjson-demo" target="_blank">Interactive Demo</a>
                </div>
                <div class="code">curl {{ request.url_root }}ndjson | head -n 10</div>
            </div>

            <div class="endpoint">
                <h3>📄 Pagination</h3>
                <p>Paginated results that don't compute unnecessary data. Only generates the requested page slice.</p>
                <div class="links">
                    <a href="/paginate?page=1&limit=50" target="_blank">Page 1 (50 items)</a>
                    <a href="/paginate?page=5&limit=25" target="_blank">Page 5 (25 items)</a>
                    <a href="/paginate?page=10&limit=100" target="_blank">Page 10 (100 items)</a>
                </div>
                <div class="code">curl "{{ request.url_root }}paginate?page=1&limit=10"</div>
            </div>

            <div class="endpoint">
                <h3>📥 File Export</h3>
                <p>Export massive datasets to downloadable files without loading everything into memory. Safe for Replit's memory limits.</p>
                <div class="links">
                    <a href="/export" target="_blank">Download Export</a>
                </div>
                <div class="code">curl -O {{ request.url_root }}export</div>
            </div>

            <div class="endpoint">
                <h3>⚡ Server-Sent Events (SSE)</h3>
                <p>Real-time streaming with heartbeat to keep connections alive. Open browser DevTools → Network to watch the live stream.</p>
                <div class="links">
                    <a href="/events" target="_blank">View Events</a>
                    <a href="#" onclick="openSSEDemo()">Live Demo</a>
                </div>
                <div class="code">curl {{ request.url_root }}events</div>
                
                <div id="sse-demo" style="display: none; margin-top: 15px;">
                    <h4>Live SSE Stream:</h4>
                    <div id="sse-output" style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; height: 200px; overflow-y: scroll; font-family: monospace; font-size: 0.8em;"></div>
                    <button onclick="stopSSE()" style="margin-top: 10px; background: rgba(220, 53, 69, 0.8); color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">Stop Stream</button>
                </div>
            </div>

            <div class="endpoint">
                <h3>🏠 Original B.E.L.L.A.</h3>
                <p>The main B.E.L.L.A. content calendar generator. All original functionality preserved.</p>
                <div class="links">
                    <a href="/" target="_blank">Content Calendar</a>
                    <a href="/image-generator" target="_blank">Image Generator</a>
                </div>
            </div>
        </div>

        <script>
            let eventSource = null;
            
            function openSSEDemo() {
                const demo = document.getElementById('sse-demo');
                const output = document.getElementById('sse-output');
                
                demo.style.display = 'block';
                output.innerHTML = '';
                
                if (eventSource) {
                    eventSource.close();
                }
                
                eventSource = new EventSource('/events');
                
                eventSource.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        const timestamp = new Date().toLocaleTimeString();
                        output.innerHTML += `[${timestamp}] ${data.type}: ${data.message || JSON.stringify(data)}\\n`;
                        output.scrollTop = output.scrollHeight;
                    } catch (e) {
                        output.innerHTML += `[${new Date().toLocaleTimeString()}] Raw: ${event.data}\\n`;
                        output.scrollTop = output.scrollHeight;
                    }
                };
                
                eventSource.onerror = function(error) {
                    output.innerHTML += `[${new Date().toLocaleTimeString()}] Connection error\\n`;
                    console.error('SSE error:', error);
                };
            }
            
            function stopSSE() {
                if (eventSource) {
                    eventSource.close();
                    eventSource = null;
                }
                document.getElementById('sse-demo').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(demo_html)