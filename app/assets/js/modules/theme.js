function changeTheme(themeName) {
    document.body.setAttribute('data-theme', themeName);
    pywebview.api.save_settings({ theme: themeName });
}

function applyTheme(themeName) {
    if (themeName) {
        document.body.setAttribute('data-theme', themeName);
    } else {
        document.body.removeAttribute('data-theme');
    }
}

function pickBackground() {
    pywebview.api.pick_background_image().then(response => {
        if (response.status === 'success') {
            applyCustomBackground(response.path);
            document.getElementById('bg-status').innerText = 'Custom background set';
            showAlert(t('success'), 'Background updated!', '✓');
        } else if (response.status === 'error') {
            showAlert(t('error'), response.message, '✗');
        }
    });
}

function resetBackground() {
    pywebview.api.clear_custom_background().then(() => {
        document.body.style.backgroundImage = '';
        document.getElementById('content-area').style.backgroundImage = '';
        document.getElementById('bg-status').innerText = 'Default background';
        showAlert(t('success'), 'Background reset to default', '✓');
    });
}

function applyCustomBackground(path) {
    if (path) {
        const url = 'file:///' + path.replace(/\\/g, '/');
        const contentArea = document.getElementById('content-area');
        if (contentArea) {
            contentArea.style.backgroundImage = `url("${url}")`;
            contentArea.style.backgroundSize = 'cover';
            contentArea.style.backgroundPosition = 'center';
        }
    }
}
