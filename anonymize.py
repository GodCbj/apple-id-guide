#!/usr/bin/env python3
"""对教程截图中的个人隐私信息做马赛克+高斯模糊脱敏。"""
from PIL import Image, ImageFilter
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"

# 每张图中需要脱敏的区域 (left, top, right, bottom)，坐标为原图像素
REGIONS = {
    # Pockyt Shop 顶部的登录邮箱
    "step5-pockyt-shop.png": [
        (140, 300, 640, 415),
    ],
    # 账户设置页：邮箱、账单寄送地址、余额
    "step6-account-settings.png": [
        (355, 365, 860, 428),   # Apple 账户邮箱
        (580, 680, 830, 745),   # 账单寄送地址 213 Kline St
        (670, 1140, 850, 1195), # 余额 $200.01
    ],
    # 兑换教程左图中的余额 $20.02
    "step7-redeem.png": [
        (335, 402, 478, 455),
    ],
}


def anonymize(path: Path, boxes):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    for (l, t, r, b) in boxes:
        # 夹取到图像范围内
        l, t = max(0, l), max(0, t)
        r, b = min(w, r), min(h, b)
        if r <= l or b <= t:
            continue
        crop = img.crop((l, t, r, b))
        cw, ch = crop.size
        # 先缩到极小再放大 → 马赛克
        small = crop.resize((max(2, cw // 24), max(2, ch // 24)), Image.BILINEAR)
        mosaic = small.resize((cw, ch), Image.NEAREST)
        # 再叠加高斯模糊，确保完全不可辨认
        mosaic = mosaic.filter(ImageFilter.GaussianBlur(radius=8))
        img.paste(mosaic, (l, t))
    img.save(path, quality=92)
    print(f"[OK] {path.name}  size={w}x{h}  regions={len(boxes)}")


for name, boxes in REGIONS.items():
    anonymize(ASSETS / name, boxes)
