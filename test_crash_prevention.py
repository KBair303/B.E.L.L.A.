"""
Test script to verify crash prevention works for larger requests
"""
import requests
import time

def test_crash_prevention():
    """Test that B.E.L.L.A. handles larger requests without crashing"""
    
    # Test data that previously caused crashes
    test_cases = [
        {"niche": "hair salon", "city": "Miami", "days": 5},
        {"niche": "nail salon", "city": "Dallas", "days": 7},
        {"niche": "spa", "city": "Seattle", "days": 10},
    ]
    
    print("🧪 Testing crash prevention for larger requests...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['days']} days for {test_case['niche']} in {test_case['city']}")
        
        start_time = time.time()
        
        try:
            # Simulate form submission
            data = {
                'niches': [test_case['niche']],
                'city': test_case['city'],
                'days': str(test_case['days'])
            }
            
            response = requests.post('http://localhost:5000/generate', data=data, timeout=120)
            end_time = time.time()
            
            if response.status_code == 200:
                # Check if we got content back (not just an error page)
                if 'table' in response.text and 'Day 1' in response.text:
                    print(f"✅ SUCCESS: Generated {test_case['days']} days in {end_time - start_time:.1f}s")
                else:
                    print(f"⚠️  PARTIAL: Server responded but may have errors")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request took longer than 2 minutes")
        except requests.exceptions.ConnectionError:
            print(f"💥 CONNECTION ERROR: Server may have crashed")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Wait between tests
        time.sleep(2)
    
    print("\n🏁 Crash prevention test complete!")

if __name__ == "__main__":
    test_crash_prevention()