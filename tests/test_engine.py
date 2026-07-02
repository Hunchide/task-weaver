import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts" / "engine.py"


class EngineCliTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.env = {"TASKWEAVER_DATA_DIR": self.tmpdir.name}

    def tearDown(self):
        self.tmpdir.cleanup()

    def run_engine(self, *args):
        result = subprocess.run(
            [sys.executable, str(ENGINE), *args],
            cwd=ROOT,
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_cli_adds_and_updates_tasks_and_completions(self):
        okr = self.run_engine("okr-add", "产品能力建设", "打通核心流程", "产品")

        task = self.run_engine(
            "task-add",
            "完成 PRD",
            "--date",
            "2026-07-02",
            "--okr-id",
            str(okr["id"]),
            "--quadrant",
            "Q1",
            "--urgency",
            "urgent",
            "--importance",
            "important",
        )
        self.assertEqual(task["title"], "完成 PRD")
        self.assertEqual(task["status"], "pending")

        updated = self.run_engine("task-update", str(task["id"]), "--quadrant", "Q2")
        self.assertEqual(updated["quadrant"], "Q2")

        completion = self.run_engine(
            "completion-add",
            "完成 PRD",
            "--date",
            "2026-07-02",
            "--task-id",
            str(task["id"]),
            "--okr-id",
            str(okr["id"]),
            "--quadrant",
            "Q2",
            "--source",
            "planned",
        )
        self.assertEqual(completion["source"], "planned")

        tasks = self.run_engine("task-list", "2026-07-02")
        self.assertEqual(tasks[0]["status"], "done")

    def test_cli_updates_okrs(self):
        okr = self.run_engine("okr-add", "旧目标", "旧描述", "旧分类")

        updated = self.run_engine(
            "okr-update",
            str(okr["id"]),
            "--title",
            "新目标",
            "--description",
            "新描述",
            "--category",
            "新分类",
            "--status",
            "done",
        )

        self.assertEqual(updated["title"], "新目标")
        self.assertEqual(updated["description"], "新描述")
        self.assertEqual(updated["category"], "新分类")
        self.assertEqual(updated["status"], "done")

    def test_weekly_report_separates_plan_completion_rate_from_extra_work(self):
        okr = self.run_engine("okr-add", "产品能力建设", "打通核心流程", "产品")
        planned_task = self.run_engine(
            "task-add",
            "完成 PRD",
            "--date",
            "2026-07-02",
            "--okr-id",
            str(okr["id"]),
            "--quadrant",
            "Q1",
        )
        self.run_engine(
            "completion-add",
            "完成 PRD",
            "--date",
            "2026-07-02",
            "--task-id",
            str(planned_task["id"]),
            "--okr-id",
            str(okr["id"]),
            "--quadrant",
            "Q1",
            "--source",
            "planned",
        )
        self.run_engine(
            "completion-add",
            "额外处理线上问题",
            "--date",
            "2026-07-02",
            "--quadrant",
            "Q1",
            "--source",
            "extra",
        )

        report = self.run_engine("weekly-report", "2026-07-02")

        self.assertEqual(report["overview"]["planned_completion_rate"], "100.0%")
        self.assertEqual(report["overview"]["completion_rate"], "100.0%")
        self.assertEqual(report["overview"]["extra_completions"], 1)
        self.assertEqual(report["overview"]["total_completed"], 2)


if __name__ == "__main__":
    unittest.main()
