import sys
import time

def test_import(module_name, import_stmt):
    t0 = time.time()
    print(f"Importing {module_name}...", end="", flush=True)
    try:
        exec(import_stmt)
        print(f" DONE in {time.time()-t0:.2f}s", flush=True)
    except Exception as e:
        print(f" ERROR: {e}", flush=True)

test_import("agents_router", "from backend.agents.api.router import router as agents_router")
test_import("me", "from backend.api.v1 import me")
test_import("orchestration", "from backend.api.v1 import orchestration")
test_import("attendance", "from backend.api.v1 import attendance")
test_import("leave", "from backend.api.v1 import leave")
test_import("payroll", "from backend.api.v1 import payroll")
test_import("employees", "from backend.api.v1 import employees")
test_import("commands_router", "from backend.commands.api.router import router as commands_router")
test_import("ml_router", "from backend.ml.api.router import router as ml_router")
test_import("EnterpriseKernel", "from backend.runtime.kernel import EnterpriseKernel")
print("All individual imports tested!", flush=True)
