import requests
BASE = "http://127.0.0.1:8000"
EMAIL = "locust.teste@example.com"
PASSWORD = "CargaTaskLab2026!"
register = requests.post(f"{BASE}/auth/register", json={"name":"Usuário de carga TaskLab","email":EMAIL,"password":PASSWORD}, timeout=15)
if register.status_code not in (201,409):
    raise SystemExit(f"Cadastro falhou: HTTP {register.status_code}: {register.text}")
login = requests.post(f"{BASE}/auth/login",json={"email":EMAIL,"password":PASSWORD},timeout=15)
login.raise_for_status()
headers={"Authorization":f"Bearer {login.json()['access_token']}"}
existing=requests.get(f"{BASE}/tasks",headers=headers,timeout=15)
existing.raise_for_status()
missing=max(0,30-len(existing.json()))
for i in range(missing):
    r=requests.post(f"{BASE}/tasks",headers=headers,json={"title":f"seed-carga-{i+1:03d}","description":"Tarefa inicial para os testes de leitura."},timeout=15)
    if r.status_code != 201: raise SystemExit(f"Seed falhou: HTTP {r.status_code}: {r.text}")
print(f"Usuário pronto; tarefas disponíveis: {len(existing.json())+missing} (mínimo 30).")
