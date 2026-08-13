# 24 ejercicios nuevos que pide Building My Future

> **INCORPORADOS el 13 de agosto de 2026.** Los 24 ya están en el API (126 → **150**), con
> ilustración masculina y femenina, mapa muscular por género e instrucciones ES/EN. Las 48
> ilustraciones se generaron con **gpt-image-2** vía `images.edit`, pasando ilustraciones ya
> publicadas como referencia de estilo (`CatalogoEjercicios/generador/gen_bmf.py`), y las
> instrucciones se escribieron a mano en `generador/instructions_bmf.json`.

**Fecha:** 13 de agosto de 2026
**Origen:** los 11 planes nuevos de la app (Arranque, Hipertrofia, Mantenimiento, Calistenia,
Cardio, Bloque Piernas, Bloque Brazos, Bloque Core, Fuerza Máxima, Bloque Postura y Movilidad).

## De dónde sale esta lista

Los 11 planes traen **201 ejercicios distintos**. De ellos, **157 no tienen ilustración ni ficha**
en la app. Al cruzarlos con este catálogo (126 ejercicios), la cuenta queda así:

| | |
|---|---|
| Ya existen aquí (imagen m/f + instrucciones + mapa muscular) | **113** |
| No son un movimiento ilustrable | **13** |
| **Faltan: hay que crearlos** | **31 nombres → 24 movimientos** |

La diferencia entre 157 y 24 son **variantes del mismo nombre**. Los planes escriben "Sentadilla
hack", "Sentadilla hack o goblet", "Sentadilla en máquina hack o goblet" y "Sentadilla goblet o
prensa" para dos ilustraciones que ya existen; eso se resuelve en el mapa de la app, no aquí.

Los 13 no ilustrables son bloques de cardio ("Bloque continuo suave", "8 x (1 min intenso + 2 min
suave)", "Pirámide 1-2-3-2-1 min intenso"…), un par de comodines ("Core a elección") y los
circuitos, que la app ya pinta con la ilustración de cada parte.

**Siete de los once planes no necesitan nada de esto**: Arranque, Hipertrofia, Mantenimiento,
Cardio, Bloque Piernas, Bloque Brazos y Fuerza Máxima están cubiertos con lo que ya hay.

## Los 24

| slug | nombre | grupo | equipo | lo pide |
|---|---|---|---|---|
| `bird-dog` | Bird dog | Core | bodyweight | Bloque Core, Bloque Postura, Calistenia |
| `hollow-hold` | Hollow hold | Core | bodyweight | Bloque Core, Calistenia |
| `hollow-rock` | Hollow rock | Core | bodyweight | Bloque Core |
| `pallof-press` | Press Pallof | Core | cable | Bloque Core |
| `farmers-walk` | Paseo del granjero | Core | dumbbell | Bloque Core |
| `diamond-push-up` | Flexión en diamante | Pecho | bodyweight | Calistenia |
| `doorway-chest-stretch` | Estiramiento de pecho en marco de puerta | Pecho | bodyweight | Bloque Postura, Movilidad |
| `wall-handstand` | Pino contra la pared | Hombros | bodyweight | Calistenia |
| `y-t-w-raise` | Y-T-W en banco inclinado | Hombros | dumbbell | Bloque Postura |
| `chin-tuck` | Retracción de barbilla (chin tuck) | Espalda | bodyweight | Bloque Postura |
| `thoracic-extension-bench` | Extensión torácica sobre banco | Espalda | bodyweight | Bloque Postura, Movilidad |
| `quadruped-thoracic-rotation` | Rotación torácica en cuadrupedia | Espalda | bodyweight | Movilidad |
| `open-book-stretch` | Apertura de pecho tumbado (libro abierto) | Espalda | bodyweight | Bloque Postura |
| `assisted-pistol-squat` | Sentadilla a una pierna asistida | Piernas | bodyweight | Calistenia |
| `deep-squat-hold` | Sentadilla profunda mantenida | Piernas | bodyweight | Movilidad |
| `hip-hinge-dowel` | Bisagra de cadera con palo | Piernas | bodyweight | Movilidad |
| `hip-flexor-stretch` | Estiramiento de flexores de cadera | Piernas | bodyweight | Bloque Postura, Movilidad |
| `low-lunge-rotation` | Zancada baja con rotación | Piernas | bodyweight | Movilidad |
| `figure-4-stretch` | Estiramiento de glúteo (figura 4) | Piernas | bodyweight | Movilidad |
| `supine-hamstring-stretch` | Estiramiento de isquios tumbado | Piernas | bodyweight | Movilidad |
| `seated-forward-fold` | Flexión adelante sentado | Piernas | bodyweight | Movilidad |
| `hip-90-90` | Postura 90/90 de cadera | Piernas | bodyweight | Movilidad |
| `calf-stretch-wall` | Estiramiento de gemelos en pared | Piernas | bodyweight | Movilidad |
| `ankle-dorsiflexion-wall` | Dorsiflexión de tobillo en pared | Piernas | bodyweight | Movilidad |

Reparto: Piernas 11, Core 5, Espalda 4, Hombros 2, Pecho 2. El catálogo pasaría de **126 a 150**.

## Ficheros que acompañan a este documento

- **`nuevos-desde-building-my-future.seed.json`** — las 24 entradas con el formato exacto de
  `exercises_seed.json` (slug, es, en, group_es, group_en, equipment, primary, secondary).
  Validado: ningún slug pisa uno existente y todos los músculos, grupos y equipos son del
  vocabulario del API.
- **`nuevos-desde-building-my-future.prompts.json`** — para cada slug, el nombre en inglés y la
  descripción de la técnica en inglés, con el formato que espera el dict `EXERCISES` del
  generador (`CatalogoEjercicios/generador/gen_circuits.py`): dos fotogramas, inicio y final.

## Cómo incorporarlos

1. Añadir las 24 entradas de `nuevos-desde-building-my-future.seed.json` a `exercises_seed.json`.
2. Generar las **48 ilustraciones** (24 × masculina y femenina) con el flujo de gpt-image, usando
   las técnicas de `nuevos-desde-building-my-future.prompts.json` y el `STYLE` de siempre
   (cara en blanco, camiseta naranja, fondo blanco puro, vector plano). Dejarlas en la carpeta de
   generados como `<slug>-male.png` / `<slug>-female.png`.
3. Correr `generador/build_api.py`: recorta las imágenes, pide las instrucciones ES/EN, dibuja los
   mapas musculares y reconstruye todos los JSON del API.

## Dos avisos

**Movilidad no tiene grupo propio.** El API tiene siete grupos (Pecho, Espalda, Hombros, Brazos,
Piernas, Core, Cardio) y catorce de estos 24 son estiramientos y movilidad. Aquí van repartidos
por la zona que estiran (los de cadera e isquios a Piernas, los torácicos a Espalda). Si algún día
interesa un grupo **Movilidad**, hay que tocar `GROUPS` en el generador; no lo he hecho para que
el seed funcione tal cual.

**Las fichas de la app no salen enteras de aquí.** El API da músculos e instrucciones, pero la
`ExerciseGuide` de Building My Future además tiene *errores típicos* y *alternativas si la máquina
está ocupada*. Eso hay que escribirlo aparte, y no solo para estos 24: son 157 ejercicios los que
hoy no tienen ficha en la app.
