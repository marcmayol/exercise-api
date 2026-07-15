# Exercise API

API abierta, gratuita y **multiidioma (ES/EN)** de ejercicios de gimnasio. Datos estáticos
servidos por GitHub Pages (CDN, HTTPS, **CORS abierto**). Cada ejercicio incluye nombre en
ES/EN, grupo, **equipamiento**, músculos principal/secundario, instrucciones, **ilustración
masculina y femenina** y un **mapa muscular** SVG. Sin claves, sin límites.

🔗 **Web / docs:** https://marcmayol.com/exercise-api/

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/v1/exercises.json` | Índice de todos los ejercicios |
| GET | `/v1/exercises/<slug>.json` | Ficha completa de un ejercicio |
| GET | `/v1/muscles.json` | Taxonomía de músculos (ES/EN) |
| GET | `/v1/groups.json` | Grupos musculares |
| GET | `/v1/by-group/<group>.json` | Ejercicios por grupo (`legs`, `chest`…) |
| GET | `/v1/by-muscle/<muscle>.json` | Ejercicios por músculo (`gluteal`…) |
| GET | `/v1/equipment.json` | Tipos de equipamiento |
| GET | `/v1/by-equipment/<type>.json` | Ejercicios por equipamiento (`machine`, `barbell`…) |
| — | `/images/<slug>-m.jpg` \| `-f.jpg` | Ilustración (hombre / mujer) |
| — | `/muscle-maps/<slug>.svg` | Mapa muscular resaltado |

## Ejemplo

```js
const base = "https://marcmayol.com/exercise-api";
const ex = await fetch(`${base}/v1/exercises/leg-press.json`).then(r => r.json());
ex.name.es;              // "Prensa de piernas"
ex.name.en;              // "Leg press"
ex.equipment.es;         // "Máquina"
ex.primaryMuscles[0].es; // "Cuádriceps"
ex.instructions.en;      // [ "Adjust the seat…", … ]
ex.images.female;        // .../leg-press-f.jpg
```

## Licencia

Estilo MIT **con atribución obligatoria** — puedes usarlo (incluso comercialmente),
pero debes **dar crédito visible a “Marc Mayol”** con enlace a este repositorio.
Ver [`LICENSE`](LICENSE).

Hecho por **Marc Mayol** con ❤ desde Mallorca. Mapas musculares a partir de
[react-native-body-highlighter](https://github.com/HichamELBSI/react-native-body-highlighter) (MIT).
