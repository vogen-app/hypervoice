# Voice cloning options

## Multipart fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `audio` | binary file | yes | MP3, WAV, M4A, FLAC, OGG, or WebM; maximum 25 MB. |
| `name` | string | yes | 1–100 characters. |
| `description` | string | no | Internal description for later selection. |
| `language` | string | no | Defaults to `auto`; use the dominant BCP-47-style code such as `en`, `zh-CN`, or `ja`. |

## Reference recording guidance

- Prefer 10–30 seconds of one speaker in a quiet room.
- Use natural, expressive speech without music, reverb, clipping, or overlapping voices.
- Do not upload secrets or unrelated personal information.
- Confirm consent and intended use before any upload.

## Response

```json
{
  "voice_id": 123,
  "name": "My narrator",
  "description": null,
  "source_type": "clone",
  "language": "en",
  "gender": null,
  "age": null,
  "accent": null,
  "tags": null,
  "created": true
}
```

Common errors: `UNSUPPORTED_AUDIO_FORMAT`, `INVALID_AUDIO_FILE`, `EMPTY_AUDIO`, `AUDIO_TOO_LARGE`, `VOICE_LIMIT_EXCEEDED`, `INVALID_API_KEY`.

## Delete

`DELETE https://api.vogen.app/v1/voices/{voice_id}` removes a private cloned or uploaded voice owned by the API key. Library voices cannot be deleted. The response is:

```json
{
  "voice_id": 123,
  "deleted": true
}
```

Common errors: `VOICE_NOT_FOUND`, `VOICE_FORBIDDEN`, `VOICE_NOT_DELETABLE`, `INVALID_API_KEY`.
