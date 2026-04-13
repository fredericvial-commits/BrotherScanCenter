import os
from PIL import Image, ImageDraw, ImageFont

def creer_icone():
    os.makedirs("assets", exist_ok=True)
    tailles = [16, 32, 48, 64, 128, 256]
    images  = []
    for taille in tailles:
        img  = Image.new("RGBA", (taille, taille), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        marge = taille // 8
        draw.rounded_rectangle(
            [marge, marge, taille - marge, taille - marge],
            radius=taille // 5, fill=(0, 48, 135, 255))
        px = taille // 5
        py = taille // 3
        pw = taille - 2 * px
        ph = taille // 3
        draw.rounded_rectangle(
            [px, py, px + pw, py + ph],
            radius=taille // 12, fill=(255, 255, 255, 230))
        sx = px + pw // 4
        sw = pw // 2
        sh = taille // 10
        draw.rounded_rectangle(
            [sx, py + ph, sx + sw, py + ph + sh],
            radius=2, fill=(200, 220, 255, 255))
        led_r = max(2, taille // 16)
        draw.ellipse(
            [px + pw - led_r * 3, py + taille // 20,
             px + pw - led_r,     py + taille // 20 + led_r * 2],
            fill=(0, 200, 80, 255))
        if taille >= 48:
            try:
                try:
                    font = ImageFont.truetype("arial.ttf", taille // 4)
                except:
                    font = ImageFont.load_default()
                draw.text((px + pw // 2, py + ph // 2),
                    "B", fill=(0, 48, 135, 255),
                    font=font, anchor="mm")
            except:
                pass
        images.append(img)
    images[0].save("assets/icon.ico", format="ICO",
        sizes=[(t, t) for t in tailles],
        append_images=images[1:])
    images[-1].save("assets/icon_preview.png")
    print("icone creee")

if __name__ == "__main__":
    creer_icone()
