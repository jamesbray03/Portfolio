import os
import shutil
import json
from pathlib import Path

# define the paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # up to root (e.g., main portfolio directory)
PORTFOLIO_PROJECTS_SCRIPT_DIR = Path(__file__).resolve().parent  # _Portfolio/projects (where this script is)
PROJECTS_CONTENT_DIR = PORTFOLIO_PROJECTS_SCRIPT_DIR / "content"  # _Portfolio/projects/content
PROJECTS_THUMBNAILS_DIR = PROJECTS_CONTENT_DIR / "thumbnails"  # New directory for all thumbnails
PROJECTS_JSON_FILE = PROJECTS_CONTENT_DIR / "projects.json"  # Main JSON index file

# Common image extensions for thumbnails
IMAGE_EXTENSIONS = [".gif", ".webp"]

# clean the content directory
if PROJECTS_CONTENT_DIR.exists():
    shutil.rmtree(PROJECTS_CONTENT_DIR)
PROJECTS_CONTENT_DIR.mkdir(parents=True)
PROJECTS_THUMBNAILS_DIR.mkdir(parents=True) # Create the thumbnails directory

# store project JSON data for the main projects.json
all_projects_data = []

print(f"Scanning for projects in: {ROOT_DIR}")

# scan for valid projects in root (excluding _Portfolio and hidden folders)
for entry in ROOT_DIR.iterdir():
    if (
        entry.is_dir()
        and entry.name != "_Portfolio"
        and not entry.name.startswith(".")
    ):
        project_name = entry.name
        print(f"\nProcessing project: {project_name}")

        project_specific_content_dir = PROJECTS_CONTENT_DIR / project_name
        
        # Handle project.json
        source_project_json_path = entry / "project.json"
        if source_project_json_path.exists() and source_project_json_path.is_file():
            try:
                # Read project.json for the main index
                with open(source_project_json_path, "r") as f:
                    project_data = json.load(f)
                    # Add the entire project_data to the list
                    all_projects_data.append(project_data)
                    print(f"  Added data from project.json to main index list.")
            except json.JSONDecodeError:
                print(f"  Error: Could not decode JSON from {source_project_json_path}. Skipping for main index.")
            except Exception as e:
                print(f"  Error processing project.json for {project_name}: {e}")
        else:
            print(f"  Warning: project.json not found for {project_name}. It will not be included in the main projects.json index.")

        # Handle Thumbnail
        found_thumbnail_source_path = None
        
        # Look for thumbnail in project root then in _media folder
        possible_thumbnail_locations = [entry, entry / "_media"]
        for loc in possible_thumbnail_locations:
            if loc.exists() and loc.is_dir():
                for item in loc.iterdir():
                    if item.is_file() and item.name.lower().startswith("thumbnail") and item.suffix.lower() in IMAGE_EXTENSIONS:
                        found_thumbnail_source_path = item
                        break # Found thumbnail
            if found_thumbnail_source_path:
                break
        
        if found_thumbnail_source_path:
            try:
                thumbnail_extension = found_thumbnail_source_path.suffix
                destination_thumbnail_path = PROJECTS_THUMBNAILS_DIR / f"{project_name}{thumbnail_extension}"
                shutil.copy2(found_thumbnail_source_path, destination_thumbnail_path)
                print(f"  Copied thumbnail: {found_thumbnail_source_path.name} to {destination_thumbnail_path}")
            except Exception as e:
                print(f"  Error copying thumbnail for {project_name}: {e}")
        else:
            print(f"  Warning: Thumbnail not found for project {project_name}.")


# write the aggregated projects data to the main projects.json
if all_projects_data:
    with open(PROJECTS_JSON_FILE, "w") as f:
        json.dump({"projects": all_projects_data}, f, indent=2)
    print(f"\nAggregated project details stored in: {PROJECTS_JSON_FILE}")
else:
    # Create an empty projects.json if no projects with project.json were found
    with open(PROJECTS_JSON_FILE, "w") as f:
        json.dump({"projects": []}, f, indent=2)
    print(f"\nNo project data found to aggregate. Empty projects.json created at: {PROJECTS_JSON_FILE}")


print("\n----------------------------------------------------")
print("Script finished.")
print(f"Deployable project content structure generated in: {PROJECTS_CONTENT_DIR}")
print(f"All thumbnails (renamed) are in: {PROJECTS_THUMBNAILS_DIR}")
print(f"Main project index (list of all project.json contents) is at: {PROJECTS_JSON_FILE}")
print("----------------------------------------------------")