# Orbit Studio

Orbit Studio is the browser-based production dashboard for the Orbit Unknown science/space channel.

Live site:
`https://mirzafraztahir-coder.github.io/Orbit-Unknown/`

## Current build

The current version is a zero-dependency GitHub Pages application. It runs fully in the browser and saves jobs in local storage.

### Working now

- Professional dashboard
- Brand settings
- One-click video package generation
- 12 built-in science/space topics
- Topic scoring and duplicate avoidance
- Voice-ready script generator
- Caption-block generator
- Scene planner
- AI video prompt generator
- Thumbnail prompt generator
- Publishing title, caption and hashtag generator
- JSON export
- TXT production export
- Manual performance logging
- 7-day content calendar
- TikTok app review purpose text
- Public website, Terms and Privacy pages
- TikTok URL property verification file

### Current limitation

This MVP intentionally does not call TikTok/Symphony, YouTube or Instagram APIs until each provider grants the required credentials or OAuth authorization. No fake API access is claimed.

### Pending external access

These require account-owner authorization or provider access before real API calls can be enabled:

- TikTok Symphony API allowlisting and credentials
- YouTube OAuth upload access
- Meta/Instagram publishing authorization

## No secrets

Do not commit API keys, client secrets, tokens or passwords to this repository. Provider credentials should be stored later through environment variables or a secure deployment platform.

## Architecture direction

The current static MVP will evolve into a full web app with backend services, job queue, database, provider adapters, scheduler and analytics.
