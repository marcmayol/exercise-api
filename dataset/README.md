# Exercise API — Dataset para IA

Convierte la Exercise API (104 ejercicios) en un **dataset multimodal bilingüe (ES/EN)**
listo para Hugging Face. Se genera con `make_dataset.py` a partir de `v1/dataset.json` y
las imágenes del proyecto.

```bash
cd dataset
python make_dataset.py     # produce ./build/
```

## Qué genera (`build/`)

| Archivo | Filas | Uso |
|---|---|---|
| `images/` + `metadata.jsonl` | 208 | **Visión / multimodal**: clasificación de imagen e image-to-text (captioning / VQA). Formato Hugging Face `imagefolder`. |
| `instructions.jsonl` | 832 | **Fine-tuning de LLM**: pares instrucción→respuesta bilingües. |
| `exercises.jsonl` / `exercises.csv` | 104 | **Tabla plana**: una fila por ejercicio. |
| `README.md` | — | Dataset card (con front-matter YAML de Hugging Face). |

Cada imagen lleva etiquetas: grupo muscular, equipamiento, músculo principal/secundario,
género y un `caption` en ambos idiomas.

> `build/` está en `.gitignore` (es regenerable y pesa ~10 MB). Súbelo a Hugging Face, no al repo.

## Cargar con 🤗 datasets

```python
from datasets import load_dataset
img  = load_dataset("imagefolder", data_dir="build", split="train")            # visión / multimodal
inst = load_dataset("json", data_files="build/instructions.jsonl", split="train")  # LLM
```

## Subir a Hugging Face Hub

```bash
huggingface-cli login
huggingface-cli upload <usuario>/exercise-api-dataset build . --repo-type=dataset
```
