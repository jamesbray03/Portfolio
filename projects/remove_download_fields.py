import json

def remove_download_fields():
    """Remove download fields from projects_master.json"""
    
    # Read the current projects_master.json
    with open('content/projects_master.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Remove download fields from each project
    for project in data['projects']:
        if 'download' in project:
            del project['download']
    
    # Write the updated file
    with open('content/projects_master.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Removed download fields from {len(data['projects'])} projects")

if __name__ == "__main__":
    remove_download_fields()