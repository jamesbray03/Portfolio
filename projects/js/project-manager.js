async function loadProjects() {
    const container = document.getElementById('project-container');
    const publicCounter = document.getElementById('public-count');
    const privateCounter = document.getElementById('private-count');

    let publicCount = 0;
    let privateCount = 0;

    try {
        // fetch the list of project folder names
        const indexResponse = await fetch('content/index.json');
        const projectFolders = await indexResponse.json();

        // loop through each project folder and fetch its project.json
        for (const folder of projectFolders) {
            const jsonPath = `content/${folder}/project.json`;
            try {
                const projectResponse = await fetch(jsonPath);
                const data = await projectResponse.json();

                // count public/private
                if (data.public === true) {
                    publicCount++;
                    const card = createProjectCard(data, folder);
                    container.appendChild(card);
                } else {
                    privateCount++;
                }
            } catch (err) {
                console.warn(`Could not load project.json for '${folder}':`, err);
            }
        }

        // update counts
        publicCounter.textContent = publicCount;
        privateCounter.textContent = privateCount;

    } catch (err) {
        console.error('Error loading project index:', err);
        container.innerHTML = '<p>Error loading projects.</p>';
    }
}

// create a project card based on json data
function createProjectCard(data, folderName) {
    const card = document.createElement('div');
    card.className = 'project-card';

    // create elements
    const title = document.createElement('h3');
    title.textContent = data.title || folderName;

    const description = document.createElement('p');
    description.textContent = data.description || 'No description provided.';

    // optional thumbnail
    let image = null;
    image = document.createElement('img');
    image.src = `../projects/content/${folderName}/_media/thumbnail.png`;
    image.alt = `${data.title || folderName} thumbnail`;
    image.className = 'project-thumbnail';

    // wrap it all up
    if (image) card.appendChild(image);
    card.appendChild(title);
    card.appendChild(description);

    return card;
}
