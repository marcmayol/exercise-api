# -*- coding: utf-8 -*-
"""
Empaqueta TODO el dataset (JSON + ilustraciones JPG + mapas SVG) en un único
`exercise-api-dataset.zip` en la raíz del repo, para descarga directa desde la landing.
Se ejecuta a mano (no en cada build) para no inflar el historial de git.

Uso:  python make_bundle.py
"""
import os, json, zipfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "exercise-api-dataset.zip")
DIRS = ["v1", "images", "muscle-maps"]

def main():
    count = json.load(open(os.path.join(ROOT, "v1", "exercises.json"), encoding="utf-8"))["count"]
    today = datetime.date.today().isoformat()
    readme = (
        "Exercise API - dataset completo\n"
        f"Generado: {today}\n"
        f"Ejercicios: {count}\n"
        "Web: https://marcmayol.com/exercise-api\n\n"
        "Contenido:\n"
        "  v1/           JSON: dataset.json (todo en 1 archivo), fichas por ejercicio,\n"
        "                indices por grupo / musculo / equipamiento, taxonomias.\n"
        "  images/       Ilustraciones -m.jpg (hombre) y -f.jpg (mujer) por ejercicio.\n"
        "  muscle-maps/  Mapa muscular SVG por ejercicio (principal naranja, secundario claro).\n\n"
        "Empieza por v1/dataset.json (todas las fichas) o v1/exercises.json (indice).\n\n"
        "Licencia: ilustraciones y datos propios, uso libre. Mapas musculares a partir de\n"
        "react-native-body-highlighter (MIT). Hecho por Marc Mayol desde Mallorca.\n"
    )

    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("README.txt", readme)
        for lic in ("LICENSE", "THIRD-PARTY-LICENSES.txt"):
            fp = os.path.join(ROOT, lic)
            if os.path.exists(fp): z.write(fp, lic); n += 1
        for d in DIRS:
            base = os.path.join(ROOT, d)
            for root, _, files in os.walk(base):
                for fn in sorted(files):
                    fp = os.path.join(root, fn)
                    arc = os.path.relpath(fp, ROOT).replace("\\", "/")
                    z.write(fp, arc); n += 1

    mb = os.path.getsize(OUT) / (1024 * 1024)
    print(f"OK · {n} archivos empaquetados · {mb:.1f} MB · {OUT}")

if __name__ == "__main__":
    main()
