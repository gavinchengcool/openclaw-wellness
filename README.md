# WHOOP (Official API) — OpenClaw Skill

This repo contains an OpenClaw skill that connects to the **official WHOOP Developer Platform** via OAuth, stores + refreshes tokens locally, and fetches WHOOP v2 metrics (recovery, sleep, strain/cycle, workouts, profile, body measurements).

- ClawHub page: https://clawhub.ai/gavinchengcool/openclaw-whoop
- Install:
  ```bash
  clawhub install openclaw-whoop
  # or pin a version
  clawhub install openclaw-whoop --version 0.1.1
  ```

## What it does

- Official OAuth (authorization code flow)
- Local token storage + automatic refresh
- Fetch daily WHOOP metrics with `start`/`end` filters + `nextToken` pagination
- Normalize raw API payloads into a stable JSON schema
- Render a simple message suitable for multiple chat channels (discord/slack/whatsapp/telegram/generic)

## Quick start (local)

1) Set environment variables:

```bash
export WHOOP_CLIENT_ID=...
export WHOOP_CLIENT_SECRET=...
export WHOOP_REDIRECT_URI=...
```

Optional:

```bash
export WHOOP_TZ=Asia/Shanghai
export WHOOP_TOKEN_PATH=~/.config/openclaw/whoop/token.json
```

2) OAuth connect once:

```bash
python3 skills/public/whoop/scripts/whoop_oauth_login.py
```

3) Fetch + render today:

```bash
python3 skills/public/whoop/scripts/whoop_fetch.py --date today --out /tmp/whoop_raw_today.json
python3 skills/public/whoop/scripts/whoop_normalize.py /tmp/whoop_raw_today.json --out /tmp/whoop_today.json
python3 skills/public/whoop/scripts/whoop_render.py /tmp/whoop_today.json --format markdown --channel generic
```

## Repository layout

- Skill folder: `skills/public/whoop/`
- Packaged output (local): `dist/whoop.skill` (not tracked)

## Notes

The ClawHub-distributed skill bundle is intentionally lean (benchmark-friendly): it ships `SKILL.md` + scripts + references, and avoids extra docs inside the skill itself.
