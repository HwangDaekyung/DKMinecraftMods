"""Forge 설치"""
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import config
from core.mc_finder import find_java
from core.mod_downloader import download_file


def is_forge_installed(mc_path: str) -> bool:
    """Forge가 이미 설치되어 있는지 확인."""
    versions_dir = Path(mc_path) / "versions"
    if not versions_dir.exists():
        return False
    for d in versions_dir.iterdir():
        if d.is_dir() and "forge" in d.name.lower() and "1.12.2" in d.name:
            return True
    return False


def install_forge(
    mc_path: str,
    progress_cb: Callable[[str], None] | None = None,
) -> bool:
    """
    Forge 1.12.2 설치.
    Forge 1.12.2 설치 프로그램은 GUI 방식만 지원하므로
    설치 창을 띄우고 유저가 완료할 때까지 대기합니다.
    """
    java = find_java()
    if java is None:
        raise EnvironmentError(
            "Java를 찾을 수 없습니다.\n"
            "https://adoptium.net/ 에서 Java 8을 먼저 설치해주세요."
        )

    if progress_cb:
        progress_cb("Forge 설치 파일 다운로드 중...")

    tmp_dir = Path(tempfile.mkdtemp())
    installer_jar = tmp_dir / f"forge-{config.FORGE_VERSION}-installer.jar"

    download_file(config.FORGE_INSTALLER_URL, installer_jar)

    if progress_cb:
        progress_cb(
            "Forge 설치 창이 열립니다.\n"
            "① 'Install client' 선택 확인\n"
            "② OK 클릭\n"
            "③ 설치 완료 후 창이 닫힐 때까지 기다려주세요."
        )

    # GUI 설치 창을 열고 완료될 때까지 대기 (blocking)
    result = subprocess.run(
        [java, "-jar", str(installer_jar)],
        cwd=str(mc_path),   # .minecraft 폴더에서 실행해야 경로를 자동 인식
    )

    if result.returncode != 0:
        raise RuntimeError("Forge 설치가 완료되지 않았습니다.")

    if progress_cb:
        progress_cb("Forge 설치 완료")

    return True
