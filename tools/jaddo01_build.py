"""«اسأل جدّو حبّوب» – الحلقة 1: مونتاج الصوت والصورة (مجاني، GitHub Actions).

1) يقرأ المقاطع الأصلية من الإصدار jaddo01_src (src/ محلياً).
2) faster-whisper (medium) على كل مقطع ← محاذاة الكلمات مع نص كل جملة ← قصّ الجمل عند السكتات.
3) ترتيب الجمل حسب النص (حوار متداخل بين حبّوب والأطفال) + الاستعاذة قبل كل تلاوة،
   والبسملة بعد الاستعاذة فقط عند أوّل سورة (التين). لا «صدق الله العظيم».
4) يكتب narration.wav + job للصور، ثم يستدعي render.render_job (نفس محرك القناة).
تقرير المحاذاة: out/jaddo01_ar_v1/align_report.json
"""
import difflib, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
WORK = os.path.join(ROOT, "work", "jaddo01")
NAME = os.environ.get("JADDO_NAME") or "jaddo01_ar_v2"
os.makedirs(WORK, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "render"))

V1 = "أفلا ينظرون إلى الإبل كيف خلقت وإلى السماء كيف رفعت وإلى الجبال كيف نصبت وإلى الأرض كيف سطحت"
V2 = "إن في خلق السماوات والأرض واختلاف الليل والنهار لآيات لأولي الألباب"
V3 = "والتين والزيتون وطور سينين وهذا البلد الأمين لقد خلقنا الإنسان في أحسن تقويم"
V4 = "أفرأيتم ما تحرثون أأنتم تزرعونه أم نحن الزارعون"

# clip -> pieces in the order they were recorded
CLIPS = {
 "c1a": [("n1", "جدو جدو وجدت كنزا"), ("i1", "كنز هذه حبة صغيرة يا نوح"), ("n2", "سر ما هو يا جدو قل لي"), ("k1", "تحدي مقبول")],
 "c1b": [("j1", "هممم لا يا إلياس هذه ليست مجرد حبة في داخلها سر كبير كبير جدا"),
         ("j2", "سأخبركما لكن في آخر حكايتنا ومن يدري ربما تكتشفانه أنتما قبلي")],
 "c2a": [("j3", "تعاليا نلعب لعبة أنا أشير إلى شيء وأنتما تنظران وتفكران اسمها من صنع هذا"),
         ("j4", "الناس يصنعون وردة من بلاستيك لكنها لا تكبر ولا تفوح رائحتها ولا تتفتح في الصباح")],
 "c2b": [("i2", "انظر يا نوح النملة تحمل شيئا أكبر منها"), ("n3", "يا لها من بطلة لو كنت أنا نملة لحملت كل الحلوى"),
         ("n4", "جدو هل يستطيع أحد من الناس أن يصنع وردة حقيقية")],
 "c3a": [("n5", "جدو من خلق كل هذا النملة والماء والورد"), ("i3", "لكن يا جدو نحن لا نرى الله فكيف نعرف أنه هو الذي خلقها"),
         ("i4", "أقول أحد رسمها"), ("n6", "لا طبعا القلم لا يمشي وحده")],
 "c3b": [("j5", "الله يا حبيبي الله هو الخالق هو الذي خلق النملة وأنزل الماء ولون الورود"),
         ("j6", "سؤال رجل كبير يا إلياس قل لي لو رأيت رسمة جميلة على الحائط ماذا تقول"),
         ("j7", "وهل يمكن أن ترسم الرسمة نفسها وحدها"),
         ("j8", "وهذه الحديقة أجمل من كل الرسومات وكل شيء فيها كأنه يقول لنا الله خلقني")],
 "c4a": [("j9", "والله نفسه يدعونا في القرآن أن ننظر ونتفكر اسمعا"), ("V1", V1),
         ("j10", "الجمل والسماء والجبال والأرض الله يقول لنا انظروا كيف خلقتها وهل تعرفان النبي صلى الله عليه وسلم كان يقوم في آخر الليل فينظر إلى السماء ويقرأ"),
         ("V2", V2),
         ("j11", "رواه البخاري والله مدح الذين يتفكرون في خلقه يعني الآن ونحن ننظر إلى النملة والورد نحن نفعل شيئا يرضي الله"),
         ("j12", "إذا تفكرت وقلت سبحان الله نعم")],
 "c4b": [("n7", "الجمل مثل جمل قرموشة الصغير"), ("n8", "يعني النظر إلى النملة عبادة")],
 "c5a": [("n9", "جدو وشجرة التين هذه هل ذكرها الله في القرآن"), ("n10", "التين في القرآن"), ("i5", "والزيتون أيضا"),
         ("n11", "يعني أنا أيضا أحسن تقويم"), ("k2", "الحمد لله")],
 "c5b": [("j13", "هناك سورة اسمها سورة التين تبدأ هكذا"), ("V3", V3),
         ("j14", "وفي الآية الرابعة يقول الله إنه خلق الإنسان في أحسن تقويم يعني في أحسن صورة وأجمل خلقة"),
         ("j15", "أنت وإلياس وكل إنسان فماذا نقول لله")],
 "c6a": [("n12", "جدو نسيت السر"), ("n13", "هذه الصغيرة تصير هذه الكبيرة"), ("i6", "يعني الله هو الذي ينبتها")],
 "c6b": [("j16", "لم أنس ارفعا رأسيكما إلى الأعلى أعلى أعلى"),
         ("j17", "الشجرة الكبيرة التي نجلس في ظلها كانت يوما ما بذرة صغيرة مثل التي في يدك"),
         ("j18", "نحن نضعها في التراب ونسقيها لكن من يخرج منها الشجرة اسمعا ماذا قال الله"), ("V4", V4),
         ("j19", "أحسنت هذا هو السر")],
 "c7a": [("j20", "مهمتكما اليوم كل واحد يبحث عن ثلاثة أشياء جميلة خلقها الله وعند كل واحد يقول سبحان الله"),
         ("j21", "الله هو الخالق وكل شيء جميل يذكرنا به سبحان الله"),
         ("j22", "آه هذا سؤال الغد وجوابه في سورة قصيرة جدا أظنكما تحفظانها من زمان")],
 "c7b": [("n14", "واحد النملة سبحان الله"), ("i7", "اثنان الشمس سبحان الله"), ("k3", "ثلاثة شجرتنا سبحان الله"),
         ("k4", "الحمد لله الذي جعلنا مسلمين نعرف ربنا ونحبه"),
         ("n15", "جدو سؤال أخير الله واحد أم أكثر من واحد"), ("k5", "أي سورة")],
}

# scene order: (scene, [piece ids / ISTI / BASM], images [(first piece id, image, motion)])
SCENES = [
 (1, ["n1", "i1", "j1", "n2", "j2", "k1"], [("n1", "img_kanz", "zoom_in")]),
 (2, ["j3", "i2", "n3", "n4", "j4"], [("j3", "img_namla", "zoom_in"), ("n4", "img_nafura", "pan_right")]),
 (3, ["n5", "j5", "i3", "j6", "i4", "j7", "n6", "j8"], [("n5", "img_hadiqa", "zoom_in"), ("j8", "img_nafura", "zoom_out")]),
 (4, ["j9", "ISTI", "V1", "n7", "j10", "ISTI", "V2", "j11", "n8", "j12"],
     [("j9", "img_hadiqa", "zoom_out"), ("j10", "img_tina", "pan_up"), ("j11", "img_namla", "zoom_out")]),
 (5, ["n9", "j13", "ISTI", "BASM", "V3", "n10", "i5", "j14", "n11", "j15", "k2"],
     [("n9", "img_tina", "pan_down"), ("j14", "img_hadiqa", "zoom_in")]),
 (6, ["n12", "j16", "j17", "n13", "j18", "ISTI", "V4", "i6", "j19"],
     [("n12", "img_tina", "pan_up"), ("n13", "img_bedhra", "zoom_in")]),
 (7, ["j20", "n14", "i7", "k3", "k4", "j21", "n15", "j22", "k5"], [("j20", "img_ghurub", "zoom_out")]),
]

GAP_TURN, GAP_RELIG, GAP_SCENE, HEAD = 0.35, 0.6, 1.1, 0.6
SR = 48000


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-2000:])
    return p.stdout + p.stderr


def norm(w):
    w = re.sub(r"[ً-ْٰـ]", "", w)
    w = re.sub(r"[إأآٱ]", "ا", w).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    return re.sub(r"[^ء-ي0-9]", "", w)


def to_wav(src, dst):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", str(SR), dst])
    return dst


def dur(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())


def silences(wav, th="-38dB", d=0.18):
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af", f"silencedetect=n={th}:d={d}", "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    if len(en) < len(st):
        en.append(dur(wav))
    return list(zip(st, en))


def snap(t, lo, hi, sil):
    """middle of the longest silence overlapping [lo, hi]; else t."""
    best, bl = t, 0.0
    for a, b in sil:
        a2, b2 = max(a, lo), min(b, hi)
        if b2 - a2 > bl:
            bl, best = b2 - a2, (a2 + b2) / 2
    return best


def voiced(wav, sil):
    """[first sound, last sound] of a file."""
    total = dur(wav)
    s = sil[0][1] if sil and sil[0][0] <= 0.02 else 0.0
    e = sil[-1][0] if sil and sil[-1][1] >= total - 0.02 else total
    return max(0, s - 0.05), min(total, e + 0.12)


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("WHISPER", "medium"), device="cpu", compute_type="int8")
    pieces, report = {}, {}
    for clip, plist in CLIPS.items():
        wav = to_wav(os.path.join(SRC, clip + ".mp3"), os.path.join(WORK, clip + ".wav"))
        total, sil = dur(wav), silences(wav)
        segs, _ = model.transcribe(wav, language="ar", word_timestamps=True, beam_size=5, vad_filter=False)
        tw = [(norm(w.word), w.start, w.end, w.word) for s in segs for w in s.words if norm(w.word)]
        exp, owner = [], []
        for pi, (pid, text) in enumerate(plist):
            for w in text.split():
                if norm(w):
                    exp.append(norm(w)); owner.append(pi)
        sm = difflib.SequenceMatcher(None, exp, [t[0] for t in tw], autojunk=False)
        m = {}
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                m[a + k] = b + k
        first, last = {}, {}
        for ei, ti in m.items():
            pi = owner[ei]
            first[pi] = min(first.get(pi, 10 ** 9), ti)
            last[pi] = max(last.get(pi, -1), ti)
        # boundaries
        cuts = [0.0]
        for pi in range(len(plist) - 1):
            if pi in last and pi + 1 in first:
                e, s = tw[last[pi]][2], tw[first[pi + 1]][1]
                cuts.append(snap((e + s) / 2, min(e, s) - 0.35, max(e, s) + 0.35, sil))
            else:
                cuts.append(None)
        cuts.append(total)
        # fill unknown boundaries with the longest silence between known neighbours
        for k in range(1, len(cuts) - 1):
            if cuts[k] is None:
                lo = max(c for c in cuts[:k] if c is not None)
                hi = min(c for c in cuts[k + 1:] if c is not None)
                cuts[k] = snap((lo + hi) / 2, lo + 0.3, hi - 0.3, sil)
        rep = []
        for pi, (pid, text) in enumerate(plist):
            a, b = cuts[pi], cuts[pi + 1]
            out = os.path.join(WORK, pid + ".wav")
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                 "-c:a", "pcm_s16le", out])
            s2 = silences(out)
            va, vb = voiced(out, s2)
            trimmed = os.path.join(WORK, pid + "_t.wav")
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", out, "-ss", f"{va:.3f}", "-to", f"{vb:.3f}",
                 "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse", "-c:a", "pcm_s16le", trimmed])
            pieces[pid] = trimmed
            heard = " ".join(t[3].strip() for t in tw if a - 0.05 <= t[1] < b)
            ratio = difflib.SequenceMatcher(None, [norm(x) for x in text.split()], [norm(x) for x in heard.split()]).ratio()
            rep.append({"id": pid, "from": round(a, 2), "to": round(b, 2), "len": round(vb - va, 2),
                        "expected": text, "heard": heard, "match": round(ratio, 2)})
        report[clip] = rep
        print(clip, [(r["id"], r["match"]) for r in rep], flush=True)

    # religious inserts
    for key, src in (("ISTI", "istiadha1"), ("BASM", "basmala1")):
        wav = to_wav(os.path.join(SRC, src + ".mp3"), os.path.join(WORK, src + ".wav"))
        sil = silences(wav, d=0.45)
        va = sil[0][1] if sil and sil[0][0] <= 0.02 else 0.0
        # first sound block only (basmala clip also holds a second line that is NOT used)
        nxt = [a for a, b in sil if a > va + 0.8]
        vb = nxt[0] if nxt else dur(wav)
        out = os.path.join(WORK, key + ".wav")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, "-ss", f"{max(0, va - 0.05):.3f}",
             "-to", f"{vb + 0.1:.3f}", "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.05,areverse", "-c:a", "pcm_s16le", out])
        pieces[key] = out
        report[key] = {"source": src, "from": round(va, 2), "to": round(vb, 2)}

    # timeline
    seq, t, starts, scene_start = [], HEAD, {}, {}
    silence = os.path.join(WORK, "sil_%d.wav")
    prev = None
    for scene, order, _imgs in SCENES:
        if prev is not None:
            t += GAP_SCENE - GAP_TURN
        scene_start[scene] = t
        for pid in order:
            if prev is not None:
                g = GAP_RELIG if (pid in ("ISTI", "BASM", "V1", "V2", "V3", "V4") or prev in ("ISTI", "BASM", "V1", "V2", "V3", "V4")) else GAP_TURN
                seq.append(("gap", g)); t += g
            if pid not in starts:
                starts[pid] = t
            d = dur(pieces[pid])
            seq.append(("clip", pieces[pid])); t += d
            prev = pid
    # build narration: concat list with generated silences
    lst, k = [], 0
    lst.append(("gap", HEAD))
    full = [("gap", HEAD)] + seq
    files = []
    for kind, v in full:
        if kind == "gap":
            p = silence % k; k += 1
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono",
                 "-t", f"{v:.3f}", "-c:a", "pcm_s16le", p])
            files.append(p)
        else:
            files.append(v)
    with open(os.path.join(WORK, "concat.txt"), "w") as f:
        for p in files:
            f.write(f"file '{p}'\n")
    narration = os.path.join(WORK, "narration.wav")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i",
         os.path.join(WORK, "concat.txt"), "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", narration])
    total = dur(narration)

    # picture segments
    marks = []
    for scene, order, imgs in SCENES:
        for pid, img, motion in imgs:
            st = scene_start[scene] if pid == order[0] else starts[pid] - 0.25
            marks.append((st, img, motion))
    marks[0] = (0.0,) + marks[0][1:]
    segs = []
    for i, (st, img, motion) in enumerate(marks):
        en = marks[i + 1][0] if i + 1 < len(marks) else "audio"
        segs.append({"image": "file://" + os.path.join(SRC, img + ".png"), "start": round(st, 3),
                     "end": en if en == "audio" else round(en, 3), "motion": motion, "amount": 0.07, "label": img})
    alt = ["zoom_in", "pan_right", "zoom_out", "pan_left", "pan_up"]
    split, aud_total = [], total + 3
    for k, sg in enumerate(segs):
        a = sg["start"]; b = aud_total if sg["end"] == "audio" else sg["end"]
        n = max(1, int(round((b - a) / 9.0)))
        for j in range(n):
            s2 = dict(sg, start=round(a + (b - a) * j / n, 3), end=round(a + (b - a) * (j + 1) / n, 3))
            if j:
                s2["motion"] = alt[(alt.index(sg["motion"]) + j) % len(alt)] if sg["motion"] in alt else alt[j % 5]
            split.append(s2)
    split[-1]["end"] = "audio"
    segs = split
    job = {"name": NAME, "audio": "file://" + narration, "crossfade": 0.8, "fade_in": 0.8, "fade_out": 1.5,
           "loudness": -14, "tail_hold": 3, "segments": segs}
    outdir = os.path.join(ROOT, "out", NAME)
    os.makedirs(outdir, exist_ok=True)
    json.dump({"pieces": report, "starts": {k: round(v, 2) for k, v in starts.items()}, "narration_s": round(total, 2),
               "job": job}, open(os.path.join(outdir, "align_report.json"), "w"), ensure_ascii=False, indent=1)
    import render
    os.makedirs(render.CACHE, exist_ok=True)
    if os.environ.get("PARALLAX", "1") == "1":
        # H: لا صور ثابتة أبداً – كل لقطة حركة كاميرا 2.5D (عمق) مجانية
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import parallax
        for s_ in job["segments"]:
            parallax._depth(s_["image"][7:])
        render.render_clip = parallax.render_clip
    raw = json.dumps(job, sort_keys=True).encode()
    st = render.render_job(job, hashlib.sha1(raw).hexdigest(), outdir)
    # also publish the narration (for dubbing / reuse)
    mp3 = os.path.join(WORK, NAME + "_narration.mp3")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", narration, "-b:a", "192k", mp3])
    render.publish(NAME, [mp3, os.path.join(outdir, "align_report.json")])
    json.dump(st, open(os.path.join(outdir, "status.json"), "w"), indent=2, ensure_ascii=False)
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
