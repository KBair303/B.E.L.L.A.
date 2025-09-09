"""
Advanced crash prevention system for large content generation
"""
import os
import gc
import psutil
import time
import threading
import signal
import sys
from functools import wraps
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class CrashPrevention:
    """Comprehensive crash prevention for large outputs"""
    
    def __init__(self):
        self.memory_threshold = 80  # Trigger cleanup at 80% memory
        self.max_generation_time = 300  # 5 minutes max per generation
        self.active_generations = {}
        self.emergency_stop = False
        
        # Monitor system resources
        self.start_resource_monitor()
    
    def start_resource_monitor(self):
        """Start background resource monitoring"""
        def monitor():
            while not self.emergency_stop:
                try:
                    memory_percent = psutil.virtual_memory().percent
                    if memory_percent > self.memory_threshold:
                        logger.warning(f"High memory usage: {memory_percent}%")
                        self.emergency_cleanup()
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Resource monitor error: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def emergency_cleanup(self):
        """Emergency memory cleanup"""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear Python caches
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            # Log cleanup
            memory_after = psutil.virtual_memory().percent
            logger.info(f"Emergency cleanup: collected {collected} objects, memory now {memory_after}%")
            
            return True
        except Exception as e:
            logger.error(f"Emergency cleanup failed: {e}")
            return False
    
    @contextmanager
    def generation_timeout(self, timeout_seconds=300):
        """Context manager for generation timeout"""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Generation timed out after {timeout_seconds} seconds")
        
        # Set timeout signal
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        try:
            yield
        finally:
            # Restore original handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def safe_generation_wrapper(self, generation_func):
        """Wrap generation functions with crash prevention"""
        @wraps(generation_func)
        def wrapper(*args, **kwargs):
            generation_id = f"{time.time()}_{threading.current_thread().ident}"
            self.active_generations[generation_id] = {
                'start_time': time.time(),
                'args': args,
                'kwargs': kwargs
            }
            
            try:
                # Pre-generation cleanup
                if psutil.virtual_memory().percent > 70:
                    self.emergency_cleanup()
                
                # Execute with timeout protection
                with self.generation_timeout(self.max_generation_time):
                    result = generation_func(*args, **kwargs)
                
                # Post-generation cleanup
                if psutil.virtual_memory().percent > 75:
                    self.emergency_cleanup()
                
                return result
                
            except TimeoutError as e:
                logger.error(f"Generation timeout: {e}")
                return self.get_emergency_fallback(*args, **kwargs)
            
            except MemoryError as e:
                logger.error(f"Memory error during generation: {e}")
                self.emergency_cleanup()
                return self.get_emergency_fallback(*args, **kwargs)
            
            except Exception as e:
                logger.error(f"Generation error: {e}")
                return self.get_emergency_fallback(*args, **kwargs)
            
            finally:
                # Remove from active generations
                self.active_generations.pop(generation_id, None)
        
        return wrapper
    
    def get_emergency_fallback(self, *args, **kwargs):
        """Generate emergency fallback content when crashes occur"""
        try:
            # Extract parameters
            if len(args) >= 3:
                niche, city, day = args[0], args[1], args[2]
            else:
                niche = kwargs.get('niche', 'business')
                city = kwargs.get('city', 'local')
                day = kwargs.get('day', 1)
            
            # Ultra-simple fallback content
            return f"Day {day} | {niche.title()} Content | Professional {niche} service in {city} | High-quality content | Quality {niche} services in {city} - book today! | #{niche.replace(' ', '')} #{city.replace(' ', '')}Business #Professional | Peak hours | Book now | Professional {niche} business in {city}, modern setup, '@salonsuitedigitalstudio' visible"
            
        except Exception as e:
            logger.error(f"Even emergency fallback failed: {e}")
            return "Day 1 | Professional Service | Quality service available | Professional content | Book your appointment today! | #Professional #Local #Service | Peak hours | Call now | Professional business setup"
    
    def chunk_large_request(self, total_items, chunk_size=10):
        """Split large requests into safe chunks"""
        chunks = []
        for i in range(0, total_items, chunk_size):
            end = min(i + chunk_size, total_items)
            chunks.append((i, end))
        return chunks
    
    def process_with_breaks(self, items, process_func, break_interval=10):
        """Process items with mandatory breaks to prevent crashes"""
        results = []
        
        for i, item in enumerate(items):
            try:
                # Process item with crash protection
                result = self.safe_generation_wrapper(process_func)(item)
                results.append(result)
                
                # Mandatory break every N items
                if (i + 1) % break_interval == 0:
                    logger.info(f"Processing break after {i + 1} items")
                    time.sleep(1)  # 1 second break
                    self.emergency_cleanup()
                
            except Exception as e:
                logger.error(f"Failed to process item {i}: {e}")
                # Add fallback for failed item
                results.append(self.get_emergency_fallback())
                continue
        
        return results

# Global crash prevention instance
crash_prevention = CrashPrevention()

def prevent_crashes(func):
    """Decorator to prevent crashes in generation functions"""
    return crash_prevention.safe_generation_wrapper(func)

def safe_batch_generation(businesses, days, max_chunk_size=5):
    """Safe batch generation with crash prevention"""
    from ssds_ai import generate_social_post
    from content_diversity import generate_diverse_content
    
    logger.info(f"Starting safe batch generation: {len(businesses)} businesses, {days} days each")
    
    # Calculate safe chunk size based on memory
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 60:
        max_chunk_size = 3  # Smaller chunks if memory is already high
    elif memory_percent > 40:
        max_chunk_size = 5
    else:
        max_chunk_size = min(max_chunk_size, 10)
    
    chunks = crash_prevention.chunk_large_request(len(businesses), max_chunk_size)
    all_results = []
    
    for chunk_start, chunk_end in chunks:
        chunk_businesses = businesses[chunk_start:chunk_end]
        logger.info(f"Processing chunk {chunk_start}-{chunk_end} ({len(chunk_businesses)} businesses)")
        
        chunk_results = []
        for business in chunk_businesses:
            try:
                niche = business.get('niche', 'business')
                city = business.get('city', 'local')
                
                # Generate calendar with crash protection
                calendar_data = []
                for day in range(1, min(days + 1, 10)):  # Cap at 10 days as requested
                    try:
                        @prevent_crashes
                        def generate_single_post():
                            post = generate_social_post(niche, city, day, calendar_data)
                            if not post or len(post.split("|")) < 6:
                                used_signatures = {
                                    f"{item.get('Activity', '').lower()}_{item.get('Script', '')[:30].lower()}" 
                                    for item in calendar_data
                                }
                                post = generate_diverse_content(niche, city, day, used_signatures)
                            return post
                        
                        post = generate_single_post()
                        
                        if post:
                            fields = post.split("|")
                            if len(fields) >= 9:
                                post_data = {
                                    'day': day,
                                    'activity': fields[1].strip(),
                                    'script': fields[2].strip(),
                                    'visual': fields[3].strip(),
                                    'caption': fields[4].strip(),
                                    'hashtags': fields[5].strip(),
                                    'time': fields[6].strip(),
                                    'cta': fields[7].strip(),
                                    'ai_prompt': fields[8].strip()
                                }
                                calendar_data.append(post_data)
                        
                        # Micro-break every 5 posts
                        if day % 5 == 0:
                            time.sleep(0.1)
                            
                    except Exception as e:
                        logger.error(f"Failed to generate post for {niche} day {day}: {e}")
                        continue
                
                chunk_results.append({
                    "business": business,
                    "calendar_data": calendar_data,
                    "status": "completed",
                    "posts_generated": len(calendar_data)
                })
                
                # Cleanup after each business
                if len(chunk_results) % 3 == 0:
                    crash_prevention.emergency_cleanup()
                
            except Exception as e:
                logger.error(f"Failed to process business {business}: {e}")
                chunk_results.append({
                    "business": business,
                    "status": "failed",
                    "error": str(e)
                })
        
        all_results.extend(chunk_results)
        
        # Major cleanup between chunks
        crash_prevention.emergency_cleanup()
        time.sleep(0.5)  # Half-second break between chunks
        
        logger.info(f"Completed chunk {chunk_start}-{chunk_end}, total results: {len(all_results)}")
    
    logger.info(f"Safe batch generation completed: {len(all_results)} businesses processed")
    return all_results