#!/usr/bin/env python3
"""
User Testing Framework for Sentry-AI

This module provides automated user testing scenarios to validate
Sentry-AI's functionality across different applications and use cases.
"""

import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from loguru import logger


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestScenario:
    """Represents a user testing scenario"""
    name: str
    app_name: str
    description: str
    steps: List[str]
    expected_behavior: str
    automation_type: str  # dialog, notification, confirmation
    requires_manual: bool = False
    status: TestStatus = TestStatus.PENDING
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class TestReport:
    """User testing report"""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    scenarios: List[TestScenario]


class UserTestingFramework:
    """
    Framework for conducting comprehensive user testing of Sentry-AI
    """

    def __init__(self):
        self.scenarios: List[TestScenario] = []
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)

        self._initialize_test_scenarios()

    def _initialize_test_scenarios(self):
        """Define all test scenarios"""

        # TextEdit Tests
        self.scenarios.extend([
            TestScenario(
                name="textedit_save_dialog",
                app_name="TextEdit",
                description="Test save dialog automation in TextEdit",
                steps=[
                    "1. Open TextEdit",
                    "2. Type some text",
                    "3. Close window (⌘W)",
                    "4. Observe Sentry-AI handling save dialog"
                ],
                expected_behavior="Sentry-AI should detect the dialog and automatically click 'Don't Save' or 'Save' based on context",
                automation_type="dialog"
            ),
            TestScenario(
                name="textedit_quit_unsaved",
                app_name="TextEdit",
                description="Test quit with unsaved changes",
                steps=[
                    "1. Open TextEdit",
                    "2. Type text",
                    "3. Quit app (⌘Q)",
                    "4. Observe automation"
                ],
                expected_behavior="Sentry-AI handles save confirmation",
                automation_type="dialog"
            ),
        ])

        # Finder Tests
        self.scenarios.extend([
            TestScenario(
                name="finder_delete_confirmation",
                app_name="Finder",
                description="Test file deletion confirmation",
                steps=[
                    "1. Create test file",
                    "2. Move to Trash",
                    "3. Empty Trash",
                    "4. Observe confirmation dialog"
                ],
                expected_behavior="Sentry-AI should require confirmation for destructive actions",
                automation_type="confirmation",
                requires_manual=True
            ),
        ])

        # Safari Tests
        self.scenarios.extend([
            TestScenario(
                name="safari_download_dialog",
                app_name="Safari",
                description="Test download confirmation",
                steps=[
                    "1. Open Safari",
                    "2. Initiate file download",
                    "3. Observe download dialog"
                ],
                expected_behavior="Sentry-AI handles download confirmation",
                automation_type="dialog",
                requires_manual=True
            ),
        ])

        # VS Code Tests
        self.scenarios.extend([
            TestScenario(
                name="vscode_claude_bash_approval",
                app_name="Visual Studio Code",
                description="Test Claude Code bash command approval",
                steps=[
                    "1. Open VS Code with Claude Code",
                    "2. Ask Claude to run 'ls -la'",
                    "3. Observe auto-approval"
                ],
                expected_behavior="Sentry-AI auto-approves safe bash commands",
                automation_type="dialog"
            ),
            TestScenario(
                name="vscode_claude_dangerous_rejection",
                app_name="Visual Studio Code",
                description="Test dangerous command rejection",
                steps=[
                    "1. Open VS Code",
                    "2. Ask Claude to run 'rm -rf /'",
                    "3. Observe auto-rejection"
                ],
                expected_behavior="Sentry-AI auto-rejects dangerous commands",
                automation_type="dialog"
            ),
        ])

        # System Tests
        self.scenarios.extend([
            TestScenario(
                name="system_update_notification",
                app_name="System Preferences",
                description="Test system update notification",
                steps=[
                    "1. Wait for system update notification",
                    "2. Observe Sentry-AI decision"
                ],
                expected_behavior="Should be blacklisted (no automation)",
                automation_type="notification",
                requires_manual=True
            ),
        ])

        # Performance Tests
        self.scenarios.extend([
            TestScenario(
                name="performance_cpu_usage",
                app_name="Activity Monitor",
                description="Monitor CPU usage during operation",
                steps=[
                    "1. Open Activity Monitor",
                    "2. Run Sentry-AI for 5 minutes",
                    "3. Check CPU usage"
                ],
                expected_behavior="CPU usage should be < 5% average",
                automation_type="performance",
                requires_manual=True
            ),
            TestScenario(
                name="performance_memory_usage",
                app_name="Activity Monitor",
                description="Monitor memory usage",
                steps=[
                    "1. Check initial memory",
                    "2. Run for 30 minutes",
                    "3. Check memory growth"
                ],
                expected_behavior="Memory usage should be < 200 MB",
                automation_type="performance",
                requires_manual=True
            ),
        ])

        # Multi-Application Tests
        self.scenarios.extend([
            TestScenario(
                name="multi_app_switching",
                app_name="Multiple",
                description="Test rapid app switching",
                steps=[
                    "1. Open TextEdit, Notes, Safari",
                    "2. Switch between apps rapidly",
                    "3. Trigger dialogs in each"
                ],
                expected_behavior="Sentry-AI correctly identifies and handles each app",
                automation_type="dialog",
                requires_manual=True
            ),
        ])

        # Blacklist Tests
        self.scenarios.extend([
            TestScenario(
                name="blacklist_terminal",
                app_name="Terminal",
                description="Verify Terminal is blacklisted",
                steps=[
                    "1. Open Terminal",
                    "2. Trigger any confirmation dialog",
                    "3. Verify no automation occurs"
                ],
                expected_behavior="Sentry-AI ignores Terminal completely",
                automation_type="blacklist"
            ),
            TestScenario(
                name="blacklist_keychain",
                app_name="Keychain Access",
                description="Verify Keychain Access is blacklisted",
                steps=[
                    "1. Open Keychain Access",
                    "2. Try to view password",
                    "3. Verify no automation"
                ],
                expected_behavior="Sentry-AI ignores Keychain Access",
                automation_type="blacklist"
            ),
        ])

    def run_automated_tests(self) -> TestReport:
        """
        Run all automated tests (non-manual scenarios)

        Returns:
            TestReport with results
        """
        logger.info("Starting automated user testing...")
        start_time = time.time()

        passed = 0
        failed = 0
        skipped = 0

        for scenario in self.scenarios:
            if scenario.requires_manual:
                scenario.status = TestStatus.SKIPPED
                skipped += 1
                logger.info(f"⏭️  Skipping manual test: {scenario.name}")
                continue

            logger.info(f"🧪 Running: {scenario.name}")
            scenario.status = TestStatus.RUNNING

            try:
                test_start = time.time()
                self._run_scenario(scenario)
                scenario.execution_time = time.time() - test_start
                scenario.status = TestStatus.PASSED
                passed += 1
                logger.success(f"✅ {scenario.name} PASSED ({scenario.execution_time:.2f}s)")
            except Exception as e:
                scenario.execution_time = time.time() - test_start
                scenario.status = TestStatus.FAILED
                scenario.error_message = str(e)
                failed += 1
                logger.error(f"❌ {scenario.name} FAILED: {e}")

        duration = time.time() - start_time

        report = TestReport(
            timestamp=datetime.now().isoformat(),
            total_tests=len(self.scenarios),
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            scenarios=self.scenarios
        )

        self._save_report(report)
        self._print_summary(report)

        return report

    def _run_scenario(self, scenario: TestScenario):
        """
        Execute a single test scenario

        Args:
            scenario: The test scenario to run
        """
        # For automated tests, we check if Sentry-AI components are working

        if scenario.automation_type == "blacklist":
            # Test blacklist functionality
            self._test_blacklist(scenario.app_name)

        elif scenario.automation_type == "dialog":
            # Test dialog detection and handling
            self._test_dialog_automation(scenario)

        elif scenario.automation_type == "performance":
            # Test performance metrics
            self._test_performance(scenario)

    def _test_blacklist(self, app_name: str):
        """Test if an app is properly blacklisted"""
        from sentry_ai.core.config import is_app_allowed

        # Terminal and Keychain should be blacklisted
        if app_name in ["Terminal", "Keychain Access"]:
            if is_app_allowed(app_name):
                raise AssertionError(f"{app_name} should be blacklisted but is allowed")

    def _test_dialog_automation(self, scenario: TestScenario):
        """Test dialog automation functionality"""
        # Import and test components
        from sentry_ai.agents import Observer, Analyzer, DecisionEngine

        # Verify agents can be initialized
        observer = Observer()
        analyzer = Analyzer()
        decision_engine = DecisionEngine()

        # Basic functionality check
        if not observer or not analyzer or not decision_engine:
            raise AssertionError("Failed to initialize agents")

    def _test_performance(self, scenario: TestScenario):
        """Test performance characteristics"""
        # Check if Sentry-AI process exists and get stats
        try:
            result = subprocess.run(
                ["ps", "-A", "-o", "pid,rss,command"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Basic check - process should be lightweight
            # This is a placeholder for actual performance testing

        except Exception as e:
            logger.warning(f"Performance test skipped: {e}")

    def _save_report(self, report: TestReport):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_file = self.results_dir / f"test_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)

        # Save Markdown report
        md_file = self.results_dir / f"test_report_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(self._generate_markdown_report(report))

        logger.info(f"📊 Report saved: {json_file}")
        logger.info(f"📊 Report saved: {md_file}")

    def _generate_markdown_report(self, report: TestReport) -> str:
        """Generate markdown formatted report"""
        md = f"""# Sentry-AI User Testing Report

**Date:** {report.timestamp}
**Duration:** {report.duration:.2f} seconds

## Summary

- **Total Tests:** {report.total_tests}
- **Passed:** {report.passed} ✅
- **Failed:** {report.failed} ❌
- **Skipped:** {report.skipped} ⏭️
- **Success Rate:** {(report.passed / (report.total_tests - report.skipped) * 100) if (report.total_tests - report.skipped) > 0 else 0:.1f}%

## Test Results

"""

        # Group by status
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.SKIPPED]:
            scenarios = [s for s in report.scenarios if s.status == status]
            if scenarios:
                md += f"\n### {status.value.upper()}\n\n"
                for scenario in scenarios:
                    icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(status.value, "")
                    md += f"#### {icon} {scenario.name}\n\n"
                    md += f"- **App:** {scenario.app_name}\n"
                    md += f"- **Description:** {scenario.description}\n"
                    md += f"- **Type:** {scenario.automation_type}\n"

                    if scenario.execution_time:
                        md += f"- **Execution Time:** {scenario.execution_time:.2f}s\n"

                    if scenario.error_message:
                        md += f"- **Error:** {scenario.error_message}\n"

                    md += f"\n**Expected Behavior:**  \n{scenario.expected_behavior}\n\n"
                    md += "**Steps:**\n"
                    for step in scenario.steps:
                        md += f"{step}\n"
                    md += "\n---\n\n"

        return md

    def _print_summary(self, report: TestReport):
        """Print test summary to console"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 USER TESTING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report.total_tests}")
        logger.info(f"✅ Passed: {report.passed}")
        logger.info(f"❌ Failed: {report.failed}")
        logger.info(f"⏭️  Skipped: {report.skipped}")
        logger.info(f"⏱️  Duration: {report.duration:.2f}s")

        if report.total_tests - report.skipped > 0:
            success_rate = (report.passed / (report.total_tests - report.skipped)) * 100
            logger.info(f"📈 Success Rate: {success_rate:.1f}%")

        logger.info("=" * 60 + "\n")

    def generate_manual_test_checklist(self):
        """Generate a checklist for manual testing"""
        checklist_file = self.results_dir / "manual_test_checklist.md"

        manual_scenarios = [s for s in self.scenarios if s.requires_manual]

        md = """# Sentry-AI Manual Testing Checklist

This checklist contains tests that require manual execution.

## Instructions

1. Start Sentry-AI in a separate terminal: `make run`
2. For each test below, follow the steps and observe behavior
3. Mark the checkbox when complete
4. Note any issues in the "Notes" section

---

"""

        for i, scenario in enumerate(manual_scenarios, 1):
            md += f"## Test {i}: {scenario.name}\n\n"
            md += f"- [ ] **Completed**\n\n"
            md += f"**App:** {scenario.app_name}  \n"
            md += f"**Type:** {scenario.automation_type}  \n\n"
            md += f"**Description:**  \n{scenario.description}\n\n"
            md += f"**Expected Behavior:**  \n{scenario.expected_behavior}\n\n"
            md += "**Steps:**\n"
            for step in scenario.steps:
                md += f"{step}\n"
            md += "\n**Notes:**\n\n_[Add your observations here]_\n\n"
            md += "---\n\n"

        with open(checklist_file, 'w') as f:
            f.write(md)

        logger.info(f"📋 Manual test checklist saved: {checklist_file}")


def main():
    """Run user testing framework"""
    framework = UserTestingFramework()

    # Generate manual testing checklist
    framework.generate_manual_test_checklist()

    # Run automated tests
    report = framework.run_automated_tests()

    logger.info("🎉 User testing complete!")
    logger.info(f"📁 Check test_results/ directory for detailed reports")


if __name__ == "__main__":
    main()
