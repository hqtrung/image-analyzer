# Style Transfer Criteria Preset

**ID:** style-transfer
**Name:** Style Transfer Analysis
**Mục đích:** Decode visual style từ reference image — color, lighting, mood, texture, film emulation — để apply style transfer

## Prompt Template

```
Analyze this reference image and extract its complete visual style DNA for style transfer.

1. STYLE IDENTITY
   - What style name would you give this? (e.g., "Cinematic Teal-Orange", "Kodak Portra 400", "Dark Moody Editorial")
   - Category: film_emulation | cinematic | editorial | vintage | modern | fine_art | street | documentary
   - Era vibe: 1970s warm | 1980s neon | 1990s grunge | 2010s instagram | timeless | futuristic

2. EMOTIONAL ESSENCE
   - Mood: nostalgic | melancholic | joyful | mysterious | intimate | powerful | dreamy | gritty | elegant | raw
   - Atmosphere: warm_inviting | cool_distant | soft_romantic | harsh_dramatic | ethereal | grounded
   - Energy: calm | dynamic | tense | peaceful | chaotic | serene

3. VISUAL FINGERPRINT
   - Overall look: One sentence capturing entire style
   - Color palette: 3-5 dominant colors with emotional context
   - Light character: soft_diffused | hard_directional | golden_hour | overcast | dramatic_contrast | flat_even
   - Shadow behavior: deep_rich | lifted_faded | colored_tinted | transparent | crushed_black
   - Highlight behavior: soft_rolloff | bright_airy | warm_glow | cool_crisp | blown_out | controlled

4. COLOR GRADING
   - Overall saturation: undersaturated | natural | slightly_boosted | vibrant | heavily_saturated
   - Color cast: warm | cool | neutral | teal_shadows_warm_highlights | orange_teal | muted
   - Dynamic range: compressed | natural | expanded | HDR_like

5. LIGHTING & MOOD
   - Quality: soft diffused | hard directional | golden hour | overcast | mixed
   - Direction: front_lit | side_lit | backlit | rim_light | ambient
   - Contrast: low_flat | medium_natural | high_dramatic | extreme_contrasty
   - Shadows: soft_transparent | deep_moody | lifted_faded | colored

6. TEXTURE & FILM
   - Grain: none | subtle_film | heavy_film | digital_noise | clean
   - Sharpness: soft_dreamy | naturally_sharp | crispy_detailed | vintage_soft
   - Skin texture: smooth_porcelain | natural_pores | gritty_textured | softly_retouched
   - Film emulation: Kodak_Portra_400 | Fuji_Pro_400H | Kodak_Ektar | Cinestill_800T | Ilford_HP5 | digital

7. SIGNATURE ELEMENTS (What makes this style recognizable)
   - Top 3 most important style elements in priority order

Respond in structured format with all fields populated.
```

## Output Fields

| Field | Type | Mô tả |
|-------|------|--------|
| style_name | string | Descriptive name for the style |
| category | string | film_emulation/cinematic/editorial/vintage/modern/fine_art/street/documentary |
| mood | string | Primary emotional mood |
| atmosphere | string | warm_inviting/cool_distant/soft_romantic/harsh_dramatic/ethereal/grounded |
| color_palette | string[] | 3-5 dominant colors with context |
| light_character | string | soft_diffused/hard_directional/golden_hour/overcast/dramatic_contrast/flat_even |
| shadow_behavior | string | deep_rich/lifted_faded/colored_tinted/transparent/crushed_black |
| highlight_behavior | string | soft_rolloff/bright_airy/warm_glow/cool_crisp/blown_out/controlled |
| saturation_level | string | undersaturated/natural/slightly_boosted/vibrant/heavily_saturated |
| color_cast | string | warm/cool/neutral/teal_shadows_warm_highlights/orange_teal/muted |
| grain | string | none/subtle_film/heavy_film/digital_noise/clean |
| film_emulation | string | Kodak_Portra_400/Fuji_Pro_400H/Kodak_Ektar/Cinestill_800T/Ilford_HP5/digital |
| signature_elements | string[] | Top 3 most recognizable style elements |
