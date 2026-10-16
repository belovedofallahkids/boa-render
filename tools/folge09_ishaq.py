#!/usr/bin/env python3
"""Schnittliste Folge 09 – Ishaq -> jobs/folge09_ishaq_v3.json.

v3 (16.10.): blessed_land (s2a) hat oben links eine Huegelstadt mit Tuermen wie Kirchtuerme (H5)
-> ersetzt durch safe_hill_sunrise_cf (Orshot 48993). Ton und alle anderen Bilder wie v2.
Dazu 5 s Endbild nach dem letzten Wort und 1 s Abblende (v2 blendete schon waehrend der letzten Worte ab).

Zeiten aus dem Descript-SRT der Komposition 8b7456dd (Erzaehlung Orshot-Audio 242, 496,4 s).
Jeder Schnitt liegt in der Pause vor dem Satz. Bildplan: Notion-Seite Folge 09, Abschnitt 6.
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
    "blessed_land": B + "boa_blessed_landpng-sF1tJ0UV8lU.png",  # nicht mehr verwenden (H5), bleibt gespeichert (H26)
    "safe_hill_sunrise": B + "boa_folge07_safe_hill_sunrise_cfjpg-5E4m5FD7Bui.jpeg",
    "cradle_waiting": B + "boa_folge09_cradle_waiting_v3_cfjpg-uQStf8xfGaD.jpeg",
    "tent_lamp_night": B + "boa_folge09_tent_lamp_night_cfjpg-ok5tckjKAUs.jpeg",
    "ibrahim_tent_food": B + "boa_folge07_ibrahim_tent_food_cfjpg-i3ZGVUHYAWq.jpeg",
    "lut_city": B + "boa_folge07_lut_city_cf_v2jpg-TGhvjKHrP84.jpeg",
    "tent_golden_light": B + "boa_folge07_tent_golden_light_cfjpg-kNDFOgtzp2z.jpeg",
    "sunrise_hope": B + "boa_folge09_sunrise_hope_cfjpg-jm9njyyaEFi.jpeg",
    "cradle_morning": B + "boa_folge09_cradle_morningjpg-O7wxuAGRbb7.jpeg",
    "two_palms": B + "boa_folge09_two_palmsjpg-dx7C76YRe6u.jpeg",
    "prayer_rug_sunrise": B + "boa_folge09_prayer_rug_sunrisejpg-Sdao2hRcTap.jpeg",
    "basket_sharing": B + "boa_folge09_basket_sharingjpg-GVPEDT8Ghkt.jpeg",
    "tree_of_lights": B + "boa_folge09_tree_of_lightsjpg-dz4ohqXPhph.jpeg",
    "lanterns_path": B + "boa_folge09_lanterns_pathjpg-VVapeHoAedK.jpeg",
}

CUTS = [  # start (s), bild, bewegung, zeile
    (0.0, "master_A_buch", "zoom_in"),          # s1a
    (26.4, "noah", "zoom_in"),                  # s1b Noah (H9)
    (30.0, "master_A_buch", "pan_left"),        # s1c
    (47.6, "safe_hill_sunrise", "pan_right"),        # s2a gesegnetes Land
    (66.5, "cradle_waiting", "zoom_in"),        # s2a „Aber Sara hatte nie ein Baby“
    (76.6, "ilyas", "zoom_in"),                 # s2b Ilyas
    (79.3, "tent_lamp_night", "zoom_in"),            # s2c
    (99.7, "ibrahim_tent_food", "zoom_in"),     # s3a
    (126.0, "ibrahim_tent_food", "pan_left"),   # s3b
    (140.5, "lut_city", "zoom_in"),             # s3b „zum Volk von Lut“
    (147.2, "tent_golden_light", "zoom_in"),    # s3b „Es waren Engel“
    (150.2, "noah", "zoom_in"),                 # s3c Noah
    (155.0, "tent_golden_light", "zoom_out"),   # s3d frohe Botschaft
    (179.8, "cradle_waiting", "pan_right"),     # s4a Sara staunt
    (203.6, "ilyas", "zoom_in"),                # s4b Ilyas
    (209.3, "tent_golden_light", "zoom_in"),    # s4c Antwort der Engel
    (234.8, "sunrise_hope", "zoom_in"),           # s4d nicht die Hoffnung verlieren
    (267.1, "cradle_morning", "zoom_in"),       # s5a Ishaq wird geboren
    (295.4, "noah", "zoom_in"),                 # s5b Noah
    (299.6, "two_palms", "pan_right"),          # s5c zwei Soehne
    (322.3, "prayer_rug_sunrise", "zoom_in"),   # s6a
    (345.5, "basket_sharing", "zoom_in"),       # s6a „gab den Armen“
    (353.5, "ilyas", "zoom_in"),                # s6b Ilyas
    (358.8, "tree_of_lights", "zoom_in"),       # s6c Yaqub, Yusuf
    (373.7, "tree_of_lights", "pan_right"),     # s6c „Der Edle, Sohn des Edlen“
    (398.7, "noah", "zoom_in"),                 # s6d Noah
    (403.4, "lanterns_path", "pan_right"),      # s6e leuchtende Kette
    (426.3, "kinder_schlafen", "zoom_out"),     # s7a „Oh, sie schlafen schon“ (H12)
    (456.7, "oma_window_night", "zoom_out"),    # s7b
]


def main():
    segs = []
    for i, (s, img, motion) in enumerate(CUTS):
        e = CUTS[i + 1][0] if i + 1 < len(CUTS) else "audio"
        length = (e - s) if e != "audio" else 40
        segs.append({"image": IMG[img], "start": s, "end": e, "motion": motion,
                     "amount": round(min(0.14, 0.04 + 0.004 * length), 3), "label": img})
    job = {
        "name": "folge09_ishaq_v3",
        "audio": "https://storage.orshot.com/cloud/w-12325/renders/audio/"
                 "boa_folge09_erzaehlung_komplett_2026-10-16mp3-qhiWVNmapwv.mp3",
        "crossfade": 0.6, "fade_in": 0.8, "fade_out": 1.0, "tail_hold": 6.0,  # 5 s Endbild nach dem letzten Wort + 1 s Abblende (Notion-Plan)
        "loudness": -14,
        "segments": segs,
    }
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "jobs", "folge09_ishaq_v3.json")
    with open(out, "w") as f:
        json.dump(job, f, indent=1, ensure_ascii=False)
    print(out, len(segs), "Abschnitte")


if __name__ == "__main__":
    main()
