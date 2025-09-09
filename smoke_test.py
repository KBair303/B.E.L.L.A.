#!/usr/bin/env python3
"""
Smoke test script for B.E.L.L.A. streaming endpoints
Tests all large output handling features
"""
import requests
import time
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_endpoint(name, endpoint, expected_status=200, stream=False, timeout=30):
    """Test an endpoint and return success status"""
    print(f"\n🧪 Testing {name}...")
    print(f"   URL: {BASE_URL}{endpoint}")
    
    try:
        start_time = time.time()
        
        if stream:
            response = requests.get(f"{BASE_URL}{endpoint}", stream=True, timeout=timeout)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=timeout)
        
        elapsed = time.time() - start_time
        
        if response.status_code == expected_status:
            if stream:
                # Read first few chunks for streaming endpoints
                chunk_count = 0
                for chunk in response.iter_content(chunk_size=1024):
                    chunk_count += 1
                    if chunk_count >= 5:  # Read first 5 chunks
                        break
                print(f"   ✅ SUCCESS: {response.status_code} - Streamed {chunk_count} chunks in {elapsed:.2f}s")
            else:
                content_length = len(response.content) if response.content else 0
                print(f"   ✅ SUCCESS: {response.status_code} - {content_length} bytes in {elapsed:.2f}s")
            return True
        else:
            print(f"   ❌ FAILED: Expected {expected_status}, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_pagination_params():
    """Test pagination with different parameters"""
    print(f"\n🧪 Testing Pagination Parameters...")
    
    test_cases = [
        ("?page=1&limit=10", 200),
        ("?page=1&limit=50", 200),
        ("?page=5&limit=25", 200),
        ("?page=0&limit=10", 400),  # Invalid page
        ("?page=1&limit=1001", 400),  # Invalid limit
    ]
    
    success_count = 0
    for params, expected_status in test_cases:
        try:
            url = f"{BASE_URL}/paginate{params}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == expected_status:
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {params}: Got {len(data.get('results', []))} results")
                else:
                    print(f"   ✅ {params}: Correctly rejected ({response.status_code})")
                success_count += 1
            else:
                print(f"   ❌ {params}: Expected {expected_status}, got {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {params}: Error - {str(e)}")
    
    print(f"   📊 Pagination tests: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

def test_ndjson_parsing():
    """Test NDJSON parsing"""
    print(f"\n🧪 Testing NDJSON Parsing...")
    
    try:
        response = requests.get(f"{BASE_URL}/ndjson", stream=True, timeout=15)
        
        if response.status_code != 200:
            print(f"   ❌ FAILED: Status {response.status_code}")
            return False
        
        line_count = 0
        valid_json_count = 0
        
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                line_count += 1
                try:
                    data = json.loads(line)
                    if 'business_type' in data and 'city' in data:
                        valid_json_count += 1
                    
                    # Stop after testing first 100 lines
                    if line_count >= 100:
                        break
                        
                except json.JSONDecodeError:
                    pass
        
        if valid_json_count > 0:
            print(f"   ✅ SUCCESS: {valid_json_count}/{line_count} valid JSON lines")
            return True
        else:
            print(f"   ❌ FAILED: No valid JSON found in {line_count} lines")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_sse_stream():
    """Test Server-Sent Events"""
    print(f"\n🧪 Testing Server-Sent Events...")
    
    try:
        response = requests.get(f"{BASE_URL}/events", stream=True, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ FAILED: Status {response.status_code}")
            return False
        
        event_count = 0
        valid_events = 0
        
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                event_count += 1
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'type' in data:
                        valid_events += 1
                except json.JSONDecodeError:
                    pass
                
                # Stop after first 10 events
                if event_count >= 10:
                    break
        
        if valid_events > 0:
            print(f"   ✅ SUCCESS: {valid_events}/{event_count} valid SSE events")
            return True
        else:
            print(f"   ❌ FAILED: No valid SSE events in {event_count} lines")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    """Run all smoke tests"""
    print("🎯 B.E.L.L.A. Streaming Features Smoke Test")
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    tests = []
    
    # Test original functionality
    tests.append(("Original Homepage", "/", 200))
    tests.append(("Health Check", "/health", 200))
    tests.append(("Demo Page", "/demo", 200))
    
    # Test streaming endpoints
    tests.append(("Text Stream", "/stream", 200, True, 15))
    tests.append(("NDJSON Stream", "/ndjson", 200, True, 15))
    tests.append(("NDJSON Demo Page", "/ndjson-demo", 200))
    tests.append(("SSE Endpoint", "/events", 200, True, 10))
    tests.append(("Export Download", "/export", 200, False, 30))
    
    # Run basic endpoint tests
    passed = 0
    total = len(tests)
    
    for test_data in tests:
        if len(test_data) == 3:
            name, endpoint, expected_status = test_data
            if test_endpoint(name, endpoint, expected_status):
                passed += 1
        elif len(test_data) >= 4:
            name, endpoint, expected_status, stream = test_data[:4]
            timeout = test_data[4] if len(test_data) > 4 else 30
            if test_endpoint(name, endpoint, expected_status, stream, timeout):
                passed += 1
    
    # Run specialized tests
    if test_pagination_params():
        passed += 1
    total += 1
    
    if test_ndjson_parsing():
        passed += 1
    total += 1
    
    if test_sse_stream():
        passed += 1
    total += 1
    
    # Final results
    print(f"\n{'='*60}")
    print(f"🎯 B.E.L.L.A. Smoke Test Results")
    print(f"{'='*60}")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Completed at: {datetime.now().isoformat()}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! B.E.L.L.A. streaming features are working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()