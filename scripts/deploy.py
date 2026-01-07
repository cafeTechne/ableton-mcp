#!/usr/bin/env python3
"""
Deploy Remote Script to Ableton's User Library.

Usage:
    python scripts/deploy.py           # Deploy and show instructions
    python scripts/deploy.py --clean   # Clear __pycache__ before deploying
"""
import os
import sys
import shutil
import argparse
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = SCRIPT_DIR / "AbletonMCP_Remote_Script"
USER_HOME = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
ABLETON_USER_LIBRARY = USER_HOME / "Documents" / "Ableton" / "User Library" / "Remote Scripts"
DEST_DIR = ABLETON_USER_LIBRARY / "AbletonMCP_Remote_Script"


def clear_pycache(directory: Path):
    """Remove all __pycache__ directories recursively."""
    count = 0
    for pycache in directory.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            count += 1
    return count


def deploy():
    """Copy Remote Script files to User Library."""
    parser = argparse.ArgumentParser(description="Deploy Remote Script to Ableton User Library")
    parser.add_argument("--clean", action="store_true", help="Clear __pycache__ before deploying")
    args = parser.parse_args()

    print(f"Source:      {SOURCE_DIR}")
    print(f"Destination: {DEST_DIR}")
    print()

    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}")
        sys.exit(1)

    if not ABLETON_USER_LIBRARY.exists():
        print(f"ERROR: Ableton User Library not found: {ABLETON_USER_LIBRARY}")
        print("       Please create it or check your Ableton installation.")
        sys.exit(1)

    # Clean pycache if requested
    if args.clean:
        print("Clearing __pycache__ in source...")
        cleared = clear_pycache(SOURCE_DIR)
        print(f"  Cleared {cleared} __pycache__ directories")
        print()

    # Copy files
    print("Deploying files...")
    if DEST_DIR.exists():
        # Remove existing to ensure clean copy
        shutil.rmtree(DEST_DIR)
    shutil.copytree(SOURCE_DIR, DEST_DIR)

    # Count files
    py_files = list(DEST_DIR.rglob("*.py"))
    print(f"  Deployed {len(py_files)} Python files to User Library")
    print()

    # Instructions
    print("=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open Ableton Live (or switch to it if already open)")
    print("  2. Go to Preferences → Link, Tempo & MIDI → Control Surface")
    print("  3. Set the Control Surface to 'None'")
    print("  4. Set it back to 'AbletonMCP_Remote_Script'")
    print()
    print("This reloads the Remote Script with your changes.")
    print()


if __name__ == "__main__":
    deploy()
