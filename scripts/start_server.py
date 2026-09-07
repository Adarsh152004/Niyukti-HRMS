import sys
import uvicorn

print("Starting Uvicorn directly with app instance...", flush=True)
try:
    from backend.app import app
    print("App imported successfully! Launching uvicorn.run on 0.0.0.0:8000...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
except Exception as e:
    print("Failed to run uvicorn:", e, flush=True)
    import traceback
    traceback.print_exc()
