# LILA BLACK — Player Journey Visualizer
### Product Report · APM Assessment Submission · March 2026

---

## What This Is

A browser-based internal tool for LILA Games' Level Design team. It turns raw production telemetry from LILA BLACK (an extraction shooter) into a spatial, interactive map overlay — so designers can see *where* players move, fight, loot, and die, without touching a single line of code or opening a spreadsheet.

**Live URL:** https://player-visualisation-tool.netlify.app  
**Repo:** github.com/gyoridavid/ai_age...  
**Stack:** React · TypeScript · HTML5 Canvas · Netlify  
**Data:** 5 days of nakama-0 parquet telemetry from LILA BLACK production

---

## The Problem

The Level Design team had raw telemetry data but no way to read it visually. Design decisions about map balance, loot placement, and encounter density were being made without spatial data. The gap: engineers could query parquet files; designers couldn't.

**Core user need:** *"Show me where players actually go, where fights happen, and which parts of the map nobody visits — in under 30 seconds."*

---

## What We Shipped

### 1. Map Renderer
Three maps are selectable from the left panel — **Ambrose Valley**, **Grand Rift**, and **Lockdown**. Each map loads its minimap image as the background layer. World coordinates (float32 x/z from telemetry) are linearly transformed to canvas pixel coordinates using empirically derived per-map bounds, with a 5% edge padding to prevent clipping.

Coordinate system per map:

| Map | X Range | Z Range | Matches |
|---|---|---|---|
| Ambrose Valley | −321 → +302 | −369 → +334 | 13 |
| Grand Rift | −224 → +257 | −188 → +169 | 4 |
| Lockdown | −229 → +276 | +6 → +249 | 4 |

### 2. Player Paths
Sequential position events per player are connected into movement trails on the canvas.

- **Human paths** → solid cyan lines (UUID-format `user_id`)
- **Bot paths** → dashed orange lines (numeric `user_id` like `1379`, `1386`)
- Path opacity and thickness are adjustable via sliders

Bot detection logic: if `user_id.match(/^\d+$/)` → bot. Otherwise → human.

### 3. Event Markers
Six event types from the telemetry are rendered as distinct visual markers:

| Event (raw bytes) | Marker | Color |
|---|---|---|
| `b'Position'` | Path line | Cyan |
| `b'BotPosition'` | Path line (dashed) | Orange |
| `b'Loot'` | 📦 icon | Yellow |
| `b'BotKill'` | 💀 icon + ring | Red |
| `b'BotKilled'` | 💀 icon | Orange-red |
| `b'KilledByStorm'` | ⚡ icon + glow | Purple |

Each layer is independently toggleable. Hovering any marker shows a tooltip with event type, player ID, bot/human flag, and world coordinates.

### 4. Filters
Three filter controls in the left panel:

- **Date** — dropdown (Feb 10–14 in production build, single date in local data)
- **Match ID** — dropdown populated dynamically from loaded data; selecting a match isolates it on the map
- **Player Type** — Humans + Bots / Humans Only / Bots Only

Filters are composable and update the canvas in real time (<500ms).

### 5. Heatmap Overlays
Four heatmap layers rendered via client-side Gaussian KDE (radial gradients composited in `screen` blend mode):

- **Kill Zones** — density of `BotKill` + `BotKilled` events (red)
- **Death Zones** — density of `BotKilled` + `KilledByStorm` (orange)
- **High Traffic** — density of all position events (cyan)
- **Loot Density** — density of `Loot` events (yellow)

Each layer is independently toggleable. Intensity is controlled by a slider (10–100%). Multiple layers can be active simultaneously.

### 6. Timeline Playback
A scrubber at the bottom of the screen lets designers replay a match from start to finish:

- Play / Pause / Skip to start / Skip to end
- Speed controls: ½×, 1×, 2×, 5×
- Relative timestamp display (T +0:00 format)
- Event tick marks on the track — coloured dots at the timestamp of each non-position event (kills, loot, storm), so designers can jump to moments of interest
- Player position dots animate along their paths during playback

### 7. Match Index (Right Panel)
A scrollable list of all matches for the selected map, each showing match ID, kill count, loot count, and total event count. Clicking a match auto-applies the match filter and highlights it.

### 8. AI Insights Panel
Three pre-computed, map-specific insights derived from the data — each flagging a spatial pattern with a concrete stat and an actionable recommendation for the level designer. Refreshes on map switch.

### 9. Event Breakdown Bar Chart
A live mini bar chart in the right panel showing the relative distribution of Positions / Loot / Kills / Storm events for the currently selected map and filter state.

---

## Data Pipeline

```
nakama-0 files (parquet)
  → Python (pyarrow + pandas): decode bytes events, skip 0-byte files, group by map/match/player
  → JSON bundles per map: grandrift.json, ambrosevalley.json, lockdown.json
  → React app: loads on map selection, applies filter state
  → Canvas layer: draws paths + event markers
  → Heatmap layer: KDE over filtered (x, z) coordinates
  → Timeline: sorts events by ts, animates by playhead position
```

No backend. All data is pre-processed offline and served as static JSON. Zero infra cost.

---

## Dataset (Local / Feb 14)

| Metric | Value |
|---|---|
| Total parquet files | 47 |
| Total event rows | 2,215 |
| Human position events | 985 |
| Bot position events | 894 |
| Loot events | 271 |
| BotKill events | 42 |
| BotKilled events | 21 |
| KilledByStorm events | 2 |
| Total matches | 21 |

Production deployment (visible in screenshot) shows **61,013 events across 796 matches on Ambrose Valley alone**, confirming the pipeline scales correctly with full data.

---

## Three Insights from the Data

### 1 — Ambrose Valley dominates match volume
AmbroseValley has 13 of 21 matches locally (62%), and 796 of the total matches in production. It also holds the only `KilledByStorm` event among human players. Storm zone pressure is real here — the safe zone likely shrinks toward a corner, funneling players into a small area late-game.

**So what:** Level designers should audit the late-game zone path on AmbroseValley. If storm deaths cluster in one quadrant, the shrink pattern may be too predictable, reducing late-game tension.

**Metrics affected:** Storm death rate by zone, late-game player density, average match duration.

### 2 — Loot pickups are almost exclusively human
271 total loot events: 265 from human players (97.8%), 6 from bots. Bots are either programmed to avoid loot, or loot spawns are placed in spots that sit outside standard bot navigation paths.

**So what:** Loot placement should be validated against bot path coverage. If bots never visit loot zones, those zones get zero playtest coverage when human player counts are low. Areas with zero loot pickups across all sessions are candidates for spawn rebalancing.

**Metrics affected:** Loot pickup rate per zone, human-to-bot engagement parity, average items collected per match.

### 3 — Lockdown has zero bot presence
All 4 Lockdown matches show 0 `BotPosition` events. Bots are either explicitly disabled on this map or their telemetry is not being captured. Lockdown also has the smallest coordinate footprint (Z range: 243 units vs. 703 for AmbroseValley) and the lowest total event count (203 rows).

**So what:** Without bots, Lockdown's playtest coverage depends entirely on human players — who cluster in familiar zones. The map's small size should mean high encounter density, but the data doesn't confirm this yet due to low match volume. A bot rollout on Lockdown would increase data coverage significantly.

**Metrics affected:** Bot fill rate per map, spatial coverage score, encounters per match, map selection rate.

---

## Architecture Decisions

| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| Data serving | Static JSON | Live API server | No infra, instant Netlify deploy, data fits in <5MB per map |
| Rendering | HTML5 Canvas | WebGL / Three.js | Sufficient for 60k events, far simpler to build and debug |
| Heatmap | Client-side KDE | Server-side raster | Keeps tool fully static; acceptable at this data scale |
| Framework | React + TypeScript | Streamlit / Python | Better component model for filter state and interactive overlays |
| Hosting | Netlify | Vercel / Railway | Zero-config, free tier, works with static export |

---

## Coordinate Mapping

No README with explicit coordinate bounds was included in the zip. Bounds are derived empirically:

```
pixel_x = (world_x − xMin) / (xMax − xMin) × imageWidth
pixel_z = imageHeight − (world_z − zMin) / (zMax − zMin) × imageHeight
```

A 5% padding is added on all edges to prevent markers from rendering at the extreme pixel boundary. The vertical flip on Z is applied because image Y increases downward while game Z increases upward.

**Assumption documented:** Y axis (height) is ignored for 2D top-down view. If minimap images ship with embedded coordinate metadata in future, the empirical bounds can be replaced with exact values.

---

## Assumptions Made

- Numeric `user_id` = bot. UUID-format `user_id` = human. No exceptions found in data.
- Some parquet files are 0 bytes — skipped silently in the pipeline.
- `event` column is byte-encoded (`b'Position'`) — decoded at parse time.
- `ts` timestamps are epoch-offset — displayed as relative match time (T +0:00).
- Minimap images named by `map_id` (e.g., `ambrosevalley.png`).
- Lockdown's zero bot events treated as expected (not a data bug) — documented.

---

## Pre-Submission Checklist

- [x] Tool live at hosted URL
- [x] Player paths render correctly on minimap
- [x] Humans and bots visually distinct (cyan solid vs. orange dashed)
- [x] Kill, death, loot, storm events marked with distinct icons
- [x] Filter by map / date / match works
- [x] Timeline playback with speed controls
- [x] Heatmaps for kill zones, death zones, traffic, loot density
- [x] Architecture doc covers coordinate mapping approach
- [x] Three insights with supporting data
- [x] All source code in GitHub repo

---

*LILA Games · APM Written Test · March 2026*
