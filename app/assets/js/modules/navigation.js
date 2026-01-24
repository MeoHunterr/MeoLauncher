function switchTab(tabName) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.getElementById(`view-${tabName}`).classList.remove('hidden');

    if (tabName === 'help') {
        switchHelpLanguage(currentLang === 'vi' ? 'vi' : 'en');
    }
    if (tabName === 'screenshots' && typeof loadScreenshots === 'function') {
        loadScreenshots();
    }
    if (tabName === 'texturepacks' && typeof loadTexturepacks === 'function') {
        loadTexturepacks();
    }
}

function switchHelpLanguage(lang) {
    document.querySelectorAll('.help-language-content').forEach(el => el.classList.add('hidden'));
    const selectedContent = document.getElementById(`help-content-${lang}`);
    if (selectedContent) {
        selectedContent.classList.remove('hidden');
    }
    document.getElementById('help-lang-en').classList.remove('text-white', 'bg-theme-accent');
    document.getElementById('help-lang-vi').classList.remove('text-white', 'bg-theme-accent');
    document.getElementById(`help-lang-${lang}`).classList.add('text-white', 'bg-theme-accent');
}
