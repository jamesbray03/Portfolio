/**
 * Project Manager - Portfolio Website
 * ====================================
 * Handles loading, filtering, and displaying projects with:
 * - Category filtering with animated tabs
 * - Adaptive media display (YouTube, PDF, carousel, thumbnail)
 * - Fast fade animations for filtering
 * - Download button support
 */

// Global state
let allProjects = [];
let currentCategory = 'all';

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    setupCategoryFilters();
});

/**
 * Load projects from the generated JSON file
 */
async function loadProjects() {
    const container = document.getElementById('project-container');
    const visibleCount = document.getElementById('visible-count');
    const totalCount = document.getElementById('total-count');

    try {
        const response = await fetch('content/projects_data.json');
        if (!response.ok) {
            throw new Error(`Failed to load projects: ${response.status}`);
        }
        
        const data = await response.json();
        allProjects = data.projects.filter(p => p.public === true);
        
        // Update counts
        if (totalCount) totalCount.textContent = allProjects.length;
        if (visibleCount) visibleCount.textContent = allProjects.length;
        
        // Render all projects initially
        renderProjects(allProjects);
        
    } catch (err) {
        console.error('Failed to load projects:', err);
        if (container) {
            container.innerHTML = `<p class="error-message">Error loading projects: ${err.message}</p>`;
        }
    }
}

/**
 * Setup category filter tab click handlers
 */
function setupCategoryFilters() {
    const tabs = document.querySelectorAll('.category-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const category = tab.dataset.category;
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Filter projects
            filterByCategory(category);
        });
    });
}

/**
 * Filter projects by category with fast fade animation
 */
function filterByCategory(category) {
    currentCategory = category;
    const container = document.getElementById('project-container');
    const visibleCount = document.getElementById('visible-count');
    
    // Get filtered projects
    const filtered = category === 'all' 
        ? allProjects 
        : allProjects.filter(p => p.category === category);
    
    // Update count
    if (visibleCount) visibleCount.textContent = filtered.length;
    
    // Animate out existing cards
    const cards = container.querySelectorAll('.project-card');
    cards.forEach(card => {
        card.classList.add('fade-out');
    });
    
    // After quick fade, update content
    setTimeout(() => {
        renderProjects(filtered);
        
        // Animate in new cards
        requestAnimationFrame(() => {
            const newCards = container.querySelectorAll('.project-card');
            newCards.forEach((card, index) => {
                card.style.animationDelay = `${index * 30}ms`;
                card.classList.add('fade-in');
            });
        });
    }, 150);
}

/**
 * Render project cards to the container
 */
function renderProjects(projects) {
    const container = document.getElementById('project-container');
    if (!container) return;
    
    if (projects.length === 0) {
        container.innerHTML = '<p class="no-projects">No projects in this category.</p>';
        return;
    }
    
    container.innerHTML = '';
    const fragment = document.createDocumentFragment();
    
    projects.forEach(project => {
        const card = createProjectCard(project);
        if (card) fragment.appendChild(card);
    });
    
    container.appendChild(fragment);
}

/**
 * Create a project card element
 */
function createProjectCard(data) {
    const card = document.createElement('div');
    card.className = 'project-card';
    card.dataset.category = data.category || 'other';

    const titleText = data.title || 'Unnamed Project';

    // Header (date + category)
    const header = document.createElement('div');
    header.className = 'project-card-header';

    // Date
    const dateElement = document.createElement('span');
    dateElement.className = 'project-date';
    if (data.date && data.date.trim()) {
        dateElement.textContent = formatDate(data.date);
    } else {
        dateElement.textContent = '';
    }

    // Category badge
    const badge = document.createElement('span');
    badge.className = `category-badge ${data.category || 'other'}`;
    badge.textContent = getCategoryLabel(data.category);

    header.appendChild(dateElement);
    header.appendChild(badge);

    // Thumbnail
    const imageElement = document.createElement('img');
    const thumbnailName = `${data.safe_name}.webp`;
    imageElement.src = `content/thumbnails/${thumbnailName}`;
    imageElement.alt = `${titleText} thumbnail`;
    imageElement.className = 'project-thumbnail';
    imageElement.loading = 'lazy';
    imageElement.onerror = function() {
        this.src = '../content/images/placeholder.webp';
        this.alt = `${titleText} (no thumbnail)`;
    };

    // Title
    const titleElement = document.createElement('h3');
    titleElement.textContent = titleText;

    // Description
    const descriptionElement = document.createElement('p');
    descriptionElement.textContent = data.description || 'No description provided.';

    // Click handler
    card.addEventListener('click', () => openProjectModal(data));

    // Build card: header above image
    card.appendChild(header);
    card.appendChild(imageElement);
    card.appendChild(titleElement);
    card.appendChild(descriptionElement);

    return card;
}

/**
 * Format date from YYYY-MM to readable format
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    const [year, month] = dateStr.split('-');
    if (!year) return '';
    if (!month) return year;
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthName = months[parseInt(month) - 1];
    return `${monthName} ${year}`;
}

/**
 * Get human-readable category label
 */
function getCategoryLabel(category) {
    const labels = {
        'academic': 'Academic',
        'hardware': 'Hardware',
        'games': 'Games & Sims',
        'applications': 'Apps',
        'other': 'Other'
    };
    return labels[category] || 'Other';
}

// ============================================
// Modal Functionality
// ============================================

/**
 * Create the modal element if it doesn't exist
 */
function createModal() {
    if (document.getElementById('project-modal')) return;
    
    const modal = document.createElement('div');
    modal.id = 'project-modal';
    modal.className = 'project-modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modal-title"></h2>
                <button class="modal-close" id="modal-close">&times;</button>
            </div>
            <div class="modal-media-container" id="modal-media-container">
                <!-- Dynamic media content goes here -->
            </div>
            <div class="modal-body">
                <div class="modal-readme" id="modal-readme"></div>
            </div>
            <div class="modal-footer" id="modal-footer" style="display: none;">
                <a class="modal-download-button" id="modal-download-button" href="#" download>
                    📥 Download Project
                </a>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listeners
    const closeBtn = modal.querySelector('#modal-close');
    closeBtn.addEventListener('click', closeProjectModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeProjectModal();
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeProjectModal();
        }
    });
}

/**
 * Open the project modal with adaptive media display
 */
async function openProjectModal(projectData) {
    createModal();
    
    const modal = document.getElementById('project-modal');
    const modalTitle = document.getElementById('modal-title');
    const mediaContainer = document.getElementById('modal-media-container');
    const modalReadme = document.getElementById('modal-readme');
    const modalFooter = document.getElementById('modal-footer');
    const modalDownloadButton = document.getElementById('modal-download-button');
    
    // Set title
    modalTitle.textContent = projectData.title || 'Unnamed Project';
    
    // Setup adaptive media
    await setupModalMedia(projectData, mediaContainer);
    
    // Load README
    await loadProjectReadme(projectData.safe_name, modalReadme);
    
    // Setup download button
    if (projectData.has_download && projectData.download_file) {
        modalDownloadButton.href = `content/downloads/${projectData.download_file}`;
        modalDownloadButton.download = projectData.download_file;
        modalFooter.style.display = 'flex';
    } else {
        modalFooter.style.display = 'none';
    }
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Setup the modal media based on available content
 */
async function setupModalMedia(projectData, container) {
    container.innerHTML = '';
    container.style.display = 'block';
    
    const mediaType = projectData.media_type;
    
    if (mediaType === 'youtube_gallery' && projectData.youtube && projectData.gallery_images?.length > 0) {
        // YouTube video + gallery images in carousel
        createMixedCarousel(projectData, container);
    } else if (mediaType === 'youtube' && projectData.youtube) {
        // YouTube video only
        const videoId = extractYouTubeVideoId(projectData.youtube);
        if (videoId) {
            const iframe = document.createElement('iframe');
            iframe.className = 'modal-youtube';
            iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&playlist=${videoId}&controls=1&modestbranding=1&rel=0`;
            iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            iframe.allowFullscreen = true;
            container.appendChild(iframe);
        }
    } else if (mediaType === 'pdf' && projectData.pdf_file) {
        // PDF viewer with mobile-friendly fallback
        const pdfPath = `content/downloads/${projectData.pdf_file}`;
        const pdfContainer = document.createElement('div');
        pdfContainer.className = 'pdf-viewer-container';
        
        // Use object tag for better mobile support
        const pdfViewer = document.createElement('object');
        pdfViewer.className = 'modal-pdf';
        pdfViewer.data = pdfPath;
        pdfViewer.type = 'application/pdf';
        
        // Fallback link for devices that can't display PDF inline
        const fallback = document.createElement('div');
        fallback.className = 'pdf-fallback';
        fallback.innerHTML = `
            <a href="${pdfPath}" target="_blank" class="pdf-download-link">Open PDF in new tab</a>
        `;
        pdfViewer.appendChild(fallback);
        
        pdfContainer.appendChild(pdfViewer);
        container.appendChild(pdfContainer);
    } else if (mediaType === 'gallery' && projectData.gallery_images?.length > 0) {
        // Image carousel
        createCarousel(projectData, container);
    } else if (projectData.has_thumbnail) {
        // Fallback to thumbnail
        const img = document.createElement('img');
        img.className = 'modal-thumbnail';
        img.src = `content/thumbnails/${projectData.safe_name}.webp`;
        img.alt = projectData.title;
        container.appendChild(img);
    } else {
        container.style.display = 'none';
    }
}

/**
 * Create an image carousel for gallery images
 */
function createCarousel(projectData, container) {
    const carousel = document.createElement('div');
    carousel.className = 'carousel';
    
    const images = projectData.gallery_images;
    let currentIndex = 0;
    
    // Image container
    const imgContainer = document.createElement('div');
    imgContainer.className = 'carousel-images';
    
    const img = document.createElement('img');
    img.className = 'carousel-image';
    img.src = `content/gallery/${projectData.safe_name}/${images[0]}`;
    img.alt = `${projectData.title} - Image 1`;
    imgContainer.appendChild(img);
    
    // Navigation buttons
    const prevBtn = document.createElement('button');
    prevBtn.className = 'carousel-btn prev';
    prevBtn.innerHTML = '❮';
    prevBtn.onclick = (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateCarousel();
    };
    
    const nextBtn = document.createElement('button');
    nextBtn.className = 'carousel-btn next';
    nextBtn.innerHTML = '❯';
    nextBtn.onclick = (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex + 1) % images.length;
        updateCarousel();
    };
    
    // Dots indicator
    const dots = document.createElement('div');
    dots.className = 'carousel-dots';
    images.forEach((_, i) => {
        const dot = document.createElement('span');
        dot.className = `carousel-dot ${i === 0 ? 'active' : ''}`;
        dot.onclick = (e) => {
            e.stopPropagation();
            currentIndex = i;
            updateCarousel();
        };
        dots.appendChild(dot);
    });
    
    function updateCarousel() {
        img.src = `content/gallery/${projectData.safe_name}/${images[currentIndex]}`;
        img.alt = `${projectData.title} - Image ${currentIndex + 1}`;
        dots.querySelectorAll('.carousel-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === currentIndex);
        });
    }
    
    carousel.appendChild(prevBtn);
    carousel.appendChild(imgContainer);
    carousel.appendChild(nextBtn);
    carousel.appendChild(dots);
    
    container.appendChild(carousel);
}

/**
 * Create a mixed carousel with YouTube video as first slide and gallery images
 */
function createMixedCarousel(projectData, container) {
    const carousel = document.createElement('div');
    carousel.className = 'carousel';
    
    const images = projectData.gallery_images;
    const videoId = extractYouTubeVideoId(projectData.youtube);
    const totalSlides = 1 + images.length; // YouTube + images
    let currentIndex = 0;
    
    // Media container (holds both video and images)
    const mediaContainer = document.createElement('div');
    mediaContainer.className = 'carousel-images';
    
    // YouTube iframe (first slide)
    const iframe = document.createElement('iframe');
    iframe.className = 'carousel-youtube';
    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&playlist=${videoId}&controls=1&modestbranding=1&rel=0`;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    iframe.allowFullscreen = true;
    
    // Image element (hidden initially)
    const img = document.createElement('img');
    img.className = 'carousel-image';
    img.style.display = 'none';
    
    mediaContainer.appendChild(iframe);
    mediaContainer.appendChild(img);
    
    // Navigation buttons
    const prevBtn = document.createElement('button');
    prevBtn.className = 'carousel-btn prev';
    prevBtn.innerHTML = '❮';
    prevBtn.onclick = (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateMixedCarousel();
    };
    
    const nextBtn = document.createElement('button');
    nextBtn.className = 'carousel-btn next';
    nextBtn.innerHTML = '❯';
    nextBtn.onclick = (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex + 1) % totalSlides;
        updateMixedCarousel();
    };
    
    // Dots indicator (first dot is for video)
    const dots = document.createElement('div');
    dots.className = 'carousel-dots';
    for (let i = 0; i < totalSlides; i++) {
        const dot = document.createElement('span');
        dot.className = `carousel-dot ${i === 0 ? 'active' : ''}`;
        if (i === 0) {
            dot.innerHTML = '▶'; // Video indicator
            dot.style.fontSize = '8px';
        }
        dot.onclick = (e) => {
            e.stopPropagation();
            currentIndex = i;
            updateMixedCarousel();
        };
        dots.appendChild(dot);
    }
    
    function updateMixedCarousel() {
        if (currentIndex === 0) {
            // Show YouTube video
            iframe.style.display = 'block';
            img.style.display = 'none';
            // Restart video if coming back to it
            iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&playlist=${videoId}&controls=1&modestbranding=1&rel=0`;
        } else {
            // Show image
            iframe.style.display = 'none';
            iframe.src = ''; // Stop video playback
            img.style.display = 'block';
            const imageIndex = currentIndex - 1;
            img.src = `content/gallery/${projectData.safe_name}/${images[imageIndex]}`;
            img.alt = `${projectData.title} - Image ${imageIndex + 1}`;
        }
        
        dots.querySelectorAll('.carousel-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === currentIndex);
        });
    }
    
    carousel.appendChild(prevBtn);
    carousel.appendChild(mediaContainer);
    carousel.appendChild(nextBtn);
    carousel.appendChild(dots);
    
    container.appendChild(carousel);
}

/**
 * Extract YouTube video ID from URL
 */
function extractYouTubeVideoId(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/watch.*[?&]v=([^&\n?#]+)/
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match && match[1]) return match[1];
    }
    return null;
}

/**
 * Close the project modal
 */
function closeProjectModal() {
    const modal = document.getElementById('project-modal');
    
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Stop any playing videos
        const iframe = modal.querySelector('iframe');
        if (iframe) iframe.src = '';
    }
}

/**
 * Load README content for a project
 */
async function loadProjectReadme(safeName, readmeContainer) {
    readmeContainer.innerHTML = '<div class="modal-loading">Loading...</div>';
    
    try {
        const response = await fetch(`content/readmes/${safeName}.md`);
        
        if (!response.ok) {
            throw new Error('README not found');
        }
        
        const markdown = await response.text();
        readmeContainer.innerHTML = parseMarkdown(markdown);
        
    } catch (error) {
        console.warn(`Failed to load README for ${safeName}:`, error);
        readmeContainer.innerHTML = '<div class="modal-error">No README available.</div>';
    }
}

/**
 * Simple Markdown parser
 */
function parseMarkdown(markdown) {
    let html = markdown;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold & Italic
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    html = html.replace(/_(.*?)_/gim, '<em>$1</em>');
    
    // Code
    html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');
    html = html.replace(/`(.*?)`/gim, '<code>$1</code>');
    
    // Links & Images
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/gim, '<img src="$2" alt="$1">');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Lists
    const lines = html.split('\n');
    let inList = false;
    let processedLines = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        const isListItem = /^[\*\-\+] (.*)/.test(trimmed);
        
        if (isListItem) {
            if (!inList) {
                processedLines.push('<ul>');
                inList = true;
            }
            processedLines.push(trimmed.replace(/^[\*\-\+] (.*)/, '<li>$1</li>'));
        } else if (inList && trimmed === '') {
            continue;
        } else if (inList && trimmed !== '') {
            processedLines.push('</ul>');
            inList = false;
            processedLines.push(trimmed);
        } else {
            processedLines.push(trimmed);
        }
    }
    
    if (inList) processedLines.push('</ul>');
    
    html = processedLines.join('\n');
    
    // Paragraphs
    const sections = html.split('\n\n');
    const processed = sections.map(section => {
        section = section.trim();
        if (!section) return '';
        if (section.startsWith('<h') || section.startsWith('<ul') || 
            section.startsWith('<pre') || section.includes('<ul>') || 
            section.includes('<h')) {
            return section;
        }
        return `<p>${section}</p>`;
    });
    
    html = processed.join('\n\n');
    
    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr>');
    
    return html;
}
