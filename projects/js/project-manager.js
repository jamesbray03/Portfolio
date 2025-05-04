async function loadProjects() {
    const container = document.getElementById('project-container');
    const publicCounter = document.getElementById('public-count');
    const privateCounter = document.getElementById('private-count');

    let publicCount = 0;
    let privateCount = 0;
    let allProjects = [];

    try {
        // fetch all project data at once from projects.json
        const indexResponse = await fetch('/projects/content/projects.json');
        const projectsData = await indexResponse.json(); // projects: [{ title, description, public, folderName, etc. }]

        // count public/private and store them in allProjects
        projectsData.projects.forEach(data => {
            if (data.public === true) {
                publicCount++;
                allProjects.push(data);  // store projects for rendering in batch
            } else {
                privateCount++;
            }
        });

        // update the public/private count
        publicCounter.textContent = publicCount;
        privateCounter.textContent = privateCount;

        // Render the first batch of projects (e.g., first 10 projects)
        renderProjectBatch(allProjects.slice(0, 10));  // Render the first 10

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

// Function to render a batch of projects
function renderProjectBatch(projects) {
    const container = document.getElementById('project-container');
    const fragment = document.createDocumentFragment();  // Avoid reflow/repaint by using a fragment

    projects.forEach(data => {
        const card = createProjectCard(data);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);  // Append all cards in one go
}

// Function to create a project card
function createProjectCard(data) {
    const card = document.createElement('div');
    card.className = 'project-card';

    // Create elements for title and description
    const title = document.createElement('h3');
    title.textContent = data.title || 'Unnamed Project';

    const description = document.createElement('p');
    description.textContent = data.description || 'No description provided.';

    // Optional thumbnail image
    const image = document.createElement('img');
    image.src = `/projects/content/${data.title}/_media/thumbnail.webp`;  // Updated path for project-specific images
    image.alt = `${data.title || 'Unnamed Project'} thumbnail`;
    image.className = 'project-thumbnail';
    image.loading = 'lazy';  // Lazy load the images

    // Append the image and text to the card
    if (image) card.appendChild(image);
    card.appendChild(title);
    card.appendChild(description);

    return card;
}
