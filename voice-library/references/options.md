# Voice library options

## Query parameters

| Parameter | Values | Default |
|---|---|---|
| `scope` | `mine`, `library`, `all` | `all` |
| `language` | language identifier | omitted |
| `gender` | `male`, `female`, `neutral` | omitted |
| `limit` | 1–100 | 50 |
| `offset` | 0 or greater | 0 |

`mine` returns private voices belonging to the API key owner. `library` returns system, shared, and public voices. `all` combines and deduplicates both sets.

## Response fields

```json
{
  "voices": [
    {
      "voice_id": 123,
      "name": "Warm narrator",
      "description": "Calm long-form narration",
      "source_type": "system",
      "language": "en",
      "gender": "female",
      "age": "adult",
      "accent": "en-us",
      "tags": ["warm", "narration"],
      "created_at": "2026-07-19T12:00:00"
    }
  ]
}
```

The Agent API intentionally omits storage URLs. Use `voice_id` as the stable synthesis identifier internally, but show users the voice name and descriptive metadata unless they explicitly request debugging information.

Private cloned or uploaded voices can be removed with `DELETE /v1/voices/{voice_id}`. Library voices cannot be deleted.
