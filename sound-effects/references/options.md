# Sound-effects API options

## Search

`POST /v1/sound-effects/search` with JSON:

| Field | Type | Default | Notes |
|---|---|---|---|
| `query` | string | required | Original natural-language request, 1–300 characters. |
| `expanded_queries` | string[] | `[]` | Up to 8 distinct short queries; each must be 1–80 characters. |
| `limit` | integer | `5` | 1–10 audio candidates. |

Each result contains `audio_id`, localized `title`, `collection_slug`, localized `collection_name`, `category_slug`, `duration_sec`, normalized `match_score`, `matched_query`, `is_free_preview`, `is_unlocked`, `locked`, `lock_reason`, and `would_consume_unlock`.

The response also reports `free_unlock_limit`, `free_unlock_used`, and `free_unlock_remaining`. The remaining value is `null` for an active unlimited account.

## Download

`GET /v1/sound-effects/audio/{audio_id}?collection={collection_slug}` returns:

- Status: `200 OK`
- Content-Type: `audio/mpeg`
- Body: MP3 bytes
- `Content-Disposition`: safe library-derived filename
- `X-Vogen-Unlock-Consumed`: `true` or `false`
- `X-Vogen-Free-Unlocks-Remaining`: present for non-member accounts

Search is read-only. A Hobby unlock is consumed only when downloading a non-preview audio that the account has not previously unlocked.
