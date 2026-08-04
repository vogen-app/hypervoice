---
name: sound-effects
description: Search, select, and download royalty-free MP3 sound effects from the VoGen library. Use for ambience, Foley, transitions, impacts, UI sounds, nature, reactions, game audio, or any request for non-speech SFX, including natural-language descriptions that do not match an exact library name.
license: MIT
compatibility: Requires internet access and a VoGen API key (VOGEN_API_KEY).
metadata:
  openclaw:
    requires:
      env:
        - VOGEN_API_KEY
    primaryEnv: VOGEN_API_KEY
---

# VoGen sound effects

Find library audio through `POST https://api.vogen.app/v1/sound-effects/search`, then download the selected MP3 from `GET https://api.vogen.app/v1/sound-effects/audio/{audio_id}?collection={collection_slug}`. Use `setup-api-key` when `VOGEN_API_KEY` is unavailable.

This skill searches existing royalty-free library audio. It does not generate a new custom sound.

## Workflow

1. Extract the audible source or object, action, material, intensity, environment, and sound type from the user's description. Ignore request filler such as “find me,” “for my video,” or “I need a sound.”
2. Produce 2–6 distinct search phrases of 1–4 keywords each. Always include one canonical English phrase. For Chinese, Spanish, or Japanese input, also retain concise phrases in that language. Do not invent a large synonym list; derive only terms supported by the request.
3. Send the original description as `query` and the short phrases as `expanded_queries`. Search does not consume a free unlock.
4. Treat the first result as high confidence only when its `match_score` is at least `0.82` and it is the only result or leads the second result by at least `0.12`. Download it automatically. If the user explicitly permits any reasonable result, use a threshold of `0.65` without requiring the lead.
5. Otherwise show at most three candidates using title, collection, and duration, and ask the user to choose. If there are no results, say that no close library sound was found; do not substitute an unrelated result.
6. Download only the chosen result. Use the user's output path when supplied; otherwise save to `./vogen-output/<collection>-<timestamp>.mp3`. After completion, report the readable title, local path, and remaining free unlocks when the response provides that header.

Example expansion:

```json
{
  "query": "木门被人用力砰地关上",
  "expanded_queries": ["door slam", "wood door close", "heavy door impact", "木门关门"],
  "limit": 5
}
```

## Python

```python
import os
from datetime import datetime
from pathlib import Path

import requests

headers = {"Authorization": f"Bearer {os.environ['VOGEN_API_KEY']}"}
search = requests.post(
    "https://api.vogen.app/v1/sound-effects/search",
    headers=headers,
    json={
        "query": "木门被人用力砰地关上",
        "expanded_queries": ["door slam", "wood door close", "木门关门"],
        "limit": 5,
    },
    timeout=30,
)
search.raise_for_status()
results = search.json()["results"]
if not results:
    raise RuntimeError("No close sound effect found")

selected = results[0]  # Apply the confidence rules above before selecting.
output_dir = Path("vogen-output")
output_dir.mkdir(parents=True, exist_ok=True)
output = output_dir / f"{selected['collection_slug']}-{datetime.now():%Y%m%d-%H%M%S}.mp3"
download = requests.get(
    f"https://api.vogen.app/v1/sound-effects/audio/{selected['audio_id']}",
    headers=headers,
    params={"collection": selected["collection_slug"]},
    stream=True,
    timeout=120,
)
download.raise_for_status()
with output.open("wb") as file:
    for chunk in download.iter_content(64 * 1024):
        if chunk:
            file.write(chunk)
print(output, download.headers.get("X-Vogen-Free-Unlocks-Remaining"))
```

## Node.js / JavaScript

```javascript
import { createWriteStream, mkdirSync } from "node:fs";
import { Readable } from "node:stream";
import { finished } from "node:stream/promises";

const headers = {
  Authorization: `Bearer ${process.env.VOGEN_API_KEY}`,
  "Content-Type": "application/json",
};
const search = await fetch("https://api.vogen.app/v1/sound-effects/search", {
  method: "POST",
  headers,
  body: JSON.stringify({
    query: "a heavy wooden door slams shut",
    expanded_queries: ["door slam", "wood door close", "heavy door impact"],
    limit: 5,
  }),
});
if (!search.ok) throw new Error(await search.text());
const [selected] = (await search.json()).results;
if (!selected) throw new Error("No close sound effect found");

const url = new URL(`https://api.vogen.app/v1/sound-effects/audio/${selected.audio_id}`);
url.searchParams.set("collection", selected.collection_slug);
const download = await fetch(url, { headers: { Authorization: headers.Authorization } });
if (!download.ok || !download.body) throw new Error(await download.text());
mkdirSync("vogen-output", { recursive: true });
const output = `vogen-output/${selected.collection_slug}-${Date.now()}.mp3`;
await finished(Readable.fromWeb(download.body).pipe(createWriteStream(output)));
console.log(output, download.headers.get("x-vogen-free-unlocks-remaining"));
```

## cURL

```bash
curl --fail-with-body -X POST "https://api.vogen.app/v1/sound-effects/search" \
  -H "Authorization: Bearer $VOGEN_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"query":"heavy wooden door slams shut","expanded_queries":["door slam","wood door close","heavy door impact"],"limit":5}'

curl --fail-with-body \
  "https://api.vogen.app/v1/sound-effects/audio/AUDIO_ID?collection=COLLECTION_SLUG" \
  -H "Authorization: Bearer $VOGEN_API_KEY" \
  --output sound-effect.mp3
```

## Required behavior

- Keep `audio_id`, `collection_slug`, and storage details internal. Show readable titles and collection names unless the user explicitly requests debugging information.
- Never expose or follow a storage key or unsigned source URL. Download only through the authenticated Agent endpoint.
- `would_consume_unlock=true` means downloading a new sound will use one Hobby unlock. High-confidence automatic downloads may consume it; never download low-confidence candidates speculatively.
- An MP3 marked `is_free_preview=true` or `is_unlocked=true` does not consume another unlock. Pro and Business accounts are unlimited while active.
- Treat the `X-Vogen-Unlock-Consumed` and `X-Vogen-Free-Unlocks-Remaining` response headers as authoritative after a download.

Read [references/options.md](references/options.md) for request and response fields. Read [references/errors.md](references/errors.md) before retrying a failed request.
