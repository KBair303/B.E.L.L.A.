"""
Production-ready Gunicorn configuration for B.E.L.L.A. enterprise scaling
"""
import os
import multiprocessing

# Determine optimal worker count
workers = int(os.environ.get('WORKERS', min(multiprocessing.cpu_count() * 2 + 1, 8)))

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
worker_class = "gevent"  # Better for I/O intensive tasks
worker_connections = 2000
workers = workers
max_requests = 1000
max_requests_jitter = 100
timeout = 300  # 5 minutes for large requests
keepalive = 5
graceful_timeout = 120

# Restart workers after serving this many requests
max_requests = 2000

# Application
preload_app = True  # Load application before forking workers
reload = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'bella_enterprise'

# Security
limit_request_line = 8192
limit_request_fields = 200
limit_request_field_size = 8190

# Performance tuning
worker_tmp_dir = '/dev/shm'  # Use memory for tmp files

def when_ready(server):
    """Called when server is ready to handle requests"""
    server.log.info("B.E.L.L.A. Enterprise server ready with %d workers", workers)

def worker_int(worker):
    """Called when worker receives SIGINT"""
    worker.log.info("Worker received SIGINT, gracefully shutting down")

def on_exit(server):
    """Called when server shuts down"""
    server.log.info("B.E.L.L.A. Enterprise server shutting down")