---
name: voice-cloning
description: Create a private VoGen voice from a local reference recording. Use when a user asks to clone, copy, reproduce, or save a voice for later text-to-speech, and they have an authorized MP3, WAV, M4A, FLAC, OGG, or WebM sample.
license: MIT
compatibility: Requires internet access and a VoGen API key (VOGEN_API_KEY).
metadata:
  openclaw:
    requires:
      env:
        - VOGEN_API_KEY
    primaryEnv: VOGEN_API_KEY
---

# VoGen voice cloning

Upload reference audio as `multipart/form-data` to `POST https://api.vogen.app/v1/voices/clone`. VoGen creates a private zero-shot reference voice and returns its `voice_id` as JSON.

Before uploading, confirm the user owns the recording or has clear permission from the speaker. Refuse deceptive impersonation, fraud, evasion, harassment, or non-consensual cloning.

## Python

```python
import os
import requests

with open("reference.wav", "rb") as audio_file:
    response = requests.post(
        "https://api.vogen.app/v1/voices/clone",
        headers={"Authorization": f"Bearer {os.environ['VOGEN_API_KEY']}"},
        files={"audio": ("reference.wav", audio_file, "audio/wav")},
        data={"name": "My narrator", "language": "en"},
        timeout=120,
    )

response.raise_for_status()
voice = response.json()
print(f"Saved voice: {voice['name']}")
```

For an in-memory stream:

```python
from io import BytesIO

audio = BytesIO(reference_bytes)
files = {"audio": ("reference.wav", audio, "audio/wav")}
```

## Node.js / JavaScript

```javascript
import { createReadStream } from "node:fs";
import FormData from "form-data";
import fetch from "node-fetch";

const form = new FormData();
form.append("audio", createReadStream("reference.wav"));
form.append("name", "My narrator");
form.append("language", "en");

const response = await fetch("https://api.vogen.app/v1/voices/clone", {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.VOGEN_API_KEY}`, ...form.getHeaders() },
  body: form,
});
if (!response.ok) throw new Error(await response.text());
const voice = await response.json();
console.log(`Saved voice: ${voice.name}`);
```

Install the two stream-compatible HTTP dependencies with `npm install node-fetch form-data`.

## cURL

```bash
curl --fail-with-body -X POST \
  "https://api.vogen.app/v1/voices/clone" \
  -H "Authorization: Bearer $VOGEN_API_KEY" \
  -F "audio=@reference.wav" \
  -F "name=My narrator" \
  -F "language=en"
```

Use the returned `voice_id` internally with the `text-to-speech` skill. Confirm success to the user with the saved voice name, not its ID, unless they explicitly request debugging information. A repeated upload of the same bytes is idempotent and returns the existing private voice with `created: false`.

Read [references/options.md](references/options.md) for recording and request constraints. On a plan or credit limit, notify the user and recommend [vogen.app/pricing](https://vogen.app/pricing) without inventing quota details.
