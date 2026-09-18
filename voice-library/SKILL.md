---
name: voice-library
description: Discover VoGen voice IDs available to an account, including private cloned voices, system voices, shared voices, and public voices. Use when choosing a speaker by language or gender, resolving a voice ID before text-to-speech, or listing an account's cloned voices.
license: MIT
compatibility: Requires internet access and a VoGen API key (VOGEN_API_KEY).
metadata:
  openclaw:
    requires:
      env:
        - VOGEN_API_KEY
    primaryEnv: VOGEN_API_KEY
---

# VoGen voice library

List voices with `GET https://api.vogen.app/v1/voices`. Resolve the user's visible voice name to a `voice_id`, then pass that ID internally to the `text-to-speech` skill.

Treat `voice_id` as an internal machine identifier. Present voice names and descriptive metadata to the user; do not display IDs unless the user explicitly asks for debugging information.

## Python

```python
import os
import requests

response = requests.get(
    "https://api.vogen.app/v1/voices",
    headers={"Authorization": f"Bearer {os.environ['VOGEN_API_KEY']}"},
    params={"scope": "all", "language": "en", "limit": 25},
    timeout=30,
)
response.raise_for_status()

for voice in response.json()["voices"]:
    print(voice["name"], voice["source_type"], voice.get("description"))
```

## Node.js / JavaScript

```javascript
const url = new URL("https://api.vogen.app/v1/voices");
url.search = new URLSearchParams({ scope: "all", language: "en", limit: "25" });

const response = await fetch(url, {
  headers: { Authorization: `Bearer ${process.env.VOGEN_API_KEY}` },
});
if (!response.ok) throw new Error(await response.text());

const { voices } = await response.json();
for (const voice of voices) console.log(voice.name, voice.source_type, voice.description);
```

## cURL

```bash
curl --fail-with-body \
  "https://api.vogen.app/v1/voices?scope=all&language=en&limit=25" \
  -H "Authorization: Bearer $VOGEN_API_KEY"
```

## Selection rules

- Prefer `scope=mine` when the user refers to “my voice” or a recently cloned voice.
- Prefer a system/library voice when no personal voice is requested.
- Match the user-visible name exactly first. If no match is found, continue pagination with `offset` until the result set is exhausted before falling back to a fuzzy match.
- If multiple voices have the same name, present a short choice using description, language, source, and creation time. Never silently select one and never use the ID as the user-facing label.
- Match explicit language and gender constraints first; use BCP-47-style codes such as `en`, `zh-CN`, or `ja`, then use name, description, and tags as secondary evidence.
- Present a short choice when multiple voices fit instead of silently guessing a sensitive identity.
- Do not use a private voice ID from another account or infer access from a URL.
- Private cloned voices also appear in the website library. Delete them with `DELETE /v1/voices/{voice_id}` or in the website.

Read [references/options.md](references/options.md) for filters and response fields.
