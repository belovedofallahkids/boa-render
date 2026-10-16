#!/usr/bin/env python3
"""Folge 08 – Ismail -> jobs/folge08_ismail_v3.json.

v3 (16.10.): wie v2, dazu 5 s Endbild nach dem letzten Wort und 1 s Abblende
(v2 blendete schon waehrend „Allah beschuetze euch“ ab).

v2 (16.10.): two_hills = neues Bild mit beiden Huegeln (Cloudflare 49030), ohne Zuschnitt.
v1 hatte das alte Bild zugeschnitten, dabei fehlte der zweite Huegel.

Ton: Roh-Erzaehlung (Orshot, 7:01,3) mit den H1-Schnitten C1–C5 (Notion, 13.10.).
Die Schnitt- und Bildzeiten stammen aus dem Wort-Transkript out/transcripts/folge08_roh.txt
(faster-whisper) und sind hier in ROH-Zeit angegeben; das Skript rechnet sie auf die Zeit
nach den Schnitten um.
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
    "valley_mecca": B + "boa_folge08_valley_mecca_metapng-w09uOkimipO.png",
    "dua_sky": B + "boa_folge06_sunset_skypng-0ZD8ADNMJwX.png",
    "empty_waterskin": B + "boa_folge08_empty_waterskinjpg-8Qx3n9vnhpB.jpeg",
    "safa_hill": B + "boa_folge08_safa_hill_v2jpg-0aBYH7VwkH3.jpeg",
    "two_hills": B + "boa_folge08_two_hills_v4_cfpng-KuA5Hsm8Xmc.jpeg",  # v1: boa_folge08_two_hillsjpg-6kmLEgM5A6Q.jpeg
    "sand_glow": B + "boa_folge08_sand_glow_v2jpg-imFi95mHKXi.jpeg",
    "zamzam_spring": B + "boa_folge08_zamzam_springjpg-YkXLNzh2AZs.jpeg",
    "birds_over_valley": B + "boa_folge08_birds_over_valleyjpg-lhDOEJ2JvrI.jpeg",
    "tents_valley": B + "boa_folge08_tents_valleyjpg-z89UaCqD278.jpeg",
    "kaaba_building": B + "boa_folge08_kaaba_buildingjpg-Y24OJagk9Af.jpeg",
    "prayer_rug_sunrise": B + "boa_folge09_prayer_rug_sunrisejpg-Sdao2hRcTap.jpeg",
}
CROP = {
    "birds_over_valley": [0.15, 0.0, 0.62],  # nur Voegel und Felsen, der Fluss unten bleibt draussen (H1)
}

# H1-Schnitte (Roh-Zeit, Sekunden), jeweils in der Sprechpause gesetzt
AUDIO_CUTS = [
    [0.0, 2.95],       # C1  „Nouh… Ilyas…“ am Anfang
    [133.45, 136.40],  # C2  „Er weinte und weinte.“
    [166.90, 169.40],  # C3  „Nouh, Ilyas,“ vor „wisst ihr was?“
    [214.40, 229.45],  # C4  „Man erzählt … Zam Zam … ihren Namen: Zamzam.“
    [395.66, 396.86],  # C5  nur „vor Freude“
]

CUTS = [  # Roh-Start, Bild, Bewegung
    (0.0, "master_A_buch", "zoom_in"),         # s1a
    (27.6, "noah", "zoom_in"),                 # s1b Noah „Bis heute? Echt, Oma?“
    (30.4, "master_A_buch", "pan_left"),       # s1c
    (44.6, "valley_mecca", "zoom_in"),         # s2a leeres Tal
    (68.8, "valley_mecca", "pan_left"),        # s2b Hadschars Fragen
    (92.4, "ilyas", "zoom_in"),                # s2c Ilyas „Sie hatte gar keine Angst?“
    (95.6, "dua_sky", "zoom_in"),              # s2d Ibrahims Bittgebet
    (118.6, "empty_waterskin", "zoom_in"),     # s3a Wasser leer
    (136.4, "safa_hill", "pan_right"),         # s3b Safa
    (147.6, "two_hills", "pan_left"),          # s3b–s3c Marwa, hin und her, sieben Mal
    (179.9, "noah", "zoom_in"),                # s3d Noah „Wirklich? Wie Hadschar?“
    (183.6, "sand_glow", "zoom_in"),           # s4a Stimme, Engel nur als Licht
    (199.5, "zamzam_spring", "zoom_in"),       # s4a–s4b Wasser sprudelt
    (229.6, "ilyas", "zoom_in"),               # s4c Ilyas „Zamzam! Das Wasser kenne ich!“
    (235.3, "zamzam_spring", "zoom_out"),      # s4d
    (255.4, "birds_over_valley", "pan_right"), # s5a Voegel
    (269.3, "tents_valley", "zoom_in"),        # s5a–s5b Reisende, Ismail waechst auf
    (297.5, "kaaba_building", "zoom_in"),      # s6a Bau der Kaaba
    (330.3, "noah", "zoom_in"),                # s6b Noah „Ist das die Kaaba?“
    (333.9, "kaaba_building", "zoom_out"),     # s6c „das ist die Kaaba in Mekka“
    (339.2, "prayer_rug_sunrise", "zoom_in"),  # s6c „beten … in ihre Richtung. Auch wir“
    (348.2, "kinder_schlafen", "zoom_out"),    # s7a „Oh, sie schlafen schon“ (H12)
    (381.3, "oma_window_night", "zoom_out"),   # s7b
]


def to_new(t):
    """Roh-Zeit -> Zeit nach den Schnitten."""
    removed = 0.0
    for a, b in AUDIO_CUTS:
        if t >= b:
            removed += b - a
        elif t > a:
            return round(a - removed, 3)
    return round(t - removed, 3)


def main():
    segs = []
    for i, (s, img, motion) in enumerate(CUTS):
        ns = to_new(s)
        ne = to_new(CUTS[i + 1][0]) if i + 1 < len(CUTS) else "audio"
        length = (ne - ns) if ne != "audio" else 30
        seg = {"image": IMG[img], "start": ns, "end": ne, "motion": motion,
               "amount": round(min(0.14, 0.04 + 0.004 * length), 3), "label": img}
        if img in CROP:
            seg["crop"] = CROP[img]
        segs.append(seg)
    job = {
        "name": "folge08_ismail_v3",
        "audio": "https://storage.orshot.com/cloud/w-12325/renders/audio/"
                 "boa_folge08_erzaehlung_komplett_rohmp3-UsgRAfWl6AV.mp3",
        "audio_cuts": AUDIO_CUTS,
        "crossfade": 0.6, "fade_in": 0.8, "fade_out": 1.0, "tail_hold": 6.0,  # 5 s Endbild nach dem letzten Wort + 1 s Abblende (Notion-Plan)
        "loudness": -14,
        "segments": segs,
    }
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "jobs", "folge08_ismail_v3.json")
    with open(out, "w") as f:
        json.dump(job, f, indent=1, ensure_ascii=False)
    # Pruef-Transkript des geschnittenen Tons (H30: Schnitte hoeren/lesen)
    print(out, len(segs), "Abschnitte; neue Laenge ca.",
          round(421.28 - sum(b - a for a, b in AUDIO_CUTS), 2), "s")
    for sg in segs:
        print(f"{sg['start']:8.2f}  {sg['label']}")


if __name__ == "__main__":
    main()
