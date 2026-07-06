import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_playwright():
    print("[*] Fetching agent states to process...")
    res = requests.get(f"{BASE_URL}/agent/states")
    assert res.status_code == 200, res.text
    states = res.json()
    print(f"[+] Found {len(states)} states.")
    
    if not states:
        print("[-] No states found. Cannot test Playwright.")
        return
        
    for state in states:
        state_id = state["id"]
        print(f"[*] Processing state ID {state_id} (Provider: {state['job']['provider']})...")
        res = requests.post(f"{BASE_URL}/agent/process", json={"agent_state_id": state_id, "action": "resume"})
        assert res.status_code == 200, res.text
        print(f"[+] Result: {res.json()}")

if __name__ == "__main__":
    test_playwright()
