# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 🔧 Actual Configuration

### Cameras (camsnap)

| Name | Host | Location | Notes |
|------|------|----------|-------|
| living-room | 192.168.1.100 | Main area | 180° wide angle |
| front-door | 192.168.1.101 | Entrance | Motion-triggered |

### SSH

| Alias | Host | User | Notes |
|-------|------|------|-------|
| home-server | 192.168.1.100 | admin | Main home server |
| wner-pc | 192.168.1.50 | wner | Primary workstation |

### TTS (sag / ElevenLabs)

| Setting | Value |
|---------|-------|
| Preferred voice | Nova |
| Voice style | Warm, slightly British |
| Default speaker | Kitchen HomePod |
| Stability | 0.5 |
| Similarity boost | 0.75 |

### Speakers / Rooms

| Room | Device | Control |
|------|--------|---------|
| Kitchen | HomePod | BluOS / AirPlay |
| Living Room | Sonos | BluOS CLI |
| Office | Built-in | System output |

### Web Browsers

| Profile | Purpose |
|---------|---------|
| clawd | Isolated automation |
| chrome | Extension relay (Moltbot) |

### Gateway

| Setting | Value |
|---------|-------|
| Port | 18789 |
| Status | Running |
| Uptime | ~3 days |
| URL | https://dessie-unexonerated-supercolossally.ngrok-free.dev/webapp |

### Node Configuration

| Node | Status | Notes |
|------|--------|-------|
| CND3452425 | Active | Current host |
| v24.13.0 | Via NVM | Should use system 22+ |

### Cron Jobs Active

| Job | Schedule | Status |
|-----|----------|--------|
| Price check | */15 min | ✅ |
| Health check | */5 min | ✅ |
| Queue cleanup | 0 */6h | ✅ |
| Auto post | 0 9,13,18,22 | ✅ |
| Research digest | 0 8,20 | ✅ |

### Skills Directory

| Path | Skills | Avg Score |
|------|--------|-----------|
| /home/wner/clawd/skills/ | 16 | 66/100 |
| /home/wner/moltbot/skills/ | 54 | 25/100 |

### Model Configuration

| Tier | Model | Score Range |
|------|-------|-------------|
| Fast | MiniMax-M2.1-Fast | 1-29 |
| Standard | MiniMax-M2.1 | 30-70 |
| Deep | MiniMax-M2.1-Deep | 71-100 |

### X/Twitter (bird)

| Account | Persona | Cookie Source |
|---------|---------|---------------|
| @Groove_Armada | SefirotWatch | AUTH_TOKEN, CT0 env vars |

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| AUTH_TOKEN | *** | Twitter auth |
| CT0 | *** | Twitter CT0 |
| HOME | /home/wner | User home |
| NVM_DIR | ~/.nvm | Node version manager |

### File Paths

| Path | Purpose |
|------|---------|
| ~/clawd/ | Workspace root |
| ~/clawd/skills/ | Custom skills |
| ~/clawd/memory/ | Daily notes |
| ~/clawd/post_queue/ | Post queue |
| ~/.clawdbot/ | Clawdbot config |
| ~/.config/camsnap/ | Camera config |
