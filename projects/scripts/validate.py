"""
Validate Projects Script
========================
Validates all project configurations and reports issues.

This script checks:
1. project.yaml syntax and required fields
2. Asset file presence (thumbnails, readmes)
3. Category validity
4. YouTube URL format
5. Image file formats

Usage:
    python validate.py              # Validate all projects
    python validate.py --verbose    # Show all details
"""

import os
import sys
import re
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PORTFOLIO_DIR = SCRIPT_DIR.parent.parent  # _Portfolio
PROJECTS_DIR = PORTFOLIO_DIR.parent  # Projects (contains all project folders)

# Valid categories
VALID_CATEGORIES = {'academic', 'hardware', 'games', 'applications', 'other'}

# Valid image extensions
VALID_IMAGE_EXTENSIONS = {'.webp', '.jpg', '.jpeg', '.png', '.gif'}

def parse_yaml(content: str) -> dict:
    """Simple YAML parser for project.yaml files."""
    result = {}
    
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        if ':' in line and not line.startswith(' '):
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''
            
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            
            result[key] = value
    
    return result

def validate_youtube_url(url: str) -> bool:
    """Check if a YouTube URL is valid."""
    if not url:
        return True  # Empty is valid (no video)
    
    patterns = [
        r'https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://youtu\.be/[\w-]+',
        r'https?://(www\.)?youtube\.com/embed/[\w-]+'
    ]
    
    return any(re.match(pattern, url) for pattern in patterns)

def validate_project(project_folder: Path, verbose: bool = False) -> list:
    """Validate a single project and return list of issues."""
    issues = []
    folder_name = project_folder.name
    portfolio_folder = project_folder / "_portfolio"
    
    # Check _portfolio folder exists
    if not portfolio_folder.exists():
        issues.append(("error", "Missing _portfolio folder"))
        return issues
    
    # Check project.yaml exists
    yaml_path = portfolio_folder / "project.yaml"
    if not yaml_path.exists():
        issues.append(("error", "Missing project.yaml"))
        return issues
    
    # Parse and validate YAML
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = parse_yaml(f.read())
    except Exception as e:
        issues.append(("error", f"Failed to parse project.yaml: {e}"))
        return issues
    
    # Required fields
    if not data.get('title'):
        issues.append(("warning", "Missing or empty title"))
    
    if not data.get('description'):
        issues.append(("warning", "Missing or empty description"))
    
    # Category validation
    category = data.get('category', '')
    if not category:
        issues.append(("warning", "Missing category"))
    elif category not in VALID_CATEGORIES:
        issues.append(("warning", f"Invalid category: {category}"))
    
    # Public field
    if 'public' not in data:
        issues.append(("warning", "Missing 'public' field"))
    
    # YouTube URL validation
    youtube = data.get('youtube', '')
    if youtube and not validate_youtube_url(youtube):
        issues.append(("warning", f"Invalid YouTube URL format: {youtube}"))
    
    # Thumbnail check
    thumbnail_path = portfolio_folder / "thumbnail.webp"
    if not thumbnail_path.exists():
        issues.append(("warning", "Missing thumbnail.webp"))
    
    # Readme check
    readme_path = portfolio_folder / "readme.md"
    if not readme_path.exists():
        issues.append(("warning", "Missing readme.md"))
    
    # .gitignore check
    gitignore_path = portfolio_folder / ".gitignore"
    if not gitignore_path.exists():
        issues.append(("info", "Missing .gitignore"))
    
    # Check image files in gallery
    images_folder = portfolio_folder / "images"
    if images_folder.exists():
        for img_file in images_folder.iterdir():
            if img_file.is_file():
                ext = img_file.suffix.lower()
                if ext not in VALID_IMAGE_EXTENSIONS:
                    issues.append(("info", f"Non-standard image format: {img_file.name}"))
    
    return issues

def get_project_folders() -> list:
    """Get all project folder names from the Projects directory."""
    folders = []
    for item in PROJECTS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            folders.append(item.name)
    return sorted(folders)

def main():
    print("=" * 60)
    print("Project Validation")
    print("=" * 60)
    
    verbose = "--verbose" in sys.argv
    
    project_folders = get_project_folders()
    print(f"Found {len(project_folders)} project folders\n")
    
    total_errors = 0
    total_warnings = 0
    total_info = 0
    projects_with_issues = 0
    
    for folder_name in project_folders:
        project_folder = PROJECTS_DIR / folder_name
        issues = validate_project(project_folder, verbose)
        
        errors = [i for i in issues if i[0] == 'error']
        warnings = [i for i in issues if i[0] == 'warning']
        infos = [i for i in issues if i[0] == 'info']
        
        total_errors += len(errors)
        total_warnings += len(warnings)
        total_info += len(infos)
        
        if issues:
            projects_with_issues += 1
            
            if verbose or errors:
                print(f"\n{folder_name}:")
                for level, msg in issues:
                    icon = "❌" if level == 'error' else "⚠️" if level == 'warning' else "ℹ️"
                    print(f"  {icon} {msg}")
        elif verbose:
            print(f"  ✓ {folder_name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("-" * 60)
    print(f"  Total projects:      {len(project_folders)}")
    print(f"  Projects with issues: {projects_with_issues}")
    print(f"  Errors:              {total_errors}")
    print(f"  Warnings:            {total_warnings}")
    print(f"  Info:                {total_info}")
    print("=" * 60)
    
    # Return non-zero if there are errors
    return 1 if total_errors > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
