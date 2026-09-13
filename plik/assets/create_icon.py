"""Generates ultra-premium Minimal, Modern, Tech icons for Plik."""

import os
from PIL import Image, ImageEnhance

def make_icons():
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(assets_dir, "app_icon.png")
    ico_path = os.path.join(assets_dir, "app_icon.ico")
    paused_png_path = os.path.join(assets_dir, "app_icon_paused.png")
    paused_ico_path = os.path.join(assets_dir, "app_icon_paused.ico")

    if not os.path.exists(png_path):
        raise FileNotFoundError(f"Missing {png_path}")

    # 1. Active Icon (Emerald Neon)
    img_active = Image.open(png_path).convert("RGBA")
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img_active.save(ico_path, format="ICO", sizes=sizes)
    print(f"Saved active icon: {ico_path}")

    # 2. Paused Icon (Amber / Gold Tint)
    # Convert RGBA -> HSV, shift green (H ~ 150) to amber/gold (H ~ 35)
    r, g, b, a = img_active.split()
    rgb = Image.merge("RGB", (r, g, b))
    hsv = rgb.convert("HSV")
    h, s, v = hsv.split()

    h_data = list(h.getdata())
    # In HSV: Emerald Green is ~ 100-170, shift to Amber ~ 25-45
    new_h = []
    for val in h_data:
        if 85 <= val <= 180:
            new_h.append(28)  # Warm Amber Gold
        else:
            new_h.append(val)
    h.putdata(new_h)

    paused_rgb = Image.merge("HSV", (h, s, v)).convert("RGB")
    pr, pg, pb = paused_rgb.split()
    paused_rgba = Image.merge("RGBA", (pr, pg, pb, a))
    paused_rgba.save(paused_png_path)
    paused_rgba.save(paused_ico_path, format="ICO", sizes=sizes)
    print(f"Saved paused icon: {paused_ico_path}")

if __name__ == "__main__":
    make_icons()
