import requests
import time

print("🔍 Testing Flask server connection...")
time.sleep(2)  # Give server time to start

try:
    response = requests.get('http://127.0.0.1:5000/', timeout=10)
    print(f"✅ SUCCESS! Server is running!")
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)} characters")
    if "ShikkhaDwar" in response.text or "LMS" in response.text:
        print("✅ Website content detected!")
    else:
        print("⚠️  Unexpected content")
except requests.exceptions.ConnectionError:
    print("❌ Connection refused - server may not be running")
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔍 Testing other endpoints...")
endpoints = ['/courses', '/auth/login', '/auth/register']
for endpoint in endpoints:
    try:
        response = requests.get(f'http://127.0.0.1:5000{endpoint}', timeout=5)
        print(f"✅ {endpoint} - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint} - Error: {type(e).__name__}")