"""
Order Management Script
=======================
Manages the display order of projects on the portfolio website.

This script maintains an order.txt file that:
- Lists all project folder names, one per line
- Determines display order on the website (top = first displayed)
- Auto-adds new projects at the end
- Auto-removes deleted projects
- Preserves manual ordering

Usage:
    python manage_order.py          # Sync order.txt with existing projects
    python manage_order.py --show   # Display current order

The order.txt file is located in _Portfolio/projects/
"""

import os
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PORTFOLIO_DIR = SCRIPT_DIR.parent.parent  # _Portfolio
PROJECTS_DIR = PORTFOLIO_DIR.parent  # Projects (contains all project folders)
ORDER_FILE = PORTFOLIO_DIR / "projects" / "order.txt"

def get_project_folders() -> set:
    """Get all project folder names that have _portfolio folders."""
    folders = set()
    for item in PROJECTS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            portfolio_folder = item / "_portfolio"
            if portfolio_folder.exists():
                folders.add(item.name)
    return folders

def load_order_file() -> list:
    """Load the current order from order.txt."""
    if not ORDER_FILE.exists():
        return []
    
    with open(ORDER_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
        # Filter out empty lines and comments
        return [line for line in lines if line and not line.startswith('#')]

def save_order_file(order: list):
    """Save the order to order.txt."""
    header = """# Project Display Order
# =====================
# Each line is a project folder name (with spaces, as in the filesystem).
# Projects are displayed in this order on the website.
# Move lines up/down to change order.
# New projects are automatically added at the end.
# Deleted projects are automatically removed.
#
# Run: python scripts/manage_order.py
# to sync this file with existing projects.
#

"""
    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        f.write(header)
        for project in order:
            f.write(f"{project}\n")

def sync_order():
    """Synchronize order.txt with existing project folders."""
    print("=" * 50)
    print("Project Order Management")
    print("=" * 50)
    
    # Get current state
    existing_folders = get_project_folders()
    current_order = load_order_file()
    
    print(f"Found {len(existing_folders)} projects with _portfolio folders")
    print(f"Found {len(current_order)} entries in order.txt")
    
    # Find new projects (in folders but not in order)
    current_set = set(current_order)
    new_projects = existing_folders - current_set
    
    # Find deleted projects (in order but not in folders)
    deleted_projects = current_set - existing_folders
    
    # Build new order list
    new_order = []
    
    # Keep existing entries that still exist
    removed_count = 0
    for project in current_order:
        if project in existing_folders:
            new_order.append(project)
        else:
            print(f"  ✗ Removed (deleted): {project}")
            removed_count += 1
    
    # Add new projects at the end
    added_count = 0
    for project in sorted(new_projects):
        new_order.append(project)
        print(f"  ✓ Added (new): {project}")
        added_count += 1
    
    # Save updated order
    save_order_file(new_order)
    
    print("\n" + "-" * 50)
    print(f"Synced: {added_count} added, {removed_count} removed")
    print(f"Total projects in order: {len(new_order)}")
    print(f"Order file: {ORDER_FILE}")
    print("=" * 50)

def show_order():
    """Display the current order."""
    print("=" * 50)
    print("Current Project Order")
    print("=" * 50)
    
    order = load_order_file()
    if not order:
        print("No projects in order.txt")
        return
    
    for i, project in enumerate(order, 1):
        print(f"  {i:3}. {project}")
    
    print(f"\nTotal: {len(order)} projects")

def main():
    if "--show" in sys.argv:
        show_order()
    else:
        sync_order()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
