#!/usr/bin/env python3
"""
Automated test runner for OpenAnonymiser string endpoints.

This script:
1. Starts the API locally with `uv run api.py`
2. Runs comprehensive unit tests for all endpoints
3. Generates a test report
4. Stops the API
5. Builds Docker container and runs tests
6. Creates PR to staging if all tests pass

Usage: python run_tests.py
"""

import subprocess
import time
import sys
import os
import signal
import psutil
from pathlib import Path
import json
from datetime import datetime


class TestRunner:
    def __init__(self):
        self.api_process = None
        self.test_results = {}
        self.start_time = datetime.now()

    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def start_api(self):
        """Start the API locally using uv run api.py."""
        self.log("🚀 Starting API locally...")

        try:
            # Start API in background
            self.api_process = subprocess.Popen(
                ["uv", "run", "api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for API to be ready
            self.log("⏳ Waiting for API to start...")
            max_retries = 30
            for i in range(max_retries):
                try:
                    result = subprocess.run(
                        ["curl", "-s", "http://localhost:8080/api/v1/health"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0 and "pong" in result.stdout:
                        self.log("✅ API is ready!")
                        return True
                except subprocess.TimeoutExpired:
                    pass

                time.sleep(2)
                self.log(f"⏳ Retry {i + 1}/{max_retries}...")

            self.log("❌ API failed to start within timeout", "ERROR")
            return False

        except Exception as e:
            self.log(f"❌ Failed to start API: {e}", "ERROR")
            return False

    def stop_api(self):
        """Stop the API process."""
        if self.api_process:
            self.log("🛑 Stopping API...")
            try:
                # Terminate the process group
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.api_process.pid)],
                        capture_output=True,
                    )
                else:
                    os.killpg(os.getpgid(self.api_process.pid), signal.SIGTERM)

                # Wait for process to terminate
                self.api_process.wait(timeout=10)
                self.log("✅ API stopped")

            except subprocess.TimeoutExpired:
                self.log("⚠️ Force killing API process", "WARNING")
                self.api_process.kill()
            except Exception as e:
                self.log(f"⚠️ Error stopping API: {e}", "WARNING")

    def run_unit_tests(self):
        """Run the pytest test suite."""
        self.log("🧪 Running unit tests...")

        try:
            # Install test dependencies
            self.log("📦 Installing test dependencies...")
            subprocess.run(["uv", "add", "--dev", "pytest", "httpx"], check=True)

            # Run tests with verbose output
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "pytest",
                    "tests/test_string_endpoints.py",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=test_results.json",
                ],
                capture_output=True,
                text=True,
            )

            self.test_results["unit_tests"] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

            if result.returncode == 0:
                self.log("✅ Unit tests passed!")
            else:
                self.log("❌ Unit tests failed!", "ERROR")
                self.log(f"STDOUT: {result.stdout}")
                self.log(f"STDERR: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            self.log(f"❌ Failed to run unit tests: {e}", "ERROR")
            self.test_results["unit_tests"] = {"success": False, "error": str(e)}
            return False

    def build_docker_image(self):
        """Build Docker image for testing."""
        self.log("🐳 Building Docker image...")

        try:
            result = subprocess.run(
                ["docker", "build", "-t", "openanonymiser:test-string-endpoints", "."],
                capture_output=True,
                text=True,
            )

            self.test_results["docker_build"] = {
                "returncode": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                self.log("✅ Docker image built successfully!")
            else:
                self.log("❌ Docker build failed!", "ERROR")
                self.log(f"STDERR: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            self.log(f"❌ Failed to build Docker image: {e}", "ERROR")
            self.test_results["docker_build"] = {"success": False, "error": str(e)}
            return False

    def test_docker_container(self):
        """Test the Docker container."""
        self.log("🐳 Testing Docker container...")

        try:
            # Start container
            self.log("🚀 Starting Docker container...")
            container_start = subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "test-openanonymiser",
                    "-p",
                    "8081:8080",
                    "openanonymiser:test-string-endpoints",
                ],
                capture_output=True,
                text=True,
            )

            if container_start.returncode != 0:
                self.log(
                    f"❌ Failed to start container: {container_start.stderr}", "ERROR"
                )
                return False

            container_id = container_start.stdout.strip()
            self.log(f"📦 Container started: {container_id[:12]}")

            # Wait for container to be ready
            self.log("⏳ Waiting for container to be ready...")
            max_retries = 20
            container_ready = False

            for i in range(max_retries):
                try:
                    result = subprocess.run(
                        ["curl", "-s", "http://localhost:8081/api/v1/health"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0 and "pong" in result.stdout:
                        self.log("✅ Container is ready!")
                        container_ready = True
                        break

                except subprocess.TimeoutExpired:
                    pass

                time.sleep(3)
                self.log(f"⏳ Container retry {i + 1}/{max_retries}...")

            if not container_ready:
                self.log("❌ Container failed to become ready", "ERROR")
                # Get container logs for debugging
                logs = subprocess.run(
                    ["docker", "logs", container_id], capture_output=True, text=True
                )
                self.log(f"Container logs: {logs.stdout}")
                self.log(f"Container errors: {logs.stderr}")
                return False

            # Run basic API tests against container
            self.log("🧪 Testing container endpoints...")
            tests_passed = True

            # Test health endpoint
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8081/api/v1/health"],
                capture_output=True,
                text=True,
            )

            if '{"ping":"pong"}' not in result.stdout:
                self.log("❌ Container health check failed", "ERROR")
                tests_passed = False
            else:
                self.log("✅ Container health check passed")

            # Test analyze endpoint
            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-X",
                    "POST",
                    "http://localhost:8081/api/v1/analyze",
                    "-H",
                    "Content-Type: application/json",
                    "-d",
                    '{"text": "Jan woont in Amsterdam", "language": "nl"}',
                ],
                capture_output=True,
                text=True,
            )

            if '"pii_entities"' in result.stdout and '"text_length"' in result.stdout:
                self.log("✅ Container analyze endpoint passed")
            else:
                self.log("❌ Container analyze endpoint failed", "ERROR")
                self.log(f"Response: {result.stdout}")
                tests_passed = False

            self.test_results["docker_tests"] = {
                "success": tests_passed,
                "container_ready": container_ready,
            }

            return tests_passed

        except Exception as e:
            self.log(f"❌ Docker container test failed: {e}", "ERROR")
            self.test_results["docker_tests"] = {"success": False, "error": str(e)}
            return False

        finally:
            # Always cleanup container
            self.log("🧹 Cleaning up Docker container...")
            subprocess.run(
                ["docker", "stop", "test-openanonymiser"], capture_output=True
            )
            subprocess.run(["docker", "rm", "test-openanonymiser"], capture_output=True)

    def generate_report(self):
        """Generate test report."""
        self.log("📊 Generating test report...")

        end_time = datetime.now()
        duration = end_time - self.start_time

        report = {
            "test_run": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "branch": self.get_current_branch(),
            },
            "results": self.test_results,
            "summary": {
                "all_tests_passed": all(
                    result.get("success", False)
                    for result in self.test_results.values()
                ),
                "total_tests": len(self.test_results),
            },
        }

        # Write JSON report
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Write human-readable report
        with open("test_report.md", "w") as f:
            f.write(self.format_markdown_report(report))

        self.print_summary(report)
        return report["summary"]["all_tests_passed"]

    def get_current_branch(self):
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"

    def format_markdown_report(self, report):
        """Format report as markdown."""
        summary = report["summary"]
        results = report["results"]

        md = f"""# OpenAnonymiser String Endpoints Test Report

## Summary
- **Status**: {"✅ PASSED" if summary["all_tests_passed"] else "❌ FAILED"}
- **Duration**: {report["test_run"]["duration_seconds"]:.1f} seconds
- **Branch**: {report["test_run"]["branch"]}
- **Timestamp**: {report["test_run"]["end_time"]}

## Test Results

"""

        for test_name, result in results.items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            md += f"### {test_name.replace('_', ' ').title()}\n"
            md += f"**Status**: {status}\n\n"

            if not result.get("success", False) and "error" in result:
                md += f"**Error**: {result['error']}\n\n"

        md += "## Next Steps\n\n"
        if summary["all_tests_passed"]:
            md += "🚀 All tests passed! Ready for deployment to staging.\n\n"
            md += "Run: `git push origin feature/string-endpoints` to create PR\n"
        else:
            md += "❌ Tests failed. Please fix issues before deployment.\n"

        return md

    def print_summary(self, report):
        """Print test summary to console."""
        self.log("=" * 60)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 60)

        summary = report["summary"]
        results = report["results"]

        self.log(
            f"Overall Status: {'✅ PASSED' if summary['all_tests_passed'] else '❌ FAILED'}"
        )
        self.log(f"Duration: {report['test_run']['duration_seconds']:.1f} seconds")
        self.log(f"Branch: {report['test_run']['branch']}")

        self.log("\nDetailed Results:")
        for test_name, result in results.items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            self.log(f"  {test_name}: {status}")

        self.log("=" * 60)

        if summary["all_tests_passed"]:
            self.log("🎉 All tests passed! Ready for staging deployment.")
            self.log("Next: Create PR with 'git push origin feature/string-endpoints'")
        else:
            self.log("⚠️ Some tests failed. Please review and fix issues.")

    def auto_tag_dev_if_ready(self):
        """Auto-tag successful test runs as 'dev' when not on main branch."""
        if not self.test_results or not all(
            r.get("success", False) for r in self.test_results.values()
        ):
            self.log("⚠️ Not tagging - tests failed", "WARNING")
            return False

        # Get current branch
        current_branch = self.get_current_branch()
        
        if current_branch == "main":
            self.log("📝 On main branch - skipping dev tag (use version tags instead)")
            return True
            
        if current_branch == "unknown":
            self.log("⚠️ Unknown branch - skipping dev tag", "WARNING")
            return False

        self.log(f"🏷️ All tests passed on branch '{current_branch}' - creating dev tag...")
        
        try:
            # Create dev tag (force update if exists)
            result = subprocess.run([
                "git", "tag", "-f", "dev", "-m", 
                f"Auto-tagged dev from {current_branch} - tests passed"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Dev tag created locally")
                
                # Push dev tag to remote (force update)
                push_result = subprocess.run([
                    "git", "push", "origin", "dev", "--force"
                ], capture_output=True, text=True)
                
                if push_result.returncode == 0:
                    self.log("🚀 Dev tag pushed to remote - ready for deployment!")
                    self.log("💡 Deploy with: kubectl set image deployment/openanonymiser openanonymiser=mwest2020/openanonymiser:dev")
                else:
                    self.log(f"⚠️ Failed to push dev tag: {push_result.stderr}", "WARNING")
            else:
                self.log(f"❌ Failed to create dev tag: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error during dev tagging: {e}", "ERROR")
            return False
        
        return True

    def create_pr_if_ready(self):
        """Create PR to staging if all tests pass."""
        if not self.test_results or not all(
            r.get("success", False) for r in self.test_results.values()
        ):
            self.log("⚠️ Not creating PR - tests failed", "WARNING")
            return False

        self.log("🚀 All tests passed! Ready for PR...")
        self.log(
            "Manual step: Run 'git push origin feature/string-endpoints' to create PR"
        )
        self.log("Then create PR from feature/string-endpoints to staging/development")
        return True

    def run_all_tests(self):
        """Run the complete test suite."""
        try:
            self.log("🎯 Starting complete test suite...")

            # Step 1: Start API locally and run unit tests
            if not self.start_api():
                return False

            try:
                if not self.run_unit_tests():
                    return False
            finally:
                self.stop_api()

            # Step 2: Build and test Docker container
            if not self.build_docker_image():
                return False

            if not self.test_docker_container():
                return False

            # Step 3: Generate report
            all_passed = self.generate_report()

            # Step 4: Auto-tag as dev if ready (non-main branches)
            if all_passed:
                self.auto_tag_dev_if_ready()
                self.create_pr_if_ready()

            return all_passed

        except KeyboardInterrupt:
            self.log("⚠️ Test run interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"❌ Test run failed: {e}", "ERROR")
            return False
        finally:
            # Cleanup
            self.stop_api()


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
