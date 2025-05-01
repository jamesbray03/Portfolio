async function loadProjects() {
    const container = document.getElementById('project-container');
    const publicCounter = document.getElementById('public-count');
    const privateCounter = document.getElementById('private-count');

    let publicCount = 0;
    let privateCount = 0;
    let allProjects = [];

    try {
        // fetch all project data at once (if available as a combined JSON)
        const indexResponse = await fetch('content/projects.json');
        const projectsData = await indexResponse.json(); // {folders: [...], projects: [...]}

        // loop through each project and create a card
        projectsData.projects.forEach(data => {
            // count public/private
            if (data.public === true) {
                publicCount++;
                allProjects.push(data);  // store projects to render in batch
            } else {
                privateCount++;
            }
        });

        // update counts
        publicCounter.textContent = publicCount;
        privateCounter.textContent = privateCount;

        // Render all projects in batches (batch size: 10)
        renderProjectBatch(allProjects.slice(0, 10)); // Load first 10 projects

        // lazy load additional projects as user scrolls
        let batchStart = 10;
        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 100) {
                const nextBatch = allProjects.slice(batchStart, batchStart + 10);
                renderProjectBatch(nextBatch);
                batchStart += 10;
            }
        });

    } catch (err) {
        console.error('Error loading project index:', err);
        container.innerHTML = '<p>Error loading projects.</p>';
    }
}

// render a batch of projects
function renderProjectBatch(projects) {
    const container = document.getElementById('project-container');
    const fragment = document.createDocumentFragment();  // Use a fragment to avoid reflow/repaint on each append

    projects.forEach(data => {
        const card = createProjectCard(data);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);  // Append all cards at once
}

// create a project card based on json data
function createProjectCard(data) {
    const card = document.createElement('div');
    card.className = 'project-card';

    // create elements
    const title = document.createElement('h3');
    title.textContent = data.title || 'Untitled Project';

    const description = document.createElement('p');
    description.textContent = data.description || 'No description provided.';

    // optional thumbnail
    let image = null;
    if (data.thumbnail) {
        image = document.createElement('img');
        image.src = data.thumbnail;  // Assuming thumbnails are optimized (e.g., smaller resolution)
        image.alt = `${data.title} thumbnail`;
        image.className = 'project-thumbnail';
        image.loading = 'lazy';  // Lazy loading for image
    }

    // wrap it all up
    if (image) card.appendChild(image);
    card.appendChild(title);
    card.appendChild(description);

    return card;
}
