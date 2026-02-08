# Priority Fixes Implementation Plan

*Created: 2026-02-07*

## P0: Fix LLM Tool Calling Integration
**Status:** 🔴 Requires OpenClaw Core Changes

### Problem
MiniMax LLM generates text but cannot execute skills. The LLM ↔ skills bridge is broken.

### Required Changes (Outside Scope)
```python
# In unified_orchestrator.py or gateway.py
class ToolExecutor:
    async def execute_skill(self, skill_name: str, params: dict) -> dict:
        # Currently missing - needs implementation
        
        # Requirements:
        # 1. Parse LLM response for tool calls
        # 2. Validate skill exists
        # 3. Execute skill with params
        # 4. Return results to LLM
```

### Current Workaround
Skills must be called directly via CLI or subprocess:
```bash
python3 /home/wner/clawd/skills/_system/prices/scripts/prices.py --asset bitcoin
```

---

## P1: Bridge LLM ↔ Skill Execution
**Status:** 🔴 Requires OpenClaw Core Changes

### Problem
Router selects skills but LLM can't invoke them. The semantic bridge is missing.

### Required Changes
1. **Intent Parser** - Extract skill name + params from natural language
2. **Skill Registry** - Map intents to skill paths
3. **Result Formatter** - Convert skill output to LLM-readable format
4. **Context Manager** - Maintain conversation context

### Design
```
User Input → Intent Classifier → Skill Selector → Executor → Result Formatter → LLM
```

---

## P2: Replace Mock Data with Real API Calls
**Status:** 🟡 In Progress

### Skills Analysis

| Skill | Status | Notes |
|-------|--------|-------|
| `prices` | ✅ Real | CoinGecko client implemented |
| `research` | ✅ Real | Brave/Serper/DuckDuckGo implemented |
| `arbitrage-signal` | ⚠️ Mixed | CoinGecko real, DEX spreads simulated |
| `colony` | ❓ Unknown | Needs testing |
| `starknet-*` | ❓ Unknown | Needs testing |

### Actions Completed
- ✅ Installed all dependencies (Flask, gunicorn, pandas, qrcode, aiosqlite)
- ✅ Verified CoinGecko client works
- ✅ Verified research providers configured

### Remaining Actions
- [ ] Test arbitrage-skill with real DEX APIs (JediSwap, Ekubo, 10K)
- [ ] Test colony Flask app
- [ ] Test starknet-mini-pay QR generation
- [ ] Add API keys for premium providers (Brave, Serper)

---

## P3: Upgrade to Semantic Routing
**Status:** 🟡 Requires Architectural Decision

### Current State
Regex-only routing:
```python
# unified_orchestrator.py
PATTERNS = {
    r'(?i)price.*bitcoin': 'prices',
    r'(?i)price.*eth(ereum)?': 'prices',
    r'(?i)search.*': 'research',
}
```

### Problems
- No semantic understanding
- Fragile pattern matching
- Can't handle complex multi-intent queries

### Options

**Option A: Embeddings + Vector Search**
```python
# Store skill descriptions as embeddings
# Query: "how much is bitcoin worth" → matches prices skill
```

**Option B: Fine-tuned Intent Classifier**
```python
# Train model on intent → skill mappings
```

**Option C: Hybrid (Recommended)**
- Use embeddings for similarity matching
- Keep regex for common patterns
- Fallback to LLM for ambiguous cases

---

## P4: Add MCP Bindings for Skills
**Status:** 🟡 Research Needed

### What is MCP?
Model Context Protocol - standard way for LLMs to call tools.

### Required Changes
1. Create `mcp.json` for each skill:
```json
{
  "name": "prices",
  "description": "Get cryptocurrency prices from CoinGecko",
  "parameters": {
    "asset": {
      "type": "string",
      "enum": ["bitcoin", "ethereum", "starknet", "solana"],
      "description": "Asset symbol"
    }
  }
}
```

2. Register skills with MCP server
3. Expose via MiniMax tool calling format

### Current Limitation
MiniMax doesn't support MCP natively. Requires adapter layer.

---

## Implementation Roadmap

### Phase 1: Testing & Validation (Today)
- [ ] Test prices skill with real API
- [ ] Test research skill with real API
- [ ] Test arbitrage signal
- [ ] Document API keys needed

### Phase 2: Documentation (Today)
- [ ] Document tool calling requirements
- [ ] Document MCP specification
- [ ] Create skill API contract

### Phase 3: Architecture (Future)
- [ ] Implement LLM ↔ skills bridge
- [ ] Add semantic routing
- [ ] Add MCP bindings

---

## Skills Ready for Testing

```bash
# Prices
python3 /home/wner/clawd/skills/_system/prices/scripts/prices.py --asset bitcoin --format json

# Research
python3 /home/wner/clawd/skills/_system/research/scripts/research.py --query "starknet news" --json

# Arbitrage
python3 /home/wner/clawd/skills/_integrations/arbitrage-signal/scripts/arbitrage_signal.py
```
