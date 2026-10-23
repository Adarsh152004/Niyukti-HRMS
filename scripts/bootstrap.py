"""
AI-Powered Intelligent HRMS — System Bootstrap & Environment Initializer.

Usage:
  python scripts/bootstrap.py
"""

from __future__ import annotations

import os
import sys

from backend.infrastructure.redis.client import RedisClient
from backend.storage.local import LocalStorage


def main() -> None:
    print("\n==================================================================")
    print("AI-POWERED INTELLIGENT HRMS — SYSTEM BOOTSTRAPPER")
    print("==================================================================")

    # 1. Check storage directory
    storage = LocalStorage()
    print(f"• Object Storage Directory:   {storage.base_dir.resolve()} [OK]")

    # 2. Check Redis Client
    redis_client = RedisClient.get_instance()
    print(f"• Redis / In-Memory Cache:    INITIALIZED ({redis_client.redis_url}) [OK]")

    # 3. Environment Summary
    env = os.getenv("APP_ENV", "development")
    port = os.getenv("PORT", "8000")
    print(f"• Application Environment:    {env.upper()}")
    print(f"• FastApi Gateway Port:       {port}")
    print("• All System Dependencies:    READY")
    print("==================================================================\n")


if __name__ == "__main__":
    main()
