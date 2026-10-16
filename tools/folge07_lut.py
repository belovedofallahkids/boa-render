#!/usr/bin/env python3
"""Schnittliste Folge 07 – Lut (Notion, 13.10.2026 11:40) -> jobs/folge07_lut_v3.json.

v3 (16.10.): blessed_land (5:06,5–5:13,6) hat oben links eine Huegelstadt mit Tuermen wie Kirchtuerme (H5)
-> ersetzt durch safe_hill_sunrise_cf (Orshot 48993). Ton und alle anderen Bilder wie v2.

Zeiten aus dem Descript-Transkript der Komposition 0bee3427 (Erzaehlung Orshot-Audio 173).
"""
import json
import os

B = "https://storage.orshot.com/cloud/w-12325/renders/brand_assets/"
IMG = {
    "master_A_buch": B + "boa_master_A_buchpng-uoxAhZwWy9D.png",
    "ilyas": B + "boa_ilyas_allein_offizielljpg-OQtwI3xapxd.jpeg",
    "noah": B + "boa_noah_allein_offizielljpg-YwfUilEIZQs.jpeg",
    "kinder_schlafen": B + "boa_kinder_schlafen_offizielljpg-aevRtHZ0V3q.jpeg",
    "oma_window_night": B + "boa_oma_window_night_offizielljpg-i61gAYOmKJ9.jpeg",
    "lut_city": B + "boa_folge07_lut_city_cf_v2jpg-TGhvjKHrP84.jpeg",
    "lut_city_b": B + "boa_folge07_lut_city_cfjpg-5FUpmqeCLHr.jpeg",
    "desert_road": B + "boa_folge07_desert_road_cfjpg-VIO4fzwShlZ.jpeg",
    "ibrahim_tent_food": B + "boa_folge07_ibrahim_tent_food_cfjpg-i3ZGVUHYAWq.jpeg",
    "tent_golden_light": B + "boa_folge07_tent_golden_light_cfjpg-kNDFOgtzp2z.jpeg",
    "lut_house_evening": B + "boa_folge07_lut_house_evening_v2jpg-KGWBRBjvJfZ.jpeg",
    "torches_alley": B + "boa_folge07_torches_alleyjpg-MWLLO1ob6pb.jpeg",
    "glowing_doorway": B + "boa_folge07_glowing_doorwayjpg-uRUiJ6Y6DqX.jpeg",
    "night_departure": B + "boa_folge07_night_departure_cf_v2jpg-9MHpkGpPPRa.jpeg",
    "dawn_storm_far": B + "boa_folge07_dawn_storm_far_v2jpg-n8mxIVsGJ0W.jpeg",
    "blessed_land": B + "boa_blessed_landpng-sF1tJ0UV8lU.png",  # nicht mehr verwenden (H5), bleibt gespeichert (H26)
    "safe_hill_sunrise": B + "boa_folge07_safe_hill_sunrise_cfjpg-5E4m5FD7Bui.jpeg",
    "open_door_welcome": B + "boa_folge07_open_door_welcomejpg-jZERmI7dSP4.jpeg",
}
# lut_city_b: linker Ausschnitt, damit der runde Lehmturm rechts (H5) nicht zu sehen ist
CROP = {"lut_city_b": [0.0, 0.1, 0.58]}


def t(s):
    m, sec = s.split(":")
    return round(int(m) * 60 + float(sec), 3)


CUTS = [  # start, bild, bewegung
    ("0:00.0", "master_A_buch", "zoom_in"),
    ("0:18.0", "ilyas", "zoom_in"),          # s1b – Ilyas spricht (H9)
    ("0:21.3", "master_A_buch", "pan_left"),
    ("0:46.5", "lut_city", "pan_right"),
    ("0:57.0", "desert_road", "zoom_in"),
    ("1:07.0", "lut_city_b", "zoom_out"),
    ("1:21.5", "noah", "zoom_in"),           # s2c – Noah spricht (H9)
    ("1:25.3", "lut_city", "zoom_in"),
    ("1:38.3", "ibrahim_tent_food", "zoom_in"),
    ("2:10.0", "tent_golden_light", "zoom_in"),
    ("2:30.2", "ilyas", "zoom_in"),          # s3d
    ("2:33.9", "tent_golden_light", "zoom_out"),
    ("2:39.5", "lut_city", "pan_left"),
    ("3:00.2", "lut_house_evening", "zoom_in"),
    ("3:22.0", "torches_alley", "zoom_in"),
    ("3:43.0", "noah", "zoom_in"),           # s4c
    ("3:46.9", "glowing_doorway", "zoom_in"),
    ("4:07.3", "night_departure", "zoom_in"),   # night_star (Folge 06) hat Kuppeln -> H5
    ("4:24.3", "dawn_storm_far", "zoom_in"),
    ("4:48.6", "ilyas", "zoom_in"),          # s5c
    ("4:52.2", "dawn_storm_far", "pan_right"),
    ("5:06.5", "safe_hill_sunrise", "zoom_in"),
    ("5:13.6", "open_door_welcome", "zoom_in"),
    ("5:34.0", "kinder_schlafen", "zoom_out"),   # ab „Oh, sie schlafen schon“ (H12)
    ("6:02.7", "oma_window_night", "zoom_out"),
]


def main():
    segs = []
    for i, (start, img, motion) in enumerate(CUTS):
        s = t(start)
        e = t(CUTS[i + 1][0]) if i + 1 < len(CUTS) else "audio"
        length = (e - s) if e != "audio" else 30
        seg = {"image": IMG[img], "start": s, "end": e, "motion": motion,
               "amount": round(min(0.14, 0.04 + 0.004 * length), 3), "label": img}
        if img in CROP:
            seg["crop"] = CROP[img]
        segs.append(seg)
    job = {
        "name": "folge07_lut_v3",
        "audio": "https://storage.orshot.com/cloud/w-12325/renders/audio/"
                 "boa_folge07_erzaehlung_komplett_noah_2026-10-13mp3-IU4UXH3rUoF.mp3",
        "crossfade": 0.6, "fade_in": 0.8, "fade_out": 2.5, "loudness": -14,
        "segments": segs,
    }
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "jobs", "folge07_lut_v3.json")
    with open(out, "w") as f:
        json.dump(job, f, indent=1, ensure_ascii=False)
    print(out, len(segs), "Abschnitte")


if __name__ == "__main__":
    main()
