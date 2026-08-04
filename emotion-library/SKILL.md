---
name: emotion-library
description: Discover VoGen audio emotion references available to an account, including private uploaded emotions, system emotions, and public emotions. Use when resolving a named emotion reference before text-to-speech with emotion_type=audio.
license: MIT
compatibility: Requires internet access and a VoGen API key (VOGEN_API_KEY).
metadata:
  openclaw:
    requires:
      env:
        - VOGEN_API_KEY
    primaryEnv: VOGEN_API_KEY
---

# VoGen emotion library

List audio emotion references with `GET https://api.vogen.app/v1/emotions`. Resolve the user's visible emotion name to an `emotion_id`, then pass that ID internally to the `text-to-speech` skill with `emotion_type=audio`.

Treat `emotion_id` as an internal machine identifier. Present emotion names and descriptive metadata to the user; do not display IDs unless the user explicitly asks for debugging information.

## Python

```python
import os
import requests

response = requests.get(
    "https://api.vogen.app/v1/emotions",
    headers={"Authorization": f"Bearer {os.environ['VOGEN_API_KEY']}"},
    params={"scope": "all", "limit": 100, "offset": 0},
    timeout=30,
)
response.raise_for_status()

for emotion in response.json()["emotions"]:
    print(emotion["name"], emotion["description"], emotion["source_type"])
```

## Node.js / JavaScript

```javascript
const url = new URL("https://api.vogen.app/v1/emotions");
url.search = new URLSearchParams({ scope: "all", limit: "100", offset: "0" });

const response = await fetch(url, {
  headers: { Authorization: `Bearer ${process.env.VOGEN_API_KEY}` },
});
if (!response.ok) throw new Error(await response.text());

const { emotions } = await response.json();
for (const emotion of emotions) {
  console.log(emotion.name, emotion.description, emotion.source_type);
}
```

## cURL

```bash
curl --fail-with-body \
  "https://api.vogen.app/v1/emotions?scope=all&limit=100&offset=0" \
  -H "Authorization: Bearer $VOGEN_API_KEY"
```

## Selection rules

- Prefer `scope=mine` when the user refers to “my emotion,” an uploaded emotion, or a recently created emotion reference.
- Match the user-visible name exactly first. If no match is found, continue pagination by increasing `offset` until a page contains fewer items than `limit`.
- If multiple emotions have the same name, present a short choice using description, source, tags, and creation time. Never silently select one and never use the ID as the user-facing label.
- Use `scope=library` for system and public emotion references, and `scope=all` only when both account and library resources are relevant.
- Do not use a private emotion ID from another account or infer access from a URL.

Read [references/options.md](references/options.md) for query parameters and response fields.
