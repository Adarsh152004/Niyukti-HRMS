import sys
import os
import time

print("1. Starting diagnostic...")
t0 = time.time()
print("2. Python executable:", sys.executable)

print("3. Importing backend.app...")
try:
    from backend.app import app
    print(f"4. backend.app imported successfully in {time.time() - t0:.2f}s!")
except Exception as e:
    print("ERROR importing backend.app:", e)
    import traceback
    traceback.print_exc()

print("5. Diagnostic complete.")
