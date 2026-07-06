import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def test_discovery():
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    print(f"[*] Registering {email}")
    res = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": "password", "full_name": "Test User"})
    assert res.status_code == 200, res.text
    
    print("[*] Logging in...")
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": "password"})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    
    client = requests.Session()
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    print("[*] Triggering Discovery for Software Engineer...")
    payload = {
        "keywords": "Software Engineer",
        "location": "",
        "experience": "",
        "salary": "",
        "remote": False,
        "providers": ["greenhouse", "lever", "ashby", "wellfound"] # Skipping LinkedIn to avoid headful browser interrupting test
    }
    
    res = client.post(f"{BASE_URL}/job-discovery/search", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    
    print(f"\n[+] Total Found: {data['total_found']}")
    print(f"[+] New Jobs Added: {data['new_jobs']}")
    
    print("\n[Provider Statuses]")
    for ps in data.get("provider_statuses", []):
        if ps["status"] == "success":
            print(f"✔ {ps['provider']}: {ps['jobs_found']} jobs")
        else:
            print(f"✖ {ps['provider']}: {ps['reason']}")

if __name__ == "__main__":
    test_discovery()
