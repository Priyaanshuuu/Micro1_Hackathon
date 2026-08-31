"""
API endpoint for live compliance gate monitoring.

Returns recent compliance check results for dashboard visualization.
"""

import json
from pathlib import Path
from typing import List, Dict

# This would be populated by the compliance agent in real-time
# For demo, we'll read from a cache file that gets updated during evaluation
COMPLIANCE_LOG_PATH = Path("output/compliance_checks.json")


def get_recent_compliance_checks(limit: int = 10) -> List[Dict]:
    """Get recent compliance checks from log file."""
    if not COMPLIANCE_LOG_PATH.exists():
        return []

    try:
        with open(COMPLIANCE_LOG_PATH, 'r') as f:
            data = json.load(f)
            checks = data.get('checks', [])
            return checks[-limit:]  # Return last N checks
    except Exception as e:
        print(f"Error reading compliance log: {e}")
        return []


# FastAPI endpoint (add to your backend)
# @app.get("/api/compliance-checks")
# async def compliance_checks_endpoint():
#     checks = get_recent_compliance_checks(limit=10)
#     return {"recent_checks": checks}
