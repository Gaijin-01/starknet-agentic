---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image (Nano Banana Pro).
homepage: https://ai.google.dev/
metadata:
  {
    "openclaw":
      {
        "emoji": "🍌",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Nano Banana Pro (Gemini 3 Pro Image)

## Overview

Generate images from text prompts or edit existing images using Gemini 3 Pro Image model. Creates high-quality images with AI, supports image editing and composition.

**When to use:**
- Generating images from text descriptions
- Editing existing images with AI
- Combining multiple images into one scene
- Creating assets for projects
- Quick image generation without external tools

**Key capabilities:**
- Text-to-image generation
- Image editing with prompts
- Multi-image composition (up to 14 images)
- Multiple resolution options (1K, 2K, 4K)
- Automatic MEDIA path output for Moltbot

## Workflow

```
1. Set GEMINI_API_KEY environment variable
2. Choose operation (generate, edit, compose)
3. Write clear prompt describing desired output
4. Execute generation script
5. Use generated image from saved path
```

## Examples

**Generate an image from prompt:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "a cozy coffee shop interior" --filename "coffee.png" --resolution 1K
```

**Edit an existing image:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "add autumn leaves to the scene" --filename "autumn.png" -i "/path/in.png" --resolution 2K
```

**Compose multiple images into one scene:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "combine these into a panoramic landscape" --filename "panorama.png" -i img1.png -i img2.png -i img3.png
```

**Generate with timestamp in filename:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "cyberpunk city" --filename "$(date +%Y-%m-%d-%H-%M-%S)-cyberpunk.png"
```

**High resolution output:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "detailed fantasy landscape" --filename "landscape.png" --resolution 4K
```

Generate

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png" --resolution 1K
```

Edit (single image)

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "edit instructions" --filename "output.png" -i "/path/in.png" --resolution 2K
```

Multi-image composition (up to 14 images)

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "combine these into one scene" --filename "output.png" -i img1.png -i img2.png -i img3.png
```

API key

- `GEMINI_API_KEY` env var
- Or set `skills."nano-banana-pro".apiKey` / `skills."nano-banana-pro".env.GEMINI_API_KEY` in `~/.openclaw/openclaw.json`

Notes

- Resolutions: `1K` (default), `2K`, `4K`.
- Use timestamps in filenames: `yyyy-mm-dd-hh-mm-ss-name.png`.
- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers.
- Do not read the image back; report the saved path only.
