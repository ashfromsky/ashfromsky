from pathlib import Path

raw_file = Path("scratch/raw_ascii.txt")
raw_text = raw_file.read_text(encoding="utf-8")

lines = [l for l in raw_text.splitlines() if l.strip()]
print(f"Total lines: {len(lines)}")
print(f"Max width: {max(len(l) for l in lines)}")

step_y = len(lines) / 25.0
max_w = max(len(l) for l in lines)
step_x = max_w / 40.0

downscaled = []
for i in range(25):
    y_idx = int(i * step_y)
    line = lines[min(y_idx, len(lines)-1)]
    row_chars = []
    for j in range(40):
        x_idx = int(j * step_x)
        char = line[min(x_idx, len(line)-1)] if x_idx < len(line) else " "
        row_chars.append(char)
    downscaled.append("".join(row_chars))

# DO NOT html.escape here because ElementTree ET.tostring handles XML escaping safely
Path("assets/ascii_dark.txt").write_text("\n".join(downscaled), encoding="utf-8")
Path("assets/ascii_light.txt").write_text("\n".join(downscaled), encoding="utf-8")

print("Successfully generated downscaled ASCII art without double-escaping!")
