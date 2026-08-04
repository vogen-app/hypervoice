# Digital-human options

## Avatar image

- Formats: JPEG (`.jpg`, `.jpeg`) or PNG (`.png`)
- Maximum size: 10 MB
- Guidance: use one clearly visible, front-facing person or character with an unobstructed face
- Optional title: 1–100 characters
- Re-uploading identical image bytes returns the existing avatar with `created: false`

## Audio

- Supply exactly one of `audio` or `source_tts_task_id`
- Local formats: MP3, WAV, M4A, FLAC, or OGG
- Maximum local file size: 25 MB
- Maximum duration through Agent/API: 5 seconds for free accounts; 30 seconds for active Pro/Business accounts
- `source_tts_task_id` must identify a completed TTS task owned by the same account

Do not silently trim over-limit content. Free users exceeding 5 seconds should be directed to `https://vogen.app/pricing`; paid users exceeding 30 seconds should shorten the audio or use `https://vogen.app/zh/app/digital-human`.

## Video controls

| `aspect_ratio` | Output resolution |
|---|---:|
| `16:9` | 832×480 |
| `4:3` | 640×480 |
| `1:1` | 512×512 |
| `3:4` | 480×640 |
| `9:16` | 480×832 |

- `aspect_ratio` is required.
- `prompt` is optional and limited to 200 characters.
- `use_enhanced` is an optional boolean; default to `false` unless the user asks for enhanced processing.

## Status and polling

Statuses are `pending`, `started`, `processing`, `completed`, `failed`, and `cancelled`. Use `scripts/wait_for_video.py` rather than an Agent-owned loop: it polls every 20 seconds for up to 90 minutes and immediately downloads the signed `video_url` on completion. A waiter timeout means the server task may still be processing and must not be resubmitted automatically.
