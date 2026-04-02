# Technical Criteria Preset

**ID:** technical
**Name:** Technical Quality Evaluation
**Mục đích:** Đánh giá chất lượng kỹ thuật — lighting, composition, camera, post-processing

## Prompt Template

```
Analyze the technical quality of this image:

1. LIGHTING
   - Key light: directional, soft, harsh, natural, artificial?
   - Quality: balanced, high contrast, flat?
   - Shadows: defined, muddy, dramatic?
   - Color temperature: warm, cool, neutral?

2. COMPOSITION
   - Rule of thirds applied?
   - Balance: symmetric, asymmetric, weighted?
   - Framing: tight, loose, dynamic crop?
   - Negative space: used well?

3. CAMERA/LENS
   - Perspective: normal, wide-angle, compressed telephoto?
   - Depth of field: shallow (bokeh), deep (everything sharp)?
   - Distortion: none, barrel, pincushion?

4. FOCUS
   - Focus point: clear and deliberate?
   - Sharpness: appropriately sharp or soft?
   - Subject isolation or full scene focus?

5. COLOR/TONE
   - Color harmony: cohesive, clashing, monochromatic?
   - Tonality: high key, low key, natural, stylized?
   - White balance: accurate or intentionally shifted?

6. POST-PROCESSING
   - Style: clean, gritty, cinematic, vintage, processed?
   - Film qualities: grain, bloom, vignette, halo?
   - Over/under-processed?

7. TECHNICAL OVERALL
   - Professional execution?
   - Any distracting technical flaws?

Respond in this format:
RESULT: [PASS/WARN/FAIL]
TECHNICAL_STRENGTHS: [What works technically]
TECHNICAL_ISSUES: [Problems found, if any]
SUGGESTIONS: [How to improve technically]
TECHNICAL_SCORE: [1-10]
```

## Output Fields

| Field | Type | Mô tả |
|-------|------|--------|
| RESULT | PASS / WARN / FAIL | Classification |
| TECHNICAL_STRENGTHS | string[] | Điểm mạnh kỹ thuật |
| TECHNICAL_ISSUES | string[] | Vấn đề kỹ thuật |
| SUGGESTIONS | string | Cách cải thiện |
| TECHNICAL_SCORE | number | 1-10 |
