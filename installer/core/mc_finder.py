"""마인크래프트 설치 경로 자동 탐지"""
import os
import sys
import platform
from pathlib import Path


def get_default_mc_path() -> Path | None:
    """OS별 기본 .minecraft 경로 반환. 없으면 None."""
    system = platform.system()

    if system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        path = Path(appdata) / ".minecraft"
    elif system == "Darwin":  # macOS
        path = Path.home() / "Library" / "Application Support" / "minecraft"
    else:  # Linux
        path = Path.home() / ".minecraft"

    return path if path.exists() else None


def is_valid_mc_path(path: str) -> bool:
    """입력된 경로가 유효한 .minecraft 폴더인지 확인."""
    p = Path(path)
    if not p.exists() or not p.is_dir():
        return False
    # versions 또는 launcher_profiles.json 이 있으면 진짜 .minecraft
    return (p / "versions").exists() or (p / "launcher_profiles.json").exists()


def get_mods_dir(mc_path: str) -> Path:
    """mods 폴더 경로 반환. 없으면 생성."""
    mods = Path(mc_path) / "mods"
    mods.mkdir(exist_ok=True)
    return mods


def find_java() -> str | None:
    """java 실행 파일 경로 반환. 없으면 None."""
    import shutil
    java = shutil.which("java")
    if java:
        return java

    # Windows: JAVA_HOME 환경변수 체크
    java_home = os.environ.get("JAVA_HOME", "")
    if java_home:
        candidate = Path(java_home) / "bin" / "java.exe"
        if candidate.exists():
            return str(candidate)

    # macOS: /usr/libexec/java_home 으로 탐지
    if platform.system() == "Darwin":
        import subprocess
        try:
            result = subprocess.run(
                ["/usr/libexec/java_home", "-v", "1.8"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                java_home = result.stdout.strip()
                candidate = Path(java_home) / "bin" / "java"
                if candidate.exists():
                    return str(candidate)
        except Exception:
            pass

    return None
