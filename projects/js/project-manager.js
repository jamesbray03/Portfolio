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

    // Add click handler to open modal
    card.addEventListener('click', () => {
        openProjectModal(data);
    });

    card.appendChild(imageElement);
    card.appendChild(titleElement);
    card.appendChild(descriptionElement);

    return card;
}

// Modal functionality
function createModal() {
    if (document.getElementById('project-modal')) {
        return; // Modal already exists
    }

    const modal = document.createElement('div');
    modal.id = 'project-modal';
    modal.className = 'project-modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modal-title"></h2>
                <button class="modal-close" id="modal-close">&times;</button>
            </div>
            <video class="modal-video" id="modal-video" controls loop muted style="display: none;">
                Your browser does not support the video tag.
            </video>
            <div class="modal-body">
                <div class="modal-readme" id="modal-readme"></div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add event listeners
    const closeBtn = modal.querySelector('#modal-close');
    closeBtn.addEventListener('click', closeProjectModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeProjectModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeProjectModal();
        }
    });
}

function openProjectModal(projectData) {
    createModal();
    
    const modal = document.getElementById('project-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalVideo = document.getElementById('modal-video');
    const modalReadme = document.getElementById('modal-readme');

    // Set title
    modalTitle.textContent = projectData.title || 'Unnamed Project';

    // Set up video
    const videoPath = `/videos/${projectData.title}.mp4`;
    modalVideo.src = videoPath;
    modalVideo.style.display = 'block';
    
    // Handle video load error
    modalVideo.onerror = function() {
        console.warn(`Video not found: ${videoPath}`);
        modalVideo.style.display = 'none';
    };

    // Load README content
    loadProjectReadme(projectData.title, modalReadme);

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

function closeProjectModal() {
    const modal = document.getElementById('project-modal');
    const modalVideo = document.getElementById('modal-video');
    
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
        
        // Pause video
        if (modalVideo) {
            modalVideo.pause();
        }
    }
}

async function loadProjectReadme(projectTitle, readmeContainer) {
    readmeContainer.innerHTML = '<div class="modal-loading">Loading README...</div>';
    
    try {
        const readmePath = `/projects/content/readmes/${projectTitle}.md`;
        const response = await fetch(readmePath);
        
        if (!response.ok) {
            throw new Error(`README not found: ${response.status}`);
        }
        
        const markdownContent = await response.text();
        const htmlContent = parseMarkdown(markdownContent);
        readmeContainer.innerHTML = htmlContent;
        
    } catch (error) {
        console.warn(`Failed to load README for ${projectTitle}:`, error);
        readmeContainer.innerHTML = '<div class="modal-error">README not available for this project.</div>';
    }
}

// Simple markdown parser
function parseMarkdown(markdown) {
    let html = markdown;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/gim, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    html = html.replace(/_(.*?)_/gim, '<em>$1</em>');
    
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');
    
    // Inline code
    html = html.replace(/`(.*?)`/gim, '<code>$1</code>');
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Images
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/gim, '<img src="$2" alt="$1">');
    
    // Lists - handle bullet points
    const lines = html.split('\n');
    let inList = false;
    let processedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        const isListItem = /^[\s]*[\*\-\+] (.*)/.test(line);
        
        if (isListItem) {
            if (!inList) {
                processedLines.push('<ul>');
                inList = true;
            }
            line = line.replace(/^[\s]*[\*\-\+] (.*)/, '<li>$1</li>');
        } else if (inList && line.trim() === '') {
            // Empty line in list, continue list
        } else if (inList) {
            // End of list
            processedLines.push('</ul>');
            inList = false;
        }
        
        processedLines.push(line);
    }
    
    // Close list if it was still open
    if (inList) {
        processedLines.push('</ul>');
    }
    
    html = processedLines.join('\n');
    
    // Line breaks and paragraphs
    html = html.replace(/\n\n+/gim, '</p><p>');
    html = html.replace(/\n/gim, '<br>');
    
    // Wrap in paragraphs
    html = '<p>' + html + '</p>';
    
    // Clean up around block elements
    html = html.replace(/<p><\/p>/gim, '');
    html = html.replace(/<p>(<h[1-6]>)/gim, '$1');
    html = html.replace(/(<\/h[1-6]>)<\/p>/gim, '$1');
    html = html.replace(/<p>(<pre>)/gim, '$1');
    html = html.replace(/(<\/pre>)<\/p>/gim, '$1');
    html = html.replace(/<p>(<ul>)/gim, '$1');
    html = html.replace(/(<\/ul>)<\/p>/gim, '$1');
    
    return html;
}