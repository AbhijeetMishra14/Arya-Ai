import os
import sys
import warnings

# Suppress the Google Generative AI package deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning)

# Ensure the app can find the models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_to_startup():
    try:
        import os, sys, winreg
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "ARYA_OS", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
    except: pass

def main():
    add_to_startup()
    # Force Windows OS to recognize the custom icon in the Taskbar
    try:
        import ctypes
        myappid = 'arya.os.production.v2.0.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    # If compiled as Windowed EXE, stdin doesn't exist. Immediately launch GUI.
    if getattr(sys, 'frozen', False):
        from arya.interfaces.gui import start_gui
        start_gui()
        return

    print("Welcome to ARYA (Advanced Responsive Yielding Assistant)")
    print("1. Start CUI (Command Line Interface)")
    print("2. Start GUI (Graphical User Interface)")
    
    try:
        choice = input("Select mode (1/2): ").strip()
    except Exception:
        choice = '2' # Default to GUI if UI env has no terminal access
        
    if choice == '1':
        from arya.interfaces.cui import start_cui
        start_cui()
    else:
        print("Starting GUI mode...")
        from arya.interfaces.gui import start_gui
        start_gui()

if __name__ == "__main__":
    main()
