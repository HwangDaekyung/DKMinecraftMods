"""GitHub Releases에서 모드 파일 다운로드"""
import requests
from pathlib import Path
from typing import Callable

import config


def get_latest_release() -> dict:
    """GitHub API로 최신 릴리즈 정보 조회."""
    url = (
        f"https://api.github.com/repos/"
        f"{config.GITHUB_OWNER}/{config.GITHUB_REPO}/releases/latest"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_asset_url(release: dict, filename: str) -> str | None:
    """릴리즈에서 파일명으로 download URL 조회."""
    for asset in release.get("assets", []):
        if asset["name"] == filename:
            return asset["browser_download_url"]
    return None


def download_file(
    url: str,
    dest: Path,
    progress_cb: Callable[[int, int], None] | None = None,
) -> None:
    """
    URL에서 파일 다운로드.
    progress_cb(downloaded_bytes, total_bytes) 콜백으로 진행률 전달.
    """
    with requests.get(url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb:
                        progress_cb(downloaded, total)


def download_mod(
    mod: dict,
    mods_dir: Path,
    release: dict,
    progress_cb: Callable[[int, int], None] | None = None,
) -> Path:
    """
    단일 모드 파일 다운로드.
    이미 존재하면 스킵.
    Returns: 저장된 파일 경로
    """
    dest = mods_dir / mod["filename"]
    if dest.exists():
        return dest   # 이미 있으면 스킵

    url = get_asset_url(release, mod["filename"])
    if url is None:
        raise FileNotFoundError(
            f"GitHub 릴리즈에서 '{mod['filename']}' 를 찾을 수 없습니다."
        )

    download_file(url, dest, progress_cb)
    return dest
