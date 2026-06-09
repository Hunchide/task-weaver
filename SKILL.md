---
name: task-weaver
description: 个人任务管理与复盘系统 —— 从日到周的任务编织器。支持 OKR 管理、晨间任务拆解与四象限标注、晚间完成勾销、周报复盘分析。当用户提到任务管理、OKR、晨间规划、晚间复盘、周报、四象限、任务编织等关键词时使用此 skill。
allowed-tools: Read, Write, Bash
agent_created: true
---

# TaskWeaver —— 个人任务编织器

将每天的零散任务编织到长期工作目标中的系统。核心哲学：**让每一天的努力都看得见方向，让每一周的复盘都长出新的可能。**

---

## 命令体系

4 个斜杠命令覆盖完整的「日 → 周」工作流：

| 命令 | 用途 | 使用时机 |
|------|------|----------|
| `/okr` | 管理 OKR / 工作目标 | 初始化 + 随时增补 |
| `/morning` | 晨间任务拆解与标注 | 每天早上 |
| `/evening` | 晚间完成记录与勾销 | 每天晚上 |
| `/weekly` | 周报复盘分析 | 每周末 |

---

## 数据引擎

使用 `scripts/engine.py` 作为数据引擎，通过命令行调用。数据存储在 `/workspace/task-weaver-data/` 目录下的 JSON 文件中。

**重要：** 每次执行命令前，先运行 `data-status` 了解当前数据状态，以便给出上下文相关的提示。

### 可用命令

```bash
# OKR 管理
python3 scripts/engine.py okr-list
python3 scripts/engine.py okr-add "<title>" "<desc>" "<category>"
python3 scripts/engine.py okr-delete <id>

# 待办管理
python3 scripts/engine.py task-list [date]
python3 scripts/engine.py task-pending [date]

# 完成记录
python3 scripts/engine.py completion-list [date]

# 周报
python3 scripts/engine.py weekly-report [date]

# 状态
python3 scripts/engine.py data-status
```

### Python 直接调用

```python
import sys; sys.path.insert(0, "scripts")
from engine import add_task, update_task, add_completion

add_task(title="xxx", for_date="2026-01-01", okr_id=1, urgency="urgent",
         importance="important", quadrant="Q1")

update_task(task_id=1, quadrant="Q2", importance="important")

add_completion(title="xxx", task_id=1, okr_id=1, quadrant="Q1",
               source="planned")  # or "extra"
```

---

## 各命令详细流程

### `/okr` —— 管理 OKR / 工作目标

**触发：** 用户输入 `/okr` 或说"管理我的工作目标"、"设定 OKR"、"添加目标"等。

**流程：**

1. 运行 `data-status` 查看当前 OKR 数量
2. OKR 为空 → 引导用户录入（口述 → AI 拆解 → 确认 → 写入）
3. OKR 已有 → 展示列表，提供查看/添加/修改/删除选项

**输出格式：**

```
📋 当前工作目标（共 N 个）

1. [分类] 目标标题
   描述：xxx
   状态：进行中 | 已完成

━━━━━━━━━━━━━━━━━━━━
你可以说：
- 「添加目标」来新增
- 「修改目标 X」来更新
- 「删除目标 X」来移除
```

---

### `/morning` —— 晨间任务拆解与四象限标注

**触发：** 用户输入 `/morning` 或说"早上好"、"今天任务"、"规划今天"等。

**流程：**

1. **口述接收** — 用户自由口述今天任务，AI 拆解为可执行待办
2. **目标关联** — 读取 OKR，自动判断每个待办关联哪个目标
3. **四象限标注** — AI 建议象限，用户快速确认或调整
4. **确认写入** — 写入数据

**四象限定义：**

| 象限 | 含义 | 策略 |
|------|------|------|
| Q1 重要且紧急 | 有 deadline、影响关键结果 | 立即处理 |
| Q2 重要不紧急 | 能力提升、长期规划、预防性工作 | **重点投入**（目标 40-60%） |
| Q3 紧急不重要 | 他人催促、常规汇报 | 委托或快速处理 |
| Q4 不重要不紧急 | 琐事、过度优化 | 减少/委托/删除 |

**输出格式：**

```
☀️ 今日任务拆解 —— 2026年X月X日 周X

📌 待办列表：

1. 🔴 Q1 | [目标：XX] 完成产品需求文档终稿
2. 🟡 Q2 | [目标：XX] 学习 Rust 异步编程（第3章）
3. 🔵 Q3 | [未关联] 回复上周的客户邮件
4. ⚪ Q4 | [目标：XX] 整理桌面文件

━━━━━━━━━━━━━━━━━━━━
四象限分布：Q1:1 | Q2:1 | Q3:1 | Q4:1

🔧 请确认或调整（回复示例）：
  「全部OK」 / 「3改Q2」 / 「2关联目标3」 / 「加一条：xxx」
```

---

### `/evening` —— 晚间完成记录与勾销

**触发：** 用户输入 `/evening` 或说"晚上好"、"今天完成了"、"复盘今天"等。

**流程：**

1. **展示今日待办** — 显示 pending 和已完成状态
2. **口述接收** — 用户自由口述实际完成的事项（不限于早上计划）
3. **智能匹配** — 与今日待做语义匹配：匹配 → 勾销；不匹配 → 额外完成
4. **补充标注** — 额外事项自动判断四象限和目标关联
5. **确认写入** — 写入完成记录并更新待办状态

**输出格式：**

```
🌙 今日回顾 —— 2026年X月X日

✅ 已完成（来自今日计划）：
  ✓ 完成产品需求文档终稿
  ✓ 回复上周的客户邮件

📝 额外完成（不在今日计划中）：
  + 🔴 Q1 | [目标：XX] 紧急修复线上 Bug #3421
  + 🟡 Q2 | [未关联] 帮同事 Review 代码

⏳ 未完成：
  ⬜ 学习 Rust 异步编程（第3章）
  ⬜ 整理桌面文件

━━━━━━━━━━━━━━━━━━━━
今日完成率：2/4（计划内）+ 2（额外）= 共 4 项
```

---

### `/weekly` —— 周报复盘分析

**触发：** 用户输入 `/weekly` 或说"周报"、"本周复盘"、"生成周报"等。

**流程：** 调用 `engine.py` 的 `weekly-report` 获取数据，然后格式化为 5 个模块：

1. **概览** — 任务数、完成数、完成率、每日趋势
2. **目标关联分析** — 每个 OKR 下完成事项数量和进展
3. **四象限分析** — 精力分配统计和对比
4. **无关事项挖掘** — 未关联目标事项聚类，识别新方向
5. **改进建议** — 可执行的改进建议

详细输出格式参见 `references/weekly-template.md`。

---

## 重要原则

1. **拆解要自然** — 保持用户原始意图，只把模糊大任务拆成具体动作
2. **关联要智能** — 语义判断而非关键词匹配
3. **确认要轻量** — 支持批量确认和快速调整
4. **语言要口语化** — 回复自然有温度
5. **数据要准确** — 写入前必须确认

## 工作目录

- 数据目录：`/workspace/task-weaver-data/`
- 引擎脚本：`scripts/engine.py`（相对于 skill 目录）
