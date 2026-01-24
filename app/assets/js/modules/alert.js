function showAlert(title, message, icon = '✓') {
    document.getElementById('alert-title').innerText = title;
    document.getElementById('alert-message').innerText = message;
    document.getElementById('alert-icon').innerText = icon;
    document.getElementById('alert-modal').classList.remove('hidden');
}

function closeAlert() {
    document.getElementById('alert-modal').classList.add('hidden');
}

function updateProgress(percent, text) {
    document.getElementById('loading-progress').style.width = percent + '%';
    document.getElementById('loading-text').innerText = text;
}
