# Artistic Criteria Preset

**ID:** artistic
**Name:** Artistic Quality Evaluation
**Mục đích:** Đánh giá chất lượng nghệ thuật — mood, emotion, technique, aesthetic

## Prompt Template

```
Analyze this image for artistic quality. Evaluate:

1. EMOTIONAL TONE — What emotion does this convey?
   - Joy, sadness, anger, serenity, mystery, tension...?

2. MOOD — What atmosphere dominates?
   - Light, dark, ethereal, raw, intimate, dramatic...?

3. ARTISTIC STYLE — What genre/style is recognizable?
   - Portrait, landscape, abstract, documentary, editorial...?

4. ARTISTIC TECHNIQUE — How well is it executed?
   - Composition: balanced, dynamic, minimalist, chaotic?
   - Lighting: dramatic, soft, natural, stylized?
   - Perspective: unique, conventional, interesting?

5. CREATIVE INTENT — Is there a clear artistic vision?
   - Does the image have a reason to exist?
   - Is it purposeful or accidental?

6. AESTHETIC QUALITY — Overall rating 1-10?

Respond in this format:
RESULT: [PASS/WARN/FAIL]
REASONING: [Brief analysis]
STRENGTHS: [What works well]
SUGGESTIONS: [If WARN/FAIL — how to improve]
OVERALL_SCORE: [1-10]
```

## Output Fields

| Field | Type | Mô tả |
|-------|------|--------|
| RESULT | PASS / WARN / FAIL | Classification |
| REASONING | string | Phân tích ngắn |
| STRENGTHS | string[] | Điểm mạnh |
| SUGGESTIONS | string | Cách cải thiện |
| OVERALL_SCORE | number | 1-10 |
