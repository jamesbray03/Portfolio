"""
Deploy Preparation Script
=========================
One-command script to prepare the website for deployment.

This script runs all maintenance tasks in order:
1. maintain_portfolios.py - Ensure all projects have _portfolio folders
2. manage_order.py - Sync order.txt with existing projects
3. build_website.py - Generate website data and copy assets

Usage:
    python deploy.py           # Run all steps
    python deploy.py --check   # Check only, don't modify
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def run_script(script_name: str, args: list = None) -> int:
    """Run a Python script and return its exit code."""
    script_path = SCRIPT_DIR / script_name
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return 1
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    print("=" * 60)
    print("Portfolio Deploy Preparation")
    print("=" * 60)
    
    check_only = "--check" in sys.argv
    
    # Step 1: Maintain portfolio folders
    print("\n" + "─" * 60)
    print("Step 1: Maintaining _portfolio folders...")
    print("─" * 60)
    args = ["--check"] if check_only else []
    result = run_script("maintain_portfolios.py", args)
    if result != 0:
        print("Error in maintain_portfolios.py")
        return result
    
    # Step 2: Sync order file
    print("\n" + "─" * 60)
    print("Step 2: Syncing project order...")
    print("─" * 60)
    result = run_script("manage_order.py")
    if result != 0:
        print("Error in manage_order.py")
        return result
    
    # Step 3: Build website data (skip if check only)
    if not check_only:
        print("\n" + "─" * 60)
        print("Step 3: Building website data...")
        print("─" * 60)
        result = run_script("build_website.py", ["--clean"])
        if result != 0:
            print("Error in build_website.py")
            return result
    
    print("\n" + "=" * 60)
    if check_only:
        print("Check complete! Run without --check to build.")
    else:
        print("Deploy preparation complete!")
        print("You can now commit and push to deploy.")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
