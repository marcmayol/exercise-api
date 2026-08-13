# -*- coding: utf-8 -*-
"""
Fusiona un fichero de instrucciones escritas a mano en instructions_cache.json,
para que build_api.py las use tal cual en vez de pedirlas a gpt-4o.

  python merge_instructions.py instructions_bmf.json [--force]

Sin --force respeta lo que ya haya en la caché.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "instructions_cache.json")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if not args:
        raise SystemExit("Uso: python merge_instructions.py <fichero.json> [--force]")
    src = args[0] if os.path.isabs(args[0]) else os.path.join(HERE, args[0])

    nuevas = json.load(open(src, encoding="utf-8"))
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}

    add = upd = skip = 0
    for slug, ins in nuevas.items():
        if slug.startswith("_"):
            continue
        if slug in cache and not force:
            skip += 1; continue
        if slug in cache:
            upd += 1
        else:
            add += 1
        cache[slug] = {"es": ins["es"], "en": ins["en"]}

    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"OK · {add} nuevas · {upd} sobrescritas · {skip} respetadas · {len(cache)} en la cache")

if __name__ == "__main__":
    main()
