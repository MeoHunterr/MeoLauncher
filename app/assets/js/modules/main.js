window.addEventListener('pywebviewready', () => {
    updateProgress(30, 'Loading settings...');
    setTimeout(() => {
        loadSettings();
        loadPerformance();
        loadSkinSettings();
        updateProgress(60, 'Loading versions...');
        setTimeout(() => {
            loadVersions();
            updateProgress(90, 'Finalizing...');
            setTimeout(() => {
                updateProgress(100, 'Ready!');
                setTimeout(() => {
                    document.getElementById('loading-screen').classList.add('hidden');
                }, 300);
            }, 200);
        }, 200);
    }, 200);
});
