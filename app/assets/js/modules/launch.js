function launchGame() {
    const btn = document.querySelector('.btn-launch');
    if (btn.classList.contains('disabled')) return;
    saveUsername();
    const originalText = btn.innerHTML;
    btn.dataset.originalText = originalText;
    btn.classList.add('disabled');
    btn.style.filter = 'brightness(0.8)';
    btn.style.cursor = 'not-allowed';
    btn.innerHTML = '<span>' + t('launching') + '</span>';

    pywebview.api.launch_game().then(response => {
        console.log("Launch:", response);
    }).catch(err => {
        console.error("Launch error:", err);
        showAlert(t('error'), err, '✗');
        resetLaunchButton();
    });
}

function resetLaunchButton() {
    const btn = document.querySelector('.btn-launch');
    if (btn.dataset.originalText) {
        btn.innerHTML = btn.dataset.originalText;
    } else {
        btn.innerHTML = `<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"></path></svg><span>${t('launch')}</span>`;
    }
    btn.classList.remove('disabled');
    btn.style.filter = 'none';
    btn.style.cursor = 'pointer';
}
