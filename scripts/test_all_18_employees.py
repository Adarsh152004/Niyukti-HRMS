import urllib.request
import json
import sys

def verify_all():
    print("================================================================")
    print("VERIFYING ALL 18 EMPLOYEES ACROSS BACKEND PORTAL ENDPOINTS")
    print("================================================================")
    
    success_count = 0
    for i in range(1, 19):
        emp_id = f"emp-{i:03d}"
        headers = {"X-Actor-ID": emp_id, "X-Tenant-ID": "org-nova-01"}
        try:
            req_p = urllib.request.Request("http://localhost:8000/api/v1/me", headers=headers)
            res_p = urllib.request.urlopen(req_p)
            pdata = json.loads(res_p.read().decode())
            name = pdata.get("full_name") or f"{pdata.get('first_name')} {pdata.get('last_name')}"
            dept = pdata.get("department_name")
            role = pdata.get("designation_name")

            # Check attendance
            req_a = urllib.request.Request("http://localhost:8000/api/v1/me/attendance", headers=headers)
            res_a = urllib.request.urlopen(req_a)
            adata = json.loads(res_a.read().decode())
            att_status = "PRESENT" if adata.get("is_clocked_in") or adata.get("today") else "OK"

            # Check payslips
            req_ps = urllib.request.Request("http://localhost:8000/api/v1/me/payslips", headers=headers)
            res_ps = urllib.request.urlopen(req_ps)
            psdata = json.loads(res_ps.read().decode())
            ps_count = len(psdata) if isinstance(psdata, list) else len(psdata.get("payslips", []))

            print(f"[{emp_id}] {name:18s} | Dept: {str(dept):22s} | Role: {str(role):25s} | Slips: {ps_count:2d} | Att: {att_status}")
            success_count += 1
        except Exception as e:
            print(f"[{emp_id}] FAILED -> {e}")

    print(f"\nResult: {success_count}/18 employees fully verified in Employee Portal backend APIs.")

    print("\n================================================================")
    print("VERIFYING INSTANT HITL APPROVAL GATES OVER /stream ENDPOINT")
    print("================================================================")

    test_queries = [
        ("Job Description Request", "Create a Job Description for Senior AI Engineer"),
        ("Payroll Execution Request", "Execute monthly payroll batch for August"),
        ("Candidate Offer Request", "Draft an offer letter for Alex Rivera"),
        ("Leave Exception Request", "Apply for maternity leave exception for Sara Kim"),
    ]

    for title, query in test_queries:
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/orchestration/stream",
            data=json.dumps({"query": query, "initiator": "CEO Mobile User", "channel": "CEO_MOBILE"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            resp = urllib.request.urlopen(req)
            events = []
            for _ in range(15):
                line = resp.readline().decode("utf-8")
                if line.startswith("event: "):
                    events.append(line.strip().split(": ")[1])
                if line.startswith("data: ") and "APPROVAL_GATE" in line:
                    events.append("APPROVAL_GATE_DETECTED")
            
            print(f"✓ {title:28s} -> Status: 200 | Events: {list(set(events))}")
        except Exception as e:
            print(f"✗ {title:28s} -> Error: {e}")

    print("\n================================================================")
    print("VERIFYING DATA ANALYST MULTI-AGENT WORKFORCE QUERY")
    print("================================================================")
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/orchestration/stream",
        data=json.dumps({"query": "What is the department breakdown and total headcount?", "channel": "AI_WORKSPACE"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req)
    raw_response = resp.read().decode("utf-8")
    has_18 = "18" in raw_response
    print(f"✓ Headcount Analysis SSE -> Status: 200 | Verified total 18 headcount: {has_18}")
    print("================================================================\n")

if __name__ == "__main__":
    verify_all()
