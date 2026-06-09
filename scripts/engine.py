#!/usr/bin/env python3
"""
TaskWeaver Engine —— 个人任务编织器数据引擎

数据存储在 /workspace/task-weaver-data/ 目录下的 JSON 文件中：
- okrs.json: 工作目标
- tasks.json: 每日待办
- completions.json: 完成记录
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(os.environ.get("TASKWEAVER_DATA_DIR", "/workspace/task-weaver-data"))


# ─── 工具函数 ───────────────────────────────────────────────

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filename):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(filename, data):
    _ensure_data_dir()
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _next_id(items):
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _parse_date(date_str=None):
    if date_str:
        return date_str
    return _today()


def _get_week_range(date_str=None):
    """获取指定日期所在周的周一和周日日期"""
    if date_str:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        d = datetime.now()
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


# ─── OKR 管理 ──────────────────────────────────────────────

def okr_list():
    return _load_json("okrs.json")


def okr_add(title, description="", category=""):
    okrs = _load_json("okrs.json")
    new_okr = {
        "id": _next_id(okrs),
        "title": title,
        "description": description,
        "category": category,
        "status": "active",
        "created_at": _today(),
    }
    okrs.append(new_okr)
    _save_json("okrs.json", okrs)
    return new_okr


def okr_update(okr_id, **kwargs):
    okrs = _load_json("okrs.json")
    for okr in okrs:
        if okr["id"] == okr_id:
            for key, value in kwargs.items():
                if value is not None:
                    okr[key] = value
            _save_json("okrs.json", okrs)
            return okr
    return None


def okr_delete(okr_id):
    okrs = _load_json("okrs.json")
    okrs = [o for o in okrs if o["id"] != okr_id]
    _save_json("okrs.json", okrs)
    return True


# ─── 待办管理 ──────────────────────────────────────────────

def task_list(date=None):
    tasks = _load_json("tasks.json")
    target_date = _parse_date(date)
    return [t for t in tasks if t.get("date") == target_date]


def task_pending(date=None):
    tasks = task_list(date)
    return [t for t in tasks if t.get("status") != "done"]


def add_task(title, for_date=None, okr_id=None, urgency=None,
             importance=None, quadrant=None, notes=None):
    tasks = _load_json("tasks.json")
    new_task = {
        "id": _next_id(tasks),
        "date": _parse_date(for_date),
        "title": title,
        "okr_id": okr_id,
        "urgency": urgency or "not_urgent",
        "importance": importance or "not_important",
        "quadrant": quadrant or "Q4",
        "status": "pending",
        "notes": notes,
        "created_at": _today(),
    }
    tasks.append(new_task)
    _save_json("tasks.json", tasks)
    return new_task


def update_task(task_id, **kwargs):
    tasks = _load_json("tasks.json")
    for task in tasks:
        if task["id"] == task_id:
            for key, value in kwargs.items():
                if value is not None:
                    task[key] = value
            _save_json("tasks.json", tasks)
            return task
    return None


def delete_task(task_id):
    tasks = _load_json("tasks.json")
    tasks = [t for t in tasks if t["id"] != task_id]
    _save_json("tasks.json", tasks)
    return True


# ─── 完成记录 ──────────────────────────────────────────────

def completion_list(date=None):
    completions = _load_json("completions.json")
    if date:
        target_date = _parse_date(date)
        return [c for c in completions if c.get("date") == target_date]
    return completions


def add_completion(title, task_id=None, okr_id=None, quadrant=None,
                   source="planned", for_date=None):
    completions = _load_json("completions.json")
    new_completion = {
        "id": _next_id(completions),
        "date": _parse_date(for_date),
        "title": title,
        "task_id": task_id,
        "okr_id": okr_id,
        "quadrant": quadrant,
        "source": source,  # "planned" or "extra"
        "created_at": _today(),
    }
    completions.append(new_completion)
    _save_json("completions.json", completions)

    # 如果关联了 task，标记 task 为 done
    if task_id:
        update_task(task_id, status="done")

    return new_completion


# ─── 周报 ──────────────────────────────────────────────────

def weekly_report(date=None):
    monday, sunday = _get_week_range(date)

    tasks = _load_json("tasks.json")
    completions = _load_json("completions.json")
    okrs = _load_json("okrs.json")

    # 筛选本周数据
    week_tasks = [t for t in tasks if monday <= t.get("date", "") <= sunday]
    week_completions = [c for c in completions if monday <= c.get("date", "") <= sunday]

    planned_completions = [c for c in week_completions if c["source"] == "planned"]
    extra_completions = [c for c in week_completions if c["source"] == "extra"]

    # 每日趋势
    daily_stats = {}
    for i in range(7):
        d = (datetime.strptime(monday, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
        day_tasks = [t for t in week_tasks if t["date"] == d]
        day_completions = [c for c in week_completions if c["date"] == d]
        daily_stats[d] = {
            "planned": len(day_tasks),
            "completed": len(day_completions),
        }

    # 目标关联分析
    okr_stats = {}
    for okr in okrs:
        okr_tasks = [t for t in week_tasks if t.get("okr_id") == okr["id"]]
        okr_completions = [c for c in week_completions if c.get("okr_id") == okr["id"]]
        okr_stats[okr["id"]] = {
            "title": okr["title"],
            "category": okr.get("category", ""),
            "task_count": len(okr_tasks),
            "completion_count": len(okr_completions),
            "completions": [c["title"] for c in okr_completions],
        }

    # 无关联目标的完成事项
    unlinked = [c for c in week_completions if c.get("okr_id") is None]

    # 四象限分布
    quadrant_dist = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for c in week_completions:
        q = c.get("quadrant", "Q4")
        if q in quadrant_dist:
            quadrant_dist[q] += 1

    # 未完成的计划任务
    pending_tasks = [t for t in week_tasks if t.get("status") != "done"]

    total_planned = len(week_tasks)
    total_completed = len(week_completions)
    completion_rate = f"{total_completed / total_planned * 100:.1f}%" if total_planned > 0 else "N/A"

    return {
        "week_range": {"start": monday, "end": sunday},
        "overview": {
            "total_planned": total_planned,
            "total_completed": total_completed,
            "planned_completions": len(planned_completions),
            "extra_completions": len(extra_completions),
            "completion_rate": completion_rate,
        },
        "daily_stats": daily_stats,
        "okr_stats": okr_stats,
        "quadrant_distribution": quadrant_dist,
        "unlinked_completions": [{"title": c["title"], "quadrant": c.get("quadrant")} for c in unlinked],
        "pending_tasks": [{"id": t["id"], "title": t["title"], "quadrant": t.get("quadrant")} for t in pending_tasks],
    }


# ─── 数据状态 ──────────────────────────────────────────────

def data_status():
    okrs = _load_json("okrs.json")
    tasks = _load_json("tasks.json")
    completions = _load_json("completions.json")
    today = _today()
    today_tasks = [t for t in tasks if t["date"] == today]
    today_pending = [t for t in today_tasks if t["status"] != "done"]
    today_completions = [c for c in completions if c["date"] == today]

    return {
        "date": today,
        "okr_count": len(okrs),
        "total_tasks": len(tasks),
        "today_tasks": len(today_tasks),
        "today_pending": len(today_pending),
        "today_completions": len(today_completions),
        "total_completions": len(completions),
    }


# ─── CLI 入口 ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python engine.py <command> [args...]")
        print("Commands: okr-list, okr-add, okr-delete, task-list, task-pending,")
        print("          completion-list, weekly-report, data-status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "okr-list":
        result = okr_list()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "okr-add":
        if len(sys.argv) < 3:
            print("Usage: python engine.py okr-add <title> [description] [category]")
            sys.exit(1)
        title = sys.argv[2]
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        cat = sys.argv[4] if len(sys.argv) > 4 else ""
        result = okr_add(title, desc, cat)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "okr-delete":
        if len(sys.argv) < 3:
            print("Usage: python engine.py okr-delete <id>")
            sys.exit(1)
        okr_delete(int(sys.argv[2]))
        print("OKR deleted")

    elif command == "task-list":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        result = task_list(date)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "task-pending":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        result = task_pending(date)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "completion-list":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        result = completion_list(date)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "weekly-report":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        result = weekly_report(date)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "data-status":
        result = data_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
