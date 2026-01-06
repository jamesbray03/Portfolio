#!/usr/bin/env python3
"""
Category Manager
================
Interactive tool for assigning projects to categories.

Usage:
    python manage_categories.py           # Interactive mode - assign categories one by one
    python manage_categories.py --list    # List all projects by category
    python manage_categories.py --export  # Export category assignments to categories.txt

Categories:
    - academic: Academic & coursework projects
    - hardware: Physical builds, electronics, hardware projects
    - games: Games, simulations, interactive experiences
    - applications: Software tools, apps, utilities
    - other: Everything else
"""

import os
import sys
from pathlib import Path
import yaml

# Base projects directory
PROJECTS_DIR = Path(__file__).parent.parent.parent.parent  # Goes up to Projects folder
PORTFOLIO_DIR = Path(__file__).parent.parent  # _Portfolio/projects
CATEGORIES_FILE = PORTFOLIO_DIR / "categories.txt"

VALID_CATEGORIES = ['academic', 'hardware', 'games', 'applications', 'other']

CATEGORY_DESCRIPTIONS = {
    'academic': 'Academic & Coursework',
    'hardware': 'Hardware & Electronics',
    'games': 'Games & Simulations',
    'applications': 'Apps & Tools',
    'other': 'Other Projects'
}


def get_all_projects():
    """Get all projects with _portfolio folders and their current categories."""
    projects = []
    
    for item in PROJECTS_DIR.iterdir():
        if not item.is_dir() or item.name.startswith(('_', '.')):
            continue
            
        portfolio_dir = item / '_portfolio'
        yaml_file = portfolio_dir / 'project.yaml'
        
        if yaml_file.exists():
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                projects.append({
                    'name': item.name,
                    'title': data.get('title', item.name),
                    'category': data.get('category', 'other'),
                    'yaml_path': yaml_file,
                    'public': data.get('public', True),
                    'data': data
                })
            except Exception as e:
                print(f"Warning: Could not read {yaml_file}: {e}")
    
    # Sort by title
    projects.sort(key=lambda p: p['title'].lower())
    return projects


def list_by_category():
    """List all projects organized by category."""
    projects = get_all_projects()
    
    # Group by category
    by_category = {cat: [] for cat in VALID_CATEGORIES}
    for p in projects:
        cat = p['category'] if p['category'] in VALID_CATEGORIES else 'other'
        by_category[cat].append(p)
    
    print("\n" + "=" * 60)
    print("PROJECTS BY CATEGORY")
    print("=" * 60)
    
    total = 0
    for cat in VALID_CATEGORIES:
        cat_projects = by_category[cat]
        print(f"\n{CATEGORY_DESCRIPTIONS[cat]} ({len(cat_projects)}):")
        print("-" * 40)
        
        if cat_projects:
            for p in cat_projects:
                visibility = "🔒" if not p['public'] else "  "
                print(f"  {visibility} {p['title']}")
        else:
            print("  (none)")
        
        total += len(cat_projects)
    
    print("\n" + "=" * 60)
    print(f"Total: {total} projects")
    print("=" * 60)


def export_categories():
    """Export category assignments to a text file for reference."""
    projects = get_all_projects()
    
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        f.write("# Project Category Assignments\n")
        f.write("# Format: category: project_folder_name\n")
        f.write("# Valid categories: academic, hardware, games, applications, other\n")
        f.write("#\n")
        f.write("# To change a category, edit the project.yaml file in each project's _portfolio folder\n")
        f.write("# or use: python manage_categories.py\n\n")
        
        for cat in VALID_CATEGORIES:
            f.write(f"\n# {CATEGORY_DESCRIPTIONS[cat]}\n")
            cat_projects = [p for p in projects if p['category'] == cat]
            for p in cat_projects:
                f.write(f"{cat}: {p['name']}\n")
    
    print(f"\nExported category assignments to: {CATEGORIES_FILE}")


def update_project_category(project, new_category):
    """Update a project's category in its YAML file."""
    yaml_path = project['yaml_path']
    data = project['data']
    
    data['category'] = new_category
    
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    return True


def interactive_categorize():
    """Interactive mode - go through each project and assign category."""
    projects = get_all_projects()
    
    # Filter to only uncategorized or 'other' projects if user wants
    print("\n" + "=" * 60)
    print("INTERACTIVE CATEGORY ASSIGNMENT")
    print("=" * 60)
    print(f"\nFound {len(projects)} projects")
    print("\nOptions:")
    print("  1. Show all projects that need categorization (category='other')")
    print("  2. Go through ALL projects")
    print("  3. Categorize a specific project")
    print("  q. Quit")
    
    choice = input("\nChoice: ").strip().lower()
    
    if choice == 'q':
        return
    elif choice == '1':
        projects = [p for p in projects if p['category'] == 'other']
        if not projects:
            print("\nNo projects with 'other' category. All projects are categorized!")
            return
    elif choice == '3':
        search = input("\nEnter project name to search: ").strip().lower()
        projects = [p for p in projects if search in p['name'].lower() or search in p['title'].lower()]
        if not projects:
            print("\nNo matching projects found.")
            return
    elif choice != '2':
        print("Invalid choice.")
        return
    
    print(f"\n{len(projects)} projects to categorize.")
    print("\nFor each project, enter:")
    print("  a = academic")
    print("  h = hardware")
    print("  g = games")
    print("  p = applications (apps)")
    print("  o = other")
    print("  s = skip (keep current)")
    print("  q = quit\n")
    
    changes = 0
    for i, project in enumerate(projects, 1):
        current = project['category']
        print(f"\n[{i}/{len(projects)}] {project['title']}")
        print(f"         Folder: {project['name']}")
        print(f"         Current: {current}")
        
        while True:
            choice = input("  Category (a/h/g/p/o/s/q): ").strip().lower()
            
            if choice == 'q':
                print(f"\nSaved {changes} changes.")
                return
            elif choice == 's':
                break
            elif choice == 'a':
                new_cat = 'academic'
            elif choice == 'h':
                new_cat = 'hardware'
            elif choice == 'g':
                new_cat = 'games'
            elif choice == 'p':
                new_cat = 'applications'
            elif choice == 'o':
                new_cat = 'other'
            else:
                print("  Invalid choice. Use a/h/g/p/o/s/q")
                continue
            
            if new_cat != current:
                if update_project_category(project, new_cat):
                    print(f"  ✓ Changed to: {new_cat}")
                    changes += 1
            break
    
    print(f"\nDone! Saved {changes} changes.")
    print("Run 'python build_website.py' to regenerate website data.")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == '--list':
            list_by_category()
        elif arg == '--export':
            export_categories()
        elif arg == '--help' or arg == '-h':
            print(__doc__)
        else:
            print(f"Unknown option: {arg}")
            print("Use --help for usage information.")
    else:
        interactive_categorize()


if __name__ == '__main__':
    main()
