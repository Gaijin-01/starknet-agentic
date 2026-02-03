#!/usr/bin/env python3
"""
songsee skill - Audio visualization tool.

Generates spectrograms and feature panels from audio files.
"""

#!/usr/bin/env python3
"""Audio visualization skill using songsee tool."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_songsee(args: list) -> dict:
    """Execute songsee command and return structured output."""
    try:
        result = subprocess.run(
            ["songsee"] + args,
            capture_output=True,
            text=True,
            timeout=120
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
        return {"success": False, "error": "songsee not found", "returncode": -1}


def cmd_track(audio: str, output: str = None, viz: list = None, 
              style: str = None, width: int = None, height: int = None,
              start: float = None, duration: float = None,
              min_freq: int = None, max_freq: int = None,
              format_str: str = "png") -> str:
    """Generate visualization for an audio track."""
    args = [audio]
    
    if output:
        args.extend(["-o", output])
    if viz:
        args.extend(["--viz", ",".join(viz)])
    if style:
        args.extend(["--style", style])
    if width:
        args.extend(["--width", str(width)])
    if height:
        args.extend(["--height", str(height)])
    if start is not None:
        args.extend(["--start", str(start)])
    if duration is not None:
        args.extend(["--duration", str(duration)])
    if min_freq is not None:
        args.extend(["--min-freq", str(min_freq)])
    if max_freq is not None:
        args.extend(["--max-freq", str(max_freq)])
    args.extend(["--format", format_str])
    
    result = run_songsee(args)
    if result["success"]:
        return f"Visualization saved: {output or 'default output'}"
    return f"Error: {result['error']}"


def cmd_stdin(output: str = None, format_str: str = "png",
              viz: list = None, style: str = None) -> str:
    """Generate visualization from stdin audio."""
    args = ["-", "--format", format_str]
    
    if output:
        args.extend(["-o", output])
    if viz:
        args.extend(["--viz", ",".join(viz)])
    if style:
        args.extend(["--style", style])
    
    result = run_songsee(args)
    if result["success"]:
        return f"Visualization saved: {output or 'default output'}"
    return f"Error: {result['error']}"


def cmd_help() -> str:
    """Show help information."""
    result = run_songsee(["--help"])
    if result["success"]:
        return result["output"]
    return f"Error: {result['error']}"


def main():
    """Main entry point for songsee skill."""
    parser = argparse.ArgumentParser(
        description="Audio visualization for Clawdbot"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # track (default)
    p_track = subparsers.add_parser("track", help="Visualize audio track")
    p_track.add_argument("audio", help="Audio file path")
    p_track.add_argument("-o", "--output", help="Output file path")
    p_track.add_argument("--viz", nargs="+", 
                         help="Visualization types: spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux")
    p_track.add_argument("--style", choices=["classic", "magma", "inferno", "viridis", "gray"],
                         help="Color palette")
    p_track.add_argument("--width", type=int, help="Output width")
    p_track.add_argument("--height", type=int, help="Output height")
    p_track.add_argument("--start", type=float, help="Start time (seconds)")
    p_track.add_argument("--duration", type=float, help="Duration (seconds)")
    p_track.add_argument("--min-freq", type=int, help="Minimum frequency")
    p_track.add_argument("--max-freq", type=int, help="Maximum frequency")
    p_track.add_argument("--format", default="png", choices=["jpg", "png"],
                         help="Output format")

    # stdin
    p_stdin = subparsers.add_parser("stdin", help="Visualize from stdin")
    p_stdin.add_argument("-o", "--output", help="Output file path")
    p_stdin.add_argument("--format", default="png", choices=["jpg", "png"],
                         help="Output format")
    p_stdin.add_argument("--viz", nargs="+", help="Visualization types")
    p_stdin.add_argument("--style", choices=["classic", "magma", "inferno", "viridis", "gray"],
                         help="Color palette")

    # help
    subparsers.add_parser("help", help="Show help")

    args = parser.parse_args()

    if not args.command or args.command == "help":
        print(cmd_help())
        sys.exit(0)

    if args.command == "track":
        output = cmd_track(
            args.audio,
            output=args.output,
            viz=args.viz,
            style=args.style,
            width=args.width,
            height=args.height,
            start=args.start,
            duration=args.duration,
            min_freq=args.min_freq,
            max_freq=args.max_freq,
            format_str=args.format
        )
    elif args.command == "stdin":
        output = cmd_stdin(
            output=args.output,
            format_str=args.format,
            viz=args.viz,
            style=args.style
        )
    else:
        output = f"Unknown command: {args.command}"

    print(output)


if __name__ == "__main__":
    main()
