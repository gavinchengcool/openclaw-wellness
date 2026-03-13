#!/usr/bin/env python3
"""Normalize raw WHOOP bundle into a stable daily summary schema.

Heuristic: pick the first item in each collection whose date best matches the
requested date. Keep it conservative; downstream prompts should rely on this
schema rather than WHOOP's raw shapes.

Usage:
  python3 scripts/whoop_normalize.py raw.json --out whoop.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


def parse_iso(dt: str) -> Optional[datetime]:
    if not dt or not isinstance(dt, str):
        return None
    # Accept trailing Z
    s = dt.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def date_of(obj: Any) -> Optional[str]:
    # Try common WHOOP timestamp keys.
    for k in ("start", "start_time", "created_at", "updated_at", "end", "end_time"):
        v = obj.get(k) if isinstance(obj, dict) else None
        d = parse_iso(v)
        if d:
            return d.date().isoformat()
    return None


def pick_best_for_date(items: Any, requested_date: str) -> Optional[Dict[str, Any]]:
    if not isinstance(items, list) or not items:
        return None
    # Prefer exact match, else first.
    for it in items:
        if isinstance(it, dict) and date_of(it) == requested_date:
            return it
    for it in items:
        if isinstance(it, dict):
            return it
    return None


def get_collection(data: Any) -> Any:
    # Common patterns in APIs: {"records": [...]}, {"data": [...]}, or direct list
    if isinstance(data, dict):
        for k in ("records", "data", "items"):
            if k in data and isinstance(data[k], list):
                return data[k]
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", help="path to raw bundle JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tz", default=None, help="IANA timezone label (stored only; no conversion here)")
    args = ap.parse_args()

    raw = json.load(open(args.raw, "r", encoding="utf-8"))
    requested_date = raw.get("requested_date")
    tz = args.tz or "Asia/Shanghai"

    endpoints = raw.get("endpoints", {})

    prof = endpoints.get("profile_basic", {}).get("data") or {}
    meas = endpoints.get("body_measurement", {}).get("data") or {}

    rec_items = get_collection(endpoints.get("recovery", {}).get("data"))
    slp_items = get_collection(endpoints.get("sleep", {}).get("data"))
    cyc_items = get_collection(endpoints.get("cycle", {}).get("data"))
    wko_items = get_collection(endpoints.get("workout", {}).get("data"))

    best_rec = pick_best_for_date(rec_items, requested_date) if requested_date else None
    best_slp = pick_best_for_date(slp_items, requested_date) if requested_date else None
    best_cyc = pick_best_for_date(cyc_items, requested_date) if requested_date else None

    # Workout: summarize for the date if possible.
    wkos = [w for w in wko_items if isinstance(w, dict)] if isinstance(wko_items, list) else []
    wkos_for_day = [w for w in wkos if (requested_date and date_of(w) == requested_date)]
    top_strain = None
    for w in (wkos_for_day or wkos):
        s = None
        # Try a few likely keys
        for k in ("strain", "score", "activity_strain"):
            if k in w:
                s = w.get(k)
                break
        try:
            if s is not None:
                s = float(s)
                top_strain = s if top_strain is None else max(top_strain, s)
        except Exception:
            pass

    out: Dict[str, Any] = {
        "date": requested_date,
        "timezone": tz,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "profile": {
            "name": prof.get("name") or prof.get("full_name"),
            "email": prof.get("email"),
        },
        "recovery": {
            "score": (best_rec or {}).get("score"),
            "hrv_ms": (best_rec or {}).get("hrv_ms") or (best_rec or {}).get("hrv"),
            "rhr_bpm": (best_rec or {}).get("resting_heart_rate") or (best_rec or {}).get("rhr"),
        },
        "sleep": {
            "duration_minutes": (best_slp or {}).get("duration") or (best_slp or {}).get("duration_minutes"),
            "performance_percent": (best_slp or {}).get("performance") or (best_slp or {}).get("performance_percent"),
        },
        "cycle": {
            "strain": (best_cyc or {}).get("strain"),
            "avg_hr_bpm": (best_cyc or {}).get("average_heart_rate") or (best_cyc or {}).get("avg_heart_rate"),
        },
        "workout": {
            "count": len(wkos_for_day) if requested_date else len(wkos),
            "top_strain": top_strain,
        },
        "source": {
            "whoop": {
                "api_base": raw.get("api_base"),
                "raw_files": [args.raw],
            }
        },
    }

    json.dump(out, open(args.out, "w", encoding="utf-8"), indent=2, sort_keys=True)
    open(args.out, "a", encoding="utf-8").write("\n")


if __name__ == "__main__":
    main()
