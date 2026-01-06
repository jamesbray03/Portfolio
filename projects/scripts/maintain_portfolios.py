"""
Portfolio Maintenance Script
============================
Ensures all project folders have properly configured _portfolio folders.

This script:
1. Scans all project folders for missing _portfolio directories
2. Creates missing _portfolio folders with template files
3. Validates existing project.yaml files
4. Reports any issues found

Usage:
    python maintain_portfolios.py           # Check and fix missing folders
    python maintain_portfolios.py --check   # Check only, don't create
"""

import os
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PORTFOLIO_DIR = SCRIPT_DIR.parent.parent  # _Portfolio
PROJECTS_DIR = PORTFOLIO_DIR.parent  # Projects (contains all project folders)

# Default category for new projects
DEFAULT_CATEGORY = "other"

def create_template_yaml(folder_name: str) -> str:
    """Generate a template project.yaml for a new project."""
    return f"""# Project Configuration
# This file defines how this project appears on the portfolio website

title: "{folder_name}"
description: ""
category: {DEFAULT_CATEGORY}
public: false

# YouTube video URL (leave empty if none)
youtube: ""

# Date of project (YYYY-MM format for sorting, leave empty if unknown)
date: ""

# Additional notes (optional, not displayed on website)
notes: ""
"""

def create_gitignore() -> str:
    """Generate .gitignore content for _portfolio folders."""
    return """# This folder contains portfolio assets
# These are managed separately and should not be tracked in project repos

*
!.gitignore
"""

def create_template_readme(folder_name: str) -> str:
    """Generate a template readme.md for a new project."""
    return f"""# {folder_name}

## Overview
Add a description of your project here.

## Features
- Feature 1
- Feature 2

## Technologies Used
- Technology 1
- Technology 2
"""

def get_project_folders() -> list:
    """Get all project folder names from the Projects directory."""
    folders = []
    for item in PROJECTS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            folders.append(item.name)
    return sorted(folders)

def check_portfolio_folder(project_folder: Path, check_only: bool = False) -> dict:
    """Check and optionally fix a project's _portfolio folder."""
    folder_name = project_folder.name
    portfolio_folder = project_folder / "_portfolio"
    
    result = {
        "name": folder_name,
        "has_portfolio": portfolio_folder.exists(),
        "has_yaml": False,
        "has_readme": False,
        "has_thumbnail": False,
        "has_gitignore": False,
        "created": False,
        "issues": []
    }
    
    if not portfolio_folder.exists():
        if not check_only:
            portfolio_folder.mkdir()
            result["created"] = True
            print(f"  ✓ Created _portfolio folder for: {folder_name}")
        else:
            result["issues"].append("Missing _portfolio folder")
            return result
    
    result["has_portfolio"] = True
    
    # Check for project.yaml
    yaml_path = portfolio_folder / "project.yaml"
    if yaml_path.exists():
        result["has_yaml"] = True
    else:
        if not check_only:
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write(create_template_yaml(folder_name))
            result["has_yaml"] = True
            print(f"  ✓ Created project.yaml for: {folder_name}")
        else:
            result["issues"].append("Missing project.yaml")
    
    # Check for readme.md
    readme_path = portfolio_folder / "readme.md"
    if readme_path.exists():
        result["has_readme"] = True
    else:
        if not check_only:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(create_template_readme(folder_name))
            result["has_readme"] = True
            print(f"  ✓ Created readme.md for: {folder_name}")
        else:
            result["issues"].append("Missing readme.md")
    
    # Check for thumbnail (just report, don't create)
    thumbnail_path = portfolio_folder / "thumbnail.webp"
    if thumbnail_path.exists():
        result["has_thumbnail"] = True
    else:
        result["issues"].append("Missing thumbnail.webp")
    
    # Check for .gitignore
    gitignore_path = portfolio_folder / ".gitignore"
    if gitignore_path.exists():
        result["has_gitignore"] = True
    else:
        if not check_only:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(create_gitignore())
            result["has_gitignore"] = True
            print(f"  ✓ Created .gitignore for: {folder_name}")
        else:
            result["issues"].append("Missing .gitignore")
    
    # Create subdirectories if they don't exist
    images_folder = portfolio_folder / "images"
    downloads_folder = portfolio_folder / "downloads"
    
    if not images_folder.exists() and not check_only:
        images_folder.mkdir()
    
    if not downloads_folder.exists() and not check_only:
        downloads_folder.mkdir()
    
    return result

def main():
    print("=" * 60)
    print("Portfolio Maintenance Script")
    print("=" * 60)
    
    check_only = "--check" in sys.argv
    if check_only:
        print("\n*** CHECK MODE - No files will be modified ***\n")
    
    # Get all project folders
    project_folders = get_project_folders()
    print(f"Found {len(project_folders)} project folders\n")
    
    results = []
    issues_count = 0
    created_count = 0
    
    for folder_name in project_folders:
        project_folder = PROJECTS_DIR / folder_name
        result = check_portfolio_folder(project_folder, check_only)
        results.append(result)
        
        if result["issues"]:
            issues_count += len(result["issues"])
        if result["created"]:
            created_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("-" * 60)
    
    with_portfolio = sum(1 for r in results if r["has_portfolio"])
    with_yaml = sum(1 for r in results if r["has_yaml"])
    with_readme = sum(1 for r in results if r["has_readme"])
    with_thumbnail = sum(1 for r in results if r["has_thumbnail"])
    
    print(f"  Projects with _portfolio:    {with_portfolio}/{len(results)}")
    print(f"  Projects with project.yaml:  {with_yaml}/{len(results)}")
    print(f"  Projects with readme.md:     {with_readme}/{len(results)}")
    print(f"  Projects with thumbnail:     {with_thumbnail}/{len(results)}")
    
    if not check_only and created_count > 0:
        print(f"\n  ✓ Created {created_count} new _portfolio folder(s)")
    
    # List projects missing thumbnails
    missing_thumbnails = [r["name"] for r in results if not r["has_thumbnail"]]
    if missing_thumbnails:
        print(f"\n  ⚠ Missing thumbnails ({len(missing_thumbnails)}):")
        for name in missing_thumbnails[:10]:
            print(f"      - {name}")
        if len(missing_thumbnails) > 10:
            print(f"      ... and {len(missing_thumbnails) - 10} more")
    
    print("=" * 60)
    
    if check_only and issues_count > 0:
        print(f"\nRun without --check to fix {issues_count} issue(s).")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
