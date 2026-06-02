"""Step 4 — 완료 화면"""
import subprocess
import platform
import customtkinter as ctk


class Step4DoneFrame(ctk.CTkFrame):
    def __init__(self, master, state: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.state = state
        self._success_frame = None
        self._fail_frame    = None
        self._build()

    def _build(self):
        # ── 성공 ────────────────────────────────────────────────
        self._success_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(
            self._success_frame, text="🎉",
            font=ctk.CTkFont(size=52),
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self._success_frame, text="설치 완료!",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack()

        ctk.CTkLabel(
            self._success_frame,
            text=(
                "마인크래프트 런처를 열고\n"
                "Forge 1.12.2 프로파일로 실행하세요."
            ),
            text_color="gray70",
            justify="center",
            font=ctk.CTkFont(size=13),
        ).pack(pady=(8, 20))

        ctk.CTkButton(
            self._success_frame,
            text="마인크래프트 런처 열기",
            height=42, font=ctk.CTkFont(size=14),
            command=self._open_launcher,
        ).pack()

        # ── 실패 ────────────────────────────────────────────────
        self._fail_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(
            self._fail_frame, text="❌",
            font=ctk.CTkFont(size=52),
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self._fail_frame, text="설치 중 오류가 발생했습니다",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e74c3c",
        ).pack()

        self._err_label = ctk.CTkLabel(
            self._fail_frame, text="",
            text_color="gray70",
            wraplength=460,
            justify="center",
        )
        self._err_label.pack(pady=(8, 0))

    def on_show(self):
        """완료 화면 표시 시 성공/실패 분기."""
        success = self.state.get("install_success", False)
        err_msg = self.state.get("install_error", "")

        # 기존 프레임 숨기기
        self._success_frame.pack_forget()
        self._fail_frame.pack_forget()

        if success:
            self._success_frame.pack(fill="both", expand=True)
        else:
            self._err_label.configure(text=err_msg)
            self._fail_frame.pack(fill="both", expand=True)

    def _open_launcher(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["explorer", "minecraft://"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Minecraft"])
        except Exception:
            pass
