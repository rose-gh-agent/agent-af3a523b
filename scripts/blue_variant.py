#!/usr/bin/env python3

from __future__ import annotations

import argparse
import colorsys
from pathlib import Path

from PIL import Image


TARGET_HUE = 0.60  # blue


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def blue_variant(image: Image.Image) -> Image.Image:
    src = image.convert("RGB")
    out = Image.new("RGB", src.size)
    src_px = src.load()
    out_px = out.load()

    for y in range(src.height):
        for x in range(src.width):
            r, g, b = src_px[x, y]
            rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
            h, l, s = colorsys.rgb_to_hls(rf, gf, bf)

            if l < 0.035:
                out_px[x, y] = (r, g, b)
                continue

            hue_distance = min(abs(h - TARGET_HUE), 1.0 - abs(h - TARGET_HUE))
            hue_influence = clamp(1.0 - (hue_distance / 0.35))
            sat_boost = 0.16 + 0.34 * hue_influence
            blue_sat = clamp(max(s, 0.18) + sat_boost * (1.0 - l * 0.65))
            blue_hue = (TARGET_HUE * (0.65 + 0.35 * hue_influence) + h * (0.35 - 0.35 * hue_influence)) % 1.0

            nr, ng, nb = colorsys.hls_to_rgb(blue_hue, l, blue_sat)

            # Preserve metallic highlights by blending some of the source back in.
            metallic_mix = clamp(0.28 + 0.34 * l - 0.18 * blue_sat)
            fr = int(round(clamp(nr * (1.0 - metallic_mix) + rf * metallic_mix) * 255.0))
            fg = int(round(clamp(ng * (1.0 - metallic_mix) + gf * metallic_mix) * 255.0))
            fb = int(round(clamp(nb * (1.0 - metallic_mix) + bf * metallic_mix) * 255.0))
            out_px[x, y] = (fr, fg, fb)

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a blue color variant of an image.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    image = Image.open(args.input)
    result = blue_variant(image)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)


if __name__ == "__main__":
    main()
