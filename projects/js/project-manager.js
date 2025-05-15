async function loadProjects() {
    const container = document.getElementById('project-container');
    const publicCounter = document.getElementById('public-count');
    const privateCounter = document.getElementById('private-count');

    let publicCount = 0;
    let privateCount = 0;
    let allPublicProjects = []; // Renamed to be more specific

    // Helper to safely update text content
    const setText = (element, text) => {
        if (element) {
            element.textContent = text;
        }
    };

    try {
        // Fetch the main projects.json which now contains all project data
        const indexResponse = await fetch('./content/projects.json'); // CHANGED: Filename
        if (!indexResponse.ok) {
            throw new Error(`Failed to load projects.json: ${indexResponse.status} ${indexResponse.statusText}`);
        }
        const allProjectsDataContainer = await indexResponse.json();

        if (!allProjectsDataContainer.projects || !Array.isArray(allProjectsDataContainer.projects)) {
            console.error('Invalid project list structure in projects.json:', allProjectsDataContainer);
            if (container) container.innerHTML = '<p>Error loading projects: Invalid data structure.</p>';
            return;
        }

        const rawProjectsData = allProjectsDataContainer.projects;

        // Filter and count public/private
        rawProjectsData.forEach(data => {
            if (!data) {
                console.warn('Encountered null project data in projects.json.');
                return;
            }

            // ASSUMPTION: Each 'data' object (from an original project.json, aggregated by Python)
            // should ideally contain 'folderName' (string, e.g., "MyProjectAlpha")
            // and 'thumbnailExtension' (string, e.g., ".png").
            // If not, createProjectCard will try fallbacks but it's less reliable.

            if (data.public === true) {
                publicCount++;
                allPublicProjects.push(data);
            } else {
                privateCount++;
            }
        });

        // Sort public projects by 'size' (difficulty) descending
        allPublicProjects.sort((a, b) => (Number(b.size) || 0) - (Number(a.size) || 0));

        setText(publicCounter, publicCount);
        setText(privateCounter, privateCount);

        if (container) {
            if (allPublicProjects.length === 0) {
                container.innerHTML = rawProjectsData.length > 0 ?
                    '<p>No public projects available at the moment.</p>' :
                    '<p>No projects found.</p>';
            } else {
                container.innerHTML = ''; // Clear any previous message
            }
        }


        // Render the first batch of public projects
        const batchSize = 10;
        renderProjectBatch(allPublicProjects.slice(0, batchSize));

        // Lazy load additional public projects on scroll
        let batchStart = batchSize;
        if (allPublicProjects.length > batchStart) {
            const scrollListener = () => {
                // Check if container is still in DOM (e.g., user hasn't navigated away)
                if (!document.body.contains(container)) {
                     window.removeEventListener('scroll', scrollListener);
                     return;
                }

                if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 150) { // Trigger a bit earlier
                    if (batchStart < allPublicProjects.length) {
                        const nextBatch = allPublicProjects.slice(batchStart, batchStart + batchSize);
                        renderProjectBatch(nextBatch);
                        batchStart += batchSize;
                        if (batchStart >= allPublicProjects.length) {
                            window.removeEventListener('scroll', scrollListener);
                        }
                    } else {
                        window.removeEventListener('scroll', scrollListener);
                    }
                }
            };
            window.addEventListener('scroll', scrollListener, { passive: true });
        }

    } catch (err) {
        console.error('Failed to load or process projects:', err);
        if (container) {
            container.innerHTML = `<p>Error loading projects: ${err.message}. Please try again later.</p>`;
        }
    }
}

function renderProjectBatch(projectsToRender) {
    const container = document.getElementById('project-container');
    if (!container) {
        console.error("Project container not found for rendering batch.");
        return;
    }
    // Use a document fragment for performance
    const fragment = document.createDocumentFragment();

    projectsToRender.forEach(data => {
        const card = createProjectCard(data);
        if (card) { // createProjectCard might return null on critical error
            fragment.appendChild(card);
        }
    });

    container.appendChild(fragment);
}

function createProjectCard(data) {
    if (!data) return null; // Should not happen if filtered earlier

    const card = document.createElement('div');
    card.className = 'project-card';

    const titleText = data.title || 'Unnamed Project';

    const titleElement = document.createElement('h3');
    titleElement.textContent = titleText;

    const descriptionElement = document.createElement('p');
    descriptionElement.textContent = data.description || 'No description provided.';

    const imageElement = document.createElement('img');
    imageElement.src = `/projects/content/thumbnails/${data.title}.webp`; // Default to .webp if extension unknown
    imageElement.alt = `${titleText} thumbnail (details missing)`;
    imageElement.alt = imageElement.alt || `${titleText} thumbnail`; // Ensure alt is set
    imageElement.className = 'project-thumbnail';
    imageElement.loading = 'lazy';

    imageElement.onerror = function() {
        // Handle broken images
        console.warn(`Failed to load image: ${this.src}.`);
        this.alt = `${titleText} (thumbnail not available)`;
    };

    card.appendChild(imageElement);
    card.appendChild(titleElement);
    card.appendChild(descriptionElement);

    return card;
}