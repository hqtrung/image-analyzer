---
name: image-analyzer
description: |
  Analyze images using xAI Grok Vision with configurable criteria presets.
  Classify safety, score artistic quality, extract content/technical details,
  or decode visual style DNA for transfer — by injecting user-selected presets.
  Supports both preset names (safety, artistic, content, technical,
  style-transfer, extreme-detail) and free-text intent descriptions.
  Dùng khi user nhắc: "phân tích ảnh", "analyze this image", "check ảnh",
  "kiểm tra ảnh", "classify this image", "đánh giá ảnh", "image analysis",
  "vision check", "analyze with [preset]", "mô tả ảnh chi tiết",
  "trích xuất style", "kiểm tra an toàn ảnh", hoặc mô tả tự do
  như "analyze cho mood và color grading", "extract visual style",
  "describe chi tiết ảnh này để recreate".
  KHÔNG dùng cho: tạo/chỉnh sửa ảnh, nén ảnh, thiết kế banner,
  hoặc bất kỳ tác vụ nào không phải phân tích/đánh giá ảnh.
---

# Goal

Phân tích ảnh generic bằng Grok Vision — không hardcode criteria cụ thể.
Criteria được định nghĩa trong `criteria/*.md` như presets, user chọn
preset nào thì inject preset đó vào prompt.

# Architecture

```
image-analyzer/
├── SKILL.md                    ← Core skill (this file)
└── criteria/                   ← Presets — user chọn để inject
    ├── safety.md               ← Safety/NSFW classification preset
    ├── artistic.md             ← Artistic quality evaluation preset
    ├── content.md              ← Content & subject analysis preset
    └── technical.md            ← Technical quality preset
```

**Muốn thêm preset mới?** Tạo `criteria/{name}.md` — skill sẽ tự nhận diện.

---

# Instructions

## Phase 1 — Validate Image Source

- **URL detected** → validate format (`http://` or `https://`) → use directly
- **Local path detected** → verify file exists → validate extension (`.jpg`, `.jpeg`, `.png`) → validate size (≤20MB) → encode as base64
- **Validation fails** → raise `ValueError` with specific message

## Phase 2 — Load Criteria Presets

- **User specifies preset** → read only that preset from `criteria/{name}.md`
- **User specifies multiple presets** → read all from `criteria/{name}.md`
- **User specifies "all"** → read all `.md` files in `criteria/`
- **User provides free-text intent** (`--intent "analyze for title and caption"`) → send user's exact text directly to Grok Vision — no preset mapping, no prompt optimization
- **User specifies nothing** → list available presets → ask user to select
- **Preset file not found** → raise `FileNotFoundError` listing available presets
- **Empty criteria result** → raise `ValueError("No criteria loaded")`

## Phase 3 — Call Grok Vision API

For **free-intent mode** (`--intent` flag):
1. Take user's exact free-text string
2. Send directly to Grok Vision as `input_text` — no preset loading, no prompt modification
3. Return raw response under `{"free": {"raw, prompt}}` key

For **each** selected preset (sequential):
1. Extract prompt template between ` ``` ` markers in preset file
2. Extract output field schema from `## Output Fields` table
3. Build request: `input_image` (base64/URL) + `input_text` (prompt)
4. Send `POST https://api.x.ai/v1/responses` with `model=grok-4.20-reasoning`, `store=False`
5. **On HTTP error** → raise with status code and message
6. **On API timeout** → raise `TimeoutError`
7. **On empty response** → raise `ValueError("Empty response from API")`
8. **On response parse failure** → log raw response → raise `ValueError("Failed to parse response")`

For **combined mode** (`--combined` flag):
1. Load all presets → deduplicate shared topics → merge into single prompt
2. Send ONE API call with merged prompt
3. Split response by `=== {PRESET} ===` headers
4. **On split failure** → assign full response to first preset → log warning

## Phase 4 — Format and Return Results

- Parse response text using preset's output field schema
- **Single preset** → return full raw response
- **Multiple presets** → return keyed dict `{preset_name: {raw, prompt}}`
- **On parse error** → return raw response with warning note

---

# Usage Examples

## Example 1: Single Preset — Artistic Analysis

**Input:**
```
User: "phân tích ảnh này với artistic: /photo.jpg"
```

**Output:**
```
## ARTISTIC
✅ PASS — 9/10
- Rembrandt lighting with soft fill
- Warm amber tones, teal shadows
- Intimate, elegant mood
```

**Logic:** `load_criteria(["artistic"])` → call API → format result

---

## Example 2: Multiple Presets — Safety + Artistic

**Input:**
```
User: "check safety + artistic cho ảnh này: https://example.com/photo.jpg"
```

**Output:**
```
## SAFETY
✅ PASS — No NSFW detected

## ARTISTIC
✅ PASS — 8.5/10
- Cinematic color grading
- Strong compositional depth
```

**Logic:** `load_criteria(["safety", "artistic"])` → sequential API calls → merge results

---

## Example 3: Combined Mode — Single API Call

**Input:**
```
User: "phân tích ảnh: /photo.jpg" with --combined flag
```

**Output:**
```
## SAFETY
✅ PASS

## ARTISTIC
✅ PASS — 8.5/10

## TECHNICAL
✅ PASS — 9/10
```

**Logic:** `analyze_combined()` → merges prompts → single API call → splits by headers

---

## Example 4: Free-Text Intent — No Preset Mapping

**Input:**
```
User: --intent "Want to write a Title and caption for this image" /photo.jpg
```

**Output:**
```
## FREE
✅ Recommended Title & Caption:
**Title:** Silk & Ink
**Caption:** A striking portrait of quiet strength and cultural contrast...
```

**Logic:** `analyze_free()` → sends user's exact text directly to Grok Vision → returns raw response under `{"free": {raw, prompt}}`

---

## Example 5: User Asks Without Specifying Preset

**Input:**
```
User: "phân tích ảnh: /photo.jpg"
```

**Output:**
```
Available presets:
  • safety    — NSFW/content classification
  • artistic  — Emotional tone & aesthetic score
  • content   — Subject, scene, objects
  • technical — Lighting, composition, camera
  • style-transfer — Visual DNA for style transfer
  • extreme-detail — Hyper-detailed YAML for reproduction

Bạn muốn dùng preset nào? (or "all")
```

**Logic:** No preset specified → `load_criteria()` → list available → ask user

---

# API Call Format

```python
import os
import httpx

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0),
)

response = client.responses.create(
    model="grok-4.20-reasoning",
    input=[
        {
            role: "user",
            content: [
                {"type": "input_image", "image_url": "<URL hoặc base64>", "detail": "high"},
                {"type": "input_text", "text": "<Prompt từ preset>"},
            ],
        }
    ],
)
```

---

# Constraints

- 🚫 KHÔNG ĐƯỢC: Hardcode criteria cụ thể trong SKILL.md
- 🚫 KHÔNG ĐƯỢC: Hardcode API key — dùng `$XAI_API_KEY` env var
- 🚫 KHÔNG ĐƯỢC: Lưu ảnh vào log — bảo mật content
- ✅ LUÔN LUÔN: Đọc criteria từ `criteria/{name}.md` trước khi phân tích
- ✅ LUÔN LUÔN: Dùng output format từ preset cho response
- ⚠️ CHÚ Ý: Verify URL hợp lệ trước khi gọi API
- ⚠️ CHÚ Ý: Ảnh tối đa 20MB, định dạng jpg/jpeg/png

<!-- Generated by Skill Creator Ultra v1.0 -->
