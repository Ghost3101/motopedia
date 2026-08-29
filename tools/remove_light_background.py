from collections import deque
from pathlib import Path
from PIL import Image, ImageFilter


def remove_background(source: str, target: str, dark: bool = False) -> None:
    image = Image.open(source).convert("RGBA")
    rgb = image.convert("RGB")
    width, height = image.size
    pixels = rgb.load()
    seen = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def qualifies(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        saturation = max(red, green, blue) - min(red, green, blue)
        brightness = (red + green + blue) / 3
        if dark:
            return saturation < 45 and brightness < 95
        return saturation < 38 and brightness > 170

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    mask = Image.new("L", image.size, 255)
    mask_pixels = mask.load()
    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if seen[index]:
            continue
        seen[index] = 1
        if not qualifies(x, y):
            continue
        mask_pixels[x, y] = 0
        if x: queue.append((x - 1, y))
        if x + 1 < width: queue.append((x + 1, y))
        if y: queue.append((x, y - 1))
        if y + 1 < height: queue.append((x, y + 1))

    mask = mask.filter(ImageFilter.GaussianBlur(1.0))
    image.putalpha(mask)
    box = image.getbbox()
    if box:
        image = image.crop(box)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    image.save(target, optimize=True)


remove_background("assets/bikes/surron-lbx-complete-source.png", "assets/bikes/surron-lbx.png", dark=True)
remove_background("assets/bikes/surron-ultra-x-source.jpg", "assets/bikes/surron-ultra-offroad.png")
