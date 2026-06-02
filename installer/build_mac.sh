#!/bin/bash
echo "=== DKInstaller macOS 빌드 ==="

pip3 install -r requirements.txt

pyinstaller \
  --onedir \
  --windowed \
  --clean \
  -y \
  --name "DKInstaller" \
  --icon "assets/icon.icns" \
  --add-data "config.py:." \
  main.py

echo ""
echo "빌드 완료: dist/DKInstaller"
