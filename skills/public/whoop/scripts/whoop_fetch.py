#!/usr/bin/env python3
"""Fetch WHOOP data for a given day.

This script fetches *collections* near the requested date and writes a raw bundle.
Downstream normalization picks the best matching record.

Requires env:
- WHOOP_CLIENT_ID
- WHOOP_CLIENT_SECRET
- WHOOP_TOKEN_PATH (optional)

Usage:
  python3 scripts/whoop_fetch.py --date today|yesterday|YYYY-MM-DD --out /tmp/whoop_raw.json

No third-party deps.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from whoop_token import get_access_token


API_BASE = "https://api.prod.whoop.com/developer"


def must_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"Missing env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def http_get_json(url: str, access_token: str) -> Any:
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        # Basic 429 handling
        if e.code == 429:
            ra = e.headers.get("Retry-After")
            if ra:
                try:
                    time.sleep(int(ra))
                    return http_get_json(url, access_token)
                except Exception:
                    pass
        raise RuntimeError(f"HTTP {e.code} GET {url}: {raw}") from e


def resolve_date(s: str) -> str:
    s = s.strip().lower()
    if s == "today":
        return datetime.now().strftime("%Y-%m-%d")
    if s == "yesterday":
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # assume YYYY-MM-DD
    datetime.strptime(s, "%Y-%m-%d")
    return s


def url_with_params(path: str, params: Optional[Dict[str, str]] = None) -> str:
    url = API_BASE.rstrip("/") + "/" + path.lstrip("/")
    if params:
        return url + "?" + urllib.parse.urlencode(params)
    return url


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="today|yesterday|YYYY-MM-DD")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=25, help="page size for collection endpoints")
    args = ap.parse_args()

    day = resolve_date(args.date)

    client_id = must_env("WHOOP_CLIENT_ID")
    client_secret = must_env("WHOOP_CLIENT_SECRET")

    access_token = get_access_token(client_id=client_id, client_secret=client_secret)

    # Fetch collections; keep it simple: first page only by default.
    # If you need reliable coverage, extend to paginate and/or use date filters when available.
    bundle: Dict[str, Any] = {
        "requested_date": day,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "api_base": API_BASE,
        "endpoints": {},
    }

    endpoints = {
        "profile_basic": ("/v2/user/profile/basic", None),
        "body_measurement": ("/v2/user/measurement/body", None),
        "recovery": ("/v2/recovery", {"limit": str(args.limit)}),
        "sleep": ("/v2/activity/sleep", {"limit": str(args.limit)}),
        "cycle": ("/v2/cycle", {"limit": str(args.limit)}),
        "workout": ("/v2/activity/workout", {"limit": str(args.limit)}),
    }

    for key, (path, params) in endpoints.items():
        url = url_with_params(path, params)
        bundle["endpoints"][key] = {
            "url": url,
            "data": http_get_json(url, access_token),
        }

    out_path = args.out
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
