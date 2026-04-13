@echo off
echo ========================================================
echo   ARYA OS v2.0 NEURAL CORE - BINARY BUILD ENGINE
echo ========================================================
echo.

:: Ensure venv is active context
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo [1/2] Purging old neural artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/2] Compiling Neuro-Core Binary (PyInstaller)...
:: Extraction of native assets for bundling
python -c "import cv2, os, shutil; path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'); shutil.copy(path, '.')"

pyinstaller --noconsole --onefile --uac-admin --icon="arya_logo_alt.ico" ^
    --add-data ".env;." ^
    --add-data "haarcascade_frontalface_default.xml;." ^
    --add-data "arya\fonts;fonts" ^
    --add-data "arya_emblem.png;." ^
    --add-data "arya_logo_alt.ico;." ^
    --name "ARYA_OS_v2" ^
    main.py

echo.
echo ========================================================
echo   BINARY COMPLETE: "dist\ARYA_OS_v2.exe" is ready.
echo   NEXT STEP: Open Inno Setup and compile ARYA_Installer_v2.iss
echo ========================================================
pause
