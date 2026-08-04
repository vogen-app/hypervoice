# API key errors

| HTTP | Code | Action |
|---|---|---|
| 401 | `API_KEY_REQUIRED` | Set `Authorization: Bearer $VOGEN_API_KEY`. |
| 401 | `INVALID_API_KEY` | Create or rotate the key at `https://vogen.app/api-keys`. |
| 403 | `ACCOUNT_DISABLED` | Ask the account owner to contact VoGen support. |

Error bodies use:

```json
{"detail":{"code":"INVALID_API_KEY","message":"The VoGen API key is invalid, expired, or revoked."}}
```
