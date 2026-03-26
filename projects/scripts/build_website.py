"""
Build Website Data Script
=========================
Aggregates project data from individual _portfolio folders into website-ready JSON.

This script:
1. Scans all project folders for _portfolio/project.yaml files
2. Reads the order.txt file for display ordering
3. Copies thumbnails and assets to the website content folder
4. Generates projects_master.json for the website

Run this script before deploying to GitHub Pages.

Usage:
    python build_website.py           # Build all website data
    python build_website.py --clean   # Clean output folders first
"""

import os
import sys
import json
import shutil
import re
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PORTFOLIO_DIR = SCRIPT_DIR.parent.parent  # _Portfolio
PROJECTS_DIR = PORTFOLIO_DIR.parent  # Projects (contains all project folders)
CONTENT_DIR = PORTFOLIO_DIR / "projects" / "content"
ORDER_FILE = PORTFOLIO_DIR / "projects" / "order.txt"

# Output paths
OUTPUT_JSON = CONTENT_DIR / "projects_data.json"
OUTPUT_THUMBNAILS = CONTENT_DIR / "thumbnails"
OUTPUT_READMES = CONTENT_DIR / "readmes"
OUTPUT_DOWNLOADS = CONTENT_DIR / "downloads"
OUTPUT_IMAGES = CONTENT_DIR / "gallery"

def parse_yaml(content: str) -> dict:
    """Simple YAML parser for project.yaml files."""
    result = {}
    current_key = None
    
    for line in content.split('\n'):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Check for key: value pattern
        if ':' in line and not line.startswith(' '):
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''
            
            # Handle quoted strings
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Handle booleans
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            
            result[key] = value
    
    return result

def folder_name_to_safe_name(folder_name: str) -> str:
    """Convert folder name (spaces) to safe_name (underscores)."""
    # Handle special cases first
    special_cases = {
        "The Chase - Revision Edition": "The_Chase_Revision_Edition",
    }
    if folder_name in special_cases:
        return special_cases[folder_name]
    
    # Remove special characters and replace spaces with underscores
    safe = re.sub(r'[^A-Za-z0-9\s_]', '', folder_name)
    safe = safe.replace(' ', '_')
    # Collapse multiple underscores
    safe = re.sub(r'_+', '_', safe)
    return safe

def load_order_file() -> list:
    """Load the project order from order.txt."""
    if not ORDER_FILE.exists():
        return []
    
    with open(ORDER_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
        return [line for line in lines if line and not line.startswith('#')]

def get_project_data(project_folder: Path) -> dict:
    """Read project data from a _portfolio folder."""
    portfolio_folder = project_folder / "_portfolio"
    yaml_path = portfolio_folder / "project.yaml"
    
    if not yaml_path.exists():
        return None
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = parse_yaml(f.read())
    
    # Add computed fields
    folder_name = project_folder.name
    safe_name = folder_name_to_safe_name(folder_name)
    
    data['folder_name'] = folder_name
    data['safe_name'] = safe_name
    
    # Check what assets exist
    data['has_thumbnail'] = (portfolio_folder / "thumbnail.webp").exists()
    data['has_readme'] = (portfolio_folder / "readme.md").exists()
    
    # Check for downloads (any .zip file)
    downloads_folder = portfolio_folder / "downloads"
    if downloads_folder.exists():
        zips = list(downloads_folder.glob("*.zip"))
        data['has_download'] = len(zips) > 0
        data['download_file'] = zips[0].name if zips else None
    else:
        data['has_download'] = False
        data['download_file'] = None
    
    # Check for PDF files
    pdfs = list(portfolio_folder.glob("*.pdf"))
    data['has_pdf'] = len(pdfs) > 0
    data['pdf_file'] = f"{safe_name}.pdf" if pdfs else None
    
    # Check for gallery images (only in images/ folder, not thumbnail)
    images_folder = portfolio_folder / "images"
    if images_folder.exists():
        images = list(images_folder.glob("*"))
        # Only count actual image files in the images folder
        image_files = [f.name for f in images if f.is_file() and f.suffix.lower() in ['.webp', '.jpg', '.jpeg', '.png', '.gif']]
        data['gallery_images'] = image_files
        data['has_gallery'] = len(image_files) > 0
    else:
        data['gallery_images'] = []
        data['has_gallery'] = False
    
    # Determine media type for the modal
    # Priority: youtube+gallery -> youtube -> pdf -> gallery -> thumbnail
    has_youtube = bool(data.get('youtube'))
    
    if has_youtube and data['has_gallery']:
        # Both YouTube and gallery - will show carousel with video embedded
        data['media_type'] = 'youtube_gallery'
    elif has_youtube:
        data['media_type'] = 'youtube'
    elif data['has_pdf']:
        data['media_type'] = 'pdf'
    elif data['has_gallery']:
        data['media_type'] = 'gallery'
    elif data['has_thumbnail']:
        data['media_type'] = 'thumbnail'
    else:
        data['media_type'] = 'none'
    
    return data

def copy_assets(project_folder: Path, project_data: dict):
    """Copy project assets to the website content folder."""
    portfolio_folder = project_folder / "_portfolio"
    safe_name = project_data['safe_name']
    
    # Copy thumbnail
    thumbnail_src = portfolio_folder / "thumbnail.webp"
    if thumbnail_src.exists():
        thumbnail_dst = OUTPUT_THUMBNAILS / f"{safe_name}.webp"
        shutil.copy2(thumbnail_src, thumbnail_dst)
    
    # Copy readme
    readme_src = portfolio_folder / "readme.md"
    if readme_src.exists():
        readme_dst = OUTPUT_READMES / f"{safe_name}.md"
        shutil.copy2(readme_src, readme_dst)
    
    # Copy downloads
    downloads_folder = portfolio_folder / "downloads"
    if downloads_folder.exists():
        for zip_file in downloads_folder.glob("*.zip"):
            zip_dst = OUTPUT_DOWNLOADS / zip_file.name
            shutil.copy2(zip_file, zip_dst)
    
    # Copy PDF files (renamed to safe_name to avoid collisions)
    for pdf_file in portfolio_folder.glob("*.pdf"):
        pdf_dst = OUTPUT_DOWNLOADS / f"{safe_name}.pdf"
        shutil.copy2(pdf_file, pdf_dst)
    
    # Copy gallery images
    images_folder = portfolio_folder / "images"
    if images_folder.exists():
        gallery_dst = OUTPUT_IMAGES / safe_name
        gallery_dst.mkdir(exist_ok=True)
        for img_file in images_folder.iterdir():
            if img_file.suffix.lower() in ['.webp', '.jpg', '.jpeg', '.png', '.gif']:
                shutil.copy2(img_file, gallery_dst / img_file.name)

def clean_output_folders():
    """Clean output folders before building."""
    folders = [OUTPUT_THUMBNAILS, OUTPUT_READMES, OUTPUT_DOWNLOADS, OUTPUT_IMAGES]
    
    for folder in folders:
        if folder.exists():
            try:
                # Try to remove files inside the folder instead of the folder itself
                for item in folder.iterdir():
                    try:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                    except Exception as e:
                        print(f"  Warning: Could not remove {item}: {e}")
            except Exception as e:
                print(f"  Warning: Could not clean {folder}: {e}")
        folder.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Build Website Data")
    print("=" * 60)
    
    clean = "--clean" in sys.argv
    if clean:
        print("\nCleaning output folders...")
        clean_output_folders()
    
    # Ensure output folders exist
    OUTPUT_THUMBNAILS.mkdir(parents=True, exist_ok=True)
    OUTPUT_READMES.mkdir(parents=True, exist_ok=True)
    OUTPUT_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)
    
    # Load order
    order = load_order_file()
    order_map = {name: i for i, name in enumerate(order)}
    print(f"Loaded order for {len(order)} projects")
    
    # Collect all project data
    projects = []
    
    for item in PROJECTS_DIR.iterdir():
        if not item.is_dir() or item.name.startswith('_'):
            continue
        
        portfolio_folder = item / "_portfolio"
        if not portfolio_folder.exists():
            continue
        
        data = get_project_data(item)
        if data:
            # Set order (projects not in order.txt go to end)
            folder_name = item.name
            data['order'] = order_map.get(folder_name, 9999)
            
            projects.append(data)
            
            # Copy assets
            copy_assets(item, data)
    
    # Sort by order
    projects.sort(key=lambda x: x['order'])
    
    # Update order field to be sequential
    for i, proj in enumerate(projects):
        proj['order'] = i
    
    # Generate output JSON
    output = {
        "metadata": {
            "description": "Auto-generated project data for portfolio website",
            "generated": datetime.now().isoformat(),
            "total_projects": len(projects)
        },
        "categories": [
            {"id": "all", "name": "All", "icon": "🏠"},
            {"id": "academic", "name": "Academic", "icon": "📚"},
            {"id": "hardware", "name": "Hardware", "icon": "🔧"},
            {"id": "games", "name": "Games & Sims", "icon": "🎮"},
            {"id": "applications", "name": "Applications", "icon": "💻"},
            {"id": "other", "name": "Other", "icon": "📦"}
        ],
        "projects": projects
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n" + "-" * 60)
    print("Summary:")
    print(f"  Total projects: {len(projects)}")
    
    # Count by category
    categories = {}
    for proj in projects:
        cat = proj.get('category', 'other')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n  By category:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count}")
    
    # Count by visibility
    public = sum(1 for p in projects if p.get('public') == True)
    private = len(projects) - public
    print(f"\n  Public: {public}, Private: {private}")
    
    # Count by media type
    media_types = {}
    for proj in projects:
        mt = proj.get('media_type', 'none')
        media_types[mt] = media_types.get(mt, 0) + 1
    
    print("\n  By media type:")
    for mt, count in sorted(media_types.items()):
        print(f"    {mt}: {count}")
    
    print(f"\nOutput: {OUTPUT_JSON}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
