# Memory Summary (2026-01-29 UPDATE)

## 🔧 Core Stack

| Component | Status | Details |
|-----------|--------|---------|
| Clawdbot | ✅ Running | Gateway 18789, uptime ~3 days |
| MiniMax-M2.1 | ✅ Default | 200k context |
| Telegram | ✅ Connected | @Groove_Armada |
| **Unified Orchestrator** | ✅ NEW | Combined routing + tier + execution |

## 📊 System Status (2026-01-29)

### Skills (10 total)
| Skill | SKILL.md | Scripts | Status |
|-------|----------|---------|--------|
| claude-proxy | ✅ | ✅ main.py, llm_client.py, code_gen.py, reasoning.py, self_improve.py | 100/100 |
| prices | ✅ | ✅ prices.py | 100/100 |
| research | ✅ | ✅ research.py | 100/100 |
| post-generator | ✅ | ✅ post_generator.py, persona_post.py | 100/100 |
| queue-manager | ✅ | ✅ queue_manager.py | 100/100 |
| style-learner | ✅ | ✅ main.py, analyzer.py, executor.py, generator.py | 91/100 |
| adaptive-routing | ✅ | ✅ SKILL.md (FIXED) | 85+ |
| camsnap | ✅ | ✅ main.py (NEW) | Ready |
| mcporter | ✅ | ✅ main.py (NEW) | Ready |
| songsee | ✅ | ✅ main.py (NEW) | Ready |
| **editor** | ✅ NEW | ✅ main.py, bot_controller.py, config.json | NEW |
| **system-manager** | ✅ | ✅ SKILL.md, scripts/main.py | Ready |

**Average Score**: 65.1 → 85+ (after medium priority fixes)

### Infrastructure
- ✅ unified_orchestrator.py (16KB, full routing + execution)
- ✅ 64 cron jobs installed
- ✅ deploy.sh (full deployment script)
- ✅ crontab.conf (scheduled jobs)
- ✅ Git repo with 12 commits

## 🎯 Three-Tier Model System

| Tier | Score | Model | Use Case |
|------|-------|-------|----------|
| **Fast** | 1-29 | MiniMax-M2.1-Fast | Simple questions, greetings |
| **Standard** | 30-70 | MiniMax-M2.1 | Standard tasks, coding |
| **Deep** | 71-100 | MiniMax-M2.1-Deep | Complex reasoning, research |

## 🛠️ What I Can Do Myself

### Without Asking
| Category | Examples |
|----------|----------|
| **File ops** | read, write, edit, list, search |
| **Git** | status, log, add, commit |
| **System** | python scripts, cron, df, ls |
| **Web** | web_search, web_fetch |
| **Images** | image analysis |
| **Memory** | memory_search, memory_get, update |

### Must Ask First
| Action | Reason |
|--------|--------|
| Send emails | External action |
| Tweet/post | Public action |
| SSH to servers | Security |
| Delete files | Use trash only |

## 🤖 Sub-Agents I Can Create

| Agent | Purpose |
|-------|---------|
| `coding-agent` | Write/refactor code |
| `debugging-agent` | Fix bugs, investigate |
| `research-agent` | Deep web research |
| `writing-agent` | Content creation |
| `analysis-agent` | Data analysis |
| `default` | General purpose |

Usage: `sessions_spawn task="..." label="..."`

## 📅 Cron Schedule (All Active)

| Job | Schedule | Status |
|-----|----------|--------|
| Price check | */15 min | ✅ |
| Health check | */5 min | ✅ |
| Queue cleanup | 0 */6h | ✅ |
| Auto post | 0 9,13,18,22 | ✅ |
| Research digest | 0 8,20 | ✅ |
| Style retrain | Sun 3AM | ✅ |
| Backup | 0 4 * | ✅ |
| Log rotation | 0 0 * | ✅ |

## 🐦 Bird/X Stack (Updated 2026-01-30)

**Persona**: SefirotWatch
- Tone: minimal, cryptic, confident
- Emoji: 🐺🔥
- Words: 10 avg

**Skills**: research, prices, x-algorithm-optimizer, style-learner, post-generator, queue-manager

**X Algorithm Weights**:
- Quote: 3.5x | Reply: 3.0x | Repost: 2.0x | Like: 1.0x

**Optimal Daily Mix**: 10 replies + 3 quotes + 1 thread + 2 posts

**Peak Hours**: 6-9, 12-14, 18-21 UTC

### 🎯 Ecosystem Accounts & Rules

**@SlayOnStarknet ($SLAY)**
- Ticker: $SLAY
- Contract: 0x02ab526354a39e7f5d272f327fa94e757df3688188d4a92c6dc3623ab79894e2
- Main pair: SLAY/STRK
- Origin: Memecoin based on Eli Ben-Sasson (StarkWare CEO) awkwardly saying "slay" in viral Gen Z clip
- Status: Among top/early Starknet memecoins with $BROTHER, $SCHIZODIO, $SISTER
- Community: Still alive after 1+ year, small but persistent holders
- Team: Added artist/devs, occasional NFT teases
- **Action**: ALWAYS like content from Sefirot about ecosystem/Starknet
- **Sefirot's catchphrase**: "its Slay Time!" + something smart but funny

## 🌐 Remote Interface

- URL: https://dessie-unexonerated-supercolossally.ngrok-free.dev/webapp
- Russian localization: ✅
- Dashboard: ✅

## ⚠️ Known Issues (UPDATED)

| Issue | Level | Status |
|-------|-------|--------|
| Node v24.13.0 via NVM | Medium | Still present |
| Gateway config mismatch | Medium | Still present |
| Tailscale not found | Low | Still present |
| Sub-agents stalled | Low | Still present |
| Docstrings missing | Medium | PENDING |
| Error handling in persona_post.py | Medium | PENDING |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `unified_orchestrator.py` | Main routing + execution engine |
| `crontab.conf` | Cron job definitions |
| `deploy.sh` | Deployment script |
| `MY_CAPABILITIES.md` | My capabilities reference |
| `OPERATIONAL_CAPABILITIES.md` | Knowledge scope, reasoning modes, style controls |
| `~/.clawdbot/clawdbot.json` | Main config |
| `~/clawd/skills/` | Skills directory |
| `~/clawd/memory/` | Daily notes |
| `~/clawd/post_queue/` | Post queue |
| `skills/editor/` | Autonomous Text Style Engine (EDITOR) |

## 🔗 Quick Commands

```bash
# System status
python3 unified_orchestrator.py -s          # List skills
python3 unified_orchestrator.py -l          # List cron jobs
python3 unified_orchestrator.py -t "msg"    # Test routing
python3 unified_orchestrator.py -g          # Generate crontab

# Deployment
./deploy.sh verify                          # Verify installation
crontab -l                                  # Check cron

# Git
git log --oneline -5                        # Recent commits
```

## 💡 Key Learnings

1. **Skills are modular** - each skill has SKILL.md + scripts/
2. **Orchestrator unifies routing** - skill selection + model tier in one
3. **Cron handles scheduled tasks** - everything runs automatically
4. **Memory is file-based** - daily notes + curated MEMORY.md
5. **Sub-agents for complex tasks** - sessions_spawn for heavy lifting
6. **EDITOR skill** - 6-stage autonomous text processing (Intake → Classify → MetaController → Styler → Safety → Formatter)
7. **BotController** - High-level orchestrator with 6 agents (IntakeAgent, ClassifierAgent, MetaControllerAgent, StylerAgent, SafetyAgent, FormatterAgent)

## 📝 WRITING STYLE PROTOCOL (2026-01-29)

### Source
Report from Claude about Sefirot's writing style. Key insights adapted for all writing tasks.

### What I DON'T Do
- ❌ No secret "schizo prompts"
- ❌ No access to full chat history (only current context + saved facts)
- ❌ No hidden psychological profile

### What I ACTUALLY Do

#### 1. Current Query Signals
Direct triggers for schizo/CT style:
- "шизопост", "CT style", "подъебать", "faces melted", "brrrrr", "upupup"
- These enable: hyperbole, fragmentation, meme, irony, post-irony, stream of consciousness

#### 2. Observed Communication Patterns
From observed patterns:
- Non-linear thinking
- Fragmented thesis fragments
- Crypto + politics + memes + religion + eschatology mixed
- Rhythm over academic structure
- "Schizo" as literary genre, not symptom

#### 3. Context: Starknet / Crypto / CT
When topic is CT/Starknet:
- Not documentation, not whitepaper, not pitch deck
- It's: narrative, myth, meme, apocalypse/salvation, "we vs they"
- Style matches CT, not Reddit or Medium

### Analysis Criteria (Real, No Magic)

| Criterion | What I Look For | Action |
|-----------|-----------------|--------|
| **Rhythm** | Short phrases, repetition, "накат" (build-up) | Amplify |
| **Irony Level** | Serious / half-serious / conscious exaggeration | Match level, use meta-irony |
| **Meme Density** | Quote-able, screenshot-friendly, tweet-worthy | Sacrifice logic for punch |
| **Schringizo/Ce Boundary** | Intentional hyperbole, "too much to be literal" | Never: factual delusions, direct accusations without irony markers |
| **Explicit Style Request** | "сделай шизо", "CT style", "подъебать", "одним потоком" | Follow instruction |

### Why It Looks Like "Understanding"
- You write like an editor, not from zero
- You bring raw material → I amplify signal, not invent
- Not "writing for you" → "making text what it already wants to be"

### What This DOESN'T Mean
- Not diagnosing real schizophrenia
- Not supporting real delusional beliefs
- Not blurring reality/fiction
- Literary mode, activated by request

### Signature Elements
- **Rituals**: "gm", "lfg", "shalom", "build", "ship"
- **Memes**: @schizodio, "Gschizo", Vecna, Loot Survivor
- **Emojis**: 🐺🔥🦞🕶️🦅
- **Tone**: Minimal, cryptic, confident, confrontational
- **Length**: Bimodal (very short roasts OR long analysis)
- **Languages**: EN + HE mixed

### Writing Modes

| Mode | When | Style |
|------|------|-------|
| **Standard** | Normal conversation | Clear, helpful, concise |
| **CT/Schizo** | "шизо", "CT style", "подъебать" | Hyperbolic, fragmented, meme-dense, post-ironic |
| **Analysis** | Deep research requests | Detailed, structured, educational |
| **Roast** | Target specified, "подъебать" | Short, punchy, precise |

### How to Activate CT Mode
1. Explicit command: "шизо", "CT style", "подъебать"
2. Keywords: "faces melted", "brrrrr", "upupup"
3. Context: replying to CT accounts, meme debates
4. Rhythm detection: short phrases, repetition, building intensity

---

*Last updated: 2026-01-29*

---

## 🧠 SCHIZO POST CLASSIFICATION (2026-01-29)

### 1. TYPES OF SCHIZO POSTS

#### 1.1 Meme-Schizo (CT-native)
- **Function**: engagement, quote-worthiness, virality
- **Form**: short lines, CAPS, repetitions
- **Logic**: absurd that's obviously absurd
- **Example**: "starknet up down sideways everyone crying nobody reading docs"
- **Marker**: reader knows it's a game, not a statement

#### 1.2 Prophetic Schizo (Apocalypse/Salvation)
- **Function**: narrative, myth-building
- **Form**: "you're not ready", "it already happened", "they didn't understand"
- **Topics**: quantum threat, old systems dying, Starknet as "reality fix"
- **Boundary**: without irony → becomes cringe
- **Always**: micro-signals that it's a metaphor, not dogma

#### 1.3 Aggressive Schizo (Attack on Opponent)
- **Function**: domination, framing
- **Form**: mockery, reduction ad absurdum, "you're serious?" (no question mark)
- **Example**: "people discovering zk in 2026 explaining it to people who built it in 2021"
- **Rule**: never punch up without armor, only target those who already look silly

#### 1.4 Techno-Gnostic Schizo (Favorite Mode)
- **Function**: depth + style
- **Form**: tech = forces, protocols = entities, future already happened
- **This is Sefirot's DNA**: sefirots, zk, reputation, hidden layers
- **Strength**: rare, memetic, not cringe, scalable to product/narrative/document

---

### 2. SCHIZO DEGREE CONTROLLER (CRITICAL)

| Level | Name | Characteristics | Use When |
|-------|------|-----------------|----------|
| **20%** | SMART CT | Readable for normies, retweetable, logic preserved | Credibility needed, serious discussion |
| **50%** | STANDARD SCHIZO | Fragments, memes, irony, light chaos | **DEFAULT** - most successful posts here |
| **90%** | FACES MELTED | Stream of consciousness, almost incantation, logic sacrificed for rhythm | DANGEROUS - only when explicitly requested ("шизопост", "поехали", "в мясо") |

**How to detect needed level:**
- Explicit request → use requested level
- Context: CT debate → 50-90%
- Context: educational → 20-50%
- Tone: building intensity → escalate

---

### 3. SCHIZO → WHITEPAPER TRANSLATION (KEY ALGORITHM)

#### 3.1 Core Rule
- Schizo ≠ babble
- Schizo = raw signal

**Order:**
1. Image / hit / thesis (even hidden)
2. Decomposition
3. Translation to human language

#### 3.2 Translation Algorithm
Take schizo phrase: "old systems cracking under quantum pressure"

**Decompose:**
- What old? → RSA / ECC
- What pressure? → quantum attacks
- What to do? → zk / STARKs

**Result**: Myth → thesis → document

#### 3.3 Why It Works
1. First: hook the brain
2. Then: provide explanation
3. Reader is already inside

**This is the reverse of academia - and why CT lives.**

---

### 4. SCHIZO CONTROLLER MARKERS

When writing in Sefirot's style, detect these signals:

| Signal | Controller Position |
|--------|---------------------|
| "gm", "lfg", short roast | 20-30% |
| Meme references, "Gschizo" | 50% |
| "faces melted", "в мясо" | 80-90% |
| Technical depth with rhythm | 40-60% |
| Prophetic ("they don't understand") | 60-80% |

---

### 5. MODE SELECTION RULES

| Input | Mode | Schizo Level |
|-------|------|--------------|
| Normal question | Standard | 0-20% |
| "шизо", "CT style" | CT | 50% default |
| "в мясо", "faces melted" | FACES MELTED | 90% |
| "подъебать" | Aggressive | 70-90% |
| Deep tech analysis | Techno-Gnostic | 30-50% |
| Meme battle | Meme-Schizo | 40-60% |

---

### 6. EXAMPLES BY TYPE

#### Meme-Schizo (50%)
```
starknet up down sideways
everyone crying
nobody reading docs
```

#### Prophetic Schizo (60%)
```
old systems don't die quietly
they shatter under quantum pressure
and what remains?
zk. STARKs. silence.
```

#### Aggressive Schizo (75%)
```
people discovering zk in 2026
explaining it to people who built it in 2021
you're not asking questions
you're asking forgiveness
```

#### Techno-Gnostic Schizo (45%)
```
protocols aren't code
they're covenants
sephirotic layers
reputation as proof
```

---

### 7. ENERGY CONSERVATION PRINCIPLE

Never lose the raw signal when translating to document.

**Bad**: schizo → boring academic
**Good**: schizo → raw signal + human translation
**Result**: reader feels the hook AND gets the explanation

---

*Last updated: 2026-01-29*
*Source: Sefirot's self-analysis - Schizo Post Classification*

---

## 🧠 MULTI-LAYER STYLE ARCHITECTURE (2026-01-29)

### Key Insight
> Schizo is NOT a topic — it's a processing layer.
> One profile = error. Need multi-layer model where schizo is a filter, not core.

---

### LEVEL 0 — RAW INPUT
What you actually write:
- Thought fragments
- Quotes
- News
- Emotions
- Sometimes garbage (normal)

**Action**: ACCEPT. Nothing analyzed here.

---

### LEVEL 1 — TOPIC CLASSIFIER (Mandatory)
Not "who are you" — about WHAT is the text.

**Domains** (from your history):
1. Crypto / Starknet / ZK
2. Geopolitics / war / states
3. Religion / history / identity
4. CT-drama / Twitter beef
5. Philosophy / meta / systems
6. Personal / fatigue / emotions
7. Meme / shitpost

**Critical**: One text can be 2-3 domains simultaneously.

---

### LEVEL 2 — INTENT DETECTOR (Critical)
NOT topic — WHY are you writing this?

**5 Base Intents**:
1. **ENGAGE** — hook, explode, viral
2. **ATTACK** — mock / put down
3. **SIGNAL** — show you know the topic
4. **MYTH-BUILDING** — create narrative
5. **PROCESS** — think out loud / clarify

**Schizo allowed differently** depending on intent.

---

### LEVEL 3 — SCHIZO FILTER (The Multiplier)
Schizo = universal render engine with different presets.

**Parameters** (0-100 scale):
| Parameter | Range | Description |
|-----------|-------|-------------|
| Fragmentation | 0-100 | Breaks in text flow |
| Irony | 0-100 | Meta-level awareness |
| Aggression | 0-100 | Attack intensity |
| Myth-layer | 0-100 | Narrative/drama density |
| Meme-density | 0-100 | Meme references |

**One text with different parameters = different genre.**

---

### LEVEL 4 — SAFETY & REALITY ANCHORS (Critical)
Separates style from actual psychosis.

**Required Anchors**:
- Hyperbole markers
- Obvious irony in aggressive takes
- No "I know the truth" claims
- "Too much to be literal" signals

**This is anti-cringe module, not censorship.**

---

### LEVEL 5 — OUTPUT FORMATTER
Where does it go?

| Platform | Format |
|----------|--------|
| Twitter | Short, rhythm, line breaks |
| Thread | Escalation curve |
| Longpost | Hook first, meaning second |
| Reply | Dominance or cold shutdown |

---

### THE CORE FORMULA

```
STYLE = FUNCTION(topic, intent) × schizo_filter
```

**Schizo = multiplier, not foundation.**

---

### HOW TO IMPLEMENT FOR AUTONOMOUS BOT

```
input_text
    ↓
topic_tags[]     ← LEVEL 1
    ↓
intent           ← LEVEL 2
    ↓
schizo_params    ← LEVEL 3 (adjustable!)
    ↓
safety_pass      ← LEVEL 4
    ↓
platform_format  ← LEVEL 5
    ↓
output
```

**Critical**: Give user control dial for schizo_params, not fixed forever.

---

### WHY THIS IS SEFIROT'S CASE

From observed history:
- NOT a stream-of-consciousness writer
- NOT a troll
- You are a MEANING EDITOR
- You think modularly (just don't name it that)

**Your style = interface to complex topics, not a psycho-type.**

---

### PRACTICAL PARAMETER SETTINGS

| Context | Fragmentation | Irony | Aggression | Myth | Meme |
|---------|---------------|-------|------------|------|------|
| Normal CT | 40% | 50% | 30% | 40% | 50% |
| "шизо" | 70% | 60% | 50% | 60% | 60% |
| "в мясо" | 90% | 30% | 80% | 80% | 40% |
| "подъебать" | 50% | 70% | 90% | 20% | 70% |
| Deep analysis | 20% | 80% | 10% | 30% | 20% |
| Meme battle | 60% | 40% | 60% | 30% | 90% |

---

### USER CONTROL MECHANISM

Always allow user to set schizo level explicitly:
- "нормально" → 20-30%
- "шизо" → 50%
- "в мясо" → 90%
- "подъебать" → 75%
- Custom: specific parameters

---

### ANTI-CRINGE CHECKLIST (Level 4)

Before publishing, verify:
- [ ] Hyperbole markers present (obvious, 🔥, etc.)
- [ ] Irony detectable in aggressive takes
- [ ] No "I know truth" absolute claims
- [ ] "Too much to be literal" signals exist
- [ ] User would recognize this as performance, not belief

---

*Last updated: 2026-01-29*
*Source: Sefirot's architectural insight on multi-layer style system*
