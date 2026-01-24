// Preview Module - Handles screenshots and texturepacks preview

async function loadScreenshots() {
    const container = document.getElementById('screenshots-grid');
    const emptyState = document.getElementById('screenshots-empty');
    const loadingState = document.getElementById('screenshots-loading');

    if (!container) return;

    loadingState?.classList.remove('hidden');
    emptyState?.classList.add('hidden');
    container.innerHTML = '';

    try {
        const result = await pywebview.api.get_screenshots();
        loadingState?.classList.add('hidden');

        if (result.status === 'success' && result.items.length > 0) {
            result.items.forEach(item => {
                const card = createPreviewCard(item, 'screenshots');
                container.appendChild(card);
            });
        } else {
            emptyState?.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Failed to load screenshots:', error);
        loadingState?.classList.add('hidden');
        emptyState?.classList.remove('hidden');
    }
}

async function loadTexturepacks() {
    const container = document.getElementById('texturepacks-grid');
    const emptyState = document.getElementById('texturepacks-empty');
    const loadingState = document.getElementById('texturepacks-loading');

    if (!container) return;

    loadingState?.classList.remove('hidden');
    emptyState?.classList.add('hidden');
    container.innerHTML = '';

    try {
        const result = await pywebview.api.get_texturepacks();
        loadingState?.classList.add('hidden');

        if (result.status === 'success' && result.items.length > 0) {
            result.items.forEach(item => {
                const card = createTexturepackCard(item);
                container.appendChild(card);
            });
        } else {
            emptyState?.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Failed to load texturepacks:', error);
        loadingState?.classList.add('hidden');
        emptyState?.classList.remove('hidden');
    }
}

function createPreviewCard(item, folderType) {
    const card = document.createElement('div');
    card.className = 'preview-card group';
    card.innerHTML = `
        <div class="preview-thumbnail">
            <img src="${item.thumbnail}" alt="${item.filename}" loading="lazy">
            <button class="delete-btn" onclick="deletePreviewItem('${folderType}', '${item.filename}')" title="Delete">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
            </button>
        </div>
        <div class="preview-info">
            <span class="preview-name" title="${item.filename}">${item.filename}</span>
        </div>
    `;
    return card;
}

function createTexturepackCard(item) {
    const card = document.createElement('div');
    card.className = 'preview-card texturepack-card group';

    const thumbnailHtml = item.thumbnail
        ? `<img src="${item.thumbnail}" alt="${item.name}" loading="lazy">`
        : `<div class="placeholder-icon">
               <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
               </svg>
           </div>`;

    card.innerHTML = `
        <div class="preview-thumbnail texturepack-thumb">
            ${thumbnailHtml}
            <button class="delete-btn" onclick="deletePreviewItem('texturepacks', '${item.filename}')" title="Delete">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
            </button>
        </div>
        <div class="preview-info">
            <span class="preview-name" title="${item.name}">${item.name}</span>
            <span class="preview-size">${formatFileSize(item.size)}</span>
        </div>
    `;
    return card;
}

async function deletePreviewItem(folderType, filename) {
    if (!confirm(`Delete "${filename}"?`)) return;

    try {
        const result = await pywebview.api.delete_file(folderType, filename);
        if (result.status === 'success') {
            if (folderType === 'screenshots') {
                loadScreenshots();
            } else {
                loadTexturepacks();
            }
        } else {
            alert('Failed to delete: ' + result.message);
        }
    } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete file');
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

window.loadScreenshots = loadScreenshots;
window.loadTexturepacks = loadTexturepacks;
window.deletePreviewItem = deletePreviewItem;
