import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000/api/v1/orchestration/stream"

TEST_CASES = [
    ("JD", "Create a Job Description for Senior AI Engineer"),
    ("Payroll", "Execute monthly payroll batch for August"),
    ("Offer", "Draft offer letter for Rahul Singh at 18 LPA"),
    ("Leave", "Approve maternity leave request for Priya Sharma"),
]

all_pass = True
for name, query in TEST_CASES:
    payload = json.dumps({"query": query, "initiator": "CEO", "channel": "AI_WORKSPACE"}).encode()
    req = urllib.request.Request(BASE_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    decision = None
    has_approval = False

    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            current_ev = None
            for line in r:
                ls = line.decode("utf-8").strip()
                if ls.startswith("event:"):
                    current_ev = ls.replace("event:", "").strip()
                elif ls.startswith("data:") and current_ev == "metadata":
                    try:
                        d = json.loads(ls[5:].strip())
                        decision = d.get("decision")
                        has_approval = bool(d.get("approval_request"))
                    except Exception:
                        pass
                if ls == "data: [DONE]":
                    break
    except Exception as e:
        print("FAIL " + name + " " + str(e))
        all_pass = False
        continue

    ok = decision == "APPROVAL_GATE" and has_approval
    print(("PASS " if ok else "FAIL ") + name + " decision=" + str(decision) + " has_approval=" + str(has_approval))
    if not ok:
        all_pass = False

print("ALL_PASS" if all_pass else "SOME_FAIL")
sys.exit(0 if all_pass else 1)
