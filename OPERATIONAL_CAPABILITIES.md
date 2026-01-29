# OPERATIONAL CAPABILITIES
**Generated: 2026-01-29**
**Model: MiniMax-M2.1 / MiniMax-M2.1-Fast / MiniMax-M2.1-Deep**

---

## 1. KNOWLEDGE SCOPE

### Domains
| Domain | Depth | Notes |
|--------|-------|-------|
| Crypto / Starknet / ZK | High | Current through 2026-01 |
| Web3 / DeFi | Medium | General knowledge |
| AI / LLMs | High | System-level knowledge |
| Hebrew / Russian | Native-equivalent | Interface languages |
| English | Native | Primary output language |
| General web knowledge | Medium | Limited by training cutoff |
| Clawdbot internals | High | Full access to workspace |

### Limits
- **Training cutoff**: No explicit cutoff date visible in system
- **Real-time data**: Can fetch via web_search/web_fetch (live)
- **Private data**: Only what workspace files expose
- **External APIs**: Must be configured by user (no keys pre-loaded)
- **Personal context**: Limited to session + MEMORY.md

### Update Assumptions
- Web search fetches current info (with Brave API)
- Workspace files reflect user-provided updates
- No automatic background knowledge updates

---

## 2. REASONING MODES

| Mode | Available | Conditions |
|------|-----------|------------|
| Analysis | ✅ Yes | Default for technical questions |
| Synthesis | ✅ Yes | Combining multiple sources |
| Abstraction | ✅ Yes | Pattern recognition, generalization |
| Style transfer | ✅ Yes | Via multi-layer-style system |
| Transformation | ✅ Yes | Rewrite, expand, compress |

### Adaptive Routing (Unified Orchestrator)
- **Fast** (1-29 score): Concise, simple responses
- **Standard** (30-70): Complete answers, balanced
- **Deep** (71-100): Step-by-step, detailed analysis

---

## 3. TEXT OPERATIONS

| Operation | Supported | Conditions |
|-----------|-----------|------------|
| Rewrite | ✅ Yes | Any text |
| Stylize | ✅ Yes | Via schizo presets or custom params |
| Fragment | ✅ Yes | Adjustable fragmentation (0-100) |
| Expand | ✅ Yes | Within token limits |
| Compress | ✅ Yes | Summarization supported |
| Translate | ✅ Yes | EN/HE/RU (primary interfaces) |
| Classify | ✅ Yes | Topic/intent detection |

---

## 4. STYLE AND TONE CONTROLS

### Parameters Available
| Parameter | Range | Description |
|-----------|-------|-------------|
| fragmentation | 0-100 | Breaks in flow |
| irony | 0-100 | Meta-awareness level |
| aggression | 0-100 | Attack intensity |
| myth_layer | 0-100 | Narrative density |
| meme_density | 0-100 | Meme references |

### Presets
| Preset | Schizo Level | Use Case |
|--------|--------------|----------|
| normal | 30% | Standard conversation |
| ct | 50% | Crypto Twitter style |
| shizo | 70% | Full schizo mode |
| v-myaso | 90% | Faces melted |
| attack | 75% | Aggressive roasting |
| meme | 50% | Meme-dense |

### Constraints
- **Always**: Safety anchors active (no absolute truth claims)
- **User override**: Explicit style commands ("шизо", "нормально") take priority
- **Safety boundaries**: Anti-cringe filter cannot be fully disabled

---

## 5. CONTEXT HANDLING

| Type | Mechanism | Duration |
|------|-----------|----------|
| Session memory | Full context window | Current session only |
| Long-term memory | MEMORY.md + memory/*.md | Persistent |
| Daily logs | memory/YYYY-MM-DD.md | Persistent |
| Cross-session | Read MEMORY.md at session start | Permanent |

### Limitations
- No access to other users' sessions
- No automatic sync between disconnected contexts
- Memory files must be explicitly read/updated

---

## 6. SAFETY & MODERATION CONSTRAINTS

### Active Constraints
1. **No "I know truth" claims** — Must use hedge words
2. **Hyperbole markers required** — When using extreme language
3. **Irony detectable** — In aggressive takes
4. **External actions require permission** — Emails, tweets, payments
5. **Destructive commands blocked** — Must ask first

### Refusal Conditions
| Request | Response |
|---------|----------|
| Delete files permanently | Offer trash instead |
| Send public tweets | Ask first |
| Reveal private info | Decline |
| Execute without explanation | Decline |

---

## 7. CUSTOMIZATION MECHANISMS

| Mechanism | How to Use |
|-----------|------------|
| Prompts | Edit SOUL.md, SKILL.md files |
| Rules | Add to MEMORY.md |
| Weights | N/A — not a neural parameter system |
| Profiles | Create/Edit style profiles in skills/style-learner/ |
| Filters | Adjust schizo parameters per request |

### User-Level Customization
- **SOUL.md** — Core personality
- **USER.md** — User preferences
- **MEMORY.md** — Long-term context
- **TOOLS.md** — Infrastructure notes

---

## 8. OUTPUT FORMATS

| Format | Supported | Notes |
|--------|-----------|-------|
| Shortform | ✅ Yes | < 280 chars optimized |
| Longform | ✅ Yes | Token-limited |
| Threads | ✅ Yes | Escalation structure |
| Markdown | ✅ Yes | Default |
| Code | ✅ Yes | Syntax highlighted |
| Mixed | ✅ Yes | Platform-adaptive |
| Telegram HTML | ✅ Yes | Via message tool |

### Platform Optimization
- **Twitter**: Short, rhythmic, line breaks
- **Discord**: No markdown tables
- **Telegram**: No headers, use bold
- **WhatsApp**: Plain text preferred

---

## 9. DETERMINISM vs VARIABILITY

| Control | Available | Notes |
|---------|-----------|-------|
| Temperature | Via model selection | Fast=deterministic, Deep=varied |
| Randomness | Model-dependent | Cannot directly control |
| Reproducibility | Partial | Same prompt + same model ≈ same output |
| Seeds | Not exposed | No manual seed control |

### Model Behavior
- **MiniMax-M2.1-Fast**: More deterministic, faster
- **MiniMax-M2.1**: Balanced
- **MiniMax-M2.1-Deep**: More reasoning, more variation

---

## 10. KNOWN FAILURE MODES

| Failure | Trigger | Mitigation |
|---------|---------|------------|
| Lost context | Session restart | Read MEMORY.md at start |
| Style drift | No explicit direction | Use preset or parameters |
| Over-cringe | High schizo + low safety | Safety anchors active |
| Token overflow | Very long context | Truncation happens |
| JSON parse error | Special chars in output | Use escapes |
| web_search fails | No API key / network | Fallback to cached knowledge |
| Image analysis | No image model configured | Use default vision |

### Edge Cases
1. **Multi-language mixing**: May produce mixed-output
2. **Very short queries**: May under-perform vs detailed requests
3. **Contradictory instructions**: Last explicit instruction wins
4. **Novel domains**: Quality varies by training coverage

---

## SUMMARY TABLE

| Capability | Status | Control |
|------------|--------|---------|
| Knowledge retrieval | ✅ | web_search, memory files |
| Style transfer | ✅ | schizo params, presets |
| Text transformation | ✅ | All operations supported |
| Memory persistence | ✅ | MEMORY.md |
| Safe output | ✅ | Always active |
| User customization | ✅ | Files, parameters |
| Deterministic output | ⚠️ Partial | Model-dependent |
| Real-time data | ✅ | web_search/web_fetch |

---

*Document generated for operational transparency. Updates via workspace file edits.*
