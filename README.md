# VoGen Agent Skills

Portable [Agent Skills](https://agentskills.io) for the VoGen voice platform. The collection works with clients that support the Agent Skills format and can make HTTP requests or run commands, including Cursor, Claude Code, Codex, and compatible ChatGPT environments.

API base: `https://api.vogen.app/v1`

## Included skills

| Skill | Purpose |
|---|---|
| [`setup-api-key`](setup-api-key/) | Configure and validate a VoGen API key safely. |
| [`voice-library`](voice-library/) | Find private, system, shared, and public voices by name. |
| [`voice-cloning`](voice-cloning/) | Create a private zero-shot voice from authorized reference audio. |
| [`emotion-library`](emotion-library/) | Find named audio-emotion references. |
| [`text-to-speech`](text-to-speech/) | Generate and stream MP3 speech from text. |
| [`sound-effects`](sound-effects/) | Search and download royalty-free MP3 sound effects. |
| [`digital-human`](digital-human/) | Create asynchronous talking-avatar videos from portraits and audio. |

The skills compose naturally. For example, `voice-library` resolves a readable voice name before `text-to-speech`; the TTS task ID can then be passed internally to `digital-human`. `setup-api-key` supports every authenticated skill.

## Install

### Download the release package

Download [vogen-skills-1.0.0.zip](https://static.vogen.app/skills/vogen-skills-1.0.0.zip), extract it, then copy the seven skill folders into one of the locations below. Keep this README outside the skills directory.

| Client | Project skills | Personal skills |
|---|---|---|
| Cursor | `.agents/skills/` or `.cursor/skills/` | `~/.agents/skills/` or `~/.cursor/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Other compatible agents | Use the Agent Skills directory documented by the client. | Use the client’s global Agent Skills directory. |

Reload the client after installing if it does not discover new skills automatically.

### GitHub and `npx skills`

Source repository: [github.com/vogen-app/hypervoice](https://github.com/vogen-app/hypervoice)

Install with the community `skills` CLI:

```bash
npx skills add vogen-app/hypervoice
```

`npx skills` is a convenient installer, not a requirement of the Agent Skills specification. The ZIP and manual directory methods remain fully supported.

## Configure

Create or revoke keys at [vogen.app/app/api-keys](https://vogen.app/app/api-keys), then store the key locally:

```bash
export VOGEN_API_KEY="vogen_..."
```

For a project `.env` file:

```dotenv
VOGEN_API_KEY=vogen_...
```

Never commit the key, paste it into chat, expose it in browser code, or print it in logs. Validate it without displaying its value:

```bash
curl --fail-with-body "https://api.vogen.app/v1/user" \
  -H "Authorization: Bearer $VOGEN_API_KEY"
```

## Use

Describe the outcome normally. Compatible agents discover the relevant skill from its description, or let you invoke it explicitly. Example requests:

- “Find a warm English narrator and save this script as an MP3.”
- “Find a cinematic metal door slam for this scene.”
- “Clone this authorized recording, then use it to narrate the supplied text.”
- “Turn this portrait and generated narration into a talking-avatar video.”

Agents keep machine identifiers such as `voice_id`, `emotion_id`, `audio_id`, collection slugs, avatar IDs, and task IDs internal unless debugging requires them. User-facing responses should use readable names and local output paths.

## Runtime behavior and limits

All calls use the API key owner’s existing VoGen account. The web product and REST API share voices, sound-effect unlocks, plan restrictions, generation queues, usage accounting, and credit deductions.

- Speech and sound-effect output is returned directly as MP3 bytes, not as a public storage URL.
- Completed digital-human tasks return a short-lived signed video URL.
- Agent/API digital-human tasks accept up to 5 seconds for free accounts and 30 seconds for active Pro/Business accounts.
- A chat-only client still needs an HTTP, command, Plugin, or MCP tool before it can execute the API workflow. The Skill files provide the portable instructions; they do not create network tools by themselves.

## Update or uninstall

To update a ZIP installation, download the newer immutable release and replace only the seven VoGen skill folders. To uninstall, remove those folders from the client’s skills directory. Removing skills does not revoke the API key; revoke unused keys separately from the [API keys page](https://vogen.app/app/api-keys).

The optional `agents/openai.yaml` files and host metadata improve presentation in clients that understand them. Core behavior lives in `SKILL.md` and does not depend on a specific vendor.
