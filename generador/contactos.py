# -*- coding: utf-8 -*-
"""
Monta hojas de contactos de las ilustraciones publicadas, etiquetadas con su slug,
para poder repasarlas todas de un vistazo y anotar cuáles se salen del estilo.

  python contactos.py            # todas, en hojas de 4x3
  python contactos.py -m         # solo las masculinas
  python contactos.py -f         # solo las femeninas

Salen en generador/contactos/hoja-NN.jpg (no se suben: están en .gitignore).
"""
import os, sys, glob
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMGS = os.path.join(ROOT, "images")
OUT = os.path.join(HERE, "contactos")

COLS, FILAS = 4, 3
CELDA_W, CELDA_H = 460, 320
ETIQUETA = 26


def main():
    solo = None
    if "-m" in sys.argv: solo = "-m.jpg"
    if "-f" in sys.argv: solo = "-f.jpg"

    files = sorted(f for f in glob.glob(os.path.join(IMGS, "*.jpg"))
                   if solo is None or f.endswith(solo))
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, "*.jpg")):
        os.remove(f)

    por_hoja = COLS * FILAS
    hojas = (len(files) + por_hoja - 1) // por_hoja
    for h in range(hojas):
        lote = files[h * por_hoja:(h + 1) * por_hoja]
        hoja = Image.new("RGB", (COLS * CELDA_W, FILAS * (CELDA_H + ETIQUETA)), "white")
        d = ImageDraw.Draw(hoja)
        for i, f in enumerate(lote):
            im = Image.open(f).convert("RGB")
            im.thumbnail((CELDA_W - 8, CELDA_H - 8))
            cx = (i % COLS) * CELDA_W
            cy = (i // COLS) * (CELDA_H + ETIQUETA)
            hoja.paste(im, (cx + (CELDA_W - im.width) // 2,
                            cy + (CELDA_H - im.height) // 2))
            d.rectangle([cx, cy, cx + CELDA_W - 1, cy + CELDA_H - 1], outline=(215, 215, 215))
            d.text((cx + 8, cy + CELDA_H + 6), os.path.basename(f)[:-4], fill=(0, 0, 0))
        hoja.save(os.path.join(OUT, f"hoja-{h+1:02d}.jpg"), quality=88)
        print(f"hoja-{h+1:02d}.jpg · {len(lote)} ilustraciones")

    print(f"\n{len(files)} ilustraciones en {hojas} hojas -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
