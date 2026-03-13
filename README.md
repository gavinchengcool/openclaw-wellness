# OpenClaw Wellness Hub

This repo contains a **Wellness Hub** skill for OpenClaw plus a growing set of official source skills (WHOOP, Strava, etc.). The goal is one place to connect your health/wellness apps and devices, then generate unified summaries and push them to any chat channel.

## ClawHub

- Wellness Hub: https://clawhub.ai/gavinchengcool/wellness
- WHOOP (Official): https://clawhub.ai/gavinchengcool/openclaw-whoop
- Strava (Official): https://clawhub.ai/gavinchengcool/openclaw-strava

Install:
```bash
clawhub install wellness
clawhub install openclaw-whoop
clawhub install openclaw-strava
```

## What you get

- A hub skill (`wellness`) with a Tier 1 + Tier 2 source catalog, a normalized schema, and digest templates
- Source skills that handle OAuth, token refresh, fetch, normalization, and rendering per vendor

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
