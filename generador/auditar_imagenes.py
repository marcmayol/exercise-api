# -*- coding: utf-8 -*-
"""
Repasa las ilustraciones publicadas y saca las que se salen del estilo de la casa,
midiendo lo que sí se puede medir:

  fondo   tinte del marco exterior (el crema/amarillo de los lotes viejos)
  altura  cuánto del alto ocupa la figura (las "enanas" ocupan poco)
  tinta   proporción de píxeles no blancos (las "redondas"/gordas manchan más)

No detecta caras ni proporciones raras: eso hay que mirarlo. El script ordena por
sospecha para no tener que revisar 302 a ojo.

  python auditar_imagenes.py            # ranking
  python auditar_imagenes.py --csv      # además escribe auditoria.csv
"""
import os, sys, glob, csv
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMGS = os.path.join(ROOT, "images")


def medir(path):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    px = im.load()

    # --- fondo: marco exterior de 6 px, solo píxeles claros ---
    marco, m = [], 6
    for x in range(0, W, 3):
        for y in list(range(m)) + list(range(H - m, H)):
            marco.append(px[x, y])
    for y in range(0, H, 3):
        for x in list(range(m)) + list(range(W - m, W)):
            marco.append(px[x, y])
    claros = [c for c in marco if min(c) > 200]
    if claros:
        r = sum(c[0] for c in claros) / len(claros)
        g = sum(c[1] for c in claros) / len(claros)
        b = sum(c[2] for c in claros) / len(claros)
        # amarillo/crema = el azul se queda por detrás del rojo
        tinte = round(r - b, 1)
        brillo = round((r + g + b) / 3, 1)
    else:
        tinte, brillo = 0.0, 255.0

    # --- silueta ---
    minx, miny, maxx, maxy, tinta = W, H, 0, 0, 0
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if min(px[x, y]) < 235:
                tinta += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    alto = round((maxy - miny) / H, 3) if maxy > miny else 0.0
    ancho = round((maxx - minx) / W, 3) if maxx > minx else 0.0
    densidad = round(tinta / ((W // 2) * (H // 2)), 3)
    return dict(tinte=tinte, brillo=brillo, alto=alto, ancho=ancho, densidad=densidad)


def main():
    filas = []
    for f in sorted(glob.glob(os.path.join(IMGS, "*.jpg"))):
        d = medir(f)
        # sospecha: fondo con tinte + figura baja + poca o demasiada tinta
        s = 0.0
        s += max(0.0, d["tinte"]) * 3          # crema/amarillo
        s += max(0.0, 255 - d["brillo"]) * 1.5  # fondo apagado
        s += max(0.0, 0.42 - d["alto"]) * 60    # figura pequeña
        d["archivo"] = os.path.basename(f)
        d["sospecha"] = round(s, 1)
        filas.append(d)

    filas.sort(key=lambda d: -d["sospecha"])
    print(f"{'archivo':44} {'sosp':>5} {'tinte':>6} {'brillo':>7} {'alto':>6} {'dens':>6}")
    for d in filas[:45]:
        print(f"{d['archivo']:44} {d['sospecha']:5} {d['tinte']:6} {d['brillo']:7} "
              f"{d['alto']:6} {d['densidad']:6}")

    print(f"\ncon tinte de fondo (>1.5): {sum(1 for d in filas if d['tinte'] > 1.5)}")
    print(f"figura baja (<0.42 del alto): {sum(1 for d in filas if d['alto'] < 0.42)}")

    if "--csv" in sys.argv:
        with open(os.path.join(HERE, "auditoria.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["archivo", "sospecha", "tinte", "brillo",
                                               "alto", "ancho", "densidad"])
            w.writeheader()
            w.writerows(filas)
        print("\n-> generador/auditoria.csv")


if __name__ == "__main__":
    main()
