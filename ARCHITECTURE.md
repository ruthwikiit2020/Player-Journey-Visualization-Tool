# Player Journey Visualization Tool Architecture

## What we built (and why)
This repo contains a **Level Designer web visualizer** for *LILA BLACK* that replays and compares player behavior (humans vs bots) on the three live maps:
- `AmbroseValley`
- `GrandRift`
- `Lockdown`

The UI is a single-page app (`index.html`) that renders to an HTML5 `canvas` and overlays:
- player/bot paths
- event markers (kills, deaths, loot, storm deaths)
- heatmaps (kill zones, death zones, high traffic, loot density)
- a timeline playback scrubber

Canvas was chosen for performance (thousands of points) and because minimap overlays are naturally raster-based.

## Data flow (parquet -> what shows up on screen)
1. **Raw telemetry (original parquet files)** live under `February_10/` … `February_14/`.
2. We run a preprocessing step to create `structured_output/player_journey_feb10_14.{parquet,csv}`.
   - Each row is one recorded event in a player (or bot) journey.
   - The script decodes the `event` byte-string into a readable type.
   - It derives `is_bot` from `user_id` (numeric IDs are bots).
   - It computes `journey_time_s` (relative time within a journey) which is used by the UI timeline.
   - It also precomputes minimap coordinates `minimap_x/minimap_y` so the browser can render precisely without repeating world->minimap math.
3. The web app loads the structured dataset from:
   - `structured_output/player_journey_feb10_14.parquet` (preferred)
   - falls back to `structured_output/player_journey_feb10_14.csv` if parquet parsing fails in the browser.
4. After filtering (map/date/match/player type), the app draws:
   - heatmaps from event subsets
   - paths from `Position` / `BotPosition` sequences per `(match_id, user_id)`
   - markers from kill/death/loot/storm events

## Coordinate mapping (world -> minimap pixels)
The tricky part is mapping 3D world coordinates to the 2D minimap image.

We use the map conversion parameters from `README.md` (scale + origin) and the standard two-step transform:

1. Convert world coordinates `(x, z)` into normalized UV:
   - `u = (x - origin_x) / scale`
   - `v = (z - origin_z) / scale`
2. Convert UV to minimap pixel coordinates for a `1024 x 1024` minimap:
   - `pixel_x = u * 1024`
   - `pixel_y = (1 - v) * 1024`  (Y is flipped because images use top-left origin)

In preprocessing, we write these as:
- `minimap_x = pixel_x`
- `minimap_y = pixel_y`

In the browser we render with a **true 1024×1024 canvas internal coordinate system**, and we draw the minimap image into the full canvas (`ctx.drawImage(img, 0, 0, canvas.width, canvas.height)`).

So pixel alignment is exact: `minimap_x/minimap_y` map 1:1 onto canvas pixels, with clamping to avoid out-of-range numeric edge cases.

## Event layering and rendering order
Rendering order (per frame):
1. Clear canvas, draw base background
2. Draw minimap image fully
3. Draw selected heatmaps using `globalCompositeOperation = "screen"`
4. Draw paths (human solid, bot dashed)
5. Draw event markers (💀 kills, ☠ deaths, 📦 loot, ⚡ storm deaths)

This ensures heatmaps never hide the minimap, and markers remain visible above paths.

## Assumptions / ambiguities handled
- **Bots vs humans**: treated as `user_id` being numeric => bot (`is_bot` true). UUID => human.
- **Timeline**: uses `journey_time_s` (derived from `ts` by subtracting each journey’s first timestamp).
- **Event semantics**:
  - kills heatmap includes `Kill` + `BotKill`
  - deaths heatmap includes `Killed` + `BotKilled` + `KilledByStorm`
- If parquet loading fails in the browser, the tool still works via CSV fallback.

## Major tradeoffs
| Decision | Why | Tradeoff |
|---|---|---|
| Precompute `minimap_x/minimap_y` in preprocessing | Pixel-accurate rendering and faster browser rendering | Requires an offline preprocessing step |
| In-browser rendering (Canvas) | Fast iteration for large datasets | Client-side performance depends on browser |
| Parquet via in-browser DuckDB WASM + CSV fallback | Higher fidelity loading, but robust | Parquet load can be slower / fail due to browser/worker constraints |
| Heatmaps drawn per frame from filtered events | Simple and consistent with timeline playback | For very large filters it may reduce FPS (acceptable for this dataset) |

## Three findings (high level)
1. **AmbroseValley** has the strongest shared **kill/death hotspot** (same top 32×32 minimap cell), suggesting a potential combat balance/pacing choke.
2. **Loot hotspots** often appear in regions with weaker direct combat heat (loot and fight “zones” are offset).
3. **Storm deaths** are a smaller share of death events overall (~5.3%) but are spatially concentrated, making storm timing/pathing impactful.

