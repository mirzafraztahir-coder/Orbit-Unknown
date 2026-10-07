# Orbit Studio

Orbit Studio is the browser-based production dashboard for the Orbit Unknown science/space channel.

Live site:
`https://mirzafraztahir-coder.github.io/Orbit-Unknown/`

## Current build

The current version is a zero-dependency GitHub Pages application. It runs in the browser and saves jobs in local storage.

### Working now

- Dashboard
- Brand settings
- Topic/package generation
- Voice-ready script generator
- Scene planner
- Video prompt generator
- Publishing metadata generator
- JSON package export
- Manual performance logging
- Terms and Privacy pages
- TikTok site verification file

### Pending external access

These require account-owner authorization or provider access before real API calls can be enabled:

- TikTok Symphony API allowlisting and credentials
- YouTube OAuth upload access
- Meta/Instagram publishing authorization

## No secrets

Do not commit API keys, client secrets, tokens or passwords to this repository.
Provider credentials should be stored later through environment variables or a secure deployment platform.

## Architecture direction

The current static MVP will evolve into a full web app with backend services, job queue, database, provider adapters, scheduler and analytics.
