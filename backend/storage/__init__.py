"""
AI-Powered Intelligent HRMS — Object Storage Package.
"""

from backend.storage.local import LocalStorage, S3CompatibleStorage
from backend.storage.port import StoragePort, StoredObject

__all__ = [
    "StoragePort",
    "StoredObject",
    "LocalStorage",
    "S3CompatibleStorage",
]
