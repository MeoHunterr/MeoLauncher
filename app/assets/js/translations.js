let currentLang = 'en';
let selectedLang = 'en';

const translations = {
    en: {
        home: "Home", settings: "Settings", screenshots: "Screenshots", texturepacks: "Texture Packs",
        performance: "Performance", about: "About", username: "Username", or: "OR",
        login_microsoft: "Login with Microsoft", launch: "Launch", launching: "Launching...",
        screenshots_desc: "View your in-game screenshots here.", texturepacks_desc: "Manage your resource packs.",
        open_folder: "Open Folder", language: "Language", memory: "Memory (RAM)", resolution: "Resolution",
        fullscreen: "Fullscreen", java_runtime: "Java Runtime", advanced: "Advanced",
        close_launcher: "Close Launcher on Start", show_console: "Show Game Console",
        debug_mode: "Debug Mode (Dev Tools)", custom_jvm: "Custom JVM Args", save_settings: "Save Settings",
        performance_desc: "Optimize your game for maximum FPS", apply_performance: "Apply Performance Settings",
        about_desc: "A modern launcher for Minecraft Beta 1.7.3 and Better Than Adventure.",
        ms_login: "Microsoft Login", ms_login_desc: "Go to the link below and enter this code:",
        copy: "Copy", copied: "Copied!", open_login_page: "Open Login Page", waiting_auth: "Waiting for authentication...",
        cancel: "Cancel", success: "Success", error: "Error", settings_saved: "Settings saved!",
        debug_restart: "Debug mode will take effect on next restart.", perf_applied: "Performance settings applied!",
        welcome: "Welcome!", logged_in_as: "Logged in as", login_failed: "Login Failed",
        g1gc_desc: "Reduces lag spikes caused by garbage collection.",
        pretouch_desc: "Pre-allocates memory at startup. Prevents stuttering.",
        largepages_desc: "Requires admin rights. Advanced users only.",
        parallel_desc: "Reduces GC pause times on multi-core CPUs.",
        aggressive_desc: "Experimental compiler optimizations.",
        stringdedup_desc: "Reduces RAM usage with minimal CPU overhead.",
        help: "Help", skin: "Skin",
        skin_desc: "Manage your Ely.by account and skin",
        elyby_login_title: "Login with Ely.by",
        elyby_login_desc: "Access your skins and capes",
        elyby_username_label: "Username or Email",
        elyby_password_label: "Password",
        elyby_2fa_label: "2FA Code",
        elyby_login_btn: "Login",
        elyby_no_account: "Don't have an account?",
        elyby_register: "Register on Ely.by",
        elyby_logout: "Logout",
        manage_skin_title: "Manage Your Skin",
        manage_skin_desc: "Click the button below to open Ely.by in your browser and manage your skins and capes.",
        open_elyby_manager: "Open Ely.by Skin Manager",
        skin_launch_note: "After changing your skin on Ely.by, just launch the game to see your new skin!",
        loading: "Loading...", confirm: "Confirm",
        danger_zone: "⚠️ Danger Zone",
        danger_zone_desc: "These actions cannot be undone. Use with caution.",
        clear_game_data: "Clear & Re-extract Game Data",
        clear_game_data_confirm: "Are you sure you want to delete all extracted game files? They will be re-extracted on next launch.",
        clearing: "Clearing...", data_cleared: "Game data cleared successfully!",
        theme: "Theme"
    },
    vi: {
        home: "Trang chủ", settings: "Cài đặt", screenshots: "Ảnh chụp màn hình", texturepacks: "Gói tài nguyên",
        performance: "Hiệu năng", about: "Giới thiệu", username: "Tên người chơi", or: "HOẶC",
        login_microsoft: "Đăng nhập Microsoft", launch: "Chơi ngay", launching: "Đang khởi động...",
        screenshots_desc: "Xem ảnh chụp màn hình trong game.", texturepacks_desc: "Quản lý gói tài nguyên.",
        open_folder: "Mở thư mục", language: "Ngôn ngữ", memory: "Bộ nhớ (RAM)", resolution: "Độ phân giải",
        fullscreen: "Toàn màn hình", java_runtime: "Java Runtime", advanced: "Nâng cao",
        close_launcher: "Đóng Launcher khi chơi", show_console: "Hiện Console game",
        debug_mode: "Chế độ Debug (Dev Tools)", custom_jvm: "Tham số JVM tùy chỉnh", save_settings: "Lưu cài đặt",
        performance_desc: "Tối ưu game để đạt FPS cao nhất", apply_performance: "Áp dụng cài đặt hiệu năng",
        about_desc: "Launcher hiện đại cho Minecraft Beta 1.7.3 và Better Than Adventure.",
        ms_login: "Đăng nhập Microsoft", ms_login_desc: "Truy cập link bên dưới và nhập mã này:",
        copy: "Sao chép", copied: "Đã sao chép!", open_login_page: "Mở trang đăng nhập", waiting_auth: "Đang chờ xác thực...",
        cancel: "Hủy", success: "Thành công", error: "Lỗi", settings_saved: "Đã lưu cài đặt!",
        debug_restart: "Chế độ debug sẽ có hiệu lực sau khi khởi động lại.", perf_applied: "Đã áp dụng cài đặt hiệu năng!",
        welcome: "Chào mừng!", logged_in_as: "Đã đăng nhập với", login_failed: "Đăng nhập thất bại",
        g1gc_desc: "Giảm giật lag do thu gom rác (garbage collection).",
        pretouch_desc: "Cấp phát bộ nhớ khi khởi động. Giảm giật khi tải thế giới.",
        largepages_desc: "Yêu cầu quyền admin. Chỉ dành cho người dùng nâng cao.",
        parallel_desc: "Giảm thời gian dừng GC trên CPU đa nhân.",
        aggressive_desc: "Tối ưu compiler thử nghiệm. Tăng tốc xử lý.",
        stringdedup_desc: "Giảm RAM với ít tải CPU. Tốt cho mods nhiều text.",
        help: "Trợ giúp", skin: "Skin",
        skin_desc: "Quản lý tài khoản Ely.by và skin của bạn",
        elyby_login_title: "Đăng nhập Ely.by",
        elyby_login_desc: "Truy cập skin và áo choàng của bạn",
        elyby_username_label: "Tên người dùng hoặc Email",
        elyby_password_label: "Mật khẩu",
        elyby_2fa_label: "Mã 2FA",
        elyby_login_btn: "Đăng nhập",
        elyby_no_account: "Chưa có tài khoản?",
        elyby_register: "Đăng ký trên Ely.by",
        elyby_logout: "Đăng xuất",
        manage_skin_title: "Quản lý Skin",
        manage_skin_desc: "Nhấn nút bên dưới để mở Ely.by trong trình duyệt và quản lý skin cũng như áo choàng của bạn.",
        open_elyby_manager: "Mở trình quản lý Skin Ely.by",
        skin_launch_note: "Sau khi thay đổi skin trên Ely.by, chỉ cần khởi động game để thấy skin mới!",
        loading: "Đang tải...", confirm: "Xác nhận",
        danger_zone: "⚠️ Vùng Nguy Hiểm",
        danger_zone_desc: "Những thao tác này không thể hoàn tác. Hãy thận trọng.",
        clear_game_data: "Xóa & Giải nén lại dữ liệu game",
        clear_game_data_confirm: "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu game đã giải nén? Chúng sẽ được giải nén lại khi khởi động lần sau.",
        clearing: "Đang xóa...", data_cleared: "Đã xóa dữ liệu game thành công!",
        theme: "Giao diện"
    }
};

function t(key) {
    return translations[currentLang][key] || translations['en'][key] || key;
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            el.innerText = translations[currentLang][key];
        }
    });

    // Auto-switch Help tab language if it exists
    if (typeof switchHelpLanguage === 'function') {
        switchHelpLanguage(currentLang);
    }
}

function selectLanguage(lang) {
    selectedLang = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('selected'));
    document.getElementById('lang-' + lang).classList.add('selected');
}

function confirmLanguage() {
    currentLang = selectedLang;
    pywebview.api.save_settings({ language: currentLang, first_run: false });
    document.getElementById('lang-modal').classList.add('hidden');
    document.getElementById('setting-language').value = currentLang;
    applyTranslations();
}

function changeLanguage(lang) {
    currentLang = lang;
    pywebview.api.save_settings({ language: lang });
    applyTranslations();
    // Also switch Help tab language if currently viewing Help
    const helpView = document.getElementById('view-help');
    if (helpView && !helpView.classList.contains('hidden')) {
        switchHelpLanguage(lang);
    }
}
