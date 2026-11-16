# TaskWeaver —— 个人任务编织器

> **Language:** [English](README.md) | 简体中文

> 让每一天的努力都看得见方向，让每一周的复盘都长出新的可能。

---

## 这是什么

TaskWeaver 是一套**从日到周的个人任务管理与复盘系统**，以 CodeBuddy/WorkBuddy Skill 的形式运行。核心理念是把每天的零散任务编织到长期工作目标中，并通过四象限（重要/紧急）分析帮助你持续聚焦。

**解决的问题：**
- 每天忙忙碌碌，但说不清楚做的事和 OKR/KPI 有什么关系
- 精力被不重要不紧急的事消耗，真正重要的事反而没推进
- 每周写周报痛苦——不记得做了什么，也不知道怎么复盘
- 一些"计划外"的事反复出现，但从未被系统性地审视过

---

## 工作流

```
设定目标 → 每日晨间规划 → 每日晚间复盘 → 周末深度复盘
  /okr       /morning        /evening        /weekly
```

### 四个命令

| 命令 | 时机 | 做什么 |
|------|------|--------|
| `/okr` | 初始化 + 随时 | 录入和管理 OKR / 工作目标 |
| `/morning` | 每天早上 | 口述今天要做什么 → AI 拆解待办 → 自动关联目标 → 建议四象限 |
| `/evening` | 每天晚上 | 口述实际完成了什么 → AI 匹配勾销 → 记录额外完成 |
| `/weekly` | 每周末 | 生成周报复盘：目标关联分析 + 四象限统计 + 无关事项挖掘 + 改进建议 |

---

## 安装

### 方式一：作为 WorkBuddy Skill 安装

将本仓库克隆到 WorkBuddy 的 skills 目录：

```bash
git clone https://github.com/Hunchide/task-weaver.git ~/.workbuddy/skills/task-weaver
```

### 方式二：手动安装

1. 下载或克隆本仓库
2. 将整个 `task-weaver` 目录复制到 `~/.workbuddy/skills/task-weaver/`
3. 确保目录结构如下：

```
~/.workbuddy/skills/task-weaver/
├── SKILL.md              # Skill 定义和 AI 行为说明书
├── README.md             # 本文件
├── scripts/
│   └── engine.py         # 核心数据引擎
└── references/
    └── weekly-template.md # 周报输出模板
```

数据默认存储在本机用户目录：

```
~/.task-weaver-data/
├── okrs.json         # 工作目标
├── tasks.json        # 每日待办
└── completions.json  # 完成记录
```

如需自定义位置，可以设置环境变量：

```bash
export TASKWEAVER_DATA_DIR="$HOME/.task-weaver-data"
```

---

## 快速上手

### 1. 设定目标

在对话中输入 `/okr`，然后口述你的工作目标：

```
"我今年主要四个方向：产品能力建设（xx平台建设、xx流程打通）、
生态对接合作（xx供应商引入）、流程优化提效（机制设计、规范制定）、
业务能力推广（标杆项目、收入转化）"
```

AI 会帮你结构化并写入。

### 2. 晨间规划

每天早上输入 `/morning`，口述今天的任务：

```
"今天主要跟xx对齐xx事，下午有个流程优化讨论会，
还要把业务管理规范第一章写了"
```

AI 会：
- 拆解为具体待办
- 自动关联到已有目标
- 建议每个待办的四象限（重要且紧急 / 重要不紧急 / 紧急不重要 / 不重要不紧急）
- 你只需回复「全部OK」或快速调整

### 3. 晚间复盘

每天晚上输入 `/evening`，口述实际完成的事（不限早上计划）：

```
"和xx聊完了，他那边有自己逻辑，我改围观了。
另外今天xx测试对接搞定了"
```

AI 会：
- 自动匹配勾销计划内待办
- 将计划外完成事项归类为「额外完成」
- 为额外事项自动判断目标关联和四象限

### 4. 周末复盘

每周末输入 `/weekly`，AI 生成完整复盘报告：

- **目标关联分析**：每个 OKR 下的进展，哪些被忽略了
- **四象限统计**：你的精力花在哪儿了
- **无关事项挖掘**：计划外事项能否长出新的工作目标
- **改进建议**：如何减少不重要不紧急、提升长期价值投入

---

## 四象限说明

| 象限 | 含义 | 策略 |
|------|------|------|
| 🔴 重要且紧急 | 有 deadline、影响关键结果 | 立即处理 |
| 🟡 重要不紧急 | 能力提升、长期规划、预防性工作 | **重点投入**（目标 40-60%） |
| 🔵 紧急不重要 | 他人催促、常规汇报 | 委托或快速处理 |
| ⚪ 不重要不紧急 | 琐事、过度优化 | 减少 / 委托 / 删除 |

---

## 数据引擎 API

`scripts/engine.py` 提供命令行和 Python 两种调用方式：

### 命令行

```bash
python3 scripts/engine.py okr-list
python3 scripts/engine.py okr-add "目标标题" "描述" "分类"
python3 scripts/engine.py okr-update 1 --title "新标题" --status active
python3 scripts/engine.py okr-delete 1
python3 scripts/engine.py task-add "完成 PRD" --date 2026-06-08 --okr-id 1 --quadrant Q1
python3 scripts/engine.py task-update 1 --status done
python3 scripts/engine.py task-delete 1
python3 scripts/engine.py task-list 2026-06-08
python3 scripts/engine.py task-pending 2026-06-08
python3 scripts/engine.py completion-add "完成 PRD" --date 2026-06-08 --task-id 1 --okr-id 1 --quadrant Q1 --source planned
python3 scripts/engine.py completion-list 2026-06-08
python3 scripts/engine.py weekly-report 2026-06-08
python3 scripts/engine.py data-status
```

### Python API

```python
import sys
sys.path.insert(0, "scripts")
from engine import okr_list, okr_add, add_task, update_task, add_completion, weekly_report

# 添加 OKR
okr = okr_add("产品能力建设", "系统之间打通", "产品")

# 添加待办
task = add_task(title="完成 PRD", for_date="2026-06-08", okr_id=1, quadrant="Q1")

# 记录完成
add_completion(title="完成 PRD", task_id=1, okr_id=1, quadrant="Q1", source="planned")

# 生成周报
report = weekly_report("2026-06-08")
```

---

## 数据文件格式

### okrs.json

```json
[
  {
    "id": 1,
    "title": "xx项目流程能力建设",
    "description": "系统之间打通，xx流程能力完善",
    "category": "产品能力建设",
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
    "title": "与xx对齐xx相关事项",
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
    "title": "xx测试对接",
    "task_id": null,
    "okr_id": 3,
    "quadrant": "Q2",
    "source": "extra",
    "created_at": "2026-06-08"
  }
]
```

---

## 设计哲学

1. **口述即输入** — 不需要填表单，像跟人聊天一样说就行
2. **AI 做判断，人做决策** — AI 给建议（关联、象限），你只需确认或微调
3. **完成不限于计划** — 晚上说的完成事项可以超出早上计划，灵活真实
4. **从无关中长出新方向** — 计划外事项不是噪音，可能是新的工作重心信号
5. **数据透明可控** — 所有数据存在本地 JSON 文件中，随时可查看、手动编辑

---

## 常见问题

**Q: 目标可以随时修改吗？**
A: 可以。对 AI 说「改目标 X」就行，也可以直接编辑 `okrs.json` 文件。

**Q: 晚上说的完成事项能超出早上计划吗？**
A: 这是设计如此。计划外的自动归类为「额外完成」，同样做四象限和目标关联分析。

**Q: 生活事项能一起管吗？**
A: 可以，添加一个「生活」分类的目标就行，比如健身、阅读等。

**Q: 数据会丢吗？**
A: 数据默认存在 `~/.task-weaver-data/` 下，纯 JSON 文件，随时可备份。也可以用 `TASKWEAVER_DATA_DIR` 指定到其他目录。

---

## License

MIT
