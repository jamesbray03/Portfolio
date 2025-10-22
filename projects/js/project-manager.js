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
        // Fetch the master projects file which now contains all project data
        const indexResponse = await fetch('content/projects_master.json');
        if (!indexResponse.ok) {
            throw new Error(`Failed to load projects_master.json: ${indexResponse.status} ${indexResponse.statusText}`);
        }
        const allProjectsDataContainer = await indexResponse.json();

        if (!allProjectsDataContainer.projects || !Array.isArray(allProjectsDataContainer.projects)) {
            console.error('Invalid project list structure in projects_master.json:', allProjectsDataContainer);
            if (container) container.innerHTML = '<p>Error loading projects: Invalid data structure.</p>';
            return;
        }

        const rawProjectsData = allProjectsDataContainer.projects;

        // Filter and count public/private
        rawProjectsData.forEach(data => {
            if (!data) {
                console.warn('Encountered null project data in projects_master.json.');
                return;
            }

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
    // Use safe_name to construct thumbnail path
    const thumbnailName = `${data.safe_name}.webp`;
    imageElement.src = `content/thumbnails/${thumbnailName}`;
    imageElement.alt = `${titleText} thumbnail`;
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
            <div class="modal-video-container" id="modal-video-container" style="display: none;">
                <iframe class="modal-youtube" id="modal-youtube" 
                    width="100%" height="315" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen
                    style="display: none;">
                </iframe>
                <video class="modal-video" id="modal-video" controls loop muted style="display: none;">
                    Your browser does not support the video tag.
                </video>
            </div>
            <div class="modal-body">
                <div class="modal-readme" id="modal-readme"></div>
            </div>
            <div class="modal-download-bar" id="modal-download-bar" style="display: none;">
                <a class="modal-download-button" id="modal-download-button" href="#" download>
                    Download Project
                </a>
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

async function openProjectModal(projectData) {
    createModal();
    
    const modal = document.getElementById('project-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalVideoContainer = document.getElementById('modal-video-container');
    const modalYoutube = document.getElementById('modal-youtube');
    const modalVideo = document.getElementById('modal-video');
    const modalReadme = document.getElementById('modal-readme');
    const modalDownloadBar = document.getElementById('modal-download-bar');
    const modalDownloadButton = document.getElementById('modal-download-button');

    // Set title
    modalTitle.textContent = projectData.title || 'Unnamed Project';

    // Load YouTube video if available
    const youtubeVideoId = await loadYouTubeVideo(projectData.title);
    
    if (youtubeVideoId) {
        // Show YouTube video with autoplay and loop
        const embedUrl = `https://www.youtube.com/embed/${youtubeVideoId}?autoplay=1&loop=1&playlist=${youtubeVideoId}&mute=1&controls=1&modestbranding=1&rel=0`;
        modalYoutube.src = embedUrl;
        modalYoutube.style.display = 'block';
        modalVideoContainer.style.display = 'block';
        modalVideo.style.display = 'none';
    } else {
        // Fall back to local video if no YouTube video
        const videoPath = `/videos/${projectData.title}.mp4`;
        modalVideo.src = videoPath;
        modalVideo.style.display = 'block';
        modalVideoContainer.style.display = 'block';
        modalYoutube.style.display = 'none';
        
        // Handle video load error
        modalVideo.onerror = function() {
            console.warn(`Video not found: ${videoPath}`);
            modalVideoContainer.style.display = 'none';
        };
    }

    // Load README content
    const safeName = projectData.safe_name || projectData.title.replace(/\s+/g, '_').replace(/[^A-Za-z0-9_]/g, '_');
    console.log('Project title:', projectData.title);
    console.log('Project safe_name:', projectData.safe_name);
    console.log('Using safeName:', safeName);
    loadProjectReadme(safeName, modalReadme);

    // Check for downloadable file and set up download button
    setupDownload(projectData, modalDownloadBar, modalDownloadButton);

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

function closeProjectModal() {
    const modal = document.getElementById('project-modal');
    const modalVideo = document.getElementById('modal-video');
    const modalYoutube = document.getElementById('modal-youtube');
    
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
        
        // Pause video
        if (modalVideo) {
            modalVideo.pause();
        }
        
        // Stop YouTube video by clearing src
        if (modalYoutube) {
            modalYoutube.src = '';
        }
    }
}

// Load YouTube video URL for a project
async function loadYouTubeVideo(projectTitle) {
    try {
        const response = await fetch('content/youtube_links.json');
        if (!response.ok) {
            console.warn('YouTube links file not found');
            return null;
        }
        
        const data = await response.json();
        
        // Look for project directly in the JSON (skip _instructions)
        const youtubeUrl = data[projectTitle];
        
        if (!youtubeUrl || youtubeUrl.startsWith('_')) {
            return null;
        }
        
        // Extract video ID from various YouTube URL formats
        const videoId = extractYouTubeVideoId(youtubeUrl);
        return videoId;
        
    } catch (error) {
        console.warn('Failed to load YouTube links:', error);
        return null;
    }
}

// Extract YouTube video ID from URL
function extractYouTubeVideoId(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/watch.*[?&]v=([^&\n?#]+)/
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match && match[1]) {
            return match[1];
        }
    }
    
    console.warn('Could not extract YouTube video ID from URL:', url);
    return null;
}

async function loadProjectReadme(safeName, readmeContainer) {
    readmeContainer.innerHTML = '<div class="modal-loading">Loading README...</div>';
    
    try {
        const readmePath = `/projects/content/readmes/${safeName}.md`;
        const response = await fetch(readmePath);
        
        if (!response.ok) {
            throw new Error(`README not found: ${response.status}`);
        }
        
        const markdownContent = await response.text();
        const htmlContent = parseMarkdown(markdownContent);
        readmeContainer.innerHTML = htmlContent;
        
    } catch (error) {
        console.warn(`Failed to load README for ${safeName}:`, error);
        readmeContainer.innerHTML = '<div class="modal-error">README not available for this project.</div>';
    }
}

function setupDownload(projectData, downloadBar, downloadButton) {
    // Use safe_name to construct download path (files are named and stored correctly)
    const downloadFileName = `${projectData.safe_name}.zip`;
    
    // Use GitHub raw content URL to properly serve LFS files
    // GitHub Pages serves LFS pointer files, but raw.githubusercontent.com serves the actual files
    const githubUser = 'jamesbray03';
    const githubRepo = 'Portfolio';
    const branch = 'main';
    const downloadPath = `https://github.com/${githubUser}/${githubRepo}/raw/${branch}/projects/content/downloads/${downloadFileName}`;
    
    // Check if file exists
    checkAndSetupDownload(downloadPath, downloadFileName, downloadBar, downloadButton);
}

async function checkAndSetupDownload(downloadPath, downloadFileName, downloadBar, downloadButton) {
    try {
        const response = await fetch(downloadPath, { method: 'HEAD' });
        
        if (response.ok) {
            // File exists, show download bar and set up button
            downloadButton.href = downloadPath;
            downloadButton.download = downloadFileName;
            downloadButton.textContent = 'Download Project';
            downloadBar.style.display = 'flex';
        } else {
            // File doesn't exist, hide download bar
            downloadBar.style.display = 'none';
        }
    } catch (error) {
        console.warn(`Could not check for download file ${downloadFileName}:`, error);
        downloadBar.style.display = 'none';
    }
}

// Simple markdown parser
function parseMarkdown(markdown) {
    let html = markdown;
    
    // Headers (process first)
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold (process before other formatting)
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
    
    // Handle lists - both bullet points and dashes
    const lines = html.split('\n');
    let inList = false;
    let processedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        const isListItem = /^[\*\-\+] (.*)/.test(line);
        
        if (isListItem) {
            if (!inList) {
                processedLines.push('<ul>');
                inList = true;
            }
            line = line.replace(/^[\*\-\+] (.*)/, '<li>$1</li>');
        } else if (inList && line === '') {
            // Empty line in list, continue list
            continue;
        } else if (inList && line !== '') {
            // End of list
            processedLines.push('</ul>');
            inList = false;
        }
        
        if (line !== '' || !inList) {
            processedLines.push(line);
        }
    }
    
    // Close list if it was still open
    if (inList) {
        processedLines.push('</ul>');
    }
    
    html = processedLines.join('\n');
    
    // Handle paragraphs - split by double newlines but preserve structure
    const sections = html.split('\n\n');
    const processedSections = [];
    
    for (let section of sections) {
        section = section.trim();
        if (section === '') continue;
        
        // Don't wrap headers, lists, code blocks, or horizontal rules in paragraphs
        if (section.startsWith('<h') || section.startsWith('<ul') || 
            section.startsWith('<pre') || section.startsWith('---') ||
            section.includes('<ul>') || section.includes('<h')) {
            processedSections.push(section);
        } else if (section.includes('<br>')) {
            // Already has line breaks, don't add paragraph
            processedSections.push(section);
        } else {
            // Regular text paragraph
            processedSections.push(`<p>${section}</p>`);
        }
    }
    
    html = processedSections.join('\n\n');
    
    // Clean up extra line breaks within elements
    html = html.replace(/\n+/g, '\n');
    
    // Handle horizontal rules
    html = html.replace(/^---$/gm, '<hr>');
    
    return html;
}