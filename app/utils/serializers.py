from datetime import datetime, date
from bson import ObjectId
from typing import Any


def normalize_value(v: Any) -> Any:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, dict):
        return normalize_doc(v)
    if isinstance(v, list):
        return [normalize_value(x) for x in v]
    return v


def normalize_doc(doc: dict) -> dict:
    return {str(k): normalize_value(v) for k, v in doc.items()}
