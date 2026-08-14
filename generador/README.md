# Cómo se construye el catálogo

Todo lo publicado (`v1/`, `images/`, `muscle-maps/`) es **generado**: no se edita a mano.
La fuente son `exercises_seed.json` (raíz) y los ficheros de este directorio.

> **Ojo:** las ilustraciones NO se generan aquí. Viven en
> `C:\Users\marcm\Desktop\CatalogoEjercicios\` (`generador/gen_bmf.py` las crea,
> `generados/*.png` las guarda) y `build_api.py` las copia desde allí. Si mueves ese
> directorio, ajusta `GEN_IMGS` en `build_api.py`.

## Las piezas

| Fichero | Qué hace |
|---|---|
| `../exercises_seed.json` | La lista maestra: slug, nombre ES/EN, grupo, equipamiento, músculos. |
| `build_api.py` | El que manda: lee el seed y emite todos los JSON, las imágenes y los mapas SVG. |
| `instructions_cache.json` | Instrucciones ES/EN ya resueltas. Si un slug está aquí, **no** se le pregunta a gpt-4o. |
| `instructions_bmf.json` + `merge_instructions.py` | Instrucciones escritas a mano que se inyectan en la caché. |
| `tips_manual*.json`, `tips_desde_app.json` | Errores típicos y alternativas en ES. |
| `build_tips.py` | Los fusiona en `tips.json` y **avisa de cualquier ficha sin cubrir**. |
| `translate_tips.py` | Traduce los tips al inglés (`tips_en.json`), con caché por firma. |
| `make_bundle.py` | Empaqueta el ZIP de descarga. |
| `../dataset/make_dataset.py` | Dataset para Hugging Face a partir de `v1/dataset.json`. |
| `body*.ts` | Paths de las siluetas (base MIT de react-native-body-highlighter) para los mapas SVG. |

Hace falta `generador/.env` con `OPENAI_API_KEY=...` (no se sube).

## Añadir ejercicios nuevos

1. **Ilustraciones.** En `CatalogoEjercicios/generador/gen_bmf.py`, añade el slug con su
   técnica en inglés y lanza:
   ```bash
   python gen_bmf.py --only mi-slug          # --force para rehacer una que salió mal
   ```
   Usa `images.edit` de **gpt-image-2** pasando ilustraciones ya publicadas como
   referencia de estilo. Es lo que hace que las nuevas salgan indistinguibles de las
   viejas: describir el estilo por texto no basta.

2. **Míralas una a una antes de seguir.** Cada lote trae fallos de técnica (un objeto que
   atraviesa el cuerpo, los dos fotogramas idénticos, una mano que no agarra nada).
   Corrige la técnica en el prompt y regenera con `--force`.

3. **Ficha.** Añade la entrada a `exercises_seed.json`.

4. **Instrucciones.** Si el ejercicio es un estiramiento, va de rodillas o lleva "inverso"
   en el nombre, **escríbelas a mano** en `instructions_bmf.json` y ejecuta
   `python merge_instructions.py instructions_bmf.json`. Para el resto, `build_api.py`
   se las pide a gpt-4o y las cachea.

5. **Errores y alternativas.** Añádelos a `tips_manual2.json` y ejecuta:
   ```bash
   python build_tips.py        # falla/avisa si alguna ficha se queda sin ellos
   python translate_tips.py    # traduce solo lo pendiente
   ```

6. **Construir y publicar.**
   ```bash
   python generador/build_api.py
   cd dataset && python make_dataset.py && cd ..
   python generador/make_bundle.py
   git add -A && git commit && git push        # GitHub Pages tarda 1-2 min
   ```
   Actualiza a mano los conteos de `dataset/README.md` y el peso del ZIP en `index.html`
   y `docs.html`.

## Trampas que ya han mordido

- **El fondo no sale blanco puro.** gpt-image-2 lo deja en 250-254 y los lotes viejos en
  crema (#FAF8F5); sobre la tarjeta blanca de la landing se ve como un rectángulo sucio.
  `build_api.py` lo blanquea con una máscara de luminancia (≥236), que llega también al
  fondo encerrado dentro del bastidor de una máquina.
- **No recortes al contenido.** Todo el catálogo comparte encuadre 3:2. Recortar cada
  ficha a su silueta deja unas apaisadas y otras cuadradas (`dead-bug-f` pasaba de
  1024×683 a 1024×210).
- **gpt-4o redacta mal ciertos ejercicios**: pone agarre supino en los "inversos" y
  "siéntate" en ejercicios de rodillas. De ahí el paso 4.
- **Los `mistakes` en inglés van en gerundio** ("Rounding your lower back"). En
  imperativo se leen como una instrucción de cometer el error; está fijado en el prompt
  de `translate_tips.py`.
- **El Pallof press no sale bien.** Cuatro intentos y el modelo siempre dibuja los brazos
  empujando hacia la polea en vez de perpendicular a ella. Publicado con la mejor versión.
