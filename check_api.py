
import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:5000/api/escolas') as response:
        print(f"Status: {response.getcode()}")
        data = response.read()
        print(f"Data: {data.decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
