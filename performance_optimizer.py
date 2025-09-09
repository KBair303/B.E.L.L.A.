"""
Performance optimization module for handling larger inputs/outputs
"""
import os
import gc
import time
import asyncio
import concurrent.futures
import threading
from functools import lru_cache
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Optimize B.E.L.L.A. for larger workloads"""
    
    def __init__(self):
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.memory_threshold = 80  # Trigger cleanup at 80% memory usage
        
    def optimize_memory(self):
        """Aggressive memory optimization for large requests"""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear internal caches
            if hasattr(gc, 'set_threshold'):
                gc.set_threshold(700, 10, 10)  # More aggressive GC
            
            logger.debug(f"Memory optimization: collected {collected} objects")
            return True
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return False
    
    def batch_generate_parallel(self, businesses: List[Dict], days: int, max_concurrent: int = 10):
        """Generate content for multiple businesses in parallel"""
        results = []
        start_time = time.time()
        
        # Split into chunks to avoid overwhelming the system
        chunk_size = min(max_concurrent, len(businesses))
        business_chunks = [businesses[i:i + chunk_size] for i in range(0, len(businesses), chunk_size)]
        
        for chunk in business_chunks:
            chunk_results = self._process_business_chunk(chunk, days)
            results.extend(chunk_results)
            
            # Memory cleanup between chunks
            if len(results) % 20 == 0:
                self.optimize_memory()
        
        total_time = time.time() - start_time
        logger.info(f"Parallel generation completed: {len(results)} businesses in {total_time:.2f}s")
        
        return results
    
    def _process_business_chunk(self, businesses: List[Dict], days: int) -> List[Dict]:
        """Process a chunk of businesses concurrently"""
        futures = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(businesses))) as executor:
            for business in businesses:
                future = executor.submit(
                    self._generate_single_business,
                    business['niche'],
                    business['city'],
                    days
                )
                futures.append((future, business))
            
            results = []
            for future, business in futures:
                try:
                    calendar_data = future.result(timeout=300)  # 5 minute timeout
                    results.append({
                        "business": business,
                        "calendar_data": calendar_data,
                        "status": "completed",
                        "posts_generated": len(calendar_data)
                    })
                except concurrent.futures.TimeoutError:
                    logger.error(f"Timeout generating calendar for {business}")
                    results.append({
                        "business": business,
                        "status": "timeout",
                        "error": "Generation timed out after 5 minutes"
                    })
                except Exception as e:
                    logger.error(f"Error generating calendar for {business}: {e}")
                    results.append({
                        "business": business,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return results
    
    def _generate_single_business(self, niche: str, city: str, days: int) -> List[Dict]:
        """Generate calendar for a single business with optimization"""
        from ssds_ai import generate_social_post
        from content_diversity import generate_diverse_content
        
        calendar_data = []
        
        for day in range(1, days + 1):
            try:
                # Generate post with fallback
                post = generate_social_post(niche, city, day, calendar_data)
                
                if not post or len(post.split("|")) < 6:
                    # Use diversity system for fallback
                    used_signatures = {
                        f"{item.get('Activity', '').lower()}_{item.get('Script', '')[:30].lower()}" 
                        for item in calendar_data
                    }
                    post = generate_diverse_content(niche, city, day, used_signatures)
                
                # Parse post data
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
                
                # Memory management for large calendars
                if day % 10 == 0:
                    self.optimize_memory()
                    
            except Exception as e:
                logger.error(f"Failed to generate post for {niche} day {day}: {e}")
                continue
        
        return calendar_data
    
    @lru_cache(maxsize=1000)
    def get_cached_template(self, niche: str, template_type: str):
        """Cache frequently used templates"""
        # This would integrate with your template system
        return f"cached_template_{niche}_{template_type}"
    
    def chunk_large_request(self, total_items: int, max_chunk_size: int = 50) -> List[int]:
        """Split large requests into manageable chunks"""
        chunks = []
        for i in range(0, total_items, max_chunk_size):
            end = min(i + max_chunk_size, total_items)
            chunks.append((i, end))
        return chunks
    
    def estimate_processing_time(self, businesses: int, days: int) -> float:
        """Estimate processing time for planning"""
        # Base time per post (in seconds)
        base_time_per_post = 1.5
        
        # Account for parallel processing efficiency
        parallel_efficiency = 0.7  # 70% efficiency due to overhead
        
        total_posts = businesses * days
        sequential_time = total_posts * base_time_per_post
        
        # Calculate parallel time based on available workers
        parallel_time = sequential_time * parallel_efficiency / min(self.max_workers, businesses)
        
        # Add overhead for batch processing
        overhead = 0.1 * parallel_time
        
        return parallel_time + overhead
    
    def __del__(self):
        """Cleanup resources"""
        try:
            self.executor.shutdown(wait=False)
        except:
            pass

# Global optimizer instance
performance_optimizer = PerformanceOptimizer()

def optimize_for_large_request(func):
    """Decorator to optimize functions for large requests"""
    def wrapper(*args, **kwargs):
        # Pre-optimization
        performance_optimizer.optimize_memory()
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Post-optimization
            processing_time = time.time() - start_time
            logger.info(f"Function {func.__name__} completed in {processing_time:.2f}s")
            
            # Cleanup if processing took a long time
            if processing_time > 60:  # 1 minute
                performance_optimizer.optimize_memory()
    
    return wrapper

class StreamingResponse:
    """Stream large responses to avoid memory buildup"""
    
    def __init__(self, data_generator):
        self.data_generator = data_generator
    
    def stream_json_response(self):
        """Stream JSON response in chunks"""
        yield '{"status": "streaming", "data": ['
        
        first = True
        for item in self.data_generator:
            if not first:
                yield ','
            yield f'{item}'
            first = False
        
        yield ']}'
    
    def stream_csv_response(self):
        """Stream CSV response for large datasets"""
        import csv
        import io
        
        for chunk in self.data_generator:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=chunk[0].keys() if chunk else [])
            
            if chunk:
                writer.writeheader()
                writer.writerows(chunk)
                yield output.getvalue()