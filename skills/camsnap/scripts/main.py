#!/usr/bin/env python3
"""
camsnap skill - Camera frame/clip capture tool.

Wraps the camsnap CLI for Clawdbot integration.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_camsnap(args: list) -> dict:
    """Execute camsnap command and return structured output."""
    try:
        result = subprocess.run(
            ["camsnap"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out", "returncode": -1}
    except FileNotFoundError:
        return {"success": False, "error": "camsnap not found", "returncode": -1}


def cmd_discover(info: bool = False) -> str:
    """Discover available cameras on the network."""
    args = ["discover"]
    if info:
        args.append("--info")
    result = run_camsnap(args)
    if result["success"]:
        return result["output"]
    return f"Error: {result['error']}"


def cmd_snap(camera: str, output: str) -> str:
    """Capture a snapshot from specified camera."""
    args = ["snap", camera, "--out", output]
    result = run_camsnap(args)
    if result["success"]:
        return f"Snapshot saved: {output}"
    return f"Error: {result['error']}"


def cmd_clip(camera: str, duration: str, output: str) -> str:
    """Capture a video clip from specified camera."""
    args = ["clip", camera, "--dur", duration, "--out", output]
    result = run_camsnap(args)
    if result["success"]:
        return f"Clip saved: {output}"
    return f"Error: {result['error']}"


def cmd_watch(camera: str, threshold: float = 0.2, action: str = None) -> str:
    """Watch camera for motion events."""
    args = ["watch", camera, "--threshold", str(threshold)]
    if action:
        args.extend(["--action", action])
    result = run_camsnap(args)
    if result["success"]:
        return result["output"]
    return f"Error: {result['error']}"


def cmd_doctor() -> str:
    """Run diagnostics on camera setup."""
    result = run_camsnap(["doctor", "--probe"])
    if result["success"]:
        return "Camera health: OK\n" + result["output"]
    return f"Error: {result['error']}"


def main():
    """Main entry point for camsnap skill."""
    parser = argparse.ArgumentParser(
        description="Camera capture tool for Clawdbot"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # discover
    p_discover = subparsers.add_parser("discover", help="Discover cameras")
    p_discover.add_argument("--info", action="store_true", help="Show detailed info")

    # snap
    p_snap = subparsers.add_parser("snap", help="Capture snapshot")
    p_snap.add_argument("camera", help="Camera name or ID")
    p_snap.add_argument("--out", required=True, help="Output file path")

    # clip
    p_clip = subparsers.add_parser("clip", help="Capture video clip")
    p_clip.add_argument("camera", help="Camera name or ID")
    p_clip.add_argument("--dur", required=True, help="Duration (e.g., 5s, 30s)")
    p_clip.add_argument("--out", required=True, help="Output file path")

    # watch
    p_watch = subparsers.add_parser("watch", help="Watch for motion")
    p_watch.add_argument("camera", help="Camera name or ID")
    p_watch.add_argument("--threshold", type=float, default=0.2, help="Motion threshold")
    p_watch.add_argument("--action", help="Action to trigger on motion")

    # doctor
    subparsers.add_parser("doctor", help="Run diagnostics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "discover":
        output = cmd_discover(args.info)
    elif args.command == "snap":
        output = cmd_snap(args.camera, args.out)
    elif args.command == "clip":
        output = cmd_clip(args.camera, args.dur, args.out)
    elif args.command == "watch":
        output = cmd_watch(args.camera, args.threshold, args.action)
    elif args.command == "doctor":
        output = cmd_doctor()
    else:
        output = f"Unknown command: {args.command}"

    print(output)


if __name__ == "__main__":
    main()
