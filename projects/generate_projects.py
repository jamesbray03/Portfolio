import os
import json
from pathlib import Path

def generate_portfolio_html(projects):
    all_tags = set()
    all_contexts = set()
    all_types = set()
    for project in projects:
        all_tags.update(project.get("tags", []))
        if project.get("context"): all_contexts.add(project["context"])
        if project.get("content_type"): all_types.add(project["content_type"])

    public_count = sum(1 for p in projects if p.get("public", True))
    private_count = len(projects) - public_count

    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Projects</title>
        <link rel="preload" href="../_media/fonts/HarmonyOS.woff2" as="font" type="font/woff2" crossorigin="anonymous">
        <style>
            @font-face {{
                font-family: 'HarmonyOS';
                src: url('../_media/fonts/HarmonyOS.woff2') format('woff2');
                font-weight: normal;
                font-style: normal;
                font-display: swap;
            }}
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
                font-family: 'HarmonyOS', sans-serif;
            }}
            body {{
                display: flex;
                flex-direction: column;
                background-color: white;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 30px;
                background-color: #f0f0f0;
                flex-shrink: 0;
                font-family: 'HarmonyOS', sans-serif;
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
                font-family: 'HarmonyOS', sans-serif;
            }}
            .header-left .info p {{
                margin: 2px 0 0;
                font-size: 0.9em;
                color: #555;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .header-right a {{
                margin-left: 15px;
            }}
            .header-right img {{
                width: 24px;
                height: 24px;
            }}
            .header-divider {{
                height: 6px;
                width: 20%;
                margin: 0 0 10px 1%;
                border-radius: 8px;
                background-color: black;
            }}
            .section-header {{
                font-size: 1.2em;
                margin-left: 5%;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .section-header h2 {{
                font-size: 2em;
                margin: 0 0 5px 0;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .section-header p {{
                margin: 0;
                color: #666;
                font-family: 'HarmonyOS', sans-serif;
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
                background-color: #fafafa;
                overflow-y: auto;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .filter-box {{
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .filter-box h3 {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 0;
                font-family: 'HarmonyOS', sans-serif;
            }}
            select.sort-control {{
                background-image: url('data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black"><path d="M7 10l5 5 5-5z"/></svg>');
                background-repeat: no-repeat;
                background-position: right 10px center;
                background-size: 12px;
                padding-right: 30px;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .tag-button, select.sort-control {{
                background-color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                margin: 6px 6px 6px 0;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                cursor: pointer;
                transition: background-color 0.2s ease, color 0.2s ease;
                font-size: 0.8em;
                appearance: none;
                position: relative;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .tag-button.active {{
                background-color: #007bff;
                color: white;
            }}
            .portfolio-column {{
                width: 65%;
                padding: 40px;
                box-sizing: border-box;
                overflow-y: auto;
                position: relative;
                font-family: 'HarmonyOS', sans-serif;
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
                overflow: hidden;
                display: none;
                flex-direction: column;
                transition: transform 0.3s ease-in-out;
                max-width: 300px;
                font-family: 'HarmonyOS', sans-serif;
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
                font-family: 'HarmonyOS', sans-serif;
            }}
            .project-info h3 {{
                margin: 0;
                font-size: 1.1em;
                font-weight: bold;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .project-info p {{
                margin: 8px 0 0;
                font-size: 0.9em;
                color: #666;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .no-projects {{
                display: none;
                text-align: center;
                font-family: 'HarmonyOS', sans-serif;
            }}
            .no-projects img {{
                width: 60%;
                max-width: 160px;
                margin: 60px auto;
            }}
        </style>
    </head>
    <body>
    
        <!--
        <div class="header">
            <div class="header-left">
                <img src="../_media/profile.png" alt="Profile Picture">
                <div class="info">
                    <h1>James Bray</h1>
                    <p>Engineer | Project Designer | Audio Enthusiast</p>
                </div>
            </div>
            <div class="header-right">
                <a href="https://github.com/jamesbray" target="_blank"><img src="../_media/github.png" alt="GitHub"></a>
                <a href="https://linkedin.com/in/jamesbray" target="_blank"><img src="../_media/linkedin.png" alt="LinkedIn"></a>
            </div>
        </div>
        <div class="header-divider"></div>
        -->

        <div class="section-header">
            <br>
            <h2>Projects</h2>
            <p>Public: {public_count}, Private: {private_count}</p>
            <p>Here are all the various projects I've worked on over the years, feel free to browse through. More content coming soon.</p>
            <br>
        </div>
        <div class="main-content">
            <div class="margin-left"></div>
            <div class="filter-panel">
    '''

    # sort options
    html_content += '''
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
                '''

    # generate all filters: tags, context, content_type
    for filter_key, filter_title, values in [
        ("tag", "Filter by Tag", sorted(all_tags)),
        ("context", "Filter by Context", sorted(all_contexts)),
        ("type", "Filter by Content", sorted(all_types)),
    ]:
        html_content += f'''
                <div class="filter-box">
                    <h3>{filter_title}
                        <button class="tag-button" onclick="selectAll('{filter_key}')">Select All</button>
                    </h3>
        '''
        for val in values:
            html_content += f'''
                    <button class="tag-button" data-group="{filter_key}" onclick="toggleValue('{filter_key}', '{val}')">{val}</button>
            '''
        html_content += '</div>'

    html_content += '''
            </div>
            <div class="portfolio-column">
                <div id="no-projects" class="no-projects">
                    <img src="_media/no_projects.png" alt="No projects">
                    <h2>No projects found</h2><p>Select more filters to view projects</p>
                </div>
                <div class="portfolio-container" id="project-grid">
    '''

    for project in projects:
        tags = ",".join(project.get("tags", []))
        context = project.get("context", "")
        content_type = project.get("content_type", "")
        description = project.get("description", "No description yet.")
        html_content += f'''
                    <div class="project-cell"
                         data-tags="{tags}"
                         data-context="{context}"
                         data-type="{content_type}"
                         data-title="{project['title'].lower()}"
                         data-difficulty="{project.get('difficulty', 5)}"
                         data-size="{project.get('size', 5)}">
                        <div class="image-container">
                            <img src="content/{project['title']}/_media/thumbnail.png" alt="{project['title']}">
                        </div>
                        <div class="project-info">
                            <h3>{project['title']}</h3>
                            <p>{description}</p>
                        </div>
                    </div>
        '''

    # close containers and add scripts
    html_content += '''
                </div>
            </div>
            <div class="margin-right"></div>
        </div>
        <script>
            const selected = {
                tag: new Set(),
                context: new Set(),
                type: new Set()
            };

            function toggleValue(group, value) {
                const btn = [...document.querySelectorAll(`.tag-button[data-group="${group}"]`)].find(b => b.textContent === value);
                btn.classList.toggle("active");
                if (selected[group].has(value)) {
                    selected[group].delete(value);
                } else {
                    selected[group].add(value);
                }
                filterProjects();
            }

            function selectAll(group) {
                const buttons = document.querySelectorAll(`.tag-button[data-group="${group}"]`);
                const allSelected = selected[group].size === buttons.length;
                selected[group].clear();
                buttons.forEach(btn => {
                    const val = btn.textContent;
                    if (!allSelected) {
                        selected[group].add(val);
                        btn.classList.add("active");
                    } else {
                        btn.classList.remove("active");
                    }
                });
                filterProjects();
            }

            function filterProjects() {
                const projects = document.querySelectorAll('.project-cell');
                let visible = 0;

                const tagButtons = document.querySelectorAll('.tag-button[data-group="tag"]');
                const allTags = Array.from(tagButtons).map(btn => btn.textContent);
                const allTagsSelected = selected.tag.size === allTags.length;

                projects.forEach(p => {
                    const tagSet = new Set(p.dataset.tags.split(',').filter(Boolean));
                    const context = p.dataset.context;
                    const type = p.dataset.type;

                    // tag filtering logic
                    const tagMatch = allTagsSelected || [...selected.tag].some(t => tagSet.has(t));
                    const contextMatch = selected.context.size === 0 || selected.context.has(context);
                    const typeMatch = selected.type.size === 0 || selected.type.has(type);

                    if (tagMatch && contextMatch && typeMatch) {
                        p.classList.add('visible');
                        visible++;
                    } else {
                        p.classList.remove('visible');
                    }
                });

                document.getElementById("no-projects").style.display = visible === 0 ? "block" : "none";
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

            window.onload = () => {
                selectAll('tag');
                selectAll('context');
                selectAll('type');
            };
        </script>
    </body>
    </html>
    '''

    # write to portfolio/projects/index.html
    output_dir = os.path.dirname(__file__)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Portfolio page generated at {os.path.join(output_dir, 'index.html')}")

def main():
    root_dir = Path(__file__).resolve().parent / "content"
    projects = []

    for item in root_dir.iterdir():
        if item.is_dir():
            json_path = item / "project.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["title"] = item.name
                    projects.append(data)

    generate_portfolio_html(projects)

if __name__ == "__main__":
    main()