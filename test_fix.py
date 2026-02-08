
import requests

try:
    res = requests.get('http://localhost:5000/api/stories')
    print(f"Status Stories: {res.status_code}")
    print(res.json())
except Exception as e:
    print(f"Erro ao testar Stories: {e}")

try:
    res = requests.get('http://localhost:5000/api/avisos?autor_id=1')
    print(f"Status Avisos: {res.status_code}")
    print(res.json())
except Exception as e:
    print(f"Erro ao testar Avisos: {e}")
