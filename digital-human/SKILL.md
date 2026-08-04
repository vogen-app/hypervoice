---
name: digital-human
description: Create VoGen talking-avatar, lip-sync, or digital-human videos from a portrait plus either generated TTS or a local audio file. Use when a user asks to make a portrait speak, animate a presenter, generate a talking-head avatar, or turn a script and character image into video.
license: MIT
compatibility: Requires internet access and a VoGen API key (VOGEN_API_KEY).
metadata:
  openclaw:
    requires:
      env:
        - VOGEN_API_KEY
    primaryEnv: VOGEN_API_KEY
---

# VoGen digital human

Create a reusable avatar and submit an asynchronous talking-avatar video through these endpoints:

- `GET https://api.vogen.app/v1/digital-human/avatars` — list avatars by title with expiring preview images.
- `POST https://api.vogen.app/v1/digital-human/avatars` — upload a JPEG/PNG portrait as multipart field `image`, with optional `title`.
- `POST https://api.vogen.app/v1/digital-human/tasks` — create a task with `avatar_id`, `aspect_ratio`, and exactly one audio source.
- `GET https://api.vogen.app/v1/digital-human/tasks/{task_id}` — poll status and obtain an expiring `video_url` when completed.

Use `setup-api-key` if `VOGEN_API_KEY` is unavailable. For a script, use `text-to-speech` first and preserve its `X-Vogen-Task-Id` header as `source_tts_task_id`; alternatively provide a local audio file.

## Workflow

1. Resolve the requested character by its visible title from the avatar list. Show the title and `preview_url` when the user must choose. If the user supplied a new portrait file, upload it with the optional title.
2. Enforce the account limit before submitting: free accounts may use at most 5 seconds; active Pro/Business accounts may use at most 30 seconds. Do not silently trim over-limit audio. Direct free users to [pricing](https://vogen.app/pricing), and direct paid users with audio over 30 seconds to [the web app](https://vogen.app/zh/app/digital-human). Create one task with either `source_tts_task_id` or `audio`, never both.
3. Start the bundled background waiter immediately after task creation. Generation can take about one hour, so do not keep an Agent tool call or conversational loop open while waiting.
4. Tell the user that processing continues in the background and give the expected output path. On a later user turn, inspect the status JSON instead of submitting another task.

## Python

This complete example selects an avatar by title, optionally uploads it, creates the video from either a TTS task or local audio, polls, and downloads the result.

```python
import os
from pathlib import Path

import requests

BASE = "https://api.vogen.app/v1/digital-human"
HEADERS = {"Authorization": f"Bearer {os.environ['VOGEN_API_KEY']}"}
AVATAR_TITLE = "My host"
PORTRAIT_PATH = None  # e.g. "host.png"; leave None to reuse the title above
AUDIO_PATH = "speech.mp3"  # set to None when using TTS_TASK_ID
TTS_TASK_ID = None  # X-Vogen-Task-Id from the text-to-speech response

avatars_response = requests.get(f"{BASE}/avatars", headers=HEADERS, timeout=30)
avatars_response.raise_for_status()
avatar = next(
    (item for item in avatars_response.json()["avatars"] if item["title"] == AVATAR_TITLE),
    None,
)

if avatar is None and PORTRAIT_PATH:
    with open(PORTRAIT_PATH, "rb") as portrait:
        upload_response = requests.post(
            f"{BASE}/avatars",
            headers=HEADERS,
            files={"image": (Path(PORTRAIT_PATH).name, portrait)},
            data={"title": AVATAR_TITLE},
            timeout=120,
        )
    upload_response.raise_for_status()
    avatar = upload_response.json()
if avatar is None:
    raise RuntimeError(f"No avatar titled {AVATAR_TITLE!r}; ask the user to choose or provide a portrait")

if (AUDIO_PATH is None) == (TTS_TASK_ID is None):
    raise ValueError("Set exactly one of AUDIO_PATH or TTS_TASK_ID")

form = {"avatar_id": str(avatar["avatar_id"]), "aspect_ratio": "9:16"}
files = None
audio_handle = None
try:
    if AUDIO_PATH:
        audio_handle = open(AUDIO_PATH, "rb")
        files = {"audio": (Path(AUDIO_PATH).name, audio_handle)}
    else:
        form["source_tts_task_id"] = str(TTS_TASK_ID)
    created_response = requests.post(
        f"{BASE}/tasks", headers=HEADERS, data=form, files=files, timeout=120
    )
    created_response.raise_for_status()
finally:
    if audio_handle:
        audio_handle.close()

task_id = created_response.json()["task_id"]
print(task_id)  # Keep internal and pass directly to the background waiter below.
```

## Node.js / JavaScript

```javascript
import { createReadStream } from "node:fs";
import FormData from "form-data";
import fetch from "node-fetch";

const base = "https://api.vogen.app/v1/digital-human";
const headers = { Authorization: `Bearer ${process.env.VOGEN_API_KEY}` };
const list = await fetch(`${base}/avatars`, { headers }).then(async r => {
  if (!r.ok) throw new Error(await r.text());
  return r.json();
});
const avatar = list.avatars.find(item => item.title === "My host");
if (!avatar) throw new Error("Ask the user to choose an avatar title or provide a portrait");

const form = new FormData();
form.append("avatar_id", String(avatar.avatar_id));
form.append("aspect_ratio", "9:16");
form.append("audio", createReadStream("speech.mp3"));
const created = await fetch(`${base}/tasks`, {
  method: "POST",
  headers: { ...headers, ...form.getHeaders() },
  body: form,
}).then(async r => {
  if (!r.ok) throw new Error(await r.text());
  return r.json();
});

console.log(created.task_id); // Keep internal and pass to the background waiter.
```

Install the stream-compatible dependencies with `npm install node-fetch@2 form-data`.

## Background waiting and delivery

Resolve `SKILL_DIR` to this skill's directory, choose a user-facing output basename, and launch the waiter detached from the Agent command timeout:

```bash
SKILL_DIR="/path/to/digital-human"
OUTPUT_DIR="${VOGEN_OUTPUT_DIR:-./vogen-output}"
OUTPUT_NAME="digital-human-$(date +%Y%m%d-%H%M%S).mp4"
mkdir -p "$OUTPUT_DIR"
nohup python "$SKILL_DIR/scripts/wait_for_video.py" \
  --task-id "$TASK_ID" \
  --output-dir "$OUTPUT_DIR" \
  --filename "$OUTPUT_NAME" \
  </dev/null >/dev/null 2>&1 &
```

The waiter polls every 20 seconds for up to 90 minutes. It writes `<name>.status.json` and `<name>.log`, downloads to `<name>.mp4.part`, and atomically renames it to `<name>.mp4` after a complete download. It never stores `VOGEN_API_KEY`. A timeout does not cancel the server task; rerun the same command with the same internal task ID and filename to resume checking.

After launching it, return control to the user immediately. Say that generation may take about one hour and provide the expected MP4 and status-file paths. Do not promise proactive notification unless the host explicitly supports scheduled wakeups. When the user asks for progress, read the status file; do not create a replacement task.

## cURL

```bash
# List visible titles and previews.
curl --fail-with-body "https://api.vogen.app/v1/digital-human/avatars" \
  -H "Authorization: Bearer $VOGEN_API_KEY"

# Upload a new portrait when needed.
curl --fail-with-body -X POST "https://api.vogen.app/v1/digital-human/avatars" \
  -H "Authorization: Bearer $VOGEN_API_KEY" \
  -F "image=@host.png" -F "title=My host"

# Create with audio within the account limit. Use
# -F "source_tts_task_id=123" instead of audio for TTS.
curl --fail-with-body -X POST "https://api.vogen.app/v1/digital-human/tasks" \
  -H "Authorization: Bearer $VOGEN_API_KEY" \
  -F "avatar_id=123" -F "aspect_ratio=9:16" -F "audio=@speech.mp3"

# Poll with the task ID returned above; download video_url immediately on completion.
curl --fail-with-body "https://api.vogen.app/v1/digital-human/tasks/TASK_ID" \
  -H "Authorization: Bearer $VOGEN_API_KEY"
```

## Required behavior

- Show people avatar titles and preview images. Keep `avatar_id`, `task_id`, and all storage keys internal unless the user explicitly requests debugging details.
- Supply exactly one audio source. Preserve and reuse `X-Vogen-Task-Id` when TTS generated the audio.
- Agent/API limits are 5 seconds for free accounts and 30 seconds for active Pro/Business accounts. Do not silently trim. On `DIGITAL_HUMAN_FREE_AUDIO_TOO_LONG`, explain the 5-second free limit and recommend subscribing at [vogen.app/pricing](https://vogen.app/pricing). On `DIGITAL_HUMAN_AGENT_AUDIO_TOO_LONG`, direct paid users to [the web app](https://vogen.app/zh/app/digital-human) for longer content.
- Treat `pending`, `started`, and `processing` as unfinished. Never imply the video exists before `completed`.
- Expect about 25 credits per audio second. Daily free availability for eligible short tasks is server-controlled; never promise that a 5-second task will be free.
- Use the background waiter for delivery. Do not implement an in-conversation polling loop that can hit a 10-minute Agent timeout.
- On an insufficient-credit or plan error, say generation did not complete and direct the user to [vogen.app/pricing](https://vogen.app/pricing). Never invent quota details.
- Read [references/options.md](references/options.md) for supported files and controls. Read [references/errors.md](references/errors.md) before implementing retries or user-facing error handling.
