"""Step 1 — 마인크래프트 경로 확인"""
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

from core.mc_finder import get_default_mc_path, is_valid_mc_path


class Step1PathFrame(ctk.CTkFrame):
    def __init__(self, master, state: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.state = state  # 공유 상태 dict {"mc_path": ...}
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="마인크래프트 경로",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 4))

        ctk.CTkLabel(
            self,
            text="설치 프로그램이 .minecraft 폴더를 찾았습니다.\n경로가 다르면 직접 선택해주세요.",
            text_color="gray70",
            justify="center",
        ).pack(pady=(0, 16))

        # 경로 입력 + 버튼
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=30)

        self.path_var = tk.StringVar()
        self.path_entry = ctk.CTkEntry(
            row, textvariable=self.path_var,
            height=38, font=ctk.CTkFont(size=12),
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row, text="찾아보기", width=90, height=38,
            command=self._browse,
        ).pack(side="right")

        # 상태 메시지
        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(12, 0))

        # 자동 탐지
        default = get_default_mc_path()
        if default:
            self.path_var.set(str(default))
            self._validate()
        else:
            self._set_status("❌ 경로를 자동으로 찾지 못했습니다. 직접 선택해주세요.", "tomato")

        # 경로 변경 감지
        self.path_var.trace_add("write", lambda *_: self._validate())

    def _browse(self):
        chosen = filedialog.askdirectory(title=".minecraft 폴더 선택")
        if chosen:
            self.path_var.set(chosen)

    def _validate(self):
        path = self.path_var.get().strip()
        if is_valid_mc_path(path):
            self.state["mc_path"] = path
            self._set_status("✅ 유효한 마인크래프트 경로입니다.", "#2ecc71")
            return True
        else:
            self.state["mc_path"] = None
            self._set_status("❌ 유효한 .minecraft 폴더가 아닙니다.", "tomato")
            return False

    def _set_status(self, msg: str, color: str):
        self.status_label.configure(text=msg, text_color=color)

    def is_valid(self) -> bool:
        return bool(self.state.get("mc_path"))
