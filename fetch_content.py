import os
import shutil
from pathlib import Path

# define the paths
ROOT_DIR = Path(__file__).resolve().parent.parent
PORTFOLIO_DIR = ROOT_DIR / "_Portfolio"
PROJECTS_DIR = PORTFOLIO_DIR / "projects"

# folders and files to copy from _Portfolio
INCLUDE_NAMES = ["index.html", "_media", "README.md", "website_generator.py"]

# clean the projects directory
if PROJECTS_DIR.exists():
    shutil.rmtree(PROJECTS_DIR)
PROJECTS_DIR.mkdir(parents=True)

# copy selected files and folders from _Portfolio
for name in INCLUDE_NAMES:
    src = PORTFOLIO_DIR / name
    dest = PROJECTS_DIR / name
    if src.exists():
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
    else:
        print(f"⚠️  Warning: {name} not found in _Portfolio")

# scan for valid projects in root directory
REQUIRED_SUBDIRS = ["_media", "_downloadables"]
REQUIRED_FILES = ["project.json", "README.md"]

for entry in ROOT_DIR.iterdir():
    if entry.is_dir() and entry.name not in ["_Portfolio"] and not entry.name.startswith("."):
        project_dest = PROJECTS_DIR / entry.name
        project_dest.mkdir(parents=True, exist_ok=True)

        # copy required folders
        for subdir in REQUIRED_SUBDIRS:
            source = entry / subdir
            if source.exists():
                shutil.copytree(source, project_dest / subdir)

        # copy required files
        for file in REQUIRED_FILES:
            source = entry / file
            if source.exists():
                shutil.copy2(source, project_dest / file)

print("✅ Deployable content stored in:", PROJECTS_DIR)
