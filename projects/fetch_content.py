import os
import shutil
from pathlib import Path

# define the paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # up to root
PROJECTS_DIR = Path(__file__).resolve().parent            # _Portfolio/projects
PROJECTS_CONTENT_DIR = PROJECTS_DIR / "content"

# folders and files to copy from each project folder
REQUIRED_SUBDIRS = ["_media", "_downloadables"]
REQUIRED_FILES = ["project.json", "README.md"]

# clean the content directory
if PROJECTS_CONTENT_DIR.exists():
    shutil.rmtree(PROJECTS_CONTENT_DIR)
PROJECTS_CONTENT_DIR.mkdir(parents=True)

# scan for valid projects in root (excluding _Portfolio)
for entry in ROOT_DIR.iterdir():
    if (
        entry.is_dir()
        and entry.name != "_Portfolio"
        and not entry.name.startswith(".")
    ):
        project_dest = PROJECTS_CONTENT_DIR / entry.name
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

print("Deployable project content stored in:", PROJECTS_CONTENT_DIR)
