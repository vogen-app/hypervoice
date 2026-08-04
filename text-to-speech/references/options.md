# Text-to-speech options

## Request

`POST /v1/text-to-speech/{voice_id}` with JSON:

| Field | Type | Default | Notes |
|---|---|---|---|
| `text` | string | required | 1–10,000 characters; account plan rules still apply. |
| `output_language` | string | `auto` | Select a language/dialect below. |
| `auto_translate_input_text` | boolean | `true` | Translate text when an explicit output language is selected. |
| `emotion_type` | string | `default` | `default`, `text`, `vector`, or `audio`. |
| `emotion_weight` | number | `0.6` | `0.0`–`1.0`; used with text emotion. |
| `emotion_vector` | number[8] | omitted | Required for `emotion_type=vector`. |
| `emotion_id` | integer | omitted | Required for `emotion_type=audio`. |

Use `emotion_type=text` to derive delivery from the input text, or `emotion_type=vector` with an eight-value vector ordered as: happy, angry, sad, anxious, disgusted, upset, surprised, calm. For `emotion_type=audio`, resolve a named reference through the `emotion-library` skill and pass its ID internally.

## Output languages

`auto`, `arabic`, `burmese`, `chinese`, `danish`, `dutch`, `english`, `finnish`, `french`, `german`, `greek`, `hebrew`, `hindi`, `indonesian`, `italian`, `japanese`, `khmer`, `korean`, `lao`, `malay`, `norwegian`, `polish`, `portuguese`, `russian`, `spanish`, `swahili`, `swedish`, `tagalog`, `thai`, `turkish`, `vietnamese`.

Chinese dialects: `sichuanese`, `cantonese`, `northeastern_mandarin`, `shaanxi`, `tianjin`, `hokkien`.

## Response

- Status: `200 OK`
- Content-Type: `audio/mpeg`
- Body: streamed MP3 bytes
- Useful headers: `X-Vogen-Task-Id`, `X-Character-Count`

Audio is returned directly in the response. Do not expect a JSON URL.
