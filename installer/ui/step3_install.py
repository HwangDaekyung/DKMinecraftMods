"""Step 3 — 설치 진행"""
import threading
import queue
import platform
import webbrowser
from pathlib import Path
import customtkinter as ctk

import config
from core.mc_finder import get_mods_dir, find_java
from core.forge_installer import install_forge, is_forge_installed
from core.mod_downloader import download_mod, get_latest_release
from core.servers_dat import add_server


# ── 메시지 타입 ────────────────────────────────────────────────
MSG_LOG      = "log"       # (type, text, color)
MSG_PROGRESS = "progress"  # (type, value 0.0~1.0)
MSG_DONE     = "done"      # (type, success, error_msg)
MSG_NO_JAVA  = "no_java"   # Java 없음 — UI에서 버튼 표시

JAVA_URL = "https://adoptium.net/temurin/releases/?version=8"


class Step3InstallFrame(ctk.CTkFrame):
    def __init__(self, master, state: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.state = state
        self._q: queue.Queue = queue.Queue()
        self._done = False
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="설치 진행 중",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(10, 4))

        # 진행 바
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(8, 4), padx=30, fill="x")

        self.progress_label = ctk.CTkLabel(
            self, text="준비 중...", text_color="gray70",
            font=ctk.CTkFont(size=12),
        )
        self.progress_label.pack()

        # 로그창
        self.log_box = ctk.CTkTextbox(
            self, height=200,
            font=ctk.CTkFont(family="Courier New", size=11),
            state="disabled",
        )
        self.log_box.pack(fill="both", expand=True, padx=30, pady=(10, 0))
        self.log_box.tag_config("ok",   foreground="#2ecc71")
        self.log_box.tag_config("err",  foreground="#e74c3c")
        self.log_box.tag_config("info", foreground="#95a5a6")

        # Java 없을 때 표시할 패널 (평소엔 숨김)
        self._java_panel = ctk.CTkFrame(self, fg_color="#2c1a1a", corner_radius=10)

        ctk.CTkLabel(
            self._java_panel,
            text="⚠️  Java 8이 설치되어 있지 않습니다",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e74c3c",
        ).pack(pady=(12, 4))

        # OS별 안내 문구
        if platform.system() == "Windows":
            guide = "아래 버튼을 눌러 Java 설치 페이지를 열고\n.msi 파일을 다운로드해서 설치해주세요."
        else:
            guide = "아래 버튼을 눌러 Java 설치 페이지를 열고\n.pkg 파일을 다운로드해서 설치해주세요."

        ctk.CTkLabel(
            self._java_panel,
            text=guide,
            text_color="gray70",
            font=ctk.CTkFont(size=12),
            justify="center",
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            self._java_panel,
            text="☕  Java 설치 페이지 열기",
            height=38,
            font=ctk.CTkFont(size=13),
            command=lambda: webbrowser.open(JAVA_URL),
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            self._java_panel,
            text="설치 완료 후 프로그램을 다시 실행해주세요.",
            text_color="gray50",
            font=ctk.CTkFont(size=11),
        ).pack(pady=(0, 12))

    # ── 설치 시작 ────────────────────────────────────────────────

    def start(self, selections: dict, files_to_delete: list[str] | None = None):
        self._done = False
        self.progress_bar.set(0)
        self._java_panel.pack_forget()
        thread = threading.Thread(
            target=self._install_worker,
            args=(selections, files_to_delete or []),
            daemon=True,
        )
        thread.start()
        self._poll_queue()

    def _install_worker(self, selections: dict, files_to_delete: list[str]):
        mc_path  = self.state["mc_path"]
        mods_dir = get_mods_dir(mc_path)
        steps    = self._count_steps(selections, files_to_delete)
        done     = 0

        def progress(n):
            self._q.put((MSG_PROGRESS, n / steps))

        def log(msg, color="info"):
            self._q.put((MSG_LOG, msg, color))

        try:
            # ── Java 사전 확인 ────────────────────────────────────
            if selections.get("forge") and find_java() is None:
                self._q.put((MSG_NO_JAVA,))
                return

            # 0. 기존 모드 삭제
            if files_to_delete:
                log(f"🗑️  기존 모드 {len(files_to_delete)}개 삭제 중...")
                for path in files_to_delete:
                    try:
                        Path(path).unlink()
                        log(f"   삭제: {Path(path).name}", "info")
                    except Exception as e:
                        log(f"   삭제 실패: {Path(path).name} ({e})", "err")
                log("✅ 기존 모드 삭제 완료", "ok")
                done += 1
                progress(done)

            # 1. Forge
            if selections.get("forge"):
                log("🔧 Forge 설치 창이 열립니다.")
                log("   ① 'Install client' 선택 확인", "info")
                log("   ② OK 클릭 → 설치 완료 후 창 닫기", "info")
                install_forge(mc_path, progress_cb=log)
                log("✅ Forge 설치 완료", "ok")
                done += 1
                progress(done)

            # 2. 모드
            selected_mods = [m for m in config.MODS if selections.get(m["id"])]
            if selected_mods:
                log("📡 GitHub 릴리즈 정보 조회 중...")
                release = get_latest_release()
                log(f"   릴리즈: {release.get('tag_name', '?')}", "info")

                for mod in selected_mods:
                    log(f"⬇️  {mod['name']} 다운로드 중...")

                    def make_cb(mod_name):
                        def cb(dl, total):
                            if total > 0:
                                pct = int(dl / total * 100)
                                self._q.put((MSG_LOG, f"   {mod_name}: {pct}%", "info"))
                        return cb

                    dest = download_mod(mod, mods_dir, release, make_cb(mod["name"]))
                    log(f"✅ {mod['name']} 완료 → {dest.name}", "ok")
                    done += 1
                    progress(done)

            # 3. 서버 IP
            if selections.get("server_ip"):
                log("🌐 서버 IP 등록 중...")
                added = add_server(mc_path)
                if added:
                    log(f"✅ 서버 IP 등록 완료 ({config.SERVER_IP})", "ok")
                else:
                    log("ℹ️  서버 IP 이미 등록되어 있습니다.", "info")
                done += 1
                progress(done)

            self._q.put((MSG_DONE, True, ""))

        except Exception as e:
            log(f"❌ 오류 발생: {e}", "err")
            self._q.put((MSG_DONE, False, str(e)))

    def _count_steps(self, selections: dict, files_to_delete: list = []) -> int:
        n = 0
        if files_to_delete: n += 1
        if selections.get("forge"): n += 1
        for mod in config.MODS:
            if selections.get(mod["id"]): n += 1
        if selections.get("server_ip"): n += 1
        return max(n, 1)

    # ── 큐 폴링 ─────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                msg = self._q.get_nowait()
                kind = msg[0]

                if kind == MSG_LOG:
                    _, text, color = msg
                    self._append_log(text, color)
                    self.progress_label.configure(text=text[:60])

                elif kind == MSG_PROGRESS:
                    _, value = msg
                    self.progress_bar.set(value)

                elif kind == MSG_NO_JAVA:
                    # Java 없음 — 안내 패널 표시
                    self.progress_label.configure(text="Java가 필요합니다.")
                    self._java_panel.pack(fill="x", padx=30, pady=(10, 0))
                    self._done = True
                    self.state["install_success"] = False
                    self.state["install_error"] = "Java 미설치"
                    if cb := self.state.get("on_install_done"):
                        cb(False)
                    return

                elif kind == MSG_DONE:
                    _, success, err = msg
                    self._done = True
                    self.state["install_success"] = success
                    self.state["install_error"]   = err
                    if success:
                        self.progress_bar.set(1.0)
                        self.progress_label.configure(text="설치 완료!")
                    else:
                        self.progress_label.configure(text="설치 실패")
                    if cb := self.state.get("on_install_done"):
                        cb(success)
                    return

        except queue.Empty:
            pass

        if not self._done:
            self.after(100, self._poll_queue)

    def _append_log(self, text: str, color: str = "info"):
        tag = {"ok": "ok", "err": "err"}.get(color, "info")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    @property
    def is_done(self) -> bool:
        return self._done
