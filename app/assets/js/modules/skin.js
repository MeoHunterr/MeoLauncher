function updateSkinUI(profile, authType) {
    const loginContainer = document.getElementById('skin-login-container');
    const profileContainer = document.getElementById('skin-profile-container');
    const microsoftNotice = document.getElementById('skin-microsoft-notice');

    if (authType === 'microsoft') {
        if (loginContainer) loginContainer.classList.add('hidden');
        if (profileContainer) profileContainer.classList.add('hidden');
        if (microsoftNotice) microsoftNotice.classList.remove('hidden');
    } else if (profile && profile.source === 'elyby') {
        if (loginContainer) loginContainer.classList.add('hidden');
        if (profileContainer) profileContainer.classList.remove('hidden');
        if (microsoftNotice) microsoftNotice.classList.add('hidden');
        document.getElementById('profile-username').innerText = profile.username;
        document.getElementById('profile-uuid').innerText = 'UUID: ' + profile.uuid;
        refreshSkin(profile.username, 'elyby');
    } else {
        if (loginContainer) loginContainer.classList.remove('hidden');
        if (profileContainer) profileContainer.classList.add('hidden');
        if (microsoftNotice) microsoftNotice.classList.add('hidden');
        const pwEl = document.getElementById('elyby-password');
        const tfaEl = document.getElementById('elyby-2fa');
        const tfaContainer = document.getElementById('elyby-2fa-container');
        if (pwEl) pwEl.value = '';
        if (tfaEl) tfaEl.value = '';
        if (tfaContainer) tfaContainer.classList.add('hidden');
    }
}

function refreshSkin(username, authType) {
    if (!username) {
        pywebview.api.get_settings().then(settings => {
            const user = settings.username;
            const type = settings.auth_type || 'offline';
            if (user) {
                refreshSkin(user, type);
            }
        });
        return;
    }

    let skinUrl;
    if (authType === 'microsoft') {
        pywebview.api.get_settings().then(settings => {
            if (settings.microsoft_skin_url) {
                renderSkinPreview(settings.microsoft_skin_url);
            }
        });
    } else {
        skinUrl = `http://skinsystem.ely.by/skins/${username}.png`;
        renderSkinPreview(skinUrl);
    }
}

function loadSkinSettings() {
    pywebview.api.get_settings().then(settings => {
        const authType = settings.auth_type || 'offline';

        if (authType === 'microsoft') {
            updateSkinUI(null, 'microsoft');
        } else if (authType === 'elyby') {
            updateSkinUI({
                username: settings.username,
                uuid: settings.uuid,
                source: 'elyby'
            }, 'elyby');
        } else {
            updateSkinUI(null, 'offline');
        }

        if (settings.custom_background) {
            const bgStatus = document.getElementById('bg-status');
            if (bgStatus) bgStatus.innerText = 'Custom background set';
        }
    });
}

function renderSkinPreview(skinPathOrUrl) {
    const canvas = document.getElementById('skin-preview');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const img = new Image();

    let src = skinPathOrUrl;
    if (!src.startsWith('http') && !src.startsWith('file://')) {
        src = 'file:///' + src.replace(/\\/g, '/');
    }

    if (src.startsWith('http')) {
        src += '?t=' + new Date().getTime();
    }

    img.crossOrigin = "Anonymous";
    img.src = src;

    img.onload = function () {
        ctx.imageSmoothingEnabled = false;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const scale = 8;
        const offsetX = (canvas.width - 16 * scale) / 2;
        const offsetY = 20;

        ctx.drawImage(img, 8, 8, 8, 8, offsetX + 4 * scale, offsetY, 8 * scale, 8 * scale);
        ctx.drawImage(img, 20, 20, 8, 12, offsetX + 4 * scale, offsetY + 8 * scale, 8 * scale, 12 * scale);
        ctx.drawImage(img, 44, 20, 4, 12, offsetX, offsetY + 8 * scale, 4 * scale, 12 * scale);

        if (img.height >= 64) {
            ctx.drawImage(img, 36, 52, 4, 12, offsetX + 12 * scale, offsetY + 8 * scale, 4 * scale, 12 * scale);
        } else {
            ctx.save();
            ctx.translate(offsetX + 16 * scale, offsetY + 8 * scale);
            ctx.scale(-1, 1);
            ctx.drawImage(img, 44, 20, 4, 12, 0, 0, 4 * scale, 12 * scale);
            ctx.restore();
        }

        ctx.drawImage(img, 4, 20, 4, 12, offsetX + 4 * scale, offsetY + 20 * scale, 4 * scale, 12 * scale);

        if (img.height >= 64) {
            ctx.drawImage(img, 20, 52, 4, 12, offsetX + 8 * scale, offsetY + 20 * scale, 4 * scale, 12 * scale);
        } else {
            ctx.save();
            ctx.translate(offsetX + 12 * scale, offsetY + 20 * scale);
            ctx.scale(-1, 1);
            ctx.drawImage(img, 4, 20, 4, 12, 0, 0, 4 * scale, 12 * scale);
            ctx.restore();
        }
    };

    img.onerror = function () {
        ctx.fillStyle = '#2d2f33';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.font = '14px sans-serif';
        ctx.fillText('No skin', canvas.width / 2, canvas.height / 2);
    };
}

function openElybyExternal() {
    pywebview.api.open_url('https://ely.by/skins');
}

function refreshElybyFrame() {
    const iframe = document.getElementById('elyby-skin-frame');
    if (iframe && iframe.src) {
        iframe.src = iframe.src;
    }
}
