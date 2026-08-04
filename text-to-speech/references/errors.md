# Text-to-speech errors

Errors use `{"detail":{"code":"...","message":"..."}}` before audio streaming begins.

| HTTP | Code | Action |
|---|---|---|
| 401 | `API_KEY_REQUIRED`, `INVALID_API_KEY` | Run `setup-api-key`; do not retry unchanged credentials. |
| 402 | `INSUFFICIENT_CREDITS` | Notify the user and link to `https://vogen.app/pricing`. |
| 403 | `VOICE_ACCESS_DENIED` | Select a voice the account can use. |
| 403/429 | `FREE_TTS_TRIAL_EXPIRED`, `DAILY_LIMIT_EXCEEDED`, `WEEKLY_LIMIT_EXCEEDED`, `MONTHLY_LIMIT_EXCEEDED`, `MULTILINGUAL_FREE_LIMIT_EXCEEDED` | Stop retrying; explain the plan limit and link to pricing. |
| 422 | validation error | Fix the request body. |
| 502 | `TTS_GENERATION_FAILED`, `EMPTY_AUDIO_RESULT` | Retry once with the same request, then report the task ID. |
| 504 | `TTS_GENERATION_TIMEOUT` | Retry with shorter text; the original server task may still finish. |

After response streaming starts, a downstream failure can end the byte stream early. Treat an unexpectedly truncated/undecodable MP3 as failed; do not present it as complete.
