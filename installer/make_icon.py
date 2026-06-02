"""아이콘 생성 스크립트 — 빌드 전 실행"""
from PIL import Image, ImageDraw, ImageFont
import os, subprocess, platform

def make_icon():
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    os.makedirs("assets", exist_ok=True)

    # ── PNG 생성 ──────────────────────────────────────────────
    pngs = {}
    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        margin = int(size * 0.06)
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=int(size * 0.18), fill=(30, 120, 30)
        )
        m2 = int(size * 0.13)
        draw.rounded_rectangle(
            [m2, m2, size - m2, size - m2],
            radius=int(size * 0.13), fill=(46, 184, 46)
        )

        font_size = max(int(size * 0.42), 8)
        try:
            if platform.system() == "Darwin":
                font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", font_size, index=1)
            elif platform.system() == "Windows":
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
            else:
                font = ImageFont.load_default(size=font_size)
        except Exception:
            font = ImageFont.load_default(size=font_size)

        text = "DK"
        tw = int(font.getlength(text))
        asc, desc = font.getmetrics()
        th = asc + desc
        draw.text(((size - tw) // 2, (size - th) // 2), text, fill="white", font=font)

        pngs[size] = img

    # ── macOS .icns ───────────────────────────────────────────
    if platform.system() == "Darwin":
        iconset = "assets/DKInstaller.iconset"
        os.makedirs(iconset, exist_ok=True)
        for size, img in pngs.items():
            img.save(f"{iconset}/icon_{size}x{size}.png")
            if size <= 512:
                img.resize((size * 2, size * 2), Image.LANCZOS).save(
                    f"{iconset}/icon_{size}x{size}@2x.png"
                )
        subprocess.run(
            ["iconutil", "-c", "icns", iconset, "-o", "assets/icon.icns"],
            check=True
        )
        print("✅ icon.icns 생성 완료")

    # ── Windows .ico ──────────────────────────────────────────
    ico_sizes = [16, 32, 48, 64, 128, 256]
    ico_imgs = [pngs[s].resize((s, s), Image.LANCZOS) for s in ico_sizes if s in pngs]
    ico_imgs[0].save(
        "assets/icon.ico",
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=ico_imgs[1:]
    )
    print("✅ icon.ico 생성 완료")


if __name__ == "__main__":
    make_icon()
