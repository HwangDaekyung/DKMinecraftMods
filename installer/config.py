# ──────────────────────────────────────────────
#  설정 파일 — 배포 전 반드시 수정하세요
# ──────────────────────────────────────────────

# GitHub 릴리즈 (모드 파일 다운로드 출처)
GITHUB_OWNER       = "HwangDaekyung"   # ← 본인 GitHub 아이디
GITHUB_REPO        = "DKMinecraftMods"  # ← 릴리즈용 repo 이름
MODS_RELEASE_TAG   = "v1.1.0"          # ← 모드 파일이 있는 릴리즈 태그

# Forge
FORGE_VERSION       = "1.12.2-14.23.5.2847"
FORGE_INSTALLER_URL = (
    "https://maven.minecraftforge.net/net/minecraftforge/forge/"
    f"{FORGE_VERSION}/forge-{FORGE_VERSION}-installer.jar"
)

# 서버 정보
SERVER_NAME = "파산게임2"
SERVER_IP   = "technology-can.gl.joinmc.link"   # ← 서버 IP:포트

# ──────────────────────────────────────────────
#  설치할 모드 목록
#  filename: GitHub Release에 올린 asset 파일명과 정확히 일치해야 함
# ──────────────────────────────────────────────
MODS = [
    {
        "id":          "dkrecipes",
        "name":        "DKRecipes",
        "filename":    "DKRecipes-1.0.0.jar",   # ✅ 릴리즈에 업로드됨
        "required":    True,
        "description": "커스텀 레시피 & HUD 모드 (필수)",
    },
    {
        "id":          "customnpc",
        "name":        "CustomNPC",
        "filename":    "CustomNPCs_1.12.2-.05Jul20.jar",   # ✅ 릴리즈에 업로드됨
        "required":    True,
        "description": "커스텀 NPC 모드 (필수)",
    },
    {
        "id":          "harvestcraft",
        "name":        "Pam's HarvestCraft",
        "filename":    "Pam.s.HarvestCraft.1.12.2zg.jar",  # ✅ 릴리즈에 업로드됨
        "required":    True,
        "description": "음식 재료 모드 (필수)",
    },
    {
        "id":          "schematica",
        "name":        "Schematica",
        "filename":    "Schematica-1.12.2-1.8.0.169-universal.jar",  # ✅ 릴리즈에 업로드됨
        "required":    False,
        "description": "건축 복사/붙여넣기 모드 (선택)",
    },
]

# UI
APP_TITLE   = "파산게임2 모드 설치 프로그램"
APP_VERSION = "1.1.0"
WINDOW_SIZE = "620x480"
