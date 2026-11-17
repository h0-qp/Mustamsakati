"""Generate assets/icon.png with PIL: black rounded square,
centred yellow document shape with three black horizontal lines."""
import os

from PIL import Image, ImageDraw

SIZE = 512
YELLOW = (233, 198, 91, 255)
BLACK = (17, 17, 17, 255)

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# black rounded-square background
d.rounded_rectangle([16, 16, SIZE - 16, SIZE - 16], radius=96, fill=(10, 10, 13, 255))

# yellow document shape (centred)
doc_w, doc_h = 208, 272
x0 = (SIZE - doc_w) // 2
y0 = (SIZE - doc_h) // 2
d.rounded_rectangle([x0, y0, x0 + doc_w, y0 + doc_h], radius=34, fill=YELLOW)

# three black horizontal lines
line_w = 118
lx = (SIZE - line_w) // 2
for i, frac in enumerate((0.30, 0.50, 0.70)):
    ly = y0 + int(doc_h * frac)
    d.rounded_rectangle([lx, ly - 11, lx + line_w, ly + 11], radius=11, fill=BLACK)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print("wrote", out, img.size)
