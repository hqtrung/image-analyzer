# image-analyzer

Claude Code skill for analyzing images using xAI Grok Vision.

## Features

- **6 analysis presets**: `safety`, `artistic`, `content`, `technical`, `style-transfer`, `extreme-detail`
- **Free-text intent**: pass any question directly to Grok Vision — no preset mapping
- **Combined mode**: merge multiple presets into one API call with prompt deduplication
- **Dry-run**: preview prompts without making API calls

## Usage

```bash
# Free-text intent (direct pass-through to Grok Vision)
python scripts/analyze.py photo.jpg --intent "Write a title and caption"

# Single preset
python scripts/analyze.py photo.jpg artistic

# Multiple presets
python scripts/analyze.py photo.jpg safety artistic style-transfer

# Combined mode (1 API call for multiple presets)
python scripts/analyze.py photo.jpg safety artistic --combined

# Dry-run (preview prompts only)
python scripts/analyze.py photo.jpg artistic --dry-run

# JSON output
python scripts/analyze.py photo.jpg artistic --format json
```

## Presets

| Preset | What it does |
|--------|-------------|
| `safety` | NSFW/content classification |
| `artistic` | Emotional tone & aesthetic scoring |
| `content` | Subject, scene, objects |
| `technical` | Lighting, composition, camera |
| `style-transfer` | Visual style DNA for style transfer |
| `extreme-detail` | Hyper-detailed YAML for image recreation |

## Setup

```bash
# Install dependencies
pip install httpx openai

# Set API key
export XAI_API_KEY=your_key_here
```

Or copy `.env.example` to `.env` and add your key.

## Architecture

```
image-analyzer/
├── SKILL.md              ← Skill definition
├── criteria/              ← Preset prompts
│   ├── safety.md
│   ├── artistic.md
│   ├── content.md
│   ├── technical.md
│   ├── style-transfer.md
│   └── extreme-detail.md
└── scripts/
    └── analyze.py         ← Main CLI script
```

Add new presets by creating `criteria/{name}.md` — the skill auto-detects them.

## License

MIT
