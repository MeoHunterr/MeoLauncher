import os
import zipfile
import shutil
import sys
import logging

logger = logging.getLogger(__name__)


class InstanceDoctor:
    NATIVE_EXTENSIONS = (".dll", ".dylib", ".so")

    def __init__(self, root_dir):
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else root_dir
            self.natives_dir = os.path.join(base, "app", "game", "natives")
        else:
            self.natives_dir = os.path.join(root_dir, "app", "game", "natives")

    def heal(self, natives_list):
        self._extract_natives(natives_list)

    def _extract_natives(self, natives_list):
        if os.path.exists(self.natives_dir):
            try:
                shutil.rmtree(self.natives_dir)
            except (IOError, OSError, PermissionError) as e:
                logger.debug("Could not clean natives dir: %s", e)
        
        os.makedirs(self.natives_dir, exist_ok=True)
        
        for native_jar in natives_list:
            if not os.path.exists(native_jar):
                continue
            try:
                with zipfile.ZipFile(native_jar, 'r') as zf:
                    for file in zf.namelist():
                        if file.endswith(self.NATIVE_EXTENSIONS):
                            zf.extract(file, self.natives_dir)
            except (zipfile.BadZipFile, IOError, OSError) as e:
                logger.debug("Failed to extract native %s: %s", native_jar, e)
