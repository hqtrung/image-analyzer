#!/usr/bin/env python3
"""
Image Analyzer — Grok Vision API caller

Usage:
    python analyze.py <image_path_or_url> [criteria_names...]
    python analyze.py https://example.com/photo.jpg safety artistic
    python analyze.py /path/to/photo.jpg all
    python analyze.py /path/to/photo.jpg all --combined  # single merged request

Environment:
    XAI_API_KEY — API key for x.ai (or set in .env file)
"""

import os
import sys
import base64
import json
import re
import argparse
from pathlib import Path
from typing import Optional, Dict, List

# Load .env if exists
SKILL_DIR = Path(__file__).parent.parent  # image-analyzer/
PROJECT_ROOT = SKILL_DIR.parent.parent.parent  # project root
_env_path = PROJECT_ROOT / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

try:
    import httpx
    from openai import OpenAI
except ImportError:
    print("Installing dependencies...")
    os.system("pip install httpx openai")
    import httpx
    from openai import OpenAI

# === Config ===
SKILL_DIR = Path(__file__).parent.parent
CRITERIA_DIR = SKILL_DIR / "criteria"
MODEL = "grok-4.20-reasoning"
ENDPOINT = "https://api.x.ai/v1/responses"


# Keyword → preset mapping for free-text intent
PRESET_KEYWORDS = {
    "safety":       ["safe", "nsfw", "content safety", "allowed", "appropriate", "kiểm tra an toàn", "an toàn", "censorship", "block"],
    "artistic":     ["artistic", "mood", "emotion", "feeling", "style", "aesthetic", "beauty", "beautiful", "đẹp", "nghệ thuật", "cảm xúc", "title", "caption", "viết title", "viết caption", "heading", "mô tả"],
    "content":      ["subject", "scene", "object", "background", "foreground", "who", "what", "where", "nội dung", "chủ thể", "mô tả"],
    "technical":    ["technical", "lighting", "exposure", "composition", "focus", "sharpness", "camera", "lens", "kỹ thuật", "ánh sáng", "cân bằng trắng"],
    "style-transfer": ["style", "transfer", "color grade", "grading", "palette", "film", "vintage", "cinematic look", "visual style", "áp dụng style"],
    "extreme-detail": ["detail", "reproduce", "recreate", "generate", "prompt", "chi tiết", "tái tạo", "mô tả chi tiết", "yaml"],
}


def match_free_text_to_presets(text: str) -> List[str]:
    """Match free-text user request to preset names. Returns list of matched presets."""
    text_lower = text.lower()
    matched = []
    for preset, keywords in PRESET_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            matched.append(preset)
    return matched if matched else ["artistic"]  # default to artistic if unclear


def load_criteria(names: Optional[List[str]] = None) -> Dict[str, dict]:
    """Load criteria presets from criteria/ folder."""
    criteria = {}

    if names and "all" in names:
        names = None

    for file in CRITERIA_DIR.glob("*.md"):
        name = file.stem
        if names and name not in names:
            continue

        content = file.read_text()

        # Extract prompt between Prompt Template markers
        prompt_start = content.find("```\n") + 5
        prompt_end = content.rfind("```")
        prompt = content[prompt_start:prompt_end].strip() if prompt_start > 4 else ""

        # Extract output fields
        output_fields = {}
        if "## Output Fields" in content:
            fields_section = content.split("## Output Fields")[1].split("##")[0]
            for line in fields_section.strip().split("\n"):
                if line.startswith("|") and not line.startswith("|---|"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 2:
                        output_fields[parts[0]] = parts[1]

        criteria[name] = {
            "prompt": prompt,
            "output_fields": output_fields,
        }

    return criteria


def load_image(source: str) -> str:
    """Load image as base64 or return URL."""
    if source.startswith("http://") or source.startswith("https://"):
        return source

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")

    # Check size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 20:
        raise ValueError(f"Image too large: {size_mb:.1f}MB (max 20MB)")

    # Check extension
    if path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        raise ValueError(f"Unsupported format: {path.suffix} (use jpg/png)")

    with open(path, "rb") as f:
        return f"data:image/{path.suffix.lstrip('.').lower()};base64,{base64.b64encode(f.read()).decode()}"


# === Prompt Optimizer Layer ===

# Topics that overlap across criteria — will be merged into shared sections
SHARED_TOPICS = {
    "color", "colour", "saturation", "tone", "tonality", "white balance",
    "lighting", "light", "exposure", "contrast", "dynamic range",
    "shadow", "highlight", "grain", "texture", "sharpness", "detail",
    "composition", "framing", "rule of thirds", "subject", "background",
    "mood", "atmosphere", "emotion", "feeling", "vibe", "energy",
    "skin", "retouch", "bokeh", "depth of field", "focus",
}


def normalize(text: str) -> str:
    """Lowercase + collapse whitespace for comparison."""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_topics(prompt: str) -> set:
    """Extract topic keywords from a prompt."""
    words = re.findall(r"\b[a-z]{4,}\b", normalize(prompt))
    return set(w for w in words if w in SHARED_TOPICS)


def merge_overlapping_lines(lines: List[str]) -> List[str]:
    """Deduplicate near-identical lines across prompts."""
    seen = set()
    merged = []
    for line in lines:
        norm = normalize(line)
        if len(norm) < 10 or norm in seen:
            continue
        # Skip if similar line already exists
        is_dup = any(normalize(n) in norm or norm in normalize(n) for n in seen)
        if is_dup:
            continue
        seen.add(norm)
        merged.append(line)
    return merged


def optimize_prompts(criteria: Dict[str, dict]) -> tuple:
    """
    Merge multiple criteria prompts into one optimized prompt.
    Returns (combined_prompt, criteria_names_list).
    """
    prompts = list(criteria.items())
    if len(prompts) == 1:
        return prompts[0][1]["prompt"], list(criteria.keys())

    sections = []
    shared_lines: List[str] = []
    seen_topics = set()

    for name, spec in prompts:
        lines = spec["prompt"].strip().split("\n")
        # Collect lines for this criteria's unique sections
        unique_lines = []
        for line in lines:
            line_norm = normalize(line)
            topics = set(w for w in re.findall(r"\b[a-z]{4,}\b", line_norm) if w in SHARED_TOPICS)
            # If line shares topics already covered, skip it (will use shared)
            if topics and topics.issubset(seen_topics):
                continue
            unique_lines.append(line)
            seen_topics.update(topics)

        if unique_lines:
            sections.append(f"=== {name.upper()} ===\n" + "\n".join(unique_lines))

    # Build combined prompt
    header = (
        "Analyze this image with multiple criteria. "
        "For each section below, provide a thorough analysis.\n\n"
    )

    # Add shared topics preamble (deduplicated common questions)
    shared_preamble = (
        "SHARED ANALYSIS (applies to all sections):\n"
        "- Color palette: dominant colors with emotional context\n"
        "- Lighting: quality, direction, contrast\n"
        "- Mood/Atmosphere: emotional tone and energy\n"
        "- Technical: sharpness, noise/grain, dynamic range\n"
    )

    combined = header + shared_preamble + "\n" + "\n\n".join(sections) + "\n\nRespond with each section clearly labeled under its header."

    return combined, list(criteria.keys())


def split_combined_response(response: str, criteria_names: List[str]) -> Dict[str, str]:
    """Split a combined response by criteria headers."""
    results = {}
    # Build pattern to match any of the criteria headers
    pattern = "|".join(re.escape(f"=== {n.upper()} ===") for n in criteria_names)
    parts = re.split(f"({pattern})", response)

    # parts will be: [preamble, header1, content1, header2, content2, ...]
    if len(parts) < 3:
        # No clear splits — treat entire response as one result for first criteria
        results[criteria_names[0]] = response.strip()
        return results

    current_name = None
    current_content = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        matched = re.match(r"=== (\w+) ===", part)
        if matched:
            # Save previous
            if current_name:
                results[current_name] = "\n".join(current_content).strip()
            current_name = matched.group(1).lower()
            current_content = []
        elif current_name:
            current_content.append(part)

    # Save last
    if current_name and current_content:
        results[current_name] = "\n".join(current_content).strip()

    # Fallback: if we couldn't split well, assign entire response to first criteria
    if not results and criteria_names:
        results[criteria_names[0]] = response.strip()

    return results


def analyze_combined(image_source: str, criteria_names: Optional[List[str]] = None) -> dict:
    """Call Grok Vision API with all criteria merged into one prompt."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable not set")

    criteria = load_criteria(criteria_names)
    if not criteria:
        raise ValueError(f"No criteria found. Available: {[f.stem for f in CRITERIA_DIR.glob('*.md')]}")

    print(f"  → Optimizing {len(criteria)} criteria prompts...", file=sys.stderr)
    combined_prompt, criteria_list = optimize_prompts(criteria)

    image_url = load_image(image_source)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
        timeout=httpx.Timeout(3600.0),
    )

    print(f"  → Analyzing {', '.join(criteria_list)} in single request...", file=sys.stderr)

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": image_url, "detail": "high"},
                    {"type": "input_text", "text": combined_prompt},
                ],
            }
        ],
        store=False,
    )

    # Parse response
    text = ""
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "content"):
                for content_item in item.content:
                    if hasattr(content_item, "text"):
                        text = content_item.text
                        break
    elif hasattr(response, "choices") and response.choices:
        text = response.choices[0].message.content or ""

    # Split into per-criteria results
    split_results = split_combined_response(text, criteria_list)

    results = {}
    for name in criteria_list:
        results[name] = {
            "raw": split_results.get(name, text),  # fallback to full text
            "prompt": criteria[name]["prompt"],
        }

    return results


def analyze_free(image_source: str, free_prompt: str) -> dict:
    """Call Grok Vision API with user's free-text prompt directly — no preset mapping."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable not set")

    image_url = load_image(image_source)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
        timeout=httpx.Timeout(3600.0),
    )

    print(f"  → Analyzing with free intent...", file=sys.stderr)

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": image_url, "detail": "high"},
                    {"type": "input_text", "text": free_prompt},
                ],
            }
        ],
        store=False,
    )

    text = ""
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "content"):
                for content_item in item.content:
                    if hasattr(content_item, "text"):
                        text = content_item.text
                        break
    elif hasattr(response, "choices") and response.choices:
        text = response.choices[0].message.content or ""

    return {"free": {"raw": text, "prompt": free_prompt}}


def analyze(image_source: str, criteria_names: Optional[List[str]] = None) -> dict:
    """Call Grok Vision API with specified criteria."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable not set")

    criteria = load_criteria(criteria_names)
    if not criteria:
        raise ValueError(f"No criteria found. Available: {[f.stem for f in CRITERIA_DIR.glob('*.md')]}")

    results = {}

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
        timeout=httpx.Timeout(3600.0),
    )

    for name, spec in criteria.items():
        print(f"  → Analyzing: {name}...", file=sys.stderr)

        image_url = load_image(image_source)

        response = client.responses.create(
            model=MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_image", "image_url": image_url, "detail": "high"},
                        {"type": "input_text", "text": spec["prompt"]},
                    ],
                }
            ],
            store=False,
        )

        # Parse response — handle both output formats
        text = ""
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if hasattr(item, "content"):
                    for content_item in item.content:
                        if hasattr(content_item, "text"):
                            text = content_item.text
                            break
        elif hasattr(response, "choices") and response.choices:
            text = response.choices[0].message.content or ""

        results[name] = {
            "raw": text,
            "prompt": spec["prompt"],
        }

    return results


def format_results(image_source: str, results: dict) -> str:
    """Format results as markdown report."""
    lines = [
        "# 📊 IMAGE ANALYSIS REPORT",
        "=" * 40,
        f"**Image:** {image_source}",
        f"**Model:** {MODEL}",
        f"**Criteria:** {', '.join(results.keys())}",
        "",
        "---",
        "",
    ]

    for name, data in results.items():
        lines.append(f"## {name.upper()}")
        lines.append("")
        lines.append("```")
        lines.append(data["raw"])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze image with Grok Vision")
    parser.add_argument("image", help="Image URL or local file path")
    parser.add_argument("criteria", nargs="*", default=["all"], help="Criteria presets (safety, artistic, content, technical, style-transfer, extreme-detail)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--combined", action="store_true", help="Merge all criteria into a single prompt (1 API call)")
    parser.add_argument("--dry-run", action="store_true", help="Show prompt and criteria without calling API")
    parser.add_argument("--intent", type=str, default=None, help="Free-text intent description (e.g., 'analyze for mood and color grading')")
    args = parser.parse_args()

    # If --intent is provided, send free-text directly to Grok Vision (no preset mapping)
    if args.intent:
        results = analyze_free(args.image, args.intent)
        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            print(format_results(args.image, results))
        return

    print(f"Loading criteria: {args.criteria}", file=sys.stderr)
    criteria = load_criteria(args.criteria)

    if not criteria:
        print(f"No criteria found. Available: {[f.stem for f in CRITERIA_DIR.glob('*.md')]}", file=sys.stderr)
        return

    # Dry-run: show what would be sent without calling API
    if args.dry_run:
        print("\n=== DRY RUN — No API call made ===", file=sys.stderr)
        for name, spec in criteria.items():
            print(f"\n--- {name.upper()} ---", file=sys.stderr)
            print(f"Prompt ({len(spec['prompt'])} chars):", file=sys.stderr)
            print(spec["prompt"][:500] + "..." if len(spec["prompt"]) > 500 else spec["prompt"], file=sys.stderr)
            print(f"Output fields: {list(spec['output_fields'].keys())}", file=sys.stderr)
        return

    if args.combined:
        results = analyze_combined(args.image, criteria_names=list(criteria.keys()))
    else:
        results = analyze(args.image, criteria_names=list(criteria.keys()))

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_results(args.image, results))


if __name__ == "__main__":
    main()
