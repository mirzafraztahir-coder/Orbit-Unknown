# Orbit Unknown: two independently verified YouTube Shorts per day

## Required fixed routine (Pakistan Standard Time, UTC+05:00)

| Edition | First build | Backup build | Primary publication | Publishing recovery attempts |
|---|---|---|---|---|
| Morning | 07:00 | 07:40 | 09:45 | 10:00, 10:25, 10:55 |
| Evening | 15:00 | 15:40 | 18:00 | 18:20, 18:40, 19:00, 20:00, 21:00 |

The afternoon episode must be different from the morning episode and previously published episodes. Never reuse an existing public video as a supposedly new release.

## Source of truth

- `.github/workflows/orbit-cinematic-build.yml` renders the edition, runs technical validation, and stores `orbit-ready-YYYY-MM-DD-{morning|evening}-RUNID` as a GitHub Actions artifact.
- `.github/workflows/orbit-daily-autopilot.yml` downloads the artifact for the **correct date and edition**, verifies its SHA-256 and audio/video metadata, checks against previously published topics, and uploads via the YouTube connection.
- `published/YYYY-MM-DD-morning.json` and `published/YYYY-MM-DD-evening.json` separately record successful YouTube IDs. This prevents a valid evening Short from overwriting or being confused with the morning upload.
- Publication receipt artifacts are archived *before* the Git commit, so an unrelated Git conflict must not cause a duplicate upload on retry.
- The historical `published/2026-10-11.json` is a legacy morning receipt; the new morning guard checks both formats.

## Production quality

A release needs a fresh science story, five separately sourced relevant high-resolution space images, about 40 seconds of 720x1280 footage, restrained pan/zoom movement, clear natural narration, original atmospheric music, readable on-screen captions, and five coherent scene beats. Never allow the obsolete 16-second silent cartoon template to publish.

NASA imagery is illustrative documentary source material; it is **not** authentic footage of fictional events such as the Moon disappearing. Descriptions must distinguish hypotheticals from observed events, and third-party copyrighted imagery must not be presented as unrestricted NASA material. The visual quality filter attempts to reject images depicting an unrelated planet; manual visual review is still preferable for extraordinary or speculative topics.

## Failures and alerts

The upload should be retried as scheduled until it succeeds or the same-day recovery window ends, but never override the quality gates, reuse yesterday's content, or post two copies. A successful upload is only verified once YouTube returns a real video ID and the edition's durable receipt is available.

GitHub Actions cron triggers can run late, NASA downloads or neural speech services can fail, Google OAuth may expire, and YouTube can reject uploads or exhaust quota. Hence two daily uploads are a **target**, not an unconditional guarantee.

## Topic supply

The canonical curated episode library is in `automation/space_cinematic_v2.py` and `automation/extra_episodes.py`. More original, nonrepeating, scientifically verified five-scene topics must be added regularly. The Orbit New Topic Supply task is scheduled twice weekly to replenish the library; it should never overwrite or delete prior episode entries.

## Manual testing

Do not run a publishing workflow manually to test just the renderer. Run the `Orbit Cinematic Build` workflow with the selected edition first. The publishing workflow has the appropriate date/slot duplicate check and scheduled opening-time gate. For final verification, examine both the Actions job conclusion and the date/slot YouTube video receipt.
