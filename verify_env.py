
import os
from dotenv import load_dotenv

print("Loading .env file...")
load_dotenv()

key_name = 'GROQ_API_KEY'
value = os.getenv(key_name)

if value:
    print(f"✅ Found {key_name} with length {len(value)}")
    print(f"First 4 chars: {value[:4]}")
else:
    print(f"❌ {key_name} NOT found in environment.")

print("\nAll keys found in environment related to GROQ:")
for k, v in os.environ.items():
    if 'groq' in k.lower():
        print(f"{k}: {'*' * len(v)}")

# Check file content directly (safely)
try:
    with open('.env', 'r') as f:
        print("\nChecking .env file content (keys only):")
        for line in f:
            if '=' in line:
                key = line.split('=')[0].strip()
                print(f"Key in file: {key}")
except Exception as e:
    print(f"Error reading .env file: {e}")
