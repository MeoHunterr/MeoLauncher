class LanguageManager:
    STRINGS = {
        "en": {
            "home": "Home", "settings": "Settings", "launch": "LAUNCH", "launching": "LAUNCHING...",
            "initializing": "Initializing...", "ready": "Ready", "missing": "Missing (Will install on launch)",
            "username": "Username", "memory_allocation": "Memory Allocation", "display": "Display",
            "resolution": "Resolution", "fullscreen": "Fullscreen", "system": "System",
            "java_runtime": "Java Runtime", "performance_mode": "Performance Mode",
            "close_launcher": "Close Launcher after launch", "advanced": "Advanced",
            "jvm_args": "JVM Arguments", "save_settings": "Save Settings", "saved": "Saved!",
            "console": "Show Console", "language": "Language"
        },
        "vi": {
            "home": "Trang chủ", "settings": "Cài đặt", "launch": "CHƠI NGAY", "launching": "ĐANG MỞ...",
            "initializing": "Đang khởi tạo...", "ready": "Sẵn sàng", "missing": "Thiếu (Sẽ cài khi chạy)",
            "username": "Tên người chơi", "memory_allocation": "Phân bổ RAM", "display": "Hiển thị",
            "resolution": "Độ phân giải", "fullscreen": "Toàn màn hình", "system": "Hệ thống",
            "java_runtime": "Java Runtime", "performance_mode": "Chế độ hiệu năng",
            "close_launcher": "Đóng Launcher khi chơi", "advanced": "Nâng cao",
            "jvm_args": "Tham số JVM", "save_settings": "Lưu cài đặt", "saved": "Đã lưu!",
            "console": "Hiện Console", "language": "Ngôn ngữ"
        }
    }

    def __init__(self):
        self.current_lang = "en"

    def set_language(self, lang_code):
        if lang_code in self.STRINGS:
            self.current_lang = lang_code

    def get(self, key):
        return self.STRINGS.get(self.current_lang, {}).get(key, key)


lang = LanguageManager()
