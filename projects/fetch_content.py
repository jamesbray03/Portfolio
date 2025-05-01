import os
import shutil
import json
from pathlib import Path

# define the paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # up to root
PROJECTS_DIR = Path(__file__).resolve().parent            # _Portfolio/projects
PROJECTS_CONTENT_DIR = PROJECTS_DIR / "content"
INDEX_FILE = PROJECTS_CONTENT_DIR / "index.json"
PROJECTS_JSON_FILE = PROJECTS_CONTENT_DIR / "projects.json"  # New file to store project details

# folders and files to copy from each project folder
REQUIRED_SUBDIRS = ["_media", "_downloadables"]
REQUIRED_FILES = ["project.json", "README.md"]

# clean the content directory
if PROJECTS_CONTENT_DIR.exists():
    shutil.rmtree(PROJECTS_CONTENT_DIR)
PROJECTS_CONTENT_DIR.mkdir(parents=True)

# store project names and details for projects.json
projects_data = []

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

        # read project.json for details
        project_json_path = entry / "project.json"
        if project_json_path.exists():
            with open(project_json_path, "r") as f:
                project_data = json.load(f)
                
                # Extract the necessary details and add to the projects data
                project_details = {
                    "title": project_data.get("title", entry.name),
                    "description": project_data.get("description", "No description provided."),
                    "public": project_data.get("public", False),
                    "thumbnail": f"../projects/content/{entry.name}/_media/thumbnail.png"  # assuming this path for thumbnail
                }
                projects_data.append(project_details)

# write projects.json
with open(PROJECTS_JSON_FILE, "w") as f:
    json.dump({"projects": projects_data}, f, indent=2)

# write index.json with sorted project names
project_names = [entry.name for entry in ROOT_DIR.iterdir() if entry.is_dir() and entry.name != "_Portfolio" and not entry.name.startswith(".")]
with open(INDEX_FILE, "w") as f:
    json.dump(sorted(project_names), f, indent=2)

print("Deployable project content stored in:", PROJECTS_CONTENT_DIR)
print("Project index file created at:", INDEX_FILE)
print("Project details stored in:", PROJECTS_JSON_FILE)
