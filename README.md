# TaskWeaver — Personal Task Weaver

> Make every day's effort point somewhere, and every weekly review grow something new.

> **Language:** English | [简体中文](README.zh-CN.md)

---

## What it is

TaskWeaver is a **day-to-week personal task management and review system** that runs as a CodeBuddy/WorkBuddy Skill. The core idea is to weave scattered daily tasks into long-term work goals, and keep you focused through Eisenhower-matrix (important/urgent) analysis.

**Problems it solves:**
- Busy all day, but unable to say how the work connects to your OKRs/KPIs
- Energy drained by unimportant, non-urgent things while what truly matters stalls
- Weekly reports are painful — you don't remember what you did, or how to reflect
- "Unplanned" things keep recurring but are never examined systematically

---

## Workflow

```
Set goals → Daily morning planning → Daily evening review → Weekly deep review
  /okr           /morning                /evening              /weekly
```

### The four commands

| Command | When | What it does |
|------|------|--------|
| `/okr` | Setup + anytime | Enter and manage OKRs / work goals |
| `/morning` | Every morning | Dictate today's tasks → AI breaks into todos → auto-links to goals → suggests quadrants |
| `/evening` | Every evening | Dictate what you actually finished → AI matches and checks off → logs extra completions |
| `/weekly` | Every weekend | Generates a review report: goal-alignment analysis + quadrant stats + off-plan discovery + improvement suggestions |

---

## Installation

### Option 1: Install as a WorkBuddy Skill

Clone this repo into your WorkBuddy skills directory:

```bash
git clone https://github.com/Hunchide/task-weaver.git ~/.workbuddy/skills/task-weaver
```

### Option 2: Manual install

1. Download or clone this repo
2. Copy the whole `task-weaver` directory to `~/.workbuddy/skills/task-weaver/`
3. Ensure the structure looks like:

```
~/.workbuddy/skills/task-weaver/
├── SKILL.md              # Skill definition and AI behavior spec
├── README.md             # This file
├── scripts/
│   └── engine.py         # Core data engine
└── references/
    └── weekly-template.md # Weekly report output template
```

Data is stored locally by default:

```
~/.task-weaver-data/
├── okrs.json         # Work goals
├── tasks.json        # Daily todos
└── completions.json  # Completion records
```

To use a custom location, set an environment variable:

```bash
export TASKWEAVER_DATA_DIR="$HOME/.task-weaver-data"
```

---

## Getting started

### 1. Set your goals

Type `/okr` in chat, then dictate your work goals:

```
"Four main directions this year: product capability building (xx platform, xx process integration),
ecosystem partnerships (xx supplier onboarding), process optimization (mechanism design, standards),
business capability promotion (benchmark projects, revenue conversion)"
```

AI structures it and writes it out.

### 2. Morning planning

Each morning type `/morning` and dictate today's tasks:

```
"Mainly aligning with xx on xx today, afternoon has a process optimization meeting,
and I need to write chapter one of the business management spec"
```

AI will:
- Break them into concrete todos
- Auto-link to existing goals
- Suggest an Eisenhower quadrant for each (important & urgent / important not urgent / urgent not important / neither)
- You just reply "all OK" or tweak quickly

### 3. Evening review

Each evening type `/evening` and dictate what you actually finished (not limited to the morning plan):

```
"Finished talking with xx — they have their own logic, so I switched to observing.
Also wrapped up the xx test integration today"
```

AI will:
- Auto-match and check off planned todos
- Classify off-plan completions as "extra completions"
- Auto-assign goal links and quadrants to the extra items

### 4. Weekly review

Each weekend type `/weekly` and AI generates a full review report:

- **Goal-alignment analysis**: progress under each OKR, what got neglected
- **Quadrant stats**: where your energy actually went
- **Off-plan discovery**: could unplanned items grow into new work goals
- **Improvement suggestions**: how to spend less on unimportant/non-urgent and invest more in long-term value

---

## The four quadrants

| Quadrant | Meaning | Strategy |
|------|------|------|
| 🔴 Important & urgent | Has a deadline, affects key results | Handle immediately |
| 🟡 Important, not urgent | Capability building, long-term planning, prevention | **Focus here** (target 40–60%) |
| 🔵 Urgent, not important | Others' requests, routine reports | Delegate or handle quickly |
| ⚪ Neither | Trivia, over-optimization | Reduce / delegate / delete |

---

## Data engine API

`scripts/engine.py` supports both CLI and Python calls.

### CLI

```bash
python3 scripts/engine.py okr-list
python3 scripts/engine.py okr-add "Goal title" "Description" "Category"
python3 scripts/engine.py okr-update 1 --title "New title" --status active
python3 scripts/engine.py okr-delete 1
python3 scripts/engine.py task-add "Finish PRD" --date 2026-06-08 --okr-id 1 --quadrant Q1
python3 scripts/engine.py task-update 1 --status done
python3 scripts/engine.py task-delete 1
python3 scripts/engine.py task-list 2026-06-08
python3 scripts/engine.py task-pending 2026-06-08
python3 scripts/engine.py completion-add "Finish PRD" --date 2026-06-08 --task-id 1 --okr-id 1 --quadrant Q1 --source planned
python3 scripts/engine.py completion-list 2026-06-08
python3 scripts/engine.py weekly-report 2026-06-08
python3 scripts/engine.py data-status
```

### Python API

```python
import sys
sys.path.insert(0, "scripts")
from engine import okr_list, okr_add, add_task, update_task, add_completion, weekly_report

# Add an OKR
okr = okr_add("Product capability building", "Integrate systems", "Product")

# Add a todo
task = add_task(title="Finish PRD", for_date="2026-06-08", okr_id=1, quadrant="Q1")

# Log a completion
add_completion(title="Finish PRD", task_id=1, okr_id=1, quadrant="Q1", source="planned")

# Generate a weekly report
report = weekly_report("2026-06-08")
```

---

## Data file formats

### okrs.json

```json
[
  {
    "id": 1,
    "title": "xx project process capability building",
    "description": "Integrate systems, complete the xx process",
    "category": "Product capability building",
    "status": "active",
    "created_at": "2026-06-08"
  }
]
```

### tasks.json

```json
[
  {
    "id": 1,
    "date": "2026-06-08",
    "title": "Align with xx on xx items",
    "okr_id": null,
    "urgency": "urgent",
    "importance": "important",
    "quadrant": "Q1",
    "status": "pending",
    "notes": null,
    "created_at": "2026-06-08"
  }
]
```

### completions.json

```json
[
  {
    "id": 1,
    "date": "2026-06-08",
    "title": "xx test integration",
    "task_id": null,
    "okr_id": 3,
    "quadrant": "Q2",
    "source": "extra",
    "created_at": "2026-06-08"
  }
]
```

---

## Design philosophy

1. **Speaking is input** — no forms to fill; just talk like you're chatting with a person
2. **AI judges, you decide** — AI suggests (links, quadrants); you confirm or fine-tune
3. **Completion isn't limited to the plan** — evening completions can exceed the morning plan; flexible and honest
4. **New directions grow from the off-plan** — unplanned items aren't noise, they may signal a new work priority
5. **Transparent, controllable data** — everything lives in local JSON files, viewable and hand-editable anytime

---

## FAQ

**Q: Can goals be changed anytime?**
A: Yes. Just tell the AI "change goal X", or edit `okrs.json` directly.

**Q: Can evening completions exceed the morning plan?**
A: By design. Off-plan items are auto-classified as "extra completions" and get the same quadrant and goal-alignment analysis.

**Q: Can I manage life stuff too?**
A: Yes — add a goal in a "Life" category, e.g. fitness or reading.

**Q: Will data be lost?**
A: Data lives in `~/.task-weaver-data/` as plain JSON — back it up anytime. You can point `TASKWEAVER_DATA_DIR` elsewhere.

---

## License

MIT
