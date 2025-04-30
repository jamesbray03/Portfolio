import os
import json
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "projects"))  # Changed to 'projects' folder
PORTFOLIO_DIR = os.getcwd()

def generate_portfolio_html(projects):
    all_tags = set()
    for project in projects:
        for tag in project.get("tags", []):
            all_tags.add(tag)

    public_count = sum(1 for p in projects if p.get("public", True))
    private_count = len(projects) - public_count

    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portfolio</title>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
            }}
            body {{
                display: flex;
                flex-direction: column;
                font-family: Arial, sans-serif;
                background-color: white;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 30px;
                background-color: #fff;
                flex-shrink: 0;
            }}
            .header-left {{
                display: flex;
                align-items: center;
            }}
            .header-left img {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                margin-right: 15px;
            }}
            .header-left .info h1 {{
                margin: 0;
                font-size: 1.3em;
            }}
            .header-left .info p {{
                margin: 2px 0 0;
                font-size: 0.9em;
                color: #555;
            }}
            .header-right a {{
                margin-left: 15px;
                display: inline-block;
            }}
            .header-right img {{
                width: 24px;
                height: 24px;
                vertical-align: middle;
            }}
            .header-divider {{
                height: 5px;
                width: 90%;
                margin: 0 auto;
                border-radius: 8px;
                background-color: black;
            }}
            .section-header {{
                text-align: center;
                margin: 20px 0 10px;
            }}
            .section-header h2 {{
                margin: 0;
                font-size: 1.5em;
            }}
            .section-header p {{
                margin: 5px 0 0;
                color: #666;
            }}
            .main-content {{
                display: flex;
                width: 100%;
                box-sizing: border-box;
                flex: 1 1 auto;
                overflow: hidden;
            }}
            .margin-left,
            .margin-right {{
                width: 5%;
            }}
            .filter-panel {{
                width: 25%;
                padding: 40px 20px;
                box-sizing: border-box;
                background-color: #fff;
                overflow-y: auto;
            }}
            .filter-box {{
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
            .filter-box h3 {{
                margin-top: 0;
            }}
            .tag-button, select.sort-control {{
                background-color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                margin: 6px 6px 6px 0;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
                cursor: pointer;
                transition: background-color 0.2s ease, color 0.2s ease;
                font-size: 0.9em;
                appearance: none;
                position: relative;
            }}
            .tag-button.active {{
                background-color: #007bff;
                color: white;
            }}
            select.sort-control {{
                background-image: url('data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black"><path d="M7 10l5 5 5-5z"/></svg>');
                background-repeat: no-repeat;
                background-position: right 10px center;
                background-size: 12px;
                padding-right: 30px;
            }}
            .portfolio-column {{
                width: 65%;
                padding: 40px;
                box-sizing: border-box;
                overflow-y: auto;
                position: relative;
            }}
            .portfolio-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 40px;
            }}
            .project-cell {{
                background-color: #fff;
                border-radius: 12px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
                box-sizing: border-box;
                overflow: hidden;
                display: none;
                flex-direction: column;
                transition: transform 0.3s ease-in-out;
            }}
            .project-cell.visible {{
                display: flex;
            }}
            .project-cell:hover {{
                transform: translateY(-5px);
            }}
            .image-container {{
                position: relative;
                width: 100%;
                padding-top: 70%;
                overflow: hidden;
            }}
            .image-container img {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .project-info {{
                padding: 15px 20px;
                text-align: left;
            }}
            .project-info h3 {{
                margin: 0;
                font-size: 1.1em;
                font-weight: bold;
            }}
            .project-info p {{
                margin: 8px 0 0;
                font-size: 0.9em;
                color: #666;
            }}
            .no-projects {{
                display: none;
                text-align: center;
            }}
            .no-projects img {{
                width: 60%;
                max-width: 400px;
                margin: 60px auto;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <img src="media/profile.png" alt="Profile Picture">
                <div class="info">
                    <h1>James Bray</h1>
                    <p>Engineer | Project Designer | Audio Enthusiast</p>
                </div>
            </div>
            <div class="header-right">
                <a href="https://github.com/jamesbray03" target="_blank"><img src="media/github.png" alt="GitHub"></a>
                <a href="https://linkedin.com/in/jamesbray03" target="_blank"><img src="media/linkedin.png" alt="LinkedIn"></a>
            </div>
        </div>
        <div class="header-divider"></div>
        <div class="section-header">
            <h2>Projects</h2>
            <p>Public: {public_count}, Private: {private_count}</p>
        </div>
        <div class="main-content">
            <div class="margin-left"></div>
            <div class="filter-panel">
                <div class="filter-box">
                    <h3>Sort by</h3>
                    <select id="sort-select" class="sort-control" onchange="sortProjects()">
                        <option value="title">Title</option>
                        <option value="difficulty">Difficulty</option>
                        <option value="size">Size</option>
                    </select>
                    <select id="sort-order" class="sort-control" onchange="sortProjects()">
                        <option value="asc">Ascending</option>
                        <option value="desc">Descending</option>
                    </select>
                </div>
                <div class="filter-box">
                    <h3>Filter by Tag</h3>
                    <button class="tag-button" onclick="selectAllTags()">Select All</button>
    '''
    for tag in sorted(all_tags):
        html_content += f'''
                    <button class="tag-button" onclick="toggleTag('{tag}')">{tag}</button>
        '''
    html_content += '''
                </div>
            </div>
            <div class="portfolio-column">
                <div id="no-projects" class="no-projects">
                    <img src="media/no_projects.png" alt="No projects" style="width: 200px; max-width: 400px; margin: 60px auto;">
                    <h2>No projects found</h2><p>Select more tags to view projects</p>
                </div>
                <div class="portfolio-container" id="project-grid">
    '''

    for project in projects:
        tags_str = ",".join(project.get("tags", []))
        description = project.get("description", "No description yet.")
        html_content += f'''
                    <div class="project-cell" data-tags="{tags_str}" data-title="{project['title'].lower()}" data-difficulty="{project.get('difficulty', 5)}" data-size="{project.get('size', 5)}">
                        <div class="image-container">
                            <img src="../{project['title']}/media/thumbnail.png" alt="{project['title']}">
                        </div>
                        <div class="project-info">
                            <h3>{project['title']}</h3>
                            <p>{description}</p>
                        </div>
                    </div>
        '''

    html_content += '''
                </div>
            </div>
            <div class="margin-right"></div>
        </div>
        <script>
            const selectedTags = new Set();

            function toggleTag(tag) {
                const button = document.querySelector(`.tag-button[onclick="toggleTag('${tag}')"]`);
                button.classList.toggle('active');
                if (selectedTags.has(tag)) {
                    selectedTags.delete(tag);
                } else {
                    selectedTags.add(tag);
                }
                filterProjects();
            }

            function selectAllTags() {
                const buttons = document.querySelectorAll('.tag-button[onclick^="toggleTag"]');
                const selecting = selectedTags.size !== buttons.length;
                selectedTags.clear();
                buttons.forEach(btn => {
                    const tag = btn.textContent;
                    if (selecting) {
                        selectedTags.add(tag);
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
                filterProjects();
            }

            function filterProjects() {
                const projects = document.querySelectorAll('.project-cell');
                let visibleCount = 0;
                projects.forEach(project => {
                    const tags = project.getAttribute('data-tags').split(',');
                    const match = Array.from(selectedTags).some(tag => tags.includes(tag));
                    if (selectedTags.size === 0) {
                        project.classList.remove('visible');
                    } else if (match) {
                        project.classList.add('visible');
                        visibleCount++;
                    } else {
                        project.classList.remove('visible');
                    }
                });
                document.getElementById("no-projects").style.display = visibleCount === 0 ? "block" : "none";
                sortProjects();
            }

            function sortProjects() {
                const key = document.getElementById('sort-select').value;
                const order = document.getElementById('sort-order').value;
                const container = document.getElementById('project-grid');
                const items = Array.from(container.querySelectorAll('.project-cell.visible'));

                items.sort((a, b) => {
                    let valA = a.dataset[key];
                    let valB = b.dataset[key];
                    if (key === 'title') {
                        return order === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
                    } else {
                        valA = parseInt(valA);
                        valB = parseInt(valB);
                        return order === 'asc' ? valA - valB : valB - valA;
                    }
                });

                items.forEach(item => container.appendChild(item));
            }
        </script>
    </body>
    </html>
    '''

    return html_content


def load_projects():
    projects = []
    for project_folder in os.listdir(BASE_DIR):
        project_path = os.path.join(BASE_DIR, project_folder)
        if os.path.isdir(project_path):
            project_file = os.path.join(project_path, 'project.json')
            if os.path.exists(project_file):
                with open(project_file, 'r') as file:
                    try:
                        project_data = json.load(file)
                        project_data['folder'] = project_folder
                        projects.append(project_data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON for {project_file}")
    return projects


if __name__ == "__main__":
    projects = load_projects()
    html_output = generate_portfolio_html(projects)
    with open(os.path.join(PORTFOLIO_DIR, "index.html"), "w") as file:
        file.write(html_output)
    print("Portfolio HTML has been generated.")
