#!/usr/bin/env python3

import argparse
import colorsys
from pathlib import Path

from PIL import Image


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def recolor_pixel(r: int, g: int, b: int) -> tuple[int, int, int]:
    max_channel = max(r, g, b)
    if max_channel <= 18:
        return r, g, b

    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(rf, gf, bf)

    # Preserve metallic highlights by keeping low-saturation bright areas close to gray,
    # while strongly recoloring visible non-black tones into a red range.
    target_hue = 0.0
    target_sat = clamp(max(s * 0.9, 0.24 + (1.0 - l) * 0.40))
    red_r, red_g, red_b = colorsys.hls_to_rgb(target_hue, l, target_sat)

    luminance = 0.2126 * rf + 0.7152 * gf + 0.0722 * bf
    gray_r = gray_g = gray_b = luminance

    blend = clamp(0.45 + s * 0.35 + (1.0 - l) * 0.20)
    out_r = gray_r * (1.0 - blend) + red_r * blend
    out_g = gray_g * (1.0 - blend) + red_g * blend
    out_b = gray_b * (1.0 - blend) + red_b * blend

    return (
        round(clamp(out_r) * 255),
        round(clamp(out_g) * 255),
        round(clamp(out_b) * 255),
    )


def recolor_image(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            pixels[x, y] = recolor_pixel(*pixels[x, y])

    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recolor artwork into a red variant.")
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    recolor_image(args.src, args.dst)


if __name__ == "__main__":
    main()
