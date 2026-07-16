# -*- coding: utf-8 -*-
"""
Convierte la Exercise API en un DATASET para IA, listo para Hugging Face.

Genera en ./build/:
  images/<slug>-<m|f>.jpg     Copia de las 208 ilustraciones (imagefolder)
  metadata.jsonl              1 fila por IMAGEN (208): file_name + etiquetas + caption
                              -> dataset de visión (clasificación) y multimodal (captioning/VQA)
  instructions.jsonl          Pares instrucción->respuesta bilingües (~fine-tuning LLM)
  exercises.jsonl / .csv      1 fila por ejercicio (104): tabla plana
  README.md                   Dataset card (con front-matter YAML de Hugging Face)

Uso:  python make_dataset.py
"""
import os, json, csv, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # exercise-api
OUT  = os.path.join(HERE, "build")
IMG_OUT = os.path.join(OUT, "images")

def load():
    return json.load(open(os.path.join(ROOT, "v1", "dataset.json"), encoding="utf-8"))

def mnames(ex, key, lang):
    return [m[lang] for m in ex[key]]

def main():
    d = load()
    exs = d["exercises"]
    os.makedirs(IMG_OUT, exist_ok=True)

    meta_rows, instr_rows, flat_rows = [], [], []

    for ex in exs:
        slug = ex["slug"]
        g_es, g_en = ex["group"]["es"], ex["group"]["en"]
        eq_es, eq_en = ex["equipment"]["es"], ex["equipment"]["en"]
        pri_ids = [m["id"] for m in ex["primaryMuscles"]]
        sec_ids = [m["id"] for m in ex["secondaryMuscles"]]
        pri_es, pri_en = mnames(ex,"primaryMuscles","es"), mnames(ex,"primaryMuscles","en")
        sec_es, sec_en = mnames(ex,"secondaryMuscles","es"), mnames(ex,"secondaryMuscles","en")
        ins_es, ins_en = ex["instructions"]["es"], ex["instructions"]["en"]
        name_es, name_en = ex["name"]["es"], ex["name"]["en"]

        # ---- filas por imagen (visión / multimodal) ----
        for gender, suf in (("male","m"), ("female","f")):
            src = os.path.join(ROOT, "images", f"{slug}-{suf}.jpg")
            if not os.path.exists(src): continue
            dst_rel = f"images/{slug}-{suf}.jpg"
            shutil.copyfile(src, os.path.join(OUT, dst_rel))
            caption_en = (f"{name_en}, a {g_en.lower()} exercise using {eq_en.lower()}. "
                          f"Primary muscles: {', '.join(pri_en) or 'n/a'}.")
            caption_es = (f"{name_es}, un ejercicio de {g_es.lower()} con {eq_es.lower()}. "
                          f"Músculos principales: {', '.join(pri_es) or 'n/a'}.")
            meta_rows.append({
                "file_name": dst_rel, "slug": slug, "gender": gender,
                "name_es": name_es, "name_en": name_en,
                "group": ex["group"]["id"], "group_es": g_es, "group_en": g_en,
                "equipment": ex["equipment"]["id"], "equipment_es": eq_es, "equipment_en": eq_en,
                "primary_muscles": pri_ids, "secondary_muscles": sec_ids,
                "primary_muscles_en": pri_en, "primary_muscles_es": pri_es,
                "instructions_en": ins_en, "instructions_es": ins_es,
                "caption_en": caption_en, "caption_es": caption_es,
                "muscle_map": ex.get("muscleMaps", {}).get(gender, ""),
            })

        # ---- tabla plana (1 por ejercicio) ----
        flat_rows.append({
            "slug": slug, "name_es": name_es, "name_en": name_en,
            "group_id": ex["group"]["id"], "group_es": g_es, "group_en": g_en,
            "equipment_id": ex["equipment"]["id"], "equipment_es": eq_es, "equipment_en": eq_en,
            "primary_muscles": "|".join(pri_ids), "secondary_muscles": "|".join(sec_ids),
            "instructions_es": " ".join(ins_es), "instructions_en": " ".join(ins_en),
            "image_male": ex["images"]["male"], "image_female": ex["images"]["female"],
            "muscle_map_male": ex.get("muscleMaps",{}).get("male",""),
            "muscle_map_female": ex.get("muscleMaps",{}).get("female",""),
        })

        # ---- instrucciones bilingües (fine-tuning) ----
        def add(instr, out): instr_rows.append({"instruction": instr, "output": out})
        add(f"¿Cómo se hace el ejercicio '{name_es}'?", " ".join(ins_es))
        add(f"How do you perform the '{name_en}' exercise?", " ".join(ins_en))
        add(f"¿Qué músculos trabaja '{name_es}'?",
            f"Principales: {', '.join(pri_es) or 'ninguno'}. Secundarios: {', '.join(sec_es) or 'ninguno'}.")
        add(f"Which muscles does '{name_en}' work?",
            f"Primary: {', '.join(pri_en) or 'none'}. Secondary: {', '.join(sec_en) or 'none'}.")
        add(f"¿Qué equipamiento necesito para '{name_es}'?", eq_es)
        add(f"What equipment do I need for '{name_en}'?", eq_en)
        add(f"¿A qué grupo muscular pertenece '{name_es}'?", g_es)
        add(f"What muscle group does '{name_en}' belong to?", g_en)

    # ---- escribir salidas ----
    def wjsonl(path, rows):
        with open(os.path.join(OUT, path), "w", encoding="utf-8") as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    wjsonl("metadata.jsonl", meta_rows)
    wjsonl("instructions.jsonl", instr_rows)
    wjsonl("exercises.jsonl", flat_rows)
    with open(os.path.join(OUT, "exercises.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys())); w.writeheader(); w.writerows(flat_rows)

    # ---- dataset card ----
    groups = {g["en"]: g["count"] for g in d["groups"]}
    card = f"""---
license: other
license_name: exercise-api-license
language:
  - es
  - en
task_categories:
  - image-classification
  - image-to-text
  - text-generation
tags:
  - fitness
  - gym
  - exercise
  - multimodal
  - bilingual
size_categories:
  - n<1K
configs:
  - config_name: images
    data_files: metadata.jsonl
  - config_name: instructions
    data_files: instructions.jsonl
  - config_name: exercises
    data_files: exercises.jsonl
---

# Exercise API — Dataset

Dataset de **{len(exs)} ejercicios** de gimnasio (bilingüe ES/EN) derivado de la
[Exercise API](https://marcmayol.com/exercise-api). Cada ejercicio incluye grupo muscular,
equipamiento, músculos principal/secundario, instrucciones paso a paso e **ilustración
masculina y femenina** ({len(meta_rows)} imágenes en total).

## Configuraciones

- **`images`** — 1 fila por imagen ({len(meta_rows)}). Etiquetas (grupo, equipamiento,
  músculos, género) + `caption_es`/`caption_en`. Para clasificación de imagen y multimodal
  (image-to-text / VQA). Formato Hugging Face `imagefolder`.
- **`instructions`** — {len(instr_rows)} pares instrucción→respuesta bilingües, para
  fine-tuning de LLMs.
- **`exercises`** — {len(exs)} filas, tabla plana (una por ejercicio).

## Grupos

{chr(10).join(f'- {k}: {v}' for k,v in groups.items())}

## Cómo cargarlo

```python
from datasets import load_dataset
img  = load_dataset("imagefolder", data_dir="build", split="train")   # visión / multimodal
inst = load_dataset("json", data_files="build/instructions.jsonl", split="train")  # LLM
```

## Licencia y créditos

Ilustraciones y datos © Marc Mayol (ver `LICENSE` del proyecto). Los mapas musculares
derivan de react-native-body-highlighter (MIT). Generado con `make_dataset.py`.
"""
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(card)

    print(f"OK · {len(exs)} ejercicios · {len(meta_rows)} imágenes · "
          f"{len(instr_rows)} instrucciones · en {OUT}")

if __name__ == "__main__":
    main()
