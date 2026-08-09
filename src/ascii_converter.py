"""
ASCII portrait converter module.
Converts input photograph into detailed monospace ASCII art for dark and light terminal themes.
"""

import html
from pathlib import Path
from typing import Tuple, List

# ASCII character ramps sorted by visually perceived density
DARK_CHARS = "  ..:--==++**##%%@@"
LIGHT_CHARS = "  ..:--==++**##%%@@"


def crop_upper_body(img):
    """
    Crops the image around the upper body / head & torso area.
    Focuses on the person and removes surrounding margins.
    """
    from PIL import Image
    width, height = img.size
    left = int(width * 0.1)
    top = int(height * 0.05)
    right = int(width * 0.9)
    bottom = int(height * 0.85)
    return img.crop((left, top, right, bottom))


def suppress_background(img, dark_theme: bool = True):
    """
    Suppresses noisy background (like snowy trees) by focusing on central portrait elements
    and applying a soft center radial mask.
    """
    from PIL import Image
    img = img.convert("RGB")
    width, height = img.size
    
    mask = Image.new("L", (width, height), 0)
    cx, cy = width / 2.0, height * 0.45

    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            dx = (x - cx) / (width * 0.48)
            dy = (y - cy) / (height * 0.52)
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 0.6:
                val = 255
            elif dist < 1.0:
                val = int(255 * (1.0 - (dist - 0.6) / 0.4))
            else:
                val = 0
            mask_pixels[x, y] = val

    # For dark theme, background is black; for light theme, background is white
    bg_color = (0, 0, 0) if dark_theme else (255, 255, 255)
    bg = Image.new("RGB", (width, height), bg_color)
    result = Image.composite(img, bg, mask)
    return result


def image_to_ascii(
    image_path: Path,
    target_width: int = 40,
    target_height: int = 25,
    font_aspect_ratio: float = 0.5,
    dark_theme: bool = True
) -> List[str]:
    """
    Converts image to detailed ASCII text lines.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Profile photograph not found at {image_path}")

    from PIL import Image, ImageEnhance, ImageOps
    with Image.open(image_path) as orig_img:
        cropped = crop_upper_body(orig_img)
        suppressed = suppress_background(cropped, dark_theme=dark_theme)
        
        gray = suppressed.convert("L")

        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.4)

        sharpener = ImageEnhance.Sharpness(gray)
        gray = sharpener.enhance(1.3)

        gray = ImageOps.autocontrast(gray, cutoff=2)

        scaled_height = int(target_height)
        scaled_width = int(target_width)
        resized = gray.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

        pixels = resized.load()
        lines: List[str] = []
        num_chars = len(DARK_CHARS)

        for y in range(scaled_height):
            line_chars: List[str] = []
            for x in range(scaled_width):
                lum = pixels[x, y]
                
                if dark_theme:
                    # In dark theme, dark pixels (lum < 25) are blank space, bright pixels get chars
                    if lum < 25:
                        char = " "
                    else:
                        idx = int((lum / 255.0) * (num_chars - 1))
                        char = DARK_CHARS[min(idx, num_chars - 1)]
                else:
                    # In light theme, bright background pixels (lum > 230) are blank space, dark pixels get chars
                    if lum > 230:
                        char = " "
                    else:
                        inv_lum = 255 - lum
                        idx = int((inv_lum / 255.0) * (num_chars - 1))
                        char = LIGHT_CHARS[min(idx, num_chars - 1)]

                line_chars.append(char)

            raw_line = "".join(line_chars)
            escaped_line = html.escape(raw_line)
            lines.append(escaped_line)

        return lines


def generate_ascii_assets(
    image_path: Path,
    dark_out_path: Path,
    light_out_path: Path,
    target_width: int = 40,
    target_height: int = 25
) -> Tuple[List[str], List[str]]:
    """
    Generates both dark and light theme ASCII text files.
    """
    dark_lines = image_to_ascii(
        image_path=image_path,
        target_width=target_width,
        target_height=target_height,
        dark_theme=True
    )
    
    light_lines = image_to_ascii(
        image_path=image_path,
        target_width=target_width,
        target_height=target_height,
        dark_theme=False
    )

    dark_out_path.parent.mkdir(parents=True, exist_ok=True)
    light_out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dark_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(dark_lines))

    with open(light_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(light_lines))

    return dark_lines, light_lines
