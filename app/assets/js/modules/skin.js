function updateSkinUI(profile) {
    const loginContainer = document.getElementById('skin-login-container');
    const profileContainer = document.getElementById('skin-profile-container');

    if (profile && profile.source === 'elyby') {
        loginContainer.classList.add('hidden');
        profileContainer.classList.remove('hidden');
        document.getElementById('profile-username').innerText = profile.username;
        document.getElementById('profile-uuid').innerText = 'UUID: ' + profile.uuid;
        refreshSkin(profile.username);
    } else {
        loginContainer.classList.remove('hidden');
        profileContainer.classList.add('hidden');
        document.getElementById('elyby-password').value = '';
        document.getElementById('elyby-2fa').value = '';
        document.getElementById('elyby-2fa-container').classList.add('hidden');
    }
}

function refreshSkin(username) {
    if (username) {
        const skinUrl = `http://skinsystem.ely.by/skins/${username}.png`;
        renderSkinPreview(skinUrl);
        return;
    }

    pywebview.api.get_settings().then(settings => {
        const user = settings.username;
        if (user) {
            const skinUrl = `http://skinsystem.ely.by/skins/${user}.png`;
            renderSkinPreview(skinUrl);
        }
    });
}

function loadSkinSettings() {
    pywebview.api.get_settings().then(settings => {
        if (settings.auth_type === 'elyby') {
            updateSkinUI({
                username: settings.username,
                uuid: settings.uuid,
                source: 'elyby'
            });
        } else {
            updateSkinUI(null);
        }

        if (settings.custom_background) {
            document.getElementById('bg-status').innerText = 'Custom background set';
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
