let firstRunTheme = 'midnight';
let firstRunRam = 2048;

function selectFirstRunTheme(theme) {
    firstRunTheme = theme;
    document.querySelectorAll('.fr-theme-btn').forEach(btn => {
        btn.classList.remove('selected', 'border-[#39d353]');
        btn.classList.add('border-transparent');
    });
    const btn = document.getElementById('fr-theme-' + theme);
    btn.classList.add('selected', 'border-[#39d353]');
    btn.classList.remove('border-transparent');
    applyTheme(theme);
}

function updateFirstRunRamDisplay(value) {
    firstRunRam = parseInt(value);
    const gb = (firstRunRam / 1024).toFixed(firstRunRam % 1024 === 0 ? 0 : 1);
    document.getElementById('fr-ram-value').innerText = gb + ' GB';
}

function confirmFirstRun() {
    if (typeof selectedLang !== 'undefined') {
        currentLang = selectedLang;
    }
    pywebview.api.save_settings({
        language: currentLang,
        theme: firstRunTheme,
        max_ram: firstRunRam,
        min_ram: Math.min(1024, firstRunRam),
        first_run: false
    });
    document.getElementById('lang-modal').classList.add('hidden');
    document.getElementById('setting-language').value = currentLang;
    document.getElementById('setting-max-ram').value = firstRunRam;
    applyTranslations();
}

function loadSettings() {
    pywebview.api.get_settings().then(settings => {
        document.getElementById('input-username').value = settings.username || '';
        document.getElementById('setting-min-ram').value = settings.min_ram || 1024;
        document.getElementById('setting-max-ram').value = settings.max_ram || 2048;
        document.getElementById('setting-width').value = settings.width || 854;
        document.getElementById('setting-height').value = settings.height || 480;
        document.getElementById('setting-fullscreen').checked = settings.fullscreen || false;
        document.getElementById('setting-java-path').value = settings.java_path || '';
        document.getElementById('setting-close-launcher').checked = settings.close_launcher !== false;
        document.getElementById('setting-show-console').checked = settings.show_console || false;
        document.getElementById('setting-debug-mode').checked = settings.debug_mode || false;
        document.getElementById('setting-custom-jvm').value = settings.custom_jvm_args || '';
        document.getElementById('setting-language').value = settings.language || 'en';

        currentLang = settings.language || 'en';
        applyTranslations();
        applyTheme(settings.theme);

        if (settings.first_run !== false) {
            document.getElementById('lang-modal').classList.remove('hidden');
            loadSystemInfo();
        }

        updateUserUI(settings.username, settings.auth_type);

        if (settings.custom_background) {
            applyCustomBackground(settings.custom_background);
        }
    });
}

function loadSystemInfo() {
    pywebview.api.get_system_info().then(info => {
        const totalGb = (info.total_ram_mb / 1024).toFixed(0);
        const recGb = (info.recommended_ram_mb / 1024).toFixed(1);

        document.getElementById('fr-total-ram').innerText = totalGb + ' GB';
        document.getElementById('fr-recommended-ram').innerText = recGb + ' GB';

        const slider = document.getElementById('fr-ram-slider');
        slider.value = info.recommended_ram_mb;
        slider.max = Math.min(info.total_ram_mb, 16384);
        firstRunRam = info.recommended_ram_mb;
        updateFirstRunRamDisplay(info.recommended_ram_mb);
    });
}

function loadPerformance() {
    pywebview.api.get_settings().then(settings => {
        const perf = settings.performance || {};
        document.getElementById('perf-microstutter').checked = perf.microstutter || false;
        document.getElementById('perf-g1gc').checked = perf.g1gc !== false;
        document.getElementById('perf-pretouch').checked = perf.pretouch !== false;
        document.getElementById('perf-parallel').checked = perf.parallel !== false;
        document.getElementById('perf-nobiasedlock').checked = perf.nobiasedlock !== false;
        document.getElementById('perf-codecache').checked = perf.codecache !== false;
        document.getElementById('perf-inlining').checked = perf.inlining !== false;
        document.getElementById('perf-noexplicitgc').checked = perf.noexplicitgc !== false;
        document.getElementById('perf-tiered').checked = perf.tiered !== false;
        document.getElementById('perf-stringdedup').checked = perf.stringdedup || false;
    });
}

function loadVersions() {
    pywebview.api.get_versions().then(versions => {
        const selector = document.getElementById('version-selector');
        selector.innerHTML = '';
        versions.forEach(ver => {
            const opt = document.createElement('option');
            opt.value = ver;
            opt.innerText = ver;
            selector.appendChild(opt);
        });
    });
}

function saveUsername() {
    const username = document.getElementById('input-username').value;
    if (username) {
        pywebview.api.save_settings({ username: username, auth_type: 'offline' }).then(() => {
            updateUserUI(username, 'offline');
        });
    }
}

function saveSettings() {
    const settings = {
        username: document.getElementById('input-username').value,
        min_ram: parseInt(document.getElementById('setting-min-ram').value),
        max_ram: parseInt(document.getElementById('setting-max-ram').value),
        width: parseInt(document.getElementById('setting-width').value),
        height: parseInt(document.getElementById('setting-height').value),
        fullscreen: document.getElementById('setting-fullscreen').checked,
        java_path: document.getElementById('setting-java-path').value,
        close_launcher: document.getElementById('setting-close-launcher').checked,
        show_console: document.getElementById('setting-show-console').checked,
        debug_mode: document.getElementById('setting-debug-mode').checked,
        custom_jvm_args: document.getElementById('setting-custom-jvm').value,
        language: document.getElementById('setting-language').value
    };

    pywebview.api.save_settings(settings).then(() => {
        showAlert(t('success'), t('settings_saved') + ' ' + t('debug_restart'), '✓');
        updateUserUI(settings.username, 'offline');
    });
}

function savePerformance() {
    const perfSettings = {
        microstutter: document.getElementById('perf-microstutter').checked,
        g1gc: document.getElementById('perf-g1gc').checked,
        pretouch: document.getElementById('perf-pretouch').checked,
        parallel: document.getElementById('perf-parallel').checked,
        nobiasedlock: document.getElementById('perf-nobiasedlock').checked,
        codecache: document.getElementById('perf-codecache').checked,
        inlining: document.getElementById('perf-inlining').checked,
        noexplicitgc: document.getElementById('perf-noexplicitgc').checked,
        tiered: document.getElementById('perf-tiered').checked,
        stringdedup: document.getElementById('perf-stringdedup').checked
    };

    pywebview.api.save_settings({ performance: perfSettings }).then(() => {
        showAlert(t('success'), t('perf_applied'), '✓');
    });
}

function openFolder(folderType) {
    pywebview.api.open_folder(folderType).then(response => {
        console.log("Opened folder:", folderType);
    }).catch(err => {
        showAlert(t('error'), 'Failed to open folder: ' + err, '✗');
    });
}

function confirmClearGameData() {
    if (confirm(t('clear_game_data_confirm'))) {
        clearGameData();
    }
}

function clearGameData() {
    showAlert(t('clearing'), t('clearing') + '...', '⏳');

    pywebview.api.clear_game_data().then(response => {
        closeAlert();
        if (response.status === 'success') {
            showAlert(t('success'), response.message || t('data_cleared'), '✓');
        } else if (response.status === 'info') {
            showAlert('Info', response.message, 'ℹ️');
        } else {
            showAlert(t('error'), response.message, '❌');
        }
    }).catch(error => {
        closeAlert();
        showAlert(t('error'), 'Failed to clear game data: ' + error, '❌');
    });
}
