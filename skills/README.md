# Clawd Skills 🦞

Централизованная система скилов для автоматизации X (Twitter) и крипто-контента.

```
clawd/skills/
├── config/                    # Централизованная конфигурация
│   ├── config.json            # Главный конфиг (API ключи, настройки)
│   ├── config.yaml            # Расширенные настройки
│   ├── config_loader.py       # Единый загрузчик конфигов
│   └── examples/              # Примеры конфигураций
│       ├── config.finance.yaml
│       └── config.news.yaml
├── research/                  # 🟢 Brave API research tool
│   ├── SKILL.md
│   └── scripts/research.py
├── prices/                    # 🟢 Coingecko API prices
│   ├── SKILL.md
│   └── scripts/prices.py
├── x-algorithm-optimizer/     # 🟢 X algorithm optimization (v2.0)
│   ├── algorithm_scorer.py    # Алгоритм подсчёта score
│   ├── STRATEGY.md            # Стратегия постинга
│   └── scripts/               # Скрипты (если нужны)
├── style-learner/             # 🟢 Persona learning system
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── executor.py
│   │   ├── analyzer.py
│   │   ├── main.py
│   │   └── generator.py
│   └── profiles/
│       └── style_profile.json # Профиль SefirotWatch
├── post-generator/            # 🟡 Template-based generator
│   ├── SKILL.md
│   └── scripts/
│       ├── post_generator.py
│       └── persona_post.py
├── queue-manager/             # 🟢 Queue management
│   ├── SKILL.md
│   └── scripts/queue_manager.py
├── workflow.py                # 🟢 Master workflow script
├── quote_workflow.py          # 🔴 Дублирует workflow.py (удалить)
└── README.md                  # Этот файл
```

## 🚀 Быстрый старт

### Master Workflow
```bash
cd ~/clawd/skills
python3 workflow.py "<query>" --type gm|news|insight
```

### Quote Workflow
```bash
python3 quote_workflow.py "<tweet_url>" --type comment|insight|hype
```

### Queue Management
```bash
cd ~/clawd/skills/queue-manager
python3 scripts/queue_manager.py list --all
python3 scripts/queue_manager.py add --content "<text>"
python3 scripts/queue_manager.py move --file <file> --to posted
```

## 📊 Persona: SefirotWatch

| Параметр | Значение |
|----------|----------|
| Tone | minimal, cryptic, confident |
| Emoji | 🐺 (3x), 🔥 (2x) |
| Avg words | 10 |
| Vocabulary | 180+ crypto/defi terms |

## 🎯 X Algorithm Optimizer v2.0

**Веса действий:**
| Действие | Вес |
|----------|-----|
| Quote | 3.5x |
| Reply | 3.0x |
| Share | 2.5x |
| Repost | 2.0x |
| Favorite | 1.0x |

**Негативные сигналы:**
| Действие | Вес |
|----------|-----|
| Report | -10.0 |
| Not interested | -5.0 |
| Block | -3.0 |
| Mute | -2.0 |

## ⏰ Peak Hours для постинга

- **6:00-9:00** UTC — Утро
- **12:00-14:00** UTC — Обед
- **18:00-21:00** UTC — Вечер

## 📝 Конфигурация

Все скилы берут настройки из `config/config.json`:

```json
{
  "x": {
    "persona": "SefirotWatch",
    "max_daily_posts": 15,
    "min_gap_minutes": 20
  },
  "api": {
    "brave": "BRAVE_API_KEY",
    "coingecko": "COINGECKO_API_KEY"
  }
}
```

## 🔧 Команды

```bash
# Проверить все скилы
cd ~/clawd/skills && ls -la

# Обновить конфиг
python3 config/config_loader.py --reload

# Запустить анализ стиля
python3 style-learner/scripts/main.py --analyze
```

## 📦 TODO

- [ ] Удалить `quote_workflow.py` (функционал в `workflow.py`)
- [ ] Интегрировать `post-generator` в `workflow.py`
- [ ] Создать единый CLI для всех скилов
- [ ] Добавить тесты для `algorithm_scorer.py`
- [ ] Обновить пути в памяти `/tmp/wsl-portable-v2/` → `~/clawd/skills/`

---
*Generated: 2026-01-23*
