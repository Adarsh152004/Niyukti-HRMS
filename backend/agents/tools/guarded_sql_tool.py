"""
Guarded Read-Only SQL Tool for Niyukti HRMS.
Allows ad-hoc analytical queries while enforcing strict read-only execution,
row-count caps, and security guardrails preventing access to authentication secrets.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any
import aiosqlite
from langchain_core.tools import tool

from backend.database.sqlite_db import get_db_connection

logger = logging.getLogger("hrms.agents.tools.guarded_sql")

# Forbidden SQL keywords and dangerous statements
DISALLOWED_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bVACUUM\b",
    r"\bEXEC\b",
]

# Sensitive patterns that must never be exposed
DISALLOWED_TABLES_COLUMNS = [
    r"\bpassword\b",
    r"\bhash\b",
    r"\brefresh_tokens\b",
    r"\bapi_keys\b",
    r"\bjwt\b",
    r"\bsecret\b",
]


@tool
async def execute_read_only_sql(sql_query: str) -> dict[str, Any]:
    """
    Executes a custom read-only SQL SELECT query against the HRMS SQLite database.
    Use this when user asks for complex multi-table aggregations or filtered data
    not covered by standard tools.
    
    Rules:
    - MUST be a SELECT or WITH statement.
    - Result is capped to max 50 rows.
    - Password, token, and secret fields are strictly blocked.
    """
    clean_sql = sql_query.strip().rstrip(";")
    upper_sql = clean_sql.upper()

    # Guard 1: Must be SELECT
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return {"error": "Security Violation: Only read-only SELECT queries are allowed."}

    # Guard 2: Disallow mutation keywords
    for pattern in DISALLOWED_KEYWORDS:
        if re.search(pattern, clean_sql, re.IGNORECASE):
            return {"error": f"Security Violation: Query contains prohibited keyword matching {pattern}"}

    # Guard 3: Disallow secret columns or tables
    for pattern in DISALLOWED_TABLES_COLUMNS:
        if re.search(pattern, clean_sql, re.IGNORECASE):
            return {"error": "Security Violation: Access to security/credential fields is prohibited."}

    # Guard 4: Enforce LIMIT 50
    if not re.search(r"\bLIMIT\s+\d+\b", clean_sql, re.IGNORECASE):
        clean_sql += " LIMIT 50"
    else:
        # Check if existing limit exceeds 50
        match = re.search(r"\bLIMIT\s+(\d+)\b", clean_sql, re.IGNORECASE)
        if match and int(match.group(1)) > 50:
            clean_sql = re.sub(r"\bLIMIT\s+\d+\b", "LIMIT 50", clean_sql, flags=re.IGNORECASE)

    start_time = time.perf_counter()
    try:
        async with get_db_connection() as conn:
            cursor = await conn.execute(clean_sql)
            rows = await cursor.fetchall()
            col_names = [d[0] for d in cursor.description] if cursor.description else []
            data = [dict(zip(col_names, row)) for row in rows]
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "success": True,
                "row_count": len(data),
                "duration_ms": duration_ms,
                "data": data,
            }
    except Exception as err:
        logger.warning(f"SQL execution error for query '{clean_sql}': {err}")
        return {
            "success": False,
            "error": f"SQL Query Error: {str(err)}",
            "query_attempted": clean_sql,
        }
