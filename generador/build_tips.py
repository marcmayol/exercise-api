# -*- coding: utf-8 -*-
"""
Fusiona las fuentes de errores/alternativas en un único tips.json (ES) y avisa de lo que falte:

  tips_desde_app.json   material previo del autor, extraído de la app Building My Future
  tips_manual*.json     redactado para el catálogo

  python build_tips.py            # fusiona y comprueba cobertura
"""
import json, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SALIDA = os.path.join(HERE, "tips.json")


def cargar(path):
    return {k: v for k, v in json.load(open(path, encoding="utf-8")).items()
            if not k.startswith("_")}


def main():
    tips = {}
    # el material del autor manda sobre lo redactado después
    for f in sorted(glob.glob(os.path.join(HERE, "tips_manual*.json"))):
        tips.update(cargar(f))
    desde_app = os.path.join(HERE, "tips_desde_app.json")
    if os.path.exists(desde_app):
        tips.update(cargar(desde_app))

    for slug, t in tips.items():
        if not t.get("mistakes") or not t.get("alternatives"):
            raise SystemExit(f"{slug}: le falta mistakes o alternatives")

    seed = json.load(open(os.path.join(ROOT, "exercises_seed.json"), encoding="utf-8"))
    slugs = [e["slug"] for e in seed]
    faltan = [s for s in slugs if s not in tips]
    sobran = [s for s in tips if s not in slugs]

    # solo se publica lo que existe en el catálogo
    json.dump({k: tips[k] for k in sorted(tips) if k in set(slugs)},
              open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"OK · {len(tips)} slugs con errores/alternativas · catálogo: {len(slugs)}")
    if faltan:
        print(f"FALTAN {len(faltan)}: {', '.join(faltan)}")
    if sobran:
        print(f"sobran (no están en el catálogo): {', '.join(sobran)}")


if __name__ == "__main__":
    main()
