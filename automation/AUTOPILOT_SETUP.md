# Orbit Unknown Autopilot Setup

This repository now contains a scheduled GitHub Actions workflow for a real no-daily-click automation.

## What runs automatically

`.github/workflows/orbit-daily-autopilot.yml` runs every day at 09:00 Pakistan time and can also be run manually.

It does this:

1. Generate a topic, script, caption and scene plan.
2. Render a simple vertical MP4 template video.
3. Save the generated package in `outbox/`.
4. Upload the package as a GitHub Actions artifact.
5. Attempt platform publishing if the required secrets are configured.

## What is already automatic

- Topic selection
- Script generation
- Caption/hashtag generation
- Simple vertical MP4 generation
- Daily schedule
- Artifact storage

## What needs one-time account authorization

Daily human clicks are not needed after these are configured, but the platform owners must grant access once.

### YouTube required secrets

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Scope needed: `https://www.googleapis.com/auth/youtube.upload`

### Meta / Instagram / Facebook required secrets

- `META_ACCESS_TOKEN`
- `META_IG_USER_ID`
- `META_PAGE_ID`
- `PUBLIC_VIDEO_URL` or a storage provider that exposes the generated MP4 publicly before publishing

Instagram Reels publishing requires a public `video_url` accessible by Meta servers.

### TikTok required secrets

TikTok can be added after the app has Content Posting API / Direct Post approval.

## Important security rule

Never paste access tokens, client secrets or refresh tokens into ChatGPT messages.
Store them only as GitHub Actions secrets or in a secure deployment provider.

## Current limitation

The current template can generate and store the MP4. YouTube can upload directly from the runner after OAuth secrets are configured. Instagram/Facebook require either public video hosting or an upload session flow to be added next.
