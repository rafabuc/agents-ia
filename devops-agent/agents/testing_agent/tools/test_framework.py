"""
Test Framework Tool for Testing Agent
"""

import os
import json
import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from pathlib import Path

from ...base.tools import BaseDevOpsTool


class TestFrameworkTool(BaseDevOpsTool):
    """Tool for executing tests with various frameworks"""

    name: str = "test_framework"
    description: str = "Execute tests using pytest, Jest, and other testing frameworks"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute test framework operations"""
        self.log_execution("test_framework", {"action": action, "kwargs": kwargs})

        try:
            if action == "run_pytest":
                return self._run_pytest_tests(
                    kwargs.get("test_path", "tests/"),
                    kwargs.get("options", [])
                )
            elif action == "run_jest":
                return self._run_jest_tests(
                    kwargs.get("test_pattern", "**/*.test.js"),
                    kwargs.get("options", [])
                )
            elif action == "run_unittest":
                return self._run_unittest_tests(kwargs.get("test_module"))
            elif action == "generate_test":
                return self._generate_test_template(
                    kwargs.get("test_type"),
                    kwargs.get("target_file")
                )
            elif action == "validate_tests":
                return self._validate_test_structure(kwargs.get("test_directory"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_pytest_tests(self, test_path: str, options: List[str]) -> Dict[str, Any]:
        """Run pytest tests with comprehensive reporting"""
        try:
            # Build pytest command
            cmd = ["pytest", test_path]

            # Add standard options for comprehensive reporting
            cmd.extend([
                "--verbose",
                "--tb=short",
                "--junit-xml=test-results.xml",
                "--html=test-report.html",
                "--self-contained-html",
                "--cov=.",
                "--cov-report=xml",
                "--cov-report=html",
                "--cov-report=term"
            ])

            # Add custom options
            cmd.extend(options)

            # Execute pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )

            # Parse test results
            test_results = self._parse_pytest_results(result)

            # Parse JUnit XML if available
            junit_results = self._parse_junit_xml("test-results.xml")
            if junit_results:
                test_results.update(junit_results)

            return {
                "success": result.returncode == 0,
                "framework": "pytest",
                "test_results": test_results,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "pytest execution timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "pytest not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_jest_tests(self, test_pattern: str, options: List[str]) -> Dict[str, Any]:
        """Run Jest tests for JavaScript/TypeScript projects"""
        try:
            # Build Jest command
            cmd = ["npx", "jest", test_pattern]

            # Add standard options
            cmd.extend([
                "--verbose",
                "--coverage",
                "--coverageReporters=text",
                "--coverageReporters=lcov",
                "--coverageReporters=html",
                "--testResultsProcessor=jest-junit"
            ])

            # Add custom options
            cmd.extend(options)

            # Set environment variables for Jest
            env = os.environ.copy()
            env["JEST_JUNIT_OUTPUT_DIR"] = "./test-results"
            env["JEST_JUNIT_OUTPUT_NAME"] = "jest-results.xml"

            # Execute Jest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=1800
            )

            # Parse Jest output
            jest_results = self._parse_jest_output(result.stdout)

            # Parse coverage information
            coverage_info = self._parse_jest_coverage(result.stdout)
            if coverage_info:
                jest_results["coverage"] = coverage_info

            return {
                "success": result.returncode == 0,
                "framework": "jest",
                "test_results": jest_results,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Jest execution timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "Jest/npm not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_unittest_tests(self, test_module: str) -> Dict[str, Any]:
        """Run Python unittest tests"""
        try:
            if not test_module:
                # Discover tests automatically
                cmd = ["python", "-m", "unittest", "discover", "-v"]
            else:
                cmd = ["python", "-m", "unittest", test_module, "-v"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800
            )

            # Parse unittest output
            unittest_results = self._parse_unittest_output(result.stderr)

            return {
                "success": result.returncode == 0,
                "framework": "unittest",
                "test_results": unittest_results,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "unittest execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_pytest_results(self, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """Parse pytest output to extract test results"""
        output = result.stdout + result.stderr

        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "execution_time": 0,
            "failures": []
        }

        try:
            # Extract test counts from pytest summary
            lines = output.split('\n')
            for line in lines:
                if "passed" in line and ("failed" in line or "error" in line or "skipped" in line):
                    # Parse summary line like "5 passed, 2 failed, 1 skipped in 10.25s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            test_results["passed"] = int(parts[i-1])
                        elif part == "failed" and i > 0:
                            test_results["failed"] = int(parts[i-1])
                        elif part == "skipped" and i > 0:
                            test_results["skipped"] = int(parts[i-1])
                        elif part == "error" and i > 0:
                            test_results["errors"] = int(parts[i-1])
                        elif "in" in part and i < len(parts) - 1 and "s" in parts[i+1]:
                            try:
                                test_results["execution_time"] = float(parts[i+1].replace('s', ''))
                            except ValueError:
                                pass

            test_results["total_tests"] = (
                test_results["passed"] +
                test_results["failed"] +
                test_results["skipped"] +
                test_results["errors"]
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse pytest results: {str(e)}")

        return test_results

    def _parse_junit_xml(self, xml_file: str) -> Dict[str, Any]:
        """Parse JUnit XML results"""
        try:
            if not os.path.exists(xml_file):
                return {}

            tree = ET.parse(xml_file)
            root = tree.getroot()

            results = {
                "junit_results": {
                    "test_suites": [],
                    "total_tests": int(root.attrib.get("tests", 0)),
                    "total_failures": int(root.attrib.get("failures", 0)),
                    "total_errors": int(root.attrib.get("errors", 0)),
                    "total_skipped": int(root.attrib.get("skipped", 0)),
                    "execution_time": float(root.attrib.get("time", 0))
                }
            }

            # Parse test suites
            for testsuite in root.findall("testsuite"):
                suite_info = {
                    "name": testsuite.attrib.get("name", ""),
                    "tests": int(testsuite.attrib.get("tests", 0)),
                    "failures": int(testsuite.attrib.get("failures", 0)),
                    "errors": int(testsuite.attrib.get("errors", 0)),
                    "skipped": int(testsuite.attrib.get("skipped", 0)),
                    "time": float(testsuite.attrib.get("time", 0)),
                    "test_cases": []
                }

                # Parse individual test cases
                for testcase in testsuite.findall("testcase"):
                    case_info = {
                        "name": testcase.attrib.get("name", ""),
                        "classname": testcase.attrib.get("classname", ""),
                        "time": float(testcase.attrib.get("time", 0)),
                        "status": "passed"
                    }

                    # Check for failures/errors
                    if testcase.find("failure") is not None:
                        case_info["status"] = "failed"
                        case_info["failure_message"] = testcase.find("failure").text
                    elif testcase.find("error") is not None:
                        case_info["status"] = "error"
                        case_info["error_message"] = testcase.find("error").text
                    elif testcase.find("skipped") is not None:
                        case_info["status"] = "skipped"

                    suite_info["test_cases"].append(case_info)

                results["junit_results"]["test_suites"].append(suite_info)

            return results

        except Exception as e:
            self.logger.warning(f"Failed to parse JUnit XML: {str(e)}")
            return {}

    def _parse_jest_output(self, output: str) -> Dict[str, Any]:
        """Parse Jest test output"""
        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_suites": 0,
            "execution_time": 0
        }

        try:
            lines = output.split('\n')
            for line in lines:
                if "Tests:" in line:
                    # Parse line like "Tests: 5 passed, 2 failed, 7 total"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed," and i > 0:
                            test_results["passed"] = int(parts[i-1])
                        elif part == "failed," and i > 0:
                            test_results["failed"] = int(parts[i-1])
                        elif part == "total" and i > 0:
                            test_results["total_tests"] = int(parts[i-1])
                elif "Test Suites:" in line:
                    # Parse test suites summary
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "total" and i > 0:
                            test_results["test_suites"] = int(parts[i-1])
                elif "Time:" in line:
                    # Parse execution time
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "Time:" and i < len(parts) - 1:
                            try:
                                time_str = parts[i+1].replace('s', '')
                                test_results["execution_time"] = float(time_str)
                            except ValueError:
                                pass

        except Exception as e:
            self.logger.warning(f"Failed to parse Jest output: {str(e)}")

        return test_results

    def _parse_jest_coverage(self, output: str) -> Dict[str, Any]:
        """Parse Jest coverage information"""
        coverage_info = {}

        try:
            lines = output.split('\n')
            in_coverage_section = False

            for line in lines:
                if "Coverage summary" in line or "% Lines" in line:
                    in_coverage_section = True
                    continue

                if in_coverage_section and "%" in line:
                    # Parse coverage lines
                    parts = line.split()
                    if len(parts) >= 4:
                        # Try to extract coverage percentages
                        for part in parts:
                            if "%" in part:
                                try:
                                    percentage = float(part.replace('%', ''))
                                    if "Functions" in line:
                                        coverage_info["functions"] = percentage
                                    elif "Lines" in line:
                                        coverage_info["lines"] = percentage
                                    elif "Statements" in line:
                                        coverage_info["statements"] = percentage
                                    elif "Branches" in line:
                                        coverage_info["branches"] = percentage
                                    break
                                except ValueError:
                                    continue

        except Exception as e:
            self.logger.warning(f"Failed to parse Jest coverage: {str(e)}")

        return coverage_info

    def _parse_unittest_output(self, output: str) -> Dict[str, Any]:
        """Parse unittest output"""
        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0
        }

        try:
            lines = output.split('\n')
            for line in lines:
                if line.startswith("Ran ") and " test" in line:
                    # Parse line like "Ran 10 tests in 0.123s"
                    parts = line.split()
                    if len(parts) >= 2:
                        test_results["total_tests"] = int(parts[1])

                if "FAILED (failures=" in line or "FAILED (errors=" in line:
                    # Parse failure summary
                    failure_part = line.split("FAILED (")[1].split(")")[0]
                    for item in failure_part.split(", "):
                        if "failures=" in item:
                            test_results["failed"] = int(item.split("=")[1])
                        elif "errors=" in item:
                            test_results["errors"] = int(item.split("=")[1])
                        elif "skipped=" in item:
                            test_results["skipped"] = int(item.split("=")[1])

                if line == "OK":
                    test_results["passed"] = test_results["total_tests"]

        except Exception as e:
            self.logger.warning(f"Failed to parse unittest output: {str(e)}")

        # Calculate passed tests if not explicitly failed
        if test_results["passed"] == 0 and test_results["total_tests"] > 0:
            test_results["passed"] = (
                test_results["total_tests"] -
                test_results["failed"] -
                test_results["errors"] -
                test_results["skipped"]
            )

        return test_results

    def _generate_test_template(self, test_type: str, target_file: str) -> Dict[str, Any]:
        """Generate test template for given file"""
        try:
            if not target_file:
                return {"success": False, "error": "Target file is required"}

            target_path = Path(target_file)
            test_file = f"test_{target_path.stem}.py"

            if test_type == "unit":
                template = self._get_unit_test_template(target_path.stem)
            elif test_type == "integration":
                template = self._get_integration_test_template(target_path.stem)
            elif test_type == "functional":
                template = self._get_functional_test_template(target_path.stem)
            else:
                return {"success": False, "error": f"Unknown test type: {test_type}"}

            # Write test file
            test_path = Path("tests") / test_file
            test_path.parent.mkdir(parents=True, exist_ok=True)

            with open(test_path, 'w') as f:
                f.write(template)

            return {
                "success": True,
                "test_file": str(test_path),
                "test_type": test_type,
                "target_file": target_file,
                "message": f"Generated {test_type} test template for {target_file}"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_unit_test_template(self, module_name: str) -> str:
        """Get unit test template"""
        return f'''"""
Unit tests for {module_name} module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest

from {module_name} import *  # Import your module here


class Test{module_name.title()}(unittest.TestCase):
    """Unit tests for {module_name} module"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    def tearDown(self):
        """Clean up after each test method."""
        pass

    def test_example_function(self):
        """Test example function with valid input."""
        # Arrange
        expected_result = "expected_value"

        # Act
        # result = example_function("input")

        # Assert
        # self.assertEqual(result, expected_result)
        pass

    def test_example_function_invalid_input(self):
        """Test example function with invalid input."""
        # Arrange & Act & Assert
        with self.assertRaises(ValueError):
            pass  # example_function(None)

    @patch('{module_name}.external_dependency')
    def test_example_function_with_mock(self, mock_dependency):
        """Test example function with mocked dependency."""
        # Arrange
        mock_dependency.return_value = "mocked_value"

        # Act
        # result = example_function_with_dependency()

        # Assert
        # mock_dependency.assert_called_once()
        # self.assertEqual(result, "expected_result")
        pass


if __name__ == '__main__':
    unittest.main()
'''

    def _get_integration_test_template(self, module_name: str) -> str:
        """Get integration test template"""
        return f'''"""
Integration tests for {module_name} module
"""

import unittest
import pytest
import tempfile
import os

from {module_name} import *  # Import your module here


class Test{module_name.title()}Integration(unittest.TestCase):
    """Integration tests for {module_name} module"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class."""
        pass

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_workflow(self):
        """Test complete workflow from start to finish."""
        # Test the complete integration workflow
        pass

    def test_database_integration(self):
        """Test database integration functionality."""
        # Test database operations
        pass

    def test_external_api_integration(self):
        """Test external API integration."""
        # Test API interactions
        pass


if __name__ == '__main__':
    unittest.main()
'''

    def _get_functional_test_template(self, module_name: str) -> str:
        """Get functional test template"""
        return f'''"""
Functional tests for {module_name} module
"""

import unittest
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Test{module_name.title()}Functional(unittest.TestCase):
    """Functional tests for {module_name} application"""

    @classmethod
    def setUpClass(cls):
        """Set up WebDriver for all tests."""
        # cls.driver = webdriver.Chrome()  # Uncomment and configure
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up WebDriver after all tests."""
        # cls.driver.quit()  # Uncomment when using WebDriver
        pass

    def setUp(self):
        """Set up before each test."""
        pass

    def test_user_login_workflow(self):
        """Test user login functionality."""
        # Test user login process
        pass

    def test_user_registration_workflow(self):
        """Test user registration functionality."""
        # Test user registration process
        pass

    def test_application_navigation(self):
        """Test application navigation."""
        # Test navigation between pages
        pass


if __name__ == '__main__':
    unittest.main()
'''

    def _validate_test_structure(self, test_directory: str) -> Dict[str, Any]:
        """Validate test directory structure and conventions"""
        try:
            test_path = Path(test_directory)
            if not test_path.exists():
                return {"success": False, "error": f"Test directory '{test_directory}' does not exist"}

            validation_results = {
                "directory": test_directory,
                "test_files_found": [],
                "structure_issues": [],
                "naming_issues": [],
                "import_issues": [],
                "recommendations": []
            }

            # Find all test files
            test_files = list(test_path.rglob("test_*.py")) + list(test_path.rglob("*_test.py"))
            validation_results["test_files_found"] = [str(f) for f in test_files]

            # Validate each test file
            for test_file in test_files:
                self._validate_single_test_file(test_file, validation_results)

            # Generate recommendations
            if not validation_results["test_files_found"]:
                validation_results["recommendations"].append("No test files found. Consider adding tests.")

            if validation_results["naming_issues"]:
                validation_results["recommendations"].append("Fix test file naming conventions.")

            if validation_results["structure_issues"]:
                validation_results["recommendations"].append("Improve test structure and organization.")

            return {
                "success": True,
                "validation_results": validation_results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_single_test_file(self, test_file: Path, results: Dict[str, Any]) -> None:
        """Validate a single test file"""
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check naming conventions
            if not (test_file.name.startswith('test_') or test_file.name.endswith('_test.py')):
                results["naming_issues"].append(f"File {test_file.name} doesn't follow naming convention")

            # Check for basic test structure
            if 'def test_' not in content and 'class Test' not in content:
                results["structure_issues"].append(f"File {test_file.name} doesn't contain test functions or classes")

            # Check for imports
            if 'import unittest' not in content and 'import pytest' not in content:
                results["import_issues"].append(f"File {test_file.name} doesn't import a testing framework")

        except Exception as e:
            results["structure_issues"].append(f"Could not validate {test_file.name}: {str(e)}")