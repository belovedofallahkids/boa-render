#!/usr/bin/env python3
"""Schnittlisten Folgen 10–14 aus dem Wort-Transkript (faster-whisper) -> jobs/folgeNN_<name>_v1.json.

Ton: ElevenLabs-Composition vom 16.10.2026 (ein Take pro Segment), Orshot-Audio 250, 251, 255, 256, 257.
Bildplan: Notion-Seiten der Folgen, Abschnitt 6 (Szenen), Bilder alle geprueft (Cloudflare FLUX + Ersatzbilder v2).

Vorgehen:
1. Skript-Woerter (ohne [Regie]-Tags) werden mit den Transkript-Woertern abgeglichen (difflib).
2. Jeder Schnitt liegt in der Mitte der Pause vor seinem ersten Wort.
3. Ein Schnitt ist entweder ein ganzes Segment (s1a ...) oder beginnt an einem Satz im Segment ("s2a|Doch dann kam").
Regeln: Kinderbild nur auf der eigenen Zeile (H9), kinder_schlafen erst ab "sie schlafen schon" (H12),
dream_sky nur Zoom 0.04 (Sonne + Mond bleiben sichtbar), Endbild 5 s + 1 s Abblende.
"""
import difflib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = "https://storage.orshot.com/cloud/w-12325/renders/brand_assets/"
A = "https://storage.orshot.com/cloud/w-12325/renders/audio/"

IMG = {
    "master_A_buch": "boa_master_A_buchpng-uoxAhZwWy9D.png",
    "ilyas": "boa_ilyas_allein_offizielljpg-OQtwI3xapxd.jpeg",
    "noah": "boa_noah_allein_offizielljpg-YwfUilEIZQs.jpeg",
    "kinder_schlafen": "boa_kinder_schlafen_offizielljpg-aevRtHZ0V3q.jpeg",
    "oma_window_night": "boa_oma_window_night_offizielljpg-i61gAYOmKJ9.jpeg",
    # wiederverwendet
    "tree_of_lights": "boa_folge09_tree_of_lightsjpg-dz4ohqXPhph.jpeg",
    "prayer_rug_sunrise": "boa_folge09_prayer_rug_sunrisejpg-Sdao2hRcTap.jpeg",
    "sunrise_hope": "boa_folge09_sunrise_hope_cfjpg-jm9njyyaEFi.jpeg",
    # Folge 10
    "desert_camp": "boa_folge10_desert_camp_cfjpg-UoE7PPTTF15.jpeg",
    "dream_sky": "boa_folge10_dream_sky_compositepng-wgS30bDF0sJ.png",
    "evening_path_empty": "boa_folge10_evening_path_empty_cfjpg-oXbVS4FYRwr.jpeg",
    "seedling_patience": "boa_folge10_seedling_patience_cfjpg-NNkXInQAWCl.jpeg",
    "lamp_seasons": "boa_folge10_lamp_seasons_cfjpg-Kh4BcvtNNsb.jpeg",
    "search_road": "boa_folge10_search_road_cfjpg-1X1c5lYUXW3.jpeg",
    "old_staff_lamp": "boa_folge10_old_staff_lamp_cfjpg-Qsjk2o5uTiR.jpeg",
    # Folge 11
    "well_night": "boa_folge11_well_night_cfjpg-kiluIu8ASLu.jpeg",
    "caravan_well": "boa_folge11_caravan_well_cfjpg-vbBoOhOpWhb.jpeg",
    "egypt_house": "boa_folge11_egypt_house_cfjpg-LpuhlomtG0v.jpeg",
    "palace_door": "boa_folge11_palace_door_cfjpg-SvCdXm2zM2S.jpeg",
    "prison_window": "boa_folge11_prison_window_cfjpg-FmYjMZjZcLY.jpeg",
    "seven_cows": "boa_folge11_seven_cows_v2_cfpng-TcvWRf2a1ha.jpeg",
    "wheat_ears": "boa_folge11_wheat_ears_cfjpg-r6OVxR0HWvD.jpeg",
    "granary_full": "boa_folge11_granary_full_cfjpg-kgEfDo5QjhA.jpeg",
    "caravan_egypt": "boa_folge11_caravan_egypt_cfjpg-lCD24SA1QEJ.jpeg",
    "shirt_light": "boa_folge11_shirt_light_v2_cfpng-53n0wh6Xal3.jpeg",
    "family_reunion_hall": "boa_folge11_family_reunion_hall_v2_cfpng-Iit0kuCmycu.jpeg",
    # Folge 12
    "green_home_valley": "boa_folge12_green_home_valley_cfjpg-2KIOSL5qbkS.jpeg",
    "wilted_garden": "boa_folge12_wilted_garden_v2_cfpng-B0AtuCzDmMS.jpeg",
    "empty_sickbed": "boa_folge12_empty_sickbed_v2_cfpng-RwaTw6ucvNo.jpeg",
    "lantern_water_night": "boa_folge12_lantern_water_night_cfjpg-wW2Jd4p24Jg.jpeg",
    "empty_path_visitors": "boa_folge12_empty_path_visitors_cfjpg-Z8AV2NSepK7.jpeg",
    "night_dua_sky": "boa_folge12_night_dua_sky_cfjpg-JhW0kGjZT4G.jpeg",
    "spring_burst": "boa_folge12_spring_burst_cfjpg-uraDbxBUjHr.jpeg",
    "blooming_garden_rainbow": "boa_folge12_blooming_garden_rainbow_cfjpg-yew1PuByn6p.jpeg",
    "golden_locusts": "boa_folge12_golden_locusts_cfjpg-oVcS4nmwZky.jpeg",
    # Folge 13
    "madyan_market": "boa_folge13_madyan_market_cfjpg-U6TqBmK8gaj.jpeg",
    "scale_tilted": "boa_folge13_scale_tilted_cfjpg-idWOpHxt1sf.jpeg",
    "scale_balanced": "boa_folge13_scale_balanced_cfjpg-WTKCSlcOah2.jpeg",
    "blocked_road": "boa_folge13_blocked_road_v2_cfpng-TEldLP2eTm0.jpeg",
    "madyan_town_evening": "boa_folge13_madyan_town_evening_cfjpg-MTSy561m5fL.jpeg",
    "storm_far": "boa_folge13_storm_far_v2_cfpng-3J6JqWml881.jpeg",
    "empty_town_morning": "boa_folge13_empty_town_morning_cfjpg-feyzGSn83IZ.jpeg",  # nur mit Zuschnitt
    "grain_pile_market": "boa_folge13_grain_pile_market_cfjpg-sjMPUYs8fSQ.jpeg",
    # Folge 14
    "pharaoh_palace": "boa_folge14_pharaoh_palace_cfpng-oFXrlDe69VZ.jpeg",
    "nile_chest": "boa_folge14_nile_chest_cfpng-1BMpUPRT1el.jpeg",
    "desert_road_long": "boa_folge14_desert_road_long_v2_cfpng-QoaHOKjHuJ0.jpeg",
    "madyan_well_sheep": "boa_folge14_madyan_well_sheep_cfpng-deCvWouH7wE.jpeg",
    "mountain_fire": "boa_folge14_mountain_fire_cfpng-db2MNxfO5Uh.jpeg",
    "holy_valley_light": "boa_folge14_holy_valley_light_cfpng-SP1L3TKpszw.jpeg",
    "staff_glow": "boa_folge14_staff_glow_cfpng-mFOV9KAMZzG.jpeg",
    "ropes_courtyard": "boa_folge14_ropes_courtyard_cfpng-BG0SssMqdXt.jpeg",
    "night_desert_departure": "boa_folge14_night_desert_departure_v2_cfpng-aViiCz3X56Z.jpeg",
    "sea_split": "boa_folge14_sea_split_cfpng-xQ3N5CS0s7Z.jpeg",
    "iftar_dates": "boa_folge14_iftar_dates_cfpng-NM0ylhuIopQ.jpeg",
}
CROP = {"empty_town_morning": [0.25, 0.25, 0.75]}  # Kuppel-aehnliche Form oben links wegschneiden (Notion 13)
KIDS = {"ilyas", "noah"}

EPISODES = json.load(open(os.path.join(ROOT, "tools", "folgen10_14_skripte.json")))


def words(text):
    text = re.sub(r"\[[^\]]*\]", " ", text)
    return [w for w in (re.sub(r"[^a-zäöüß]", "", t.lower()) for t in text.split()) if w]


def load_transcript(name):
    rows = []
    for line in open(os.path.join(ROOT, "out", "transcripts", name + ".txt")):
        p = line.split(None, 2)
        if len(p) == 3:
            w = re.sub(r"[^a-zäöüß]", "", p[2].lower())
            if w:
                rows.append((float(p[0]), float(p[1]), w))
    return rows


def build(key):
    ep = EPISODES[key]
    seg_text = ep["segments"]  # {id: text}
    order = list(seg_text)
    sw, owner = [], []  # script words, (seg id, index in seg)
    for sid in order:
        for i, w in enumerate(words(seg_text[sid])):
            sw.append(w)
            owner.append((sid, i))
    tr = load_transcript(ep["transcript"])
    tw = [t[2] for t in tr]
    sm = difflib.SequenceMatcher(a=sw, b=tw, autojunk=False)
    match = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            match[a + k] = b + k
    ratio = len(match) / len(sw)

    def word_index(sid, phrase=None):
        seg_words = [k for k, o in enumerate(owner) if o[0] == sid]
        start = seg_words[0]
        if phrase:
            pw = words(phrase)
            sub = [sw[k] for k in seg_words]
            for j in range(len(sub) - len(pw) + 1):
                if sub[j:j + len(pw)] == pw:
                    start = seg_words[j]
                    break
            else:
                raise SystemExit(f"{key}: Satz nicht gefunden: {sid}|{phrase}")
        # erstes Wort ab hier, das im Transkript gefunden wurde
        for k in range(start, start + 6):
            if k in match:
                return match[k], k - start
        raise SystemExit(f"{key}: kein Zeitpunkt fuer {sid}|{phrase}")

    cuts, report = [], []
    for item in ep["plan"]:
        at, img, motion = item[0], item[1], item[2]
        sid, _, phrase = at.partition("|")
        ti, skipped = word_index(sid, phrase or None)
        if skipped:  # erste Woerter falsch erkannt: zurueck zur groessten Pause davor
            cands = [k for k in range(max(1, ti - skipped), ti + 1)]
            gaps = [(tr[k][0] - tr[k - 1][1], k) for k in cands]
            best = max(gaps)
            ti = best[1] if best[0] >= 0.15 else cands[0]
        t0 = tr[ti][0]
        prev_end = tr[ti - 1][1] if ti > 0 else 0.0
        cut = 0.0 if not cuts else round((prev_end + t0) / 2, 2)
        cuts.append((cut, img, motion, at))
        report.append(f"{cut:7.2f}  {at:40s} {img:22s} {motion}  ('{tr[ti][2]}'{', +%d' % skipped if skipped else ''})")
    segs = []
    for i, (s, img, motion, at) in enumerate(cuts):
        e = cuts[i + 1][0] if i + 1 < len(cuts) else "audio"
        length = (e - s) if e != "audio" else 40
        if img == "dream_sky":
            amount = 0.04
        elif img in KIDS:
            amount = 0.05
        else:
            amount = round(min(0.13, 0.04 + 0.004 * length), 3)
        seg = {"image": B + IMG[img], "start": s, "end": e, "motion": motion, "amount": amount,
               "label": img, "script": at}
        if img in CROP:
            seg["crop"] = CROP[img]
        segs.append(seg)
    # Pruefungen
    for i in range(1, len(segs)):
        assert segs[i]["label"] != segs[i - 1]["label"], f"{key}: zweimal {segs[i]['label']} hintereinander"
        assert segs[i]["end"] == "audio" or segs[i]["end"] - segs[i]["start"] > 1.0, f"{key}: zu kurz {segs[i]}"
    for s in segs:
        if s["label"] in KIDS:
            line = ep["segments"][s["script"].split("|")[0]]
            assert "[childlike voice]" in line, f"{key}: Kinderbild nicht auf Kinderzeile {s['script']}"
    job = {"name": ep["job"], "audio": A + ep["audio"], "crossfade": 0.6, "fade_in": 0.8, "fade_out": 1.0,
           "tail_hold": 6.0, "loudness": -14, "segments": segs}
    with open(os.path.join(ROOT, "jobs", ep["job"] + ".json"), "w") as f:
        json.dump(job, f, indent=1, ensure_ascii=False)
    print(f"== {ep['job']}: {len(segs)} Abschnitte, Abgleich Skript/Transkript {ratio:.1%}")
    print("\n".join(report))


if __name__ == "__main__":
    for k in (sys.argv[1:] or list(EPISODES)):
        build(k)
