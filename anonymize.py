#!/usr/bin/env python3
"""对教程截图中的个人隐私信息做脱敏（马赛克 / 背景色实心覆盖）。

对外发布前必须对邮箱、昵称、头像、余额、账单地址等敏感信息脱敏。
本脚本只处理 TARGETS 列出的图片；每次运行前请先把这些图从原始截图重新复制过来，保证幂等。
"""
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
TARGETS = ["new4-media-signout.png", "new5-appstore-switch.png"]

# 马赛克区域 (l, t, r, b)：适用于头像等图像
MOSAIC = {
    "new4-media-signout.png": [
        (385, 215, 560, 380),   # 头像
    ],
    "new5-appstore-switch.png": [
        (300, 210, 465, 370),   # 头像照片
    ],
}

# 实心覆盖区域：适用于文字，取区域左侧紧邻的背景色填充，彻底遮盖
SOLID = {
    "new4-media-signout.png": [
        (285, 430, 655, 512),   # 昵称「叫我彭于晏」
        (240, 502, 705, 568),   # QQ 邮箱整行
        (60, 1080, 620, 1160),  # 订阅行 Gmail 整行
        (60, 1696, 640, 1778),  # 媒体与购买项目行 Gmail 整行
    ],
    "new5-appstore-switch.png": [
        (292, 388, 478, 448),   # 英文名 xiao fei
        (220, 448, 565, 508),   # 邮箱行
    ],
}


def apply_mosaic(img, boxes):
    for (l, t, r, b) in boxes:
        crop = img.crop((l, t, r, b))
        cw, ch = crop.size
        small = crop.resize((max(2, cw // 24), max(2, ch // 24)), Image.BILINEAR)
        mosaic = small.resize((cw, ch), Image.NEAREST).filter(ImageFilter.GaussianBlur(radius=10))
        img.paste(mosaic, (l, t))


def apply_solid(img, boxes):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for (l, t, r, b) in boxes:
        l, t = max(0, l), max(0, t)
        r, b = min(w, r), min(h, b)
        # 采样区域左侧相邻像素作为背景色，使覆盖更自然
        sample_x = max(0, l - 12)
        sample = img.getpixel((sample_x, (t + b) // 2))
        draw.rectangle([l, t, r, b], fill=sample)


def process(name):
    path = ASSETS / name
    img = Image.open(path).convert("RGB")
    apply_mosaic(img, MOSAIC.get(name, []))
    apply_solid(img, SOLID.get(name, []))
    img.save(path, quality=92)
    print(f"[OK] {name} size={img.size} mosaic={len(MOSAIC.get(name, []))} solid={len(SOLID.get(name, []))}")


for n in TARGETS:
    process(n)
