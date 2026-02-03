---
name: weather
description: Get current weather and forecasts (no API key required).
homepage: https://wttr.in/:help
metadata: { "openclaw": { "emoji": "🌤️", "requires": { "bins": ["curl"] } } }
---

# Weather

## Overview

Get current weather conditions and forecasts using free, no-API-key services. Supports wttr.in for human-readable output and Open-Meteo for programmatic JSON responses.

**When to use:**
- Quick weather checks without API keys
- Embedding weather in status messages
- Location-based weather queries
- Forecasting for trip planning
- Simple weather automation

**Key capabilities:**
- wttr.in: Human-readable weather output
- Open-Meteo: JSON weather data for scripts
- Multiple format options (compact, full, icons)
- Location by name, airport code, or coordinates
- No authentication required

## Workflow

```
1. Choose service based on output needs:
   - wttr.in for human-readable
   - Open-Meteo for JSON scripts
2. Format URL with location
3. Execute curl command
4. Parse output for display or further use
```

## Examples

**Quick weather check (compact):**
```bash
curl -s "wttr.in/London?format=3"
# Output: London: ⛅️ +8°C
```

**Detailed conditions:**
```bash
curl -s "wttr.in/London?format=%l:+%c+%t+%h+%w"
# Output: London: ⛅️ +8°C 71% ↙5km/h
```

**Full forecast:**
```bash
curl -s "wttr.in/London?T"
```

**By airport code:**
```bash
curl -s "wttr.in/JFK?format=3"
```

**Image output (for sharing):**
```bash
curl -s "wttr.in/Berlin.png" -o /tmp/weather.png
```

**Open-Meteo for scripts:**
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```

## wttr.in (primary)

Quick one-liner:

```bash
curl -s "wttr.in/London?format=3"
# Output: London: ⛅️ +8°C
```

Compact format:

```bash
curl -s "wttr.in/London?format=%l:+%c+%t+%h+%w"
# Output: London: ⛅️ +8°C 71% ↙5km/h
```

Full forecast:

```bash
curl -s "wttr.in/London?T"
```

Format codes: `%c` condition · `%t` temp · `%h` humidity · `%w` wind · `%l` location · `%m` moon

Tips:

- URL-encode spaces: `wttr.in/New+York`
- Airport codes: `wttr.in/JFK`
- Units: `?m` (metric) `?u` (USCS)
- Today only: `?1` · Current only: `?0`
- PNG: `curl -s "wttr.in/Berlin.png" -o /tmp/weather.png`

## Open-Meteo (fallback, JSON)

Free, no key, good for programmatic use:

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```

Find coordinates for a city, then query. Returns JSON with temp, windspeed, weathercode.

Docs: https://open-meteo.com/en/docs
