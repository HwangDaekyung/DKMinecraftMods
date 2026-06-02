@echo off
echo === DKInstaller Windows 빌드 ===

pip install -r requirements.txt

python make_icon.py

pyinstaller ^
  --onefile ^
  --windowed ^
  --clean ^
  -y ^
  --name "DKInstaller" ^
  --icon "assets/icon.ico" ^
  --add-data "config.py;." ^
  main.py

echo.
echo 빌드 완료: dist\DKInstaller.exe
pause
