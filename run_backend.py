import sys
import os
sys.path.insert(0, os.path.abspath("."))
print("Starting uvicorn backend on port 8000...", flush=True)

import uvicorn

if __name__ == '__main__':
    uvicorn.run('backend.app:app', host='0.0.0.0', port=8000, reload=False, log_level='info')

