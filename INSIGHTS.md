# Insights from Feb 10–14 Player Journeys

## 1) AmbroseValley: strongest shared kill/death hotspot
**What caught my eye**
The kill and death heatmaps on `AmbroseValley` concentrate in the *same* minimap region, meaning engagements happen repeatedly in one choke/section rather than spreading evenly.

**Backed by data**
- `AmbroseValley` total: `1799` kill events, `505` death events, `17` storm deaths.
- Top 32×32 minimap cell hotspot (shared):
  - Kill hotspot: cell `(13, 15)` with `65` kill events at approx world `(X=+9.7, Z=-8.9)`
  - Death hotspot: same cell `(13, 15)` with `42` death events at approx world `(X=+9.7, Z=-8.9)`

**Actionable metrics affected**
- `Kill Zones` and `Death Zones` heatmaps
- Engagement density (kills/deaths per minimap cell)
- Match timelines for combat-heavy sequences

**Actionable items**
- Add/adjust cover geometry or route gating around that region to control encounter frequency.
- If that hotspot is unintended: shift spawn pressure or objective pathing so fights distribute across more areas.
- If that hotspot is intended: validate that the loot and rotations around it support healthy extraction paths (so teams aren’t repeatedly trapped).

**Why a level designer should care**
A shared kill/death hotspot typically indicates a map segment that heavily influences match outcomes (rotation timing, fight likelihood, and “snowball” positioning). Small layout changes here usually move outcomes more than changes elsewhere.

---

## 2) Loot hotspots are offset from combat hotspots
**What caught my eye**
On `AmbroseValley`, the highest loot density appears away from the strongest kill/death hotspot, suggesting players are looting in a region that doesn’t always correspond to where the most direct combat happens (or that combat occurs there but looting is happening elsewhere).

**Backed by data**
- `AmbroseValley` total loot events: `9955`
- Top loot hotspot (32×32 minimap cell): cell `(11, 27)` with `583` loot events at approx world `(X=-46.6, Z=-346.4)`
- Top kill/death hotspot (from Insight #1) is near `(X=+9.7, Z=-8.9)`, clearly displaced from the loot hotspot.

**Actionable metrics affected**
- `Loot Density` heatmap
- Loot-to-combat spatial relationship (distance/overlap between loot and kill/death hotspots)
- Rotation patterns observed on player paths over time

**Actionable items**
- If high-value loot is meant to drive combat: adjust loot placement/rarity so it pulls rotations toward the combat choke.
- If high-value loot is meant to diversify risk: keep loot offset but ensure there are safe routes between the looting region and the main fighting area.
- Consider adding intermediate POIs or traversal shortcuts that connect the loot hotspot to more varied fight zones.

**Why a level designer should care**
Loot placement strongly shapes player movement and rotation. When loot and combat zones are offset, it can create “dead time” rotations or unexpected pacing. Balancing this relationship improves match readability and fairness.

---

## 3) Storm deaths are a meaningful minority, but spatially concentrated
**What caught my eye**
Storm deaths are not the majority of deaths, but they still happen often enough to matter, and their positions are concentrated enough that storm timing/pathing likely interacts with specific route choices.

**Backed by data**
- Overall across Feb 10–14 structured dataset:
  - `KilledByStorm = 39` storm deaths
  - Total death events (`Killed` + `BotKilled` + `KilledByStorm`) = `742`
  - Storm share ≈ `5.26%` of all death events
- Map-level storm concentration (average world location):
  - `AmbroseValley` storm avg world: `(X=+19.7, Z=-30.5)` with `17` storm deaths
  - `Lockdown` storm avg world: `(X=+48.9, Z=+44.2)` with `17` storm deaths
  - `GrandRift` storm avg world: `(X=+3.7, Z=+3.7)` with `5` storm deaths

**Actionable metrics affected**
- `Storm Deaths` marker distribution on the minimap
- `Deaths` heatmap when toggled
- Timeline segments near storm end (observable as late-match positional clustering)

**Actionable items**
- Validate storm shrink pacing vs intended extraction lanes (are players dying before reaching viable exits?).
- Adjust environmental cover or route funneling so that storm pressure drives players through intended areas instead of producing “random” storm losses.
- Use the timeline playback to compare: do storm deaths spike after certain objective/rotation moments?

**Why a level designer should care**
Storm pressure is one of the strongest levers for pacing and forced movement. Even a ~5% death share can materially change which parts of the map become “endgame zones.”

