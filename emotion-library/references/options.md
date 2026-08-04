# Emotion library options

## Query parameters

| Parameter | Values | Default |
|---|---|---|
| `scope` | `mine`, `library`, `all` | `all` |
| `limit` | 1–100 | 50 |
| `offset` | 0 or greater | 0 |

`mine` returns active private emotions belonging to the API key owner. `library` returns active system and public emotions. `all` combines and deduplicates both sets.

## Response fields

```json
{
  "emotions": [
    {
      "emotion_id": 123,
      "name": "Bright delivery",
      "description": "Energetic and cheerful reference",
      "source_type": "upload",
      "tags": ["positive", "energetic"],
      "created_at": "2026-07-19T12:00:00"
    }
  ]
}
```

The Agent API intentionally omits user IDs, storage keys, and audio URLs. Use `emotion_id` internally for `emotion_type=audio`, but show users the emotion name and descriptive metadata unless they explicitly request debugging information.
