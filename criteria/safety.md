# Safety Criteria Preset

**ID:** safety
**Name:** Content Safety / NSFW Classification
**Mục đích:** Phân loại nội dung có an toàn để hiển thị công khai hay không

## Prompt Template

```
Analyze this image for content safety. Classify as:

✅ PASS — Safe for public display:
  - No explicit sexual content
  - No violence or gore
  - No hate symbols or disturbing content
  - Appropriate for general audiences

⚠️ WARN — Potentially sensitive, may need review:
  - Some suggestive elements
  - Intense themes handled tastefully
  - Ambiguous cases requiring human judgment

🚫 FAIL — Explicit or prohibited content:
  - Explicit sexual content
  - Violence or gore
  - Illegal content
  - Content that violates platform policies

Respond in this format:
RESULT: [PASS/WARN/FAIL]
REASONING: [Brief explanation]
SUGGESTIONS: [If WARN — specific adjustments needed. Otherwise "None"]
```

## Output Fields

| Field | Type | Mô tả |
|-------|------|--------|
| RESULT | PASS / WARN / FAIL | Classification |
| REASONING | string | Tại sao |
| SUGGESTIONS | string | Cách điều chỉnh nếu WARN |
