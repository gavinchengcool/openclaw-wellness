#!/usr/bin/env python3
"""Interactive Strava OAuth login.

Env:
- STRAVA_CLIENT_ID
- STRAVA_CLIENT_SECRET
- STRAVA_REDIRECT_URI
Optional:
- STRAVA_SCOPES (default: activity:read_all)
- STRAVA_TOKEN_PATH

Writes token JSON to STRAVA_TOKEN_PATH.
"""

from __future__ import annotations

import os
import sys
import urllib.parse

from strava_token import AUTH_URL, exchange_code_for_token, save_token, token_path


DEFAULT_SCOPES = "activity:read_all"


def must_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"Missing env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_code(user_input: str) -> str:
    s = user_input.strip()
    if s.startswith("http://") or s.startswith("https://"):
        u = urllib.parse.urlparse(s)
        q = urllib.parse.parse_qs(u.query)
        code = (q.get("code") or [None])[0]
        if code:
            return code
        raise SystemExit("Could not find ?code= in the pasted redirect URL")
    return s


def main() -> None:
    client_id = must_env("STRAVA_CLIENT_ID")
    client_secret = must_env("STRAVA_CLIENT_SECRET")
    redirect_uri = must_env("STRAVA_REDIRECT_URI")

    scopes = os.environ.get("STRAVA_SCOPES", DEFAULT_SCOPES)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": scopes,
    }

    auth_url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("Open this URL in a browser and approve access:\n")
    print(auth_url)
    print("\nAfter approval, paste either the full redirect URL or just the code:")
    code = parse_code(input("> "))

    tok = exchange_code_for_token(code=code, client_id=client_id, client_secret=client_secret)
    p = save_token(tok, token_path())
    print(f"\n[OK] Token saved to: {p}")


if __name__ == "__main__":
    main()
