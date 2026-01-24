function updateUserUI(username, authType) {
    const userNameEl = document.getElementById('user-name');
    const userStatusEl = document.getElementById('user-status');
    const avatarEl = document.getElementById('user-avatar');

    const loginSection = document.getElementById('home-login-section');
    const accountSection = document.getElementById('home-account-section');
    const accountUsername = document.getElementById('account-username');
    const accountType = document.getElementById('account-type');
    const accountAvatar = document.getElementById('account-avatar');

    userNameEl.innerText = username || 'Player';

    let statusText = 'Offline';
    let statusColor = '#9ca3af';
    let isPremium = false;

    if (authType === 'microsoft') {
        statusText = 'Premium';
        statusColor = '#39d353';
        isPremium = true;
    } else if (authType === 'elyby') {
        statusText = 'Ely.by';
        statusColor = '#60a5fa';
        isPremium = true;
    }

    userStatusEl.innerText = statusText;
    userStatusEl.style.color = statusColor;

    if (username) {
        avatarEl.innerText = username.charAt(0).toUpperCase();
    } else {
        avatarEl.innerText = 'P';
    }

    if (isPremium && loginSection && accountSection) {
        loginSection.classList.add('hidden');
        accountSection.classList.remove('hidden');
        if (accountUsername) accountUsername.innerText = username || 'Player';
        if (accountType) {
            accountType.innerText = statusText;
            accountType.style.color = statusColor;
        }
        if (accountAvatar) accountAvatar.innerText = (username || 'P').charAt(0).toUpperCase();
    } else if (loginSection && accountSection) {
        loginSection.classList.remove('hidden');
        accountSection.classList.add('hidden');
    }
}

function startMicrosoftLogin() {
    pywebview.api.start_microsoft_login().then(response => {
        if (response.status === 'error') {
            showAlert(t('error'), response.message, '✗');
        }
    }).catch(err => {
        showAlert(t('error'), err.toString(), '✗');
    });
}

function closeLoginModal() {
    document.getElementById('login-modal').classList.add('hidden');
}

function copyCode() {
    const code = document.getElementById('device-code').innerText;
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.getElementById('copy-btn');
        btn.classList.add('copied');
        btn.innerText = t('copied');
        setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerText = t('copy');
        }, 2000);
    });
}

function onLoginSuccess(profile) {
    closeLoginModal();
    updateUserUI(profile.name, 'microsoft');
    showAlert(t('welcome'), t('logged_in_as') + ' ' + profile.name, '✓');
    loadSettings();
}

function onLoginError(msg) {
    document.getElementById('login-modal').classList.add('hidden');
    showAlert(t('login_failed'), msg, '✗');
}

function updateLoginStatus(status) {
    const el = document.getElementById('login-status');
    if (el) el.innerText = status;
}

function handleElybyLogin(event) {
    event.preventDefault();

    const username = document.getElementById('elyby-username').value;
    const password = document.getElementById('elyby-password').value;
    const twoFactor = document.getElementById('elyby-2fa').value;
    const btn = document.getElementById('elyby-login-btn');
    const spinner = btn.querySelector('.loading-spinner');
    const errorDiv = document.getElementById('elyby-login-error');

    btn.disabled = true;
    spinner.classList.remove('hidden');
    errorDiv.classList.add('hidden');

    pywebview.api.start_elyby_login(username, password, twoFactor).then(response => {
        btn.disabled = false;
        spinner.classList.add('hidden');

        if (response.status === 'success') {
            const profile = response.profile;
            pywebview.api.save_settings({ username: profile.username }).then(() => {
                updateUserUI(profile.username, 'elyby');
                updateSkinUI(profile);
                showAlert(t('success'), 'Logged in as ' + profile.username, '✓');
                switchTab('home');
            });
        } else if (response.status === '2fa_required') {
            document.getElementById('elyby-2fa-container').classList.remove('hidden');
            errorDiv.innerText = response.message;
            errorDiv.classList.remove('hidden');
        } else {
            errorDiv.innerText = response.message;
            errorDiv.classList.remove('hidden');
        }
    }).catch(err => {
        btn.disabled = false;
        spinner.classList.add('hidden');
        errorDiv.innerText = 'Error: ' + err;
        errorDiv.classList.remove('hidden');
    });
}

function handleElybyHomeLogin() {
    switchTab('skin');
    setTimeout(() => {
        const input = document.getElementById('elyby-username');
        if (input) input.focus();
    }, 300);
}

function handleLogout() {
    pywebview.api.save_settings({
        auth_type: 'offline',
        access_token: '0',
        uuid: null,
        refresh_token: '',
        microsoft_skin_url: '',
        microsoft_cape_url: ''
    }).then(() => {
        updateUserUI(null, 'offline');
        if (typeof updateSkinUI === 'function') updateSkinUI(null);
        pywebview.api.get_settings().then(settings => {
            document.getElementById('input-username').value = settings.username || '';
        });
        showAlert(t('success'), 'Logged out', '✓');
    });
}

function handleElybyLogout() {
    handleLogout();
}
