"""Audio tracks (ar/en/fr/tr/bs/sq) for the TV compilation, same length as the video.
Cards/intro/outro keep their own soft night ambience; every episode gets its published dubbed track
(meta/tv/dub_tracks_selected.json – latest version whose report length equals the published video),
padded/trimmed to the exact episode length so the languages never drift.
Usage: python3 tools/tv_dub_tracks.py <out_dir with list.txt + parts> <dub_dir with NN_xx.mp3>
"""
import os, re, subprocess, sys

LANGS = ['ar', 'en', 'fr', 'tr', 'bs', 'sq']


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'csv=p=0', p]).decode())


def main(out, dub):
    parts = [l.split("'")[1] for l in open(os.path.join(out, 'list.txt')) if l.startswith('file')]
    video = os.path.join(out, 'boa_tv_compilation_teil1_01-16_de.mp4')
    total = dur(video)
    tmp = os.path.join(out, 'atmp')
    os.makedirs(tmp, exist_ok=True)
    # card ambience once (shared by all languages)
    for p in parts:
        b = os.path.basename(p)
        if b.startswith('c'):
            w = os.path.join(tmp, b + '.wav')
            if not os.path.exists(w):
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p, '-vn', '-ac', '2', '-ar', '48000', w], check=True)
    for L in LANGS:
        seq = []
        for p in parts:
            b = os.path.basename(p)
            m = re.match(r'e(\d\d)\.mp4', b)
            if not m:
                seq.append(os.path.join(tmp, b + '.wav'))
                continue
            n = m.group(1)
            d = dur(p)
            w = os.path.join(tmp, f'{n}_{L}.wav')
            if not os.path.exists(w):
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(dub, f'{n}_{L}.mp3'),
                                '-af', f'aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{d:.4f}',
                                '-ac', '2', '-ar', '48000', w], check=True)
            seq.append(w)
        lst = os.path.join(tmp, f'list_{L}.txt')
        with open(lst, 'w') as f:
            f.writelines(f"file '{s}'\n" for s in seq)
        o = os.path.join(out, f'boa_tv_teil1_audio_{L}.mp3')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-af', f'apad,atrim=0:{total:.4f}', '-c:a', 'libmp3lame', '-b:a', '112k', '-ar', '48000', o],
                       check=True)
        print(L, round(dur(o), 2), 'video', round(total, 2), round(os.path.getsize(o) / 1048576, 1), 'MB', flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
