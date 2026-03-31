"""
Prepare a browser-friendly structured dataset for the visualization tool.

Input:
  February_10..February_14 directories containing parquet (no extension; *.nakama-0 files).

Output:
  structured_output/player_journey_feb10_14.{parquet,csv}

The visualization tool depends on:
  - event type decoding (event stored as bytes in parquet)
  - bot detection (numeric user_id == bot)
  - minimap coordinate mapping (minimap_x/minimap_y)
  - journey-relative timestamps (journey_time_s)
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parents[1]

DAYS = [10, 11, 12, 13, 14]

MAP_CFG = {
    "AmbroseValley": {"scale": 900.0, "origin_x": -370.0, "origin_z": -473.0},
    "GrandRift": {"scale": 581.0, "origin_x": -290.0, "origin_z": -290.0},
    "Lockdown": {"scale": 1000.0, "origin_x": -500.0, "origin_z": -500.0},
}

MAP_PX = 1024.0


def is_bot_user_id(user_id: str) -> bool:
    return bool(re.fullmatch(r"\d+", str(user_id)))


def world_to_minimap(map_id: str, x: float, z: float) -> tuple[float, float]:
    cfg = MAP_CFG[map_id]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    px = u * MAP_PX
    py = (1.0 - v) * MAP_PX  # image origin (top-left)
    return float(px), float(py)


def load_day(day_folder: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for f in day_folder.glob("*.nakama-0"):
        try:
            df = pq.read_table(f).to_pandas()
        except Exception:
            continue

        if "event" in df.columns:
            # parquet stores event as bytes in this dataset
            df["event"] = df["event"].apply(
                lambda x: x.decode("utf-8") if isinstance(x, (bytes, bytearray)) else x
            )

        df["source_file"] = f.name
        df["day"] = day_folder.name
        df["is_bot"] = df["user_id"].astype(str).apply(is_bot_user_id)

        # journey-relative time
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts").reset_index(drop=True)
        min_ts = df["ts"].min()
        df["journey_time_s"] = (df["ts"] - min_ts).dt.total_seconds()

        # Minimaps: precompute pixel locations so the browser only draws
        def to_minimap(row: pd.Series) -> pd.Series:
            if row["map_id"] not in MAP_CFG:
                return pd.Series({"minimap_x": pd.NA, "minimap_y": pd.NA})
            px, py = world_to_minimap(row["map_id"], float(row["x"]), float(row["z"]))
            return pd.Series({"minimap_x": px, "minimap_y": py})

        mm = df.apply(to_minimap, axis=1)
        df["minimap_x"] = mm["minimap_x"]
        df["minimap_y"] = mm["minimap_y"]

        # Timeline helper used by UI
        df["timeline_s"] = df["journey_time_s"]
        df["player_type"] = df["is_bot"].map({True: "bot", False: "human"})
        df["journey_id"] = df["user_id"].astype(str) + "_" + df["match_id"].astype(str)

        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    frames: list[pd.DataFrame] = []
    for d in DAYS:
        day_dir = BASE / f"February_{d}"
        if not day_dir.exists():
            continue
        print(f"Loading {day_dir} ...")
        df_day = load_day(day_dir)
        if len(df_day):
            frames.append(df_day)

    if not frames:
        raise SystemExit("No parquet files were loaded.")

    all_df = pd.concat(frames, ignore_index=True)
    all_df = all_df.sort_values(["day", "match_id", "user_id", "ts"]).reset_index(drop=True)

    out_dir = BASE / "structured_output"
    out_dir.mkdir(exist_ok=True)

    parquet_path = out_dir / "player_journey_feb10_14.parquet"
    csv_path = out_dir / "player_journey_feb10_14.csv"
    summary_path = out_dir / "player_journey_summary_feb10_14.csv"

    all_df.to_parquet(parquet_path, index=False)
    all_df.to_csv(csv_path, index=False)

    summary = all_df.groupby("day").agg(
        files=("source_file", "nunique"),
        events=("journey_id", "count"),
        unique_players=("user_id", "nunique"),
        unique_matches=("match_id", "nunique"),
        bots=("is_bot", "sum"),
    ).reset_index()
    summary.to_csv(summary_path, index=False)

    print("Wrote:")
    print(" ", parquet_path)
    print(" ", csv_path)
    print(" ", summary_path)


if __name__ == "__main__":
    main()

