"""
Coverage Analyzer Tool for Testing Agent
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from pathlib import Path
import subprocess

from ...base.tools import BaseDevOpsTool


class CoverageAnalyzer(BaseDevOpsTool):
    """Tool for analyzing test coverage"""

    name: str = "coverage_analyzer"
    description: str = "Analyze code coverage from various testing frameworks"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute coverage analysis operations"""
        self.log_execution("coverage_analyzer", {"action": action, "kwargs": kwargs})

        try:
            if action == "analyze_coverage":
                return self._analyze_coverage_data(
                    kwargs.get("coverage_file"),
                    kwargs.get("format", "xml")
                )
            elif action == "generate_coverage":
                return self._generate_coverage_report(
                    kwargs.get("source_path", "."),
                    kwargs.get("test_path", "tests/")
                )
            elif action == "compare_coverage":
                return self._compare_coverage_reports(
                    kwargs.get("baseline_file"),
                    kwargs.get("current_file")
                )
            elif action == "identify_gaps":
                return self._identify_coverage_gaps(
                    kwargs.get("coverage_data"),
                    kwargs.get("threshold", 80)
                )
            elif action == "coverage_trends":
                return self._analyze_coverage_trends(
                    kwargs.get("historical_data", [])
                )
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_coverage_data(self, coverage_file: str, format_type: str) -> Dict[str, Any]:
        """Analyze coverage data from file"""
        try:
            if not coverage_file or not os.path.exists(coverage_file):
                return {"success": False, "error": "Coverage file not found"}

            if format_type == "xml":
                return self._analyze_xml_coverage(coverage_file)
            elif format_type == "json":
                return self._analyze_json_coverage(coverage_file)
            elif format_type == "lcov":
                return self._analyze_lcov_coverage(coverage_file)
            else:
                return {"success": False, "error": f"Unsupported coverage format: {format_type}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_xml_coverage(self, coverage_file: str) -> Dict[str, Any]:
        """Analyze XML coverage report (coverage.xml)"""
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            coverage_data = {
                "overall_coverage": 0.0,
                "line_coverage": 0.0,
                "branch_coverage": 0.0,
                "function_coverage": 0.0,
                "files": [],
                "summary": {
                    "total_lines": 0,
                    "covered_lines": 0,
                    "total_branches": 0,
                    "covered_branches": 0,
                    "total_functions": 0,
                    "covered_functions": 0
                }
            }

            # Parse overall coverage (line-rate attribute in root)
            line_rate = float(root.attrib.get("line-rate", "0"))
            branch_rate = float(root.attrib.get("branch-rate", "0"))

            coverage_data["line_coverage"] = line_rate * 100
            coverage_data["branch_coverage"] = branch_rate * 100
            coverage_data["overall_coverage"] = coverage_data["line_coverage"]

            # Parse packages and classes
            for package in root.findall(".//package"):
                package_name = package.attrib.get("name", "")

                for class_elem in package.findall(".//class"):
                    filename = class_elem.attrib.get("filename", "")
                    class_line_rate = float(class_elem.attrib.get("line-rate", "0"))
                    class_branch_rate = float(class_elem.attrib.get("branch-rate", "0"))

                    # Count lines and branches
                    lines = class_elem.findall(".//line")
                    total_lines = len(lines)
                    covered_lines = len([line for line in lines if line.attrib.get("hits", "0") != "0"])

                    file_data = {
                        "filename": filename,
                        "package": package_name,
                        "line_coverage": class_line_rate * 100,
                        "branch_coverage": class_branch_rate * 100,
                        "total_lines": total_lines,
                        "covered_lines": covered_lines,
                        "uncovered_lines": []
                    }

                    # Find uncovered lines
                    for line in lines:
                        if line.attrib.get("hits", "0") == "0":
                            line_number = int(line.attrib.get("number", "0"))
                            file_data["uncovered_lines"].append(line_number)

                    coverage_data["files"].append(file_data)

                    # Update summary
                    coverage_data["summary"]["total_lines"] += total_lines
                    coverage_data["summary"]["covered_lines"] += covered_lines

            return {
                "success": True,
                "coverage_analysis": coverage_data,
                "format": "xml"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to parse XML coverage: {str(e)}"}

    def _analyze_json_coverage(self, coverage_file: str) -> Dict[str, Any]:
        """Analyze JSON coverage report"""
        try:
            with open(coverage_file, 'r') as f:
                coverage_json = json.load(f)

            coverage_data = {
                "overall_coverage": 0.0,
                "line_coverage": 0.0,
                "branch_coverage": 0.0,
                "function_coverage": 0.0,
                "files": [],
                "summary": coverage_json.get("totals", {})
            }

            # Extract overall metrics
            totals = coverage_json.get("totals", {})
            coverage_data["line_coverage"] = totals.get("percent_covered", 0)
            coverage_data["overall_coverage"] = coverage_data["line_coverage"]

            # Parse individual files
            files_data = coverage_json.get("files", {})
            for filename, file_info in files_data.items():
                file_data = {
                    "filename": filename,
                    "line_coverage": file_info.get("summary", {}).get("percent_covered", 0),
                    "total_lines": file_info.get("summary", {}).get("num_statements", 0),
                    "covered_lines": file_info.get("summary", {}).get("covered_lines", 0),
                    "uncovered_lines": file_info.get("missing_lines", [])
                }
                coverage_data["files"].append(file_data)

            return {
                "success": True,
                "coverage_analysis": coverage_data,
                "format": "json"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to parse JSON coverage: {str(e)}"}

    def _analyze_lcov_coverage(self, coverage_file: str) -> Dict[str, Any]:
        """Analyze LCOV coverage report"""
        try:
            coverage_data = {
                "overall_coverage": 0.0,
                "line_coverage": 0.0,
                "branch_coverage": 0.0,
                "function_coverage": 0.0,
                "files": [],
                "summary": {
                    "total_lines": 0,
                    "covered_lines": 0,
                    "total_branches": 0,
                    "covered_branches": 0,
                    "total_functions": 0,
                    "covered_functions": 0
                }
            }

            with open(coverage_file, 'r') as f:
                content = f.read()

            # Parse LCOV format
            records = content.split('end_of_record')

            for record in records:
                if not record.strip():
                    continue

                file_data = self._parse_lcov_record(record)
                if file_data:
                    coverage_data["files"].append(file_data)

                    # Update summary
                    coverage_data["summary"]["total_lines"] += file_data.get("total_lines", 0)
                    coverage_data["summary"]["covered_lines"] += file_data.get("covered_lines", 0)
                    coverage_data["summary"]["total_functions"] += file_data.get("total_functions", 0)
                    coverage_data["summary"]["covered_functions"] += file_data.get("covered_functions", 0)

            # Calculate overall coverage
            if coverage_data["summary"]["total_lines"] > 0:
                coverage_data["line_coverage"] = (
                    coverage_data["summary"]["covered_lines"] /
                    coverage_data["summary"]["total_lines"] * 100
                )
                coverage_data["overall_coverage"] = coverage_data["line_coverage"]

            return {
                "success": True,
                "coverage_analysis": coverage_data,
                "format": "lcov"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to parse LCOV coverage: {str(e)}"}

    def _parse_lcov_record(self, record: str) -> Dict[str, Any]:
        """Parse individual LCOV record"""
        lines = record.strip().split('\n')
        file_data = {
            "filename": "",
            "line_coverage": 0.0,
            "function_coverage": 0.0,
            "branch_coverage": 0.0,
            "total_lines": 0,
            "covered_lines": 0,
            "total_functions": 0,
            "covered_functions": 0,
            "uncovered_lines": []
        }

        for line in lines:
            line = line.strip()
            if line.startswith('SF:'):  # Source file
                file_data["filename"] = line[3:]
            elif line.startswith('LH:'):  # Lines hit
                file_data["covered_lines"] = int(line[3:])
            elif line.startswith('LF:'):  # Lines found
                file_data["total_lines"] = int(line[3:])
            elif line.startswith('FH:'):  # Functions hit
                file_data["covered_functions"] = int(line[3:])
            elif line.startswith('FF:'):  # Functions found
                file_data["total_functions"] = int(line[3:])

        # Calculate coverage percentages
        if file_data["total_lines"] > 0:
            file_data["line_coverage"] = (file_data["covered_lines"] / file_data["total_lines"]) * 100

        if file_data["total_functions"] > 0:
            file_data["function_coverage"] = (file_data["covered_functions"] / file_data["total_functions"]) * 100

        return file_data if file_data["filename"] else None

    def _generate_coverage_report(self, source_path: str, test_path: str) -> Dict[str, Any]:
        """Generate coverage report using coverage.py"""
        try:
            # Run coverage with pytest
            cmd = [
                "coverage", "run", "--source", source_path,
                "-m", "pytest", test_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Coverage run failed: {result.stderr}",
                    "stdout": result.stdout
                }

            # Generate coverage report
            report_cmd = ["coverage", "report", "--format=json"]
            report_result = subprocess.run(
                report_cmd,
                capture_output=True,
                text=True
            )

            # Generate XML report
            xml_cmd = ["coverage", "xml"]
            subprocess.run(xml_cmd, capture_output=True)

            # Generate HTML report
            html_cmd = ["coverage", "html"]
            subprocess.run(html_cmd, capture_output=True)

            if report_result.returncode == 0:
                try:
                    coverage_data = json.loads(report_result.stdout)
                    return {
                        "success": True,
                        "coverage_data": coverage_data,
                        "reports_generated": {
                            "json": "coverage.json",
                            "xml": "coverage.xml",
                            "html": "htmlcov/"
                        }
                    }
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to parse coverage JSON"}
            else:
                return {"success": False, "error": f"Coverage report failed: {report_result.stderr}"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Coverage generation timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "Coverage tool not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _compare_coverage_reports(self, baseline_file: str, current_file: str) -> Dict[str, Any]:
        """Compare two coverage reports"""
        try:
            if not os.path.exists(baseline_file) or not os.path.exists(current_file):
                return {"success": False, "error": "Coverage files not found for comparison"}

            # Analyze both reports
            baseline_result = self._analyze_coverage_data(baseline_file, "xml")
            current_result = self._analyze_coverage_data(current_file, "xml")

            if not baseline_result["success"] or not current_result["success"]:
                return {"success": False, "error": "Failed to analyze coverage files"}

            baseline_data = baseline_result["coverage_analysis"]
            current_data = current_result["coverage_analysis"]

            comparison = {
                "baseline_coverage": baseline_data["overall_coverage"],
                "current_coverage": current_data["overall_coverage"],
                "coverage_change": current_data["overall_coverage"] - baseline_data["overall_coverage"],
                "improvement": current_data["overall_coverage"] > baseline_data["overall_coverage"],
                "file_changes": [],
                "summary": {
                    "files_improved": 0,
                    "files_degraded": 0,
                    "files_unchanged": 0,
                    "new_files": 0,
                    "removed_files": 0
                }
            }

            # Create file mapping for comparison
            baseline_files = {f["filename"]: f for f in baseline_data["files"]}
            current_files = {f["filename"]: f for f in current_data["files"]}

            # Compare individual files
            all_files = set(baseline_files.keys()) | set(current_files.keys())

            for filename in all_files:
                baseline_file = baseline_files.get(filename)
                current_file = current_files.get(filename)

                if baseline_file and current_file:
                    # File exists in both reports
                    coverage_change = current_file["line_coverage"] - baseline_file["line_coverage"]

                    file_comparison = {
                        "filename": filename,
                        "baseline_coverage": baseline_file["line_coverage"],
                        "current_coverage": current_file["line_coverage"],
                        "coverage_change": coverage_change,
                        "status": "improved" if coverage_change > 0 else ("degraded" if coverage_change < 0 else "unchanged")
                    }

                    comparison["file_changes"].append(file_comparison)

                    # Update summary
                    if coverage_change > 0:
                        comparison["summary"]["files_improved"] += 1
                    elif coverage_change < 0:
                        comparison["summary"]["files_degraded"] += 1
                    else:
                        comparison["summary"]["files_unchanged"] += 1

                elif current_file and not baseline_file:
                    # New file
                    comparison["file_changes"].append({
                        "filename": filename,
                        "baseline_coverage": 0,
                        "current_coverage": current_file["line_coverage"],
                        "coverage_change": current_file["line_coverage"],
                        "status": "new"
                    })
                    comparison["summary"]["new_files"] += 1

                elif baseline_file and not current_file:
                    # Removed file
                    comparison["file_changes"].append({
                        "filename": filename,
                        "baseline_coverage": baseline_file["line_coverage"],
                        "current_coverage": 0,
                        "coverage_change": -baseline_file["line_coverage"],
                        "status": "removed"
                    })
                    comparison["summary"]["removed_files"] += 1

            return {
                "success": True,
                "coverage_comparison": comparison
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _identify_coverage_gaps(self, coverage_data: Dict[str, Any], threshold: float) -> Dict[str, Any]:
        """Identify coverage gaps and areas needing attention"""
        try:
            gaps = {
                "low_coverage_files": [],
                "uncovered_critical_paths": [],
                "missing_test_areas": [],
                "recommendations": []
            }

            if not coverage_data or "files" not in coverage_data:
                return {"success": False, "error": "Invalid coverage data provided"}

            # Identify files with low coverage
            for file_data in coverage_data["files"]:
                if file_data["line_coverage"] < threshold:
                    gaps["low_coverage_files"].append({
                        "filename": file_data["filename"],
                        "current_coverage": file_data["line_coverage"],
                        "target_coverage": threshold,
                        "coverage_gap": threshold - file_data["line_coverage"],
                        "uncovered_lines_count": len(file_data.get("uncovered_lines", [])),
                        "priority": "high" if file_data["line_coverage"] < threshold * 0.5 else "medium"
                    })

            # Generate recommendations
            if gaps["low_coverage_files"]:
                gaps["recommendations"].extend([
                    f"Focus on files with coverage below {threshold}%",
                    "Prioritize high-impact and critical path files",
                    "Add unit tests for uncovered functions and methods",
                    "Consider integration tests for complex workflows"
                ])

            # Identify critical paths (heuristic based on filename patterns)
            critical_patterns = ["main.py", "app.py", "__init__.py", "models.py", "views.py", "api.py"]
            for file_data in coverage_data["files"]:
                filename = os.path.basename(file_data["filename"])
                if any(pattern in filename for pattern in critical_patterns):
                    if file_data["line_coverage"] < threshold * 1.2:  # Higher standard for critical files
                        gaps["uncovered_critical_paths"].append({
                            "filename": file_data["filename"],
                            "coverage": file_data["line_coverage"],
                            "reason": "Critical path with insufficient coverage"
                        })

            if gaps["uncovered_critical_paths"]:
                gaps["recommendations"].append("Prioritize testing of critical application paths")

            return {
                "success": True,
                "coverage_gaps": gaps,
                "threshold_used": threshold
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_coverage_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze coverage trends over time"""
        try:
            if len(historical_data) < 2:
                return {"success": False, "error": "Need at least 2 data points for trend analysis"}

            trends = {
                "overall_trend": "unknown",
                "trend_slope": 0.0,
                "coverage_points": [],
                "improvement_rate": 0.0,
                "prediction": {},
                "insights": []
            }

            # Extract coverage values and timestamps
            coverage_points = []
            for i, data in enumerate(historical_data):
                coverage_points.append({
                    "timestamp": data.get("timestamp", f"point_{i}"),
                    "coverage": data.get("overall_coverage", 0),
                    "index": i
                })

            trends["coverage_points"] = coverage_points

            # Calculate trend
            if len(coverage_points) >= 2:
                first_coverage = coverage_points[0]["coverage"]
                last_coverage = coverage_points[-1]["coverage"]

                trends["trend_slope"] = (last_coverage - first_coverage) / len(coverage_points)

                if trends["trend_slope"] > 0.5:
                    trends["overall_trend"] = "improving"
                elif trends["trend_slope"] < -0.5:
                    trends["overall_trend"] = "declining"
                else:
                    trends["overall_trend"] = "stable"

                # Calculate improvement rate
                trends["improvement_rate"] = ((last_coverage - first_coverage) / first_coverage) * 100

            # Generate insights
            if trends["overall_trend"] == "improving":
                trends["insights"].append("Coverage is trending upward - good progress!")
            elif trends["overall_trend"] == "declining":
                trends["insights"].append("Coverage is declining - attention needed")
                trends["insights"].append("Consider reviewing recent changes and adding tests")
            else:
                trends["insights"].append("Coverage is stable - maintain current testing practices")

            # Simple prediction (linear extrapolation)
            if len(coverage_points) >= 3:
                next_predicted = coverage_points[-1]["coverage"] + trends["trend_slope"]
                trends["prediction"] = {
                    "next_coverage_estimate": max(0, min(100, next_predicted)),
                    "confidence": "low",  # Simple linear prediction has low confidence
                    "method": "linear_extrapolation"
                }

            return {
                "success": True,
                "coverage_trends": trends
            }

        except Exception as e:
            return {"success": False, "error": str(e)}