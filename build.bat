@echo off
echo Building ARYA OS Standalone Executable...
echo Cleaning very old builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo Activating Virtual Environment...
call .\venv\Scripts\activate.bat

echo Running PyInstaller Engine...
REM Find the customtkinter module path to dynamically pull its assets
FOR /F "tokens=*" %%g IN ('python -c "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"') do (SET CTK_PATH=%%g)

REM Build the executable via PyInstaller
pyinstaller --noconfirm --onedir --windowed --uac-admin --icon="arya_logo_alt.ico" --name "ARYA OS" --add-data "%CTK_PATH%;customtkinter/" --add-data ".env;." --add-data "arya_emblem.png;." --add-data "arya_logo_alt.ico;." --hidden-import "PIL._tkinter_finder" --hidden-import "pystray" --hidden-import "pymongo" --hidden-import "psutil" --hidden-import "pyttsx3" main.py

echo.
echo =======================================
echo BUILD FINISHED SUCCESSFULLY!
echo Look inside the 'dist\ARYA OS' folder.
echo You can double-click 'ARYA OS.exe' now.
echo =======================================
pause
