# Digital-human errors

Handle the JSON error code without exposing internal IDs or storage keys.

| HTTP | Codes | Action |
|---:|---|---|
| 401 | `API_KEY_REQUIRED`, `INVALID_API_KEY` | Configure or replace `VOGEN_API_KEY` with `setup-api-key`. |
| 402 | `INSUFFICIENT_CREDITS` | Stop and direct the user to `https://vogen.app/pricing`. |
| 403 | `DIGITAL_HUMAN_FREE_AUDIO_TOO_LONG`, `DIGITAL_HUMAN_AGENT_AUDIO_TOO_LONG`, `ACCOUNT_DISABLED` | Free audio is limited to 5 seconds: recommend `https://vogen.app/pricing`. Paid Agent/API audio is limited to 30 seconds: shorten it or use `https://vogen.app/zh/app/digital-human`. Restore disabled accounts before retrying. |
| 404 | `DIGITAL_HUMAN_AVATAR_NOT_FOUND`, `DIGITAL_HUMAN_TASK_NOT_FOUND` | Refresh the avatar list or verify that the task belongs to this API-key owner. |
| 400 | `DIGITAL_HUMAN_INVALID_ASPECT_RATIO`, `DIGITAL_HUMAN_INVALID_AUDIO_SOURCE`, `DIGITAL_HUMAN_CREDIT_QUOTE_BLOCKED` | Correct the request rather than retrying unchanged. |
| 413 | `IMAGE_TOO_LARGE`, `AUDIO_TOO_LARGE` | Reduce the uploaded file size. |
| 422 | `PROVIDE_EXACTLY_ONE_AUDIO_SOURCE`, `UNSUPPORTED_IMAGE_FORMAT`, `UNSUPPORTED_AUDIO_FORMAT`, `INVALID_IMAGE_FILE`, `INVALID_AUDIO_FILE`, `UNREADABLE_AUDIO`, `VALIDATION_ERROR` | Correct fields or replace the file. |
| 502 | `DIGITAL_HUMAN_SUBMIT_FAILED` | Report that submission failed; retry only with user consent. |
| 503 | `WRITE_MAINTENANCE_MODE` | Wait and retry later. |

A successfully submitted task may later return status `failed` with `error_code: DIGITAL_HUMAN_GENERATION_FAILED`. Treat it as terminal and do not retry automatically or claim a video was produced.
