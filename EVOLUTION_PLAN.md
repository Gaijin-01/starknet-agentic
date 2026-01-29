# План работ — Исправление проблем (2026-01-29)

## Статус выполнения

### ✅ P1 — Critical (ЗАВЕРШЕНО)
| Задача | Статус | Дата |
|--------|--------|------|
| 1.1 Скрипты для adaptive-routing | ✅ Готово | 2026-01-29 |
| 1.2 TOOLS.md — заполнить | ✅ Готово | 2026-01-29 |
| 1.3 Error handling в BotController | ✅ Готово | 2026-01-29 |
| 1.4 Error handling в persona_post.py | ✅ Готово | 2026-01-29 |

### ✅ P2 — High (ЧАСТИЧНО ЗАВЕРШЕНО)
| Задача | Статус | Дата |
|--------|--------|------|
| 2.1 SKILL.md camsnap — Overview/Workflow/Examples | ✅ Уже было | 2026-01-29 |
| 2.2 SKILL.md mcporter — Overview/Workflow/Examples | ✅ Уже было | 2026-01-29 |
| 2.3 SKILL.md songsee — Overview/Workflow/Examples | ✅ Готово | 2026-01-29 |
| 2.4 style-learner — добавить Workflow | ✅ Готово | 2026-01-29 |
| 2.5 Retry logic в web-search | 📋 В очереди | После P2.4 |
| 2.6 Docstrings в ключевых файлах | 📋 В очереди | После P2.5 |

### 📋 P3 — Medium (Новые скиллы)
| Задача | Статус | Сроки |
|--------|--------|-------|
| 3.1 twitter-api (нативное X API) | 📋 В очереди | После P2 |
| 3.2 crypto-trading (onchain, whale tracking) | 📋 В очереди | После P2 |
| 3.3 ct-intelligence (competitor tracking) | 📋 В очереди | После P2 |

---

## Детализация P1

### 1.1 adaptive-routing — создать скрипты

**Текущее состояние:** SKILL.md есть, scripts/ пуст

**Что нужно:**
```
skills/adaptive-routing/scripts/
├── router.py          # AdaptiveRouter класс
├── skill_detector.py  # Паттерн-матчинг
├── cli.py             # CLI интерфейс
└── __init__.py
```

**Функционал:**
- `AdaptiveRouter.route(message, context)` → RoutingResult
- Паттерн-матчинг для скиллов
- Confidence scoring (0.0-1.0)
- Fallback на claude-proxy при low confidence

### 1.2 TOOLS.md — заполнить

**Что добавить:**
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

### 1.3 Error handling — BotController

**Проблемы:**
- Нет try/except в execute()
- Нет graceful fallback при LLM errors
- Нет logging для debugging

**Что добавить:**
- Retry logic (3 attempts)
- Timeout handling
- Graceful degradation
- Structured logging

### 1.4 Error handling — persona_post.py

**Проблемы:**
- PROFILE["persona"]["name"] — KeyError
- Нет exception handling
- Жёстко закодированные templates

**Что добавить:**
- Safe profile access
- Fallback templates
- Logging

---

## Исполнители

- **claude-proxy:** Генерация кода, анализ
- **Evolver:** Оркестрация, координация
- **Claude (внешний):** Сложные архитектурные решения

---

## Чеклист выполнения P1

- [ ] adaptive-routing/scripts/router.py
- [ ] adaptive-routing/scripts/skill_detector.py
- [ ] adaptive-routing/scripts/cli.py
- [ ] adaptive-routing/scripts/__init__.py
- [ ] TOOLS.md заполнен
- [ ] BotController — retry logic + logging
- [ ] persona_post.py — error handling + safe access
