import requests
import json
import time
import os
import uuid

BASE_URL = "http://localhost:8000/api/v1"
client = requests.Session()

def wait_for_backend():
    print("[*] Waiting for backend...")
    for _ in range(10):
        try:
            res = client.get("http://localhost:8000/health")
            if res.status_code == 200:
                print("[+] Backend is healthy")
                return
        except Exception:
            pass
        time.sleep(1)
    raise Exception("Backend not available")

def run_e2e_demo():
    wait_for_backend()
    
    # 1. Create Demo User
    demo_email = f"demo_{uuid.uuid4().hex[:8]}@example.com"
    print(f"[*] Registering {demo_email}")
    res = client.post(f"{BASE_URL}/auth/register", json={"email": demo_email, "password": "password123"})
    assert res.status_code == 200, res.text
    
    # 2. Login
    print("[*] Logging in...")
    res = client.post(f"{BASE_URL}/auth/login", data={"username": demo_email, "password": "password123"})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 3. Create dummy resume file
    print("[*] Uploading Resume...")
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("demo_resume.pdf")
    c.drawString(100, 800, "Aditya M")
    c.drawString(100, 780, "AI Engineer with 5 years of Python, Machine Learning, and FastAPI experience.")
    c.drawString(100, 760, "Skills: Python, TypeScript, React, PostgreSQL, Docker, AWS.")
    c.save()
    
    with open("demo_resume.pdf", "rb") as f:
        res = client.post(f"{BASE_URL}/resume/upload", files={"file": ("demo_resume.pdf", f, "application/pdf")})
        
    assert res.status_code == 200, res.text
    resume_id = res.json()["id"]
    print(f"[+] Resume uploaded, ID: {resume_id}")
    
    # 4. Job Discovery
    print("[*] Running Job Discovery (Wellfound)...")
    res = client.post(f"{BASE_URL}/job-discovery/search", json={
        "keywords": f"AI Engineer {uuid.uuid4().hex[:6]}",
        "location": "Remote",
        "experience": "",
        "remote": True,
        "salary": "",
        "providers": ["wellfound"]
    })
    assert res.status_code == 200, res.text
    jobs = res.json()
    jobs_list = jobs.get("matched_jobs", [])
    print(f"[+] Found {len(jobs_list)} jobs")
    if not jobs_list:
        print(f"[-] No jobs found, raw response: {jobs}")
        return
        
    discovery_job_id = jobs_list[0]["id"]
    job_text = jobs_list[0].get("description", "Software Engineer Job")
    
    print(f"[*] Saving Discovered Job {discovery_job_id} to Jobs Table...")
    res = client.post(f"{BASE_URL}/jobs/upload", data={"raw_text": job_text})
    assert res.status_code == 200, res.text
    job_id = res.json()["id"]
    print(f"[+] Saved as Job ID: {job_id}")
    
    # 5. Matching & Decision Engine
    print(f"[*] Running Decision Engine for Job {job_id}...")
    res = client.post(f"{BASE_URL}/decision/run", json={"job_id": job_id, "resume_id": resume_id})
    assert res.status_code == 200, res.text
    decision = res.json()
    print(f"[+] Decision Engine result: {decision.get('decision', 'Unknown')}")
    
    # 6. Apply & Track Application
    print("[*] Creating Application...")
    res = client.post(f"{BASE_URL}/applications/", json={"job_id": job_id, "resume_id": resume_id, "notes": "Demo run"})
    assert res.status_code == 200, res.text
    app_id = res.json()["id"]
    print(f"[+] Application Created, ID: {app_id}")
    
    # 7. Check Career Memory Analytics
    print("[*] Fetching Career Memory Analytics...")
    res = client.get(f"{BASE_URL}/memory/analytics")
    assert res.status_code == 200, res.text
    print(f"[+] Career Memory Analytics: {res.json()}")
    
    # 8. Check Automation Queue
    print("[*] Checking Agent States...")
    res = client.get(f"{BASE_URL}/agent/states")
    assert res.status_code == 200, res.text
    states = res.json()
    print(f"[+] Agent States Found: {len(states)}")
    
    # 9. Trigger Playwright Execution
    for state in states:
        state_id = state["id"]
        print(f"[*] Executing Playwright for state ID {state_id}...")
        res = client.post(f"{BASE_URL}/agent/process", json={"agent_state_id": state_id, "action": "resume"})
        assert res.status_code == 200, res.text
        print(f"[+] Playwright Result: {res.json()}")
    
    print("\n[+] E2E Demo and Playwright Test completed successfully!")
    
if __name__ == "__main__":
    run_e2e_demo()
