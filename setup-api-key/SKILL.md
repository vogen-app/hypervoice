---
name: setup-api-key
description: Configure and validate a VoGen API key for HyperVoice integrations. Use when VOGEN_API_KEY is missing, invalid, expired, or revoked, or when a user asks how to access VoGen from an Agent or server-side application.
license: MIT
compatibility: Requires internet access to vogen.app and api.vogen.app.
---

# Set up a VoGen API key

Configure `VOGEN_API_KEY` without exposing it in chat, logs, source control, or browser code.

## Workflow

1. Check whether `VOGEN_API_KEY` exists in the process environment. If absent, check a local `.env` file without printing its value.
2. If a key exists, validate it with `GET https://api.vogen.app/v1/user` and `Authorization: Bearer <key>`.
3. If validation succeeds, stop. Do not rotate a working key unless the user requests it.
4. If no valid key exists, direct the user to [vogen.app/api-keys](https://vogen.app/api-keys). Ask them to sign in, create a named key, and save the one-time value locally as:

   ```dotenv
   VOGEN_API_KEY=vogen_your_key_here
   ```

5. Ask the user to confirm that they saved it; never ask them to paste it into chat.
6. Re-read `.env`, validate the saved value, and report only success or the error code.

## Validate with cURL

```bash
curl --fail-with-body "https://api.vogen.app/v1/user" \
  -H "Authorization: Bearer $VOGEN_API_KEY"
```

## Safety rules

- Use VoGen API keys only in trusted server-side or local Agent environments.
- Never embed a key in browser JavaScript, mobile bundles, public repositories, screenshots, or shell history.
- Prefer a secret manager in production and `.env` for local development.
- Revoke a disclosed key immediately at [vogen.app/api-keys](https://vogen.app/api-keys).
- Treat `401 INVALID_API_KEY` as a setup problem; do not retry it repeatedly.

Read [references/errors.md](references/errors.md) when validation fails.
