# -*- coding: utf-8 -*-
"""
Traduce al inglés los errores y alternativas de tips.json y deja el resultado cacheado
en tips_en.json (una entrada por slug). Solo traduce lo que falte o haya cambiado, así
que se puede relanzar sin gastar de más.

  python translate_tips.py            # traduce lo pendiente
  python translate_tips.py --force    # rehace todo
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
TIPS = os.path.join(HERE, "tips.json")
CACHE = os.path.join(HERE, "tips_en.json")
MODEL = "gpt-4o"

SYS = ("You translate gym-app microcopy from Spanish to English. Keep it short, direct and "
       "practical, same number of items and same order, and use standard English gym "
       "vocabulary (lower back, glutes, lats, hip hinge, cable machine, dumbbell, barbell...). "
       "Do not add or drop information.\n"
       "CRITICAL — each item in 'mistakes' names something the reader must NOT do, so write it "
       'as a gerund noun phrase ("Rounding your lower back as you lift", "Letting the cable '
       'rotate your torso"), NEVER as an imperative ("Round your lower back"), which would '
       "read as an instruction to do it.\n"
       "Items in 'alternatives' are exercise names or short suggestions: keep them as noun "
       'phrases ("Goblet squat.", "Leg press.").\n'
       'Return JSON: {"mistakes": [...], "alternatives": [...]}.')


def load_key():
    for line in open(os.path.join(HERE, ".env"), encoding="utf-8"):
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("Falta OPENAI_API_KEY")


def firma(t):
    return hashlib.sha1(json.dumps(t, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


def main():
    force = "--force" in sys.argv
    tips = json.load(open(TIPS, encoding="utf-8"))
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}

    pendientes = [s for s, t in tips.items()
                  if force or s not in cache or cache[s].get("_firma") != firma(t)]
    print(f"{len(tips)} slugs · a traducir: {len(pendientes)}")
    if not pendientes:
        return

    from openai import OpenAI
    client = OpenAI(api_key=load_key())

    for i, slug in enumerate(pendientes, 1):
        t = tips[slug]
        user = json.dumps({"mistakes": t["mistakes"], "alternatives": t["alternatives"]},
                          ensure_ascii=False)
        r = client.chat.completions.create(
            model=MODEL, temperature=0.2, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYS},
                      {"role": "user", "content": f'Exercise "{slug}". Translate:\n{user}'}])
        d = json.loads(r.choices[0].message.content)
        if len(d.get("mistakes", [])) != len(t["mistakes"]) or \
           len(d.get("alternatives", [])) != len(t["alternatives"]):
            print(f"  ojo: {slug} devolvió otro número de elementos")
        cache[slug] = {"mistakes": d.get("mistakes", []),
                       "alternatives": d.get("alternatives", []),
                       "_firma": firma(t)}
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  [{i}/{len(pendientes)}] {slug}", flush=True)

    print("Hecho.")


if __name__ == "__main__":
    main()
