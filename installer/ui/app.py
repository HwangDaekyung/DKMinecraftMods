"""메인 앱 윈도우"""
import customtkinter as ctk
import config
from ui.step1_path    import Step1PathFrame
from ui.step2_select  import Step2SelectFrame
from ui.step3_install import Step3InstallFrame
from ui.step4_done    import Step4DoneFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class InstallerApp(ctk.CTk):
    STEPS = ["경로 확인", "항목 선택", "설치 중", "완료"]

    def __init__(self):
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(config.WINDOW_SIZE)
        self.resizable(False, False)

        # 공유 상태
        self._state: dict = {}
        self._current = 0

        self._build_header()
        self._build_step_indicator()
        self._build_content()
        self._build_footer()

        self._show_step(0)

    # ── 레이아웃 ────────────────────────────────────────────────

    def _build_header(self):
        hdr = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a2e", height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr,
            text=f"  🎮  {config.APP_TITLE}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            anchor="w",
        ).pack(side="left", padx=16, fill="y")

        ctk.CTkLabel(
            hdr,
            text=f"v{config.APP_VERSION}",
            text_color="gray50",
            font=ctk.CTkFont(size=11),
        ).pack(side="right", padx=16)

    def _build_step_indicator(self):
        bar = ctk.CTkFrame(self, fg_color="gray15", height=44, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self._step_labels = []
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        for i, name in enumerate(self.STEPS):
            # 번호 원
            num = ctk.CTkLabel(
                inner,
                text=str(i + 1),
                width=26, height=26,
                corner_radius=13,
                fg_color="gray35",
                font=ctk.CTkFont(size=11, weight="bold"),
            )
            num.grid(row=0, column=i * 3, padx=2)

            # 이름
            lbl = ctk.CTkLabel(
                inner,
                text=name,
                font=ctk.CTkFont(size=11),
                text_color="gray60",
            )
            lbl.grid(row=0, column=i * 3 + 1, padx=(0, 4))

            self._step_labels.append((num, lbl))

            # 구분선
            if i < len(self.STEPS) - 1:
                ctk.CTkLabel(
                    inner, text="──", text_color="gray40",
                    font=ctk.CTkFont(size=11),
                ).grid(row=0, column=i * 3 + 2, padx=4)

    def _build_content(self):
        self._content = ctk.CTkFrame(self, fg_color="gray13", corner_radius=0)
        self._content.pack(fill="both", expand=True, padx=0, pady=0)

        self._state["on_install_done"] = self._on_install_done

        self._frames = [
            Step1PathFrame(self._content,   self._state),
            Step2SelectFrame(self._content, self._state),
            Step3InstallFrame(self._content, self._state),
            Step4DoneFrame(self._content,   self._state),
        ]

    def _build_footer(self):
        footer = ctk.CTkFrame(self, corner_radius=0, fg_color="gray17", height=60)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self._btn_prev = ctk.CTkButton(
            footer, text="← 이전", width=110, height=36,
            fg_color="gray30", hover_color="gray40",
            command=self._prev,
        )
        self._btn_prev.pack(side="left", padx=20, pady=12)

        self._btn_next = ctk.CTkButton(
            footer, text="다음 →", width=110, height=36,
            command=self._next,
        )
        self._btn_next.pack(side="right", padx=20, pady=12)

    # ── 네비게이션 ───────────────────────────────────────────────

    def _show_step(self, idx: int):
        for f in self._frames:
            f.pack_forget()
        self._frames[idx].pack(fill="both", expand=True, padx=0, pady=0)

        # on_show 훅
        if hasattr(self._frames[idx], "on_show"):
            self._frames[idx].on_show()

        self._update_step_indicator(idx)
        self._update_buttons(idx)
        self._current = idx

    def _update_step_indicator(self, current: int):
        for i, (num, lbl) in enumerate(self._step_labels):
            if i < current:
                num.configure(fg_color="#2ecc71", text_color="white")
                lbl.configure(text_color="#2ecc71")
            elif i == current:
                num.configure(fg_color="#3498db", text_color="white")
                lbl.configure(text_color="white")
            else:
                num.configure(fg_color="gray35", text_color="gray70")
                lbl.configure(text_color="gray60")

    def _update_buttons(self, idx: int):
        # 이전 버튼
        if idx == 0 or idx == 2:  # 설치 중엔 이전 막기
            self._btn_prev.configure(state="disabled")
        else:
            self._btn_prev.configure(state="normal")

        # 다음 버튼
        if idx == 2:  # 설치 중 — 자동 전환
            self._btn_next.configure(state="disabled", text="설치 중...")
        elif idx == 3:  # 완료
            self._btn_next.configure(state="normal", text="닫기", command=self.destroy)
        else:
            self._btn_next.configure(state="normal", text="다음 →", command=self._next)

    def _prev(self):
        if self._current > 0:
            self._show_step(self._current - 1)

    def _next(self):
        idx = self._current

        if idx == 0:
            if not self._frames[0].is_valid():
                return
            self._show_step(1)

        elif idx == 1:
            selections = self._frames[1].get_selections()
            self._state["selections"] = selections
            self._show_step(2)
            # 설치 시작
            self._frames[2].start(selections)

        elif idx == 3:
            self.destroy()

    def _on_install_done(self, success: bool):
        """설치 완료 콜백 (백그라운드 스레드에서 호출됨)."""
        self.after(800, lambda: self._show_step(3))
