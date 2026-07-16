# -*- coding: utf-8 -*-
"""
Genera la API estática de ejercicios (JSON + imágenes + mapas musculares + landing)
para publicar en GitHub Pages. Lee exercises_seed.json y:
  - redacta instrucciones ORIGINALES en ES y EN con OpenAI (cacheadas),
  - dibuja el mapa muscular SVG (principal/secundario) por ejercicio,
  - copia las ilustraciones (masculina/femenina),
  - emite /v1/*.json y una landing.
"""
import os, re, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                                   # exercise-api
GEN_IMGS = r"C:/Users/marcm/Desktop/CatalogoEjercicios/generados"
BASE = "https://marcmayol.com/exercise-api"              # URL pública (Pages)

MUSCLES = {
  "chest":{"es":"Pectoral","en":"Chest"}, "deltoids":{"es":"Hombros","en":"Shoulders"},
  "triceps":{"es":"Tríceps","en":"Triceps"}, "biceps":{"es":"Bíceps","en":"Biceps"},
  "forearm":{"es":"Antebrazo","en":"Forearm"}, "abs":{"es":"Abdomen","en":"Abs"},
  "obliques":{"es":"Oblicuos","en":"Obliques"}, "upper-back":{"es":"Dorsal","en":"Upper back"},
  "trapezius":{"es":"Trapecio","en":"Trapezius"}, "lower-back":{"es":"Lumbar","en":"Lower back"},
  "gluteal":{"es":"Glúteo","en":"Glutes"}, "quadriceps":{"es":"Cuádriceps","en":"Quadriceps"},
  "hamstring":{"es":"Femoral","en":"Hamstrings"}, "calves":{"es":"Gemelos","en":"Calves"},
  "adductors":{"es":"Aductores","en":"Adductors"},
}

EQUIP = {  # tipos de equipamiento (ES/EN)
  "machine":{"es":"Máquina","en":"Machine"}, "cable":{"es":"Polea","en":"Cable"},
  "barbell":{"es":"Barra","en":"Barbell"}, "dumbbell":{"es":"Mancuerna","en":"Dumbbell"},
  "bodyweight":{"es":"Peso corporal","en":"Bodyweight"}, "cardio":{"es":"Cardio","en":"Cardio"},
}
EQUIPMENT = {  # slug -> tipo de equipamiento
  "seated-chest-press":"machine","incline-chest-press-machine":"machine","butterflies":"machine",
  "barbell-bench-press":"barbell","chest-pulldown":"machine","close-grip-chest-pulldown":"machine",
  "neutral-grip-pulldown":"machine","seated-row-machine":"machine","seated-cable-back-rows":"cable",
  "seated-dumbbell-overhead-shoulder-press":"dumbbell","machine-shoulder-press":"machine",
  "dumbbell-lateral-raises":"dumbbell","face-pull":"cable","upright-row":"barbell",
  "alternating-dumbbell-biceps-curl":"dumbbell","dumbbell-hammer-biceps-curl":"dumbbell",
  "triceps-pushdown":"cable","dips-machine":"machine","leg-press":"machine",
  "seated-leg-curl":"machine","lying-leg-curls":"machine","seated-leg-extensions":"machine",
  "barbell-hip-thrust":"barbell","box-squat":"bodyweight","goblet-squats":"dumbbell",
  "barbell-squat":"barbell","bulgarian-split-squat":"dumbbell","seated-calf-raises":"machine",
  "plank":"bodyweight","side-plank":"bodyweight","dead-bug":"bodyweight",
}

# ---------------------------------------------------------------- mapas musculares (SVG)
def parse_body(fn):
    txt = open(os.path.join(HERE, fn), encoding="utf-8").read()
    out = {}
    for seg in re.split(r'slug:\s*"', txt)[1:]:
        slug = seg[:seg.index('"')]
        out[slug] = re.findall(r'"([Mm][^"]*)"', seg)
    return out
FRONT = parse_body("bodyFront.ts"); BACK = parse_body("bodyBack.ts")
FRONT_F = parse_body("bodyFemaleFront.ts"); BACK_F = parse_body("bodyFemaleBack.ts")

def muscle_svg(primary, secondary, front=None, back=None, vb="0 0 1448 1448"):
    front = FRONT if front is None else front
    back  = BACK  if back  is None else back
    BODY="#C9C2BD"; PRI="#FF6A3D"; SEC="#FFC49A"; SEP="#ffffff"
    def paths(data):
        s=[]
        for slug,pl in data.items():
            fill = PRI if slug in primary else (SEC if slug in secondary else BODY)
            for p in pl: s.append(f'<path d="{p}" fill="{fill}"/>')
        for slug,pl in data.items():
            if slug in ("head","hair","neck"): continue
            for p in pl: s.append(f'<path d="{p}" fill="none" stroke="{SEP}" stroke-width="2"/>')
        return "".join(s)
    w,h = vb.split()[2], vb.split()[3]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">'
            f'{paths(front)}{paths(back)}</svg>')

# ---------------------------------------------------------------- instrucciones (OpenAI, caché)
def load_key():
    for line in open(os.path.join(HERE,".env"),encoding="utf-8"):
        if line.startswith("OPENAI_API_KEY="): return line.split("=",1)[1].strip()
CACHE = os.path.join(HERE,"instructions_cache.json")

def get_instructions(client, ex):
    cache = json.load(open(CACHE,encoding="utf-8")) if os.path.exists(CACHE) else {}
    if ex["slug"] in cache: return cache[ex["slug"]]
    musc = ", ".join(MUSCLES[m]["en"] for m in ex["primary"])
    sysm = ("You write original, concise gym exercise instructions. Given an exercise, output "
            "3-4 short numbered steps, safe and correct. Original wording (do not copy any source). "
            'Return JSON: {"es": ["paso 1", ...], "en": ["step 1", ...]} with the SAME steps in both languages.')
    r = client.chat.completions.create(model="gpt-4o", temperature=0.3,
        response_format={"type":"json_object"},
        messages=[{"role":"system","content":sysm},
                  {"role":"user","content":f'Exercise: "{ex["en"]}" (primary muscles: {musc}). Write the instructions.'}])
    d = json.loads(r.choices[0].message.content)
    res = {"es": d.get("es",[]), "en": d.get("en",[])}
    cache[ex["slug"]] = res
    json.dump(cache, open(CACHE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("  instrucciones:", ex["slug"]); return res

# ---------------------------------------------------------------- build
def main():
    from openai import OpenAI
    from PIL import Image, ImageChops
    client = OpenAI(api_key=load_key())
    seed = json.load(open(os.path.join(ROOT,"exercises_seed.json"),encoding="utf-8"))

    for d in ("v1","v1/exercises","v1/by-muscle","v1/by-group","v1/by-equipment","images","muscle-maps"):
        os.makedirs(os.path.join(ROOT,d), exist_ok=True)

    def copy_img(slug, gender, suffix):
        src = os.path.join(GEN_IMGS, f"{slug}-{gender}.png")
        if not os.path.exists(src): return None
        im = Image.open(src).convert("RGB")
        bb = ImageChops.difference(im, Image.new("RGB",im.size,(255,255,255))).getbbox()
        if bb:
            p=14;l,t,r,b=bb; im=im.crop((max(0,l-p),max(0,t-p),min(im.size[0],r+p),min(im.size[1],b+p)))
        if im.width>1024: im=im.resize((1024,round(im.height*1024/im.width)))
        rel = f"images/{slug}-{suffix}.jpg"; im.save(os.path.join(ROOT,rel),quality=85)
        return f"{BASE}/{rel}"

    index=[]; full_all=[]; by_muscle={}; by_group={}; by_equipment={}
    def dump(path, obj): json.dump(obj, open(os.path.join(ROOT,path),"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    for ex in seed:
        slug=ex["slug"]
        eq = ex.get("equipment") or EQUIPMENT.get(slug,"machine"); eqobj={"id":eq,**EQUIP[eq]}
        instr = get_instructions(client, ex)
        img_m = copy_img(slug,"male","m"); img_f = copy_img(slug,"female","f")
        prim, sec = set(ex["primary"]), set(ex["secondary"])
        svg_rel = f"muscle-maps/{slug}.svg"
        open(os.path.join(ROOT,svg_rel),"w",encoding="utf-8").write(muscle_svg(prim,sec))
        svg_f_rel = f"muscle-maps/{slug}-f.svg"
        open(os.path.join(ROOT,svg_f_rel),"w",encoding="utf-8").write(muscle_svg(prim,sec,FRONT_F,BACK_F,vb="0 0 1460 1448"))

        def mlist(keys): return [{"id":k,"es":MUSCLES[k]["es"],"en":MUSCLES[k]["en"]} for k in keys]
        full = {
          "slug":slug,
          "name":{"es":ex["es"],"en":ex["en"]},
          "group":{"id":ex["group_en"].lower(),"es":ex["group_es"],"en":ex["group_en"]},
          "equipment":eqobj,
          "primaryMuscles":mlist(ex["primary"]),
          "secondaryMuscles":mlist(ex["secondary"]),
          "instructions":instr,
          "images":{"male":img_m,"female":img_f},
          "muscleMap":f"{BASE}/{svg_rel}",
          "muscleMaps":{"male":f"{BASE}/{svg_rel}","female":f"{BASE}/{svg_f_rel}"},
        }
        dump(f"v1/exercises/{slug}.json", full)
        full_all.append(full)
        # resumen reutilizable (índice, por grupo, por músculo)
        summ = {"slug":slug,"name":full["name"],"group":full["group"],"equipment":eqobj,
                "image":full["images"],"url":f"{BASE}/v1/exercises/{slug}.json"}
        index.append({**summ,"primaryMuscles":[m["id"] for m in full["primaryMuscles"]]})
        g = ex["group_en"].lower()
        by_group.setdefault(g,{"group":full["group"],"exercises":[]})["exercises"].append(summ)
        by_equipment.setdefault(eq,{"equipment":eqobj,"exercises":[]})["exercises"].append(summ)
        for m in dict.fromkeys(ex["primary"]+ex["secondary"]):
            by_muscle.setdefault(m,[]).append(summ)

    dump("v1/exercises.json", {"count":len(index),"exercises":index})
    dump("v1/muscles.json", [{"id":k,**v} for k,v in MUSCLES.items()])
    dump("v1/groups.json", [{"id":g,"es":d["group"]["es"],"en":d["group"]["en"],
                             "count":len(d["exercises"]),"url":f"{BASE}/v1/by-group/{g}.json"}
                            for g,d in by_group.items()])
    for g,d in by_group.items():
        dump(f"v1/by-group/{g}.json", {"group":d["group"],"count":len(d["exercises"]),"exercises":d["exercises"]})
    for m,arr in by_muscle.items():
        dump(f"v1/by-muscle/{m}.json",
             {"muscle":{"id":m,**MUSCLES[m]},"count":len(arr),"exercises":arr})
    dump("v1/equipment.json", [{"id":e,"es":EQUIP[e]["es"],"en":EQUIP[e]["en"],
                                "count":len(d["exercises"]),"url":f"{BASE}/v1/by-equipment/{e}.json"}
                               for e,d in by_equipment.items()])
    for e,d in by_equipment.items():
        dump(f"v1/by-equipment/{e}.json", {"equipment":d["equipment"],"count":len(d["exercises"]),"exercises":d["exercises"]})

    # dataset completo en un solo archivo (todas las fichas + taxonomías) para descarga directa
    import datetime
    dump("v1/dataset.json", {
        "name":"Exercise API dataset",
        "base":BASE,
        "generated": datetime.date.today().isoformat(),
        "count": len(full_all),
        "license":"Ilustraciones y datos propios · mapas musculares a partir de react-native-body-highlighter (MIT)",
        "groups":     [{"id":g,"es":d["group"]["es"],"en":d["group"]["en"],"count":len(d["exercises"])} for g,d in by_group.items()],
        "muscles":    [{"id":k,**v} for k,v in MUSCLES.items()],
        "equipment":  [{"id":e,"es":EQUIP[e]["es"],"en":EQUIP[e]["en"],"count":len(d["exercises"])} for e,d in by_equipment.items()],
        "exercises":  full_all,
    })
    print(f"\nOK · {len(index)} ejercicios · {len(by_group)} grupos · {len(by_equipment)} equipamientos · en {ROOT}")

if __name__=="__main__":
    main()
