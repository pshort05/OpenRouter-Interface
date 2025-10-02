#!/usr/bin/env python3
"""
Status Manager for Prompt Chain Runner

Manages persistent status tracking for chain execution with restart capabilities.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ChainStatusManager:
    """Manages persistent status tracking for chain execution."""

    def __init__(self, config_file: Path, temp_dir: Path = None):
        """
        Initialize status manager.

        Args:
            config_file: Path to the chain configuration file
            temp_dir: Temporary directory for this run
        """
        self.config_file = config_file
        self.status_file = config_file.with_suffix('.status')
        self.temp_dir = temp_dir
        self.status_data = self._initialize_status()

    def _initialize_status(self) -> Dict[str, Any]:
        """Initialize or load existing status data."""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Could not load existing status file {self.status_file}: {e}")

        # Create new status structure
        return {
            "chain_config": self.config_file.name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "running",
            "temp_directory": str(self.temp_dir) if self.temp_dir else None,
            "files": {}
        }

    def update_temp_directory(self, temp_dir: Path):
        """Update temp directory after it's created."""
        self.temp_dir = temp_dir
        self.status_data["temp_directory"] = str(temp_dir)
        self.save_status()

    def update_file_start(self, filename: str, file_size: str):
        """Mark file processing as started."""
        if filename not in self.status_data["files"]:
            self.status_data["files"][filename] = {
                "status": "running",
                "file_size": file_size,
                "steps": {}
            }
        else:
            self.status_data["files"][filename]["status"] = "running"
            self.status_data["files"][filename]["file_size"] = file_size

        self.save_status()

    def update_step_start(self, filename: str, step: str, step_name: str):
        """Mark step as started."""
        if filename not in self.status_data["files"]:
            self.status_data["files"][filename] = {"status": "running", "steps": {}}

        self.status_data["files"][filename]["steps"][step] = {
            "status": "running",
            "name": step_name,
            "start_time": time.time()
        }
        self.save_status()

    def update_step_complete(self, filename: str, step: str, execution_time: float, output_size: str):
        """Mark step as completed successfully."""
        if filename in self.status_data["files"] and step in self.status_data["files"][filename]["steps"]:
            self.status_data["files"][filename]["steps"][step].update({
                "status": "completed",
                "time": execution_time,
                "output_size": output_size
            })
            self.save_status()

    def update_step_failed(self, filename: str, step: str, execution_time: float, error: str):
        """Mark step as failed with error details."""
        if filename in self.status_data["files"] and step in self.status_data["files"][filename]["steps"]:
            self.status_data["files"][filename]["steps"][step].update({
                "status": "failed",
                "time": execution_time,
                "error": error
            })

            # Mark file as failed
            self.status_data["files"][filename]["status"] = "failed"
            self.save_status()

    def update_step_skipped(self, filename: str, step: str, step_name: str, reason: str = "restart"):
        """Mark step as skipped (for restart scenarios)."""
        if filename not in self.status_data["files"]:
            self.status_data["files"][filename] = {"status": "running", "steps": {}}

        self.status_data["files"][filename]["steps"][step] = {
            "status": "skipped",
            "name": step_name,
            "reason": reason,
            "time": 0.0
        }
        self.save_status()

    def update_file_complete(self, filename: str):
        """Mark file processing as completed."""
        if filename in self.status_data["files"]:
            self.status_data["files"][filename]["status"] = "completed"
            self.save_status()

    def update_chain_complete(self, success: bool):
        """Mark entire chain as completed."""
        self.status_data["status"] = "completed" if success else "failed"
        self.status_data["end_time"] = datetime.now().isoformat()
        self.save_status()

    def save_status(self):
        """Write status to file (called after each update)."""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.warning(f"Could not save status file {self.status_file}: {e}")

    def get_restart_point(self, filename: str) -> Optional[str]:
        """Determine first failed or incomplete step for file."""
        if filename not in self.status_data["files"]:
            return None

        file_data = self.status_data["files"][filename]
        if file_data.get("status") == "completed":
            return None

        steps = file_data.get("steps", {})
        for step in sorted(steps.keys(), key=lambda x: float(x.replace('_', '.'))):
            step_data = steps[step]
            if step_data.get("status") in ["failed", "running"]:
                return step

        return None

    def analyze_restart_scenario(self) -> Dict[str, Any]:
        """Analyze current status and determine restart requirements."""
        restart_info = {
            "restart_needed": False,
            "files_to_restart": {},
            "files_completed": [],
            "total_files": len(self.status_data["files"])
        }

        for filename, file_data in self.status_data["files"].items():
            if file_data.get("status") == "completed":
                restart_info["files_completed"].append(filename)
            else:
                restart_point = self.get_restart_point(filename)
                if restart_point:
                    restart_info["restart_needed"] = True
                    restart_info["files_to_restart"][filename] = {
                        "restart_step": restart_point,
                        "completed_steps": [
                            step for step, data in file_data.get("steps", {}).items()
                            if data.get("status") == "completed"
                        ]
                    }

        return restart_info

    def should_skip_step(self, filename: str, step: str) -> bool:
        """Determine if step should be skipped based on previous completion."""
        if filename not in self.status_data["files"]:
            return False

        steps = self.status_data["files"][filename].get("steps", {})
        if step in steps:
            return steps[step].get("status") == "completed"

        return False

    def get_last_successful_output(self, filename: str, before_step: str) -> Optional[str]:
        """Get the output file from the last successfully completed step before given step."""
        if filename not in self.status_data["files"]:
            return None

        steps = self.status_data["files"][filename].get("steps", {})
        completed_steps = []

        for step, data in steps.items():
            if data.get("status") == "completed":
                try:
                    step_num = float(step.replace('_', '.'))
                    before_num = float(before_step.replace('_', '.'))
                    if step_num < before_num:
                        completed_steps.append((step_num, step))
                except ValueError:
                    continue

        if completed_steps:
            # Return the highest numbered completed step
            completed_steps.sort()
            last_step = completed_steps[-1][1]
            return last_step

        return None

    def print_status_summary(self):
        """Print a summary of the current chain status."""
        print(f"\nChain Status: {self.config_file.name}")

        if not self.status_data["files"]:
            print("No files processed yet.")
            return

        for filename, file_data in self.status_data["files"].items():
            status = file_data.get("status", "unknown")
            steps = file_data.get("steps", {})
            completed_count = sum(1 for s in steps.values() if s.get("status") == "completed")
            total_steps = len(steps)

            if status == "completed":
                print(f"├── {filename}: COMPLETED ({completed_count}/{total_steps} steps)")
            elif status == "failed":
                failed_step = None
                for step, data in steps.items():
                    if data.get("status") == "failed":
                        failed_step = step
                        break
                print(f"├── {filename}: FAILED at step {failed_step} ({completed_count}/{total_steps} steps completed)")
            else:
                print(f"├── {filename}: {status.upper()} ({completed_count}/{total_steps} steps)")

        restart_info = self.analyze_restart_scenario()
        if restart_info["restart_needed"]:
            print(f"\nRestart recommendation: Use --restart to resume from failed steps")
        elif restart_info["files_completed"]:
            print(f"\nAll files completed successfully.")