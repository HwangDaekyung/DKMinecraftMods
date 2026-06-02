"""DKInstaller 진입점"""
from ui.app import InstallerApp


def main():
    app = InstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
