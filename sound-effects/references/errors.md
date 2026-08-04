# Sound-effects errors

Errors use `{"detail":{"code":"...","message":"..."}}` before audio streaming begins.

| HTTP | Code | Action |
|---|---|---|
| 401 | `API_KEY_REQUIRED`, `INVALID_API_KEY` | Run `setup-api-key`; do not retry unchanged credentials. |
| 402 | `MEMBERSHIP_REQUIRED` | Stop downloading new sounds and direct the user to `https://vogen.app/pricing`. Previously unlocked and free-preview sounds remain available. |
| 404 | `TAG_NOT_FOUND` | Search again and use the returned collection slug. |
| 404 | `AUDIO_NOT_FOUND` | Search again; do not combine an audio ID with another collection. |
| 404 | `AUDIO_UNAVAILABLE` | Do not retry repeatedly; select another candidate. |
| 422 | validation error | Shorten the original query or expanded query list and correct the request body. |

Treat an empty, truncated, or undecodable MP3 as failed. Do not present a partial file as a completed download.
