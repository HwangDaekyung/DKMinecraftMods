"""Step 2 — 설치 항목 선택"""
import customtkinter as ctk
import config
from core.forge_installer import is_forge_installed


class Step2SelectFrame(ctk.CTkFrame):
    def __init__(self, master, state: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.state = state
        self._check_vars = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="설치 항목 선택",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(10, 4))

        ctk.CTkLabel(
            self,
            text="설치할 항목을 선택하세요. 필수 항목은 해제할 수 없습니다.",
            text_color="gray70",
        ).pack(pady=(0, 16))

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

    def _add_section(self, title: str):
        ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=30, pady=(10, 2))
        ctk.CTkFrame(self, height=1, fg_color="gray30").pack(fill="x", padx=30, pady=(0, 4))

    def _add_item(self, key: str, label: str, desc: str, required: bool):
        var = ctk.BooleanVar(value=True)
        self._check_vars[key] = var

        row = ctk.CTkFrame(self, fg_color="gray17", corner_radius=8)
        row.pack(fill="x", padx=30, pady=3)

        cb = ctk.CTkCheckBox(
            row, text=label,
            variable=var,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled" if required else "normal",
        )
        cb.pack(side="left", padx=12, pady=8)

        ctk.CTkLabel(
            row, text=desc,
            text_color="gray60",
            font=ctk.CTkFont(size=11),
        ).pack(side="right", padx=12)

    def on_show(self):
        """Step 2가 표시될 때 Forge 이미 설치 여부 체크."""
        mc_path = self.state.get("mc_path", "")
        if mc_path and is_forge_installed(mc_path):
            self._check_vars["forge"].set(False)

    def get_selections(self) -> dict:
        """선택된 항목 반환 {key: bool}."""
        return {k: v.get() for k, v in self._check_vars.items()}
