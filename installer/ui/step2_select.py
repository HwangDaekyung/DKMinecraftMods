"""Step 2 — 설치 항목 선택"""
from pathlib import Path
import customtkinter as ctk
import config
from core.forge_installer import is_forge_installed
from core.mc_finder import get_mods_dir


class Step2SelectFrame(ctk.CTkFrame):
    def __init__(self, master, state: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.state = state
        self._check_vars = {}      # 설치 항목 체크박스
        self._delete_vars = {}     # 삭제 항목 체크박스
        self._build()

    def _build(self):
        # ── 고정 헤더 ─────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="설치 항목 선택",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(10, 4))

        ctk.CTkLabel(
            self,
            text="설치할 항목을 선택하세요. 필수 항목은 해제할 수 없습니다.",
            text_color="gray70",
        ).pack(pady=(0, 8))

        # ── 스크롤 영역 ───────────────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self._scroll.pack(fill="both", expand=True, padx=0, pady=(0, 4))

        # ── Forge ────────────────────────────────────────────────
        self._add_section("⚙️  Forge 1.12.2")
        self._add_item(
            key="forge",
            label="Forge 1.12.2-14.23.5.2847",
            desc="마인크래프트 모드 로더 (필수)",
            required=True,
        )

        # ── 모드 ─────────────────────────────────────────────────
        self._add_section("📦  모드")
        for mod in config.MODS:
            self._add_item(
                key=mod["id"],
                label=mod["name"],
                desc=mod["description"],
                required=mod["required"],
            )

        # ── 서버 설정 ─────────────────────────────────────────────
        self._add_section("🌐  서버")
        self._add_item(
            key="server_ip",
            label="서버 IP 자동 등록",
            desc=f"{config.SERVER_NAME} ({config.SERVER_IP})",
            required=False,
        )

        # ── 기존 모드 삭제 (on_show에서 채워짐) ───────────────────
        self._add_section("🗑️  기존 모드 삭제")

        self._delete_hint = ctk.CTkLabel(
            self._scroll,
            text="경로 확인 후 목록이 표시됩니다.",
            text_color="gray50",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._delete_hint.pack(fill="x", padx=16, pady=(0, 6))

        self._delete_container = ctk.CTkFrame(
            self._scroll, fg_color="transparent"
        )
        self._delete_container.pack(fill="x")

    # ── 섹션/항목 추가 헬퍼 ──────────────────────────────────────

    def _add_section(self, title: str):
        ctk.CTkLabel(
            self._scroll, text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(10, 2))
        ctk.CTkFrame(
            self._scroll, height=1, fg_color="gray30"
        ).pack(fill="x", padx=16, pady=(0, 4))

    def _add_item(self, key: str, label: str, desc: str, required: bool):
        var = ctk.BooleanVar(value=True)
        self._check_vars[key] = var

        if required:
            var.trace_add("write", lambda *_, v=var: v.set(True) if not v.get() else None)

        row = ctk.CTkFrame(self._scroll, fg_color="gray17", corner_radius=8)
        row.pack(fill="x", padx=16, pady=3)

        ctk.CTkCheckBox(
            row, text=label, variable=var,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=12, pady=8)

        tag = "🔒 필수" if required else ""
        ctk.CTkLabel(
            row, text=f"{tag}  {desc}".strip(),
            text_color="gray60",
            font=ctk.CTkFont(size=11),
        ).pack(side="right", padx=12)

    # ── 기존 모드 목록 (on_show마다 새로 그림) ────────────────────

    def _refresh_delete_list(self):
        # 컨테이너 초기화
        for w in self._delete_container.winfo_children():
            w.destroy()
        self._delete_vars.clear()

        mc_path = self.state.get("mc_path", "")
        if not mc_path:
            return

        mods_dir = get_mods_dir(mc_path)
        jar_files = sorted(mods_dir.glob("*.jar"))

        if not jar_files:
            self._delete_hint.configure(text="mods 폴더가 비어있습니다.")
            return

        self._delete_hint.configure(
            text=f"mods 폴더에 {len(jar_files)}개 파일이 있습니다. 삭제할 파일을 선택하세요."
        )

        # 전체 선택 버튼
        btn_row = ctk.CTkFrame(self._delete_container, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkButton(
            btn_row, text="전체 선택", width=80, height=26,
            fg_color="gray30", hover_color="gray40",
            font=ctk.CTkFont(size=11),
            command=lambda: [v.set(True) for v in self._delete_vars.values()],
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="전체 해제", width=80, height=26,
            fg_color="gray30", hover_color="gray40",
            font=ctk.CTkFont(size=11),
            command=lambda: [v.set(False) for v in self._delete_vars.values()],
        ).pack(side="left")

        # 파일 목록
        for jar in jar_files:
            var = ctk.BooleanVar(value=False)
            self._delete_vars[str(jar)] = var

            row = ctk.CTkFrame(
                self._delete_container, fg_color="gray17", corner_radius=8
            )
            row.pack(fill="x", padx=16, pady=2)

            ctk.CTkCheckBox(
                row, text=jar.name, variable=var,
                font=ctk.CTkFont(size=11),
                text_color="#e74c3c",
            ).pack(side="left", padx=12, pady=6)

            size_kb = jar.stat().st_size // 1024
            ctk.CTkLabel(
                row, text=f"{size_kb:,} KB",
                text_color="gray50",
                font=ctk.CTkFont(size=10),
            ).pack(side="right", padx=12)

    # ── 훅 ───────────────────────────────────────────────────────

    def on_show(self):
        mc_path = self.state.get("mc_path", "")
        if mc_path and is_forge_installed(mc_path):
            self._check_vars["forge"].set(False)
        self._refresh_delete_list()

    def get_selections(self) -> dict:
        return {k: v.get() for k, v in self._check_vars.items()}

    def get_files_to_delete(self) -> list[str]:
        """삭제 체크된 파일 경로 목록 반환."""
        return [path for path, var in self._delete_vars.items() if var.get()]
