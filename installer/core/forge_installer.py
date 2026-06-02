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
    forge_ver = config.FORGE_VERSION
    # 예: 1.12.2-forge1.12.2-14.23.5.2847
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
    progress_cb(message): 진행 상황 텍스트 콜백
    Returns: 성공 여부
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

    # 다운로드
    download_file(config.FORGE_INSTALLER_URL, installer_jar)

    if progress_cb:
        progress_cb("Forge 설치 실행 중... (잠시 기다려주세요)")

    # --installClient: GUI 없이 클라이언트 설치
    result = subprocess.run(
        [java, "-jar", str(installer_jar), "--installClient"],
        capture_output=True,
        text=True,
        cwd=str(tmp_dir),
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Forge 설치 실패:\n{result.stderr[-500:] if result.stderr else '알 수 없는 오류'}"
        )

    if progress_cb:
        progress_cb("Forge 설치 완료")

    return True
