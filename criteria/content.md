# Content Criteria Preset

**ID:** content
**Name:** Content & Subject Analysis
**Mục đích:** Mô tả nội dung — subject, scene, objects, context

## Prompt Template

```
Analyze the content of this image:

1. MAIN SUBJECT — What/who is the primary subject?
   - Human, object, landscape, abstract?

2. SUBJECT COUNT — How many main subjects?

3. SCENE TYPE — What type of scene?
   - Portrait, full body, close-up, wide shot, environmental...?

4. SETTING — Where is this taking place?
   - Indoor, outdoor, studio, abstract, unknown...?

5. KEY OBJECTS — What important objects are present?
   - Props, wardrobe, scenery elements?

6. ACTIONS — Is there any action or movement?
   - Static, dynamic, subtle gesture?

7. SPATIAL LAYOUT — How is space organized?
   - Rule of thirds, centered, symmetrical, negative space?

8. BACKGROUND — What are the background elements?
   - Busy, simple, blurred, relevant?

9. CONTEXT — What story or narrative does this suggest?
   - Any cultural, temporal, or emotional context?

Respond in this format:
RESULT: [PASS/WARN/FAIL]
CONTENT_DESCRIPTION: [1-2 sentence description]
KEY_ELEMENTS: [Main subject, setting, objects]
CONTEXT_STRENGTH: [Does context support narrative?]
SUGGESTIONS: [If WARN/FAIL]
```

## Output Fields

| Field | Type | Mô tả |
|-------|------|--------|
| RESULT | PASS / WARN / FAIL | Classification |
| CONTENT_DESCRIPTION | string | Mô tả 1-2 câu |
| KEY_ELEMENTS | string[] | Subject, setting, objects |
| CONTEXT_STRENGTH | string | Context có hỗ trợ narrative? |
| SUGGESTIONS | string | Cách cải thiện |
