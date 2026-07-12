"""Quick debug script: call /orchestrate with one item and print steps vs gold."""
import json
import httpx
import subprocess
import time
import sys

# Start mock service
proc = subprocess.Popen(
    [sys.executable, "apps/eval/mock_tool_service.py", "--port", "9090"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
time.sleep(2)

try:
    data = json.load(open("data/task3/public_eval_50.json"))
    gold = json.load(open("data/task3/public_eval_50_gold.json"))
    item = data[0]
    task_id = item["task_id"]

    # Rewrite URLs
    mock_url = f"http://localhost:9090/scenario/{task_id}"
    item["mock_service_url"] = mock_url
    for t in item["available_tools"]:
        t["endpoint"] = f"{mock_url}/{t['name']}"

    r = httpx.post("http://localhost:8000/orchestrate", json=item, timeout=60)
    resp = r.json()

    print(f"Task: {task_id}")
    print(f"Status: {resp['status']}")
    print(f"\n--- OUR STEPS ({len(resp.get('steps_executed', []))}) ---")
    for s in resp.get("steps_executed", []):
        print(f"  Step {s['step']}: {s['tool']} | params={json.dumps(s['parameters'], indent=None)}")

    print(f"\n--- GOLD ASSERTIONS (goal_completion) ---")
    g = gold[0]
    for a in g.get("outcome_assertions", []):
        if a.get("dimension") == "goal_completion":
            print(f"  {a['label']}: tool={a.get('tool')} match={a.get('match')} min={a.get('min')} equals={a.get('equals')}")
finally:
    proc.terminate()
