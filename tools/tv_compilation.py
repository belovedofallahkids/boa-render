"""TV compilation (owner 14.11.2026): all 16 episodes in one long video, no music.
Creative element: "Kette der Propheten" – between episodes a 5 s card where a chain of 16 lanterns
lights up one by one, so children see the order of the prophets from Adam onwards.
Usage: python3 tools/tv_compilation.py <episodes_dir> <out_dir>
episodes_dir holds 01.mp4 … 16.mp4 (published versions).
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, 'assets/fonts/Poppins-ExtraBold.ttf')
FONT_B = os.path.join(ROOT, 'assets/fonts/Poppins-Bold.ttf')
AMB = os.path.join(ROOT, 'assets/sfx/amb_night_room.mp3')
NAMES = ['ADAM', 'IDRIS', 'NUH', 'HUD', 'SALIH', 'IBRAHIM', 'LUT', 'ISMAIL', 'ISHAQ', 'YAQUB',
         'YUSUF', 'AYYUB', 'SHUAIB', 'MUSA', 'HARUN', 'DHUL-KIFL',
         'DAWUD', 'SULAIMAN', 'ILYAS', 'AL-YASA', 'YUNUS', 'ZAKARIYA', 'YAHYA', 'ISA', 'MUHAMMAD']  # 17-25 still coming
DONE = 16
AR = ['آدم', 'إدريس', 'نوح', 'هود', 'صالح', 'إبراهيم', 'لوط', 'إسماعيل', 'إسحاق', 'يعقوب', 'يوسف', 'أيوب', 'شعيب',
      'موسى', 'هارون', 'ذو الكفل', 'داود', 'سليمان', 'إلياس', 'اليسع', 'يونس', 'زكريا', 'يحيى', 'عيسى', 'محمد']
FONT_AR = os.path.join(ROOT, 'assets/fonts/NotoKufiArabic.ttf')
# story scene (frame of the published episode, no text) for the card; times checked on a contact sheet 14.11.2026
SCENE_T = {1: 33, 2: 15, 3: 15, 4: 15, 5: 111, 6: 351, 7: 160, 8: 45, 9: 160, 10: 100, 11: 70, 12: 45, 13: 100,
           14: 100, 15: 100, 16: 40.5}
SCENE_DIR = None
GOLD = (255, 205, 90)


def thumb(n):
    p = os.path.join(SCENE_DIR, f'scene_{n:02d}.jpg')
    if not os.path.exists(p):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(SCENE_T[n]), '-i',
                        os.path.join(SCENE_DIR, f'e{n:02d}.mp4'), '-frames:v', '1', '-q:v', '2', p], check=True)
    return Image.open(p).convert('RGB')


def ar_text(d, xy_center, txt, size, fill, anchor='mm'):
    f = ImageFont.truetype(FONT_AR, size)
    d.text(xy_center, txt, font=f, fill=fill, anchor=anchor, direction='rtl', language='ar')


def sky():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(12 + 18 * t), int(18 + 30 * t), int(52 + 50 * t)))
    import random
    rnd = random.Random(7)
    for _ in range(260):
        x, y, r = rnd.randrange(W), rnd.randrange(int(H * 0.8)), rnd.choice([1, 1, 1, 2, 2, 3])
        c = rnd.randrange(150, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, min(255, c + 20)))
    # crescent
    m = Image.new('L', (220, 220), 0)
    md = ImageDraw.Draw(m)
    md.ellipse([10, 10, 210, 210], fill=255)
    md.ellipse([70, -10, 250, 170], fill=0)
    glow = Image.new('RGB', (220, 220), (255, 236, 170))
    img.paste(glow, (1640, 60), m)
    return img


SKY = None
CHAIN_Y = 930
XS = [int(110 + i * (W - 220) / 24) for i in range(25)]


def lantern(d, x, y, state, pulse=0.0):
    """state 0 = dim, 1 = lit, 2 = current"""
    if state == 0:
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(70, 80, 120), outline=(120, 130, 170), width=2)
    elif state == 1:
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=GOLD, outline=(255, 240, 200), width=2)
    else:
        r = 24 + 5 * pulse
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 225, 130), outline=(255, 255, 230), width=4)


def frame(cur, t, dur, mode):
    """cur = 1..16 (episode about to start); mode 'card' | 'intro' | 'outro'"""
    img = SKY.copy()
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(img)
    # chain line
    if mode == 'intro':
        lit_upto = min(DONE, int(t / (dur * 0.8) * DONE + 0.0001))  # lights sweep over the finished ones
        cur_i = None
    elif mode == 'outro':
        lit_upto, cur_i = DONE, None
    else:
        lit_upto, cur_i = cur - 1, cur - 1
    d.line([(XS[0], CHAIN_Y), (XS[-1], CHAIN_Y)], fill=(90, 100, 150), width=4)
    if lit_upto > 0:
        end = XS[min(lit_upto, DONE) - 1]
        d.line([(XS[0], CHAIN_Y), (end, CHAIN_Y)], fill=GOLD, width=6)
    if cur_i is not None and cur_i > 0:  # light travels from previous to current in first 1.2 s
        k = min(1.0, t / 1.2)
        x0, x1 = XS[cur_i - 1], XS[cur_i]
        d.line([(x0, CHAIN_Y), (int(x0 + (x1 - x0) * k), CHAIN_Y)], fill=GOLD, width=6)
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    for i, x in enumerate(XS):
        if cur_i is not None and i == cur_i:
            st = 2 if t >= (1.2 if cur_i > 0 else 0) else 0
        else:
            st = 1 if i < lit_upto else 0
        if st:
            rr = 46 if st == 2 else 28
            gd.ellipse([x - rr, CHAIN_Y - rr, x + rr, CHAIN_Y + rr], fill=(255, 210, 100, 120 if st == 2 else 70))
        lantern(d, x, CHAIN_Y, st, pulse)
    # small names under every lantern
    fs = ImageFont.truetype(FONT_B, 17)
    for i, x in enumerate(XS):
        lit = (i < lit_upto) or (cur_i is not None and i == cur_i and t >= 1.2)
        nm = NAMES[i]
        w = d.textlength(nm, font=fs)
        y = CHAIN_Y + 30 if i % 2 == 0 else CHAIN_Y + 56  # two staggered rows so 25 names never touch
        d.text((x - w / 2, y), nm, font=fs, fill=(255, 235, 180) if lit else (110, 120, 165))
    if mode != 'intro':
        f_c = ImageFont.truetype(FONT_B, 26)
        d.text((XS[DONE] - 10, CHAIN_Y - 62), '…', font=f_c, fill=(170, 180, 220))
    img = Image.alpha_composite(img.convert('RGBA'), glow.filter(ImageFilter.GaussianBlur(14))).convert('RGB')
    d = ImageDraw.Draw(img)
    f_lab = ImageFont.truetype(FONT_B, 34)
    lab = 'Beloved of Allah Kids'
    d.text(((W - d.textlength(lab, font=f_lab)) / 2, 40), lab, font=f_lab, fill=(255, 230, 160))
    if mode == 'card':
        a = min(1.0, t / 0.6)
        th = thumb(cur).resize((960, 540))
        shadow = Image.new('RGBA', (1000, 580), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([20, 20, 980, 560], 30, fill=(255, 210, 110, int(150 * a)))
        img.paste(shadow.filter(ImageFilter.GaussianBlur(16)), (90, 150), shadow.filter(ImageFilter.GaussianBlur(16)))
        mask = Image.new('L', (960, 540), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 960, 540], 26, fill=int(255 * a))
        img.paste(th, (110, 170), mask)
        cx = 1500
        r = 70
        d.ellipse([cx - r, 250 - r, cx + r, 250 + r], fill=(255, 210, 100), outline=(255, 245, 210), width=5)
        d.text((cx, 250), str(cur), font=ImageFont.truetype(FONT, 88), fill=(40, 30, 70), anchor='mm')
        nm = NAMES[cur - 1]
        f2 = ImageFont.truetype(FONT, 100 if len(nm) <= 6 else (84 if len(nm) <= 8 else 70))
        d.text((cx, 430), nm, font=f2, fill=GOLD, anchor='mm', stroke_width=3, stroke_fill=(60, 40, 10))
        ar_text(d, (cx, 560), AR[cur - 1], 72, (255, 255, 255))
        ar_text(d, (cx, 650), 'عليه السلام', 40, (220, 225, 255))
    elif mode == 'intro':
        ar_text(d, (W // 2, 260), 'قصص الأنبياء', 130, GOLD)
        d.text((W // 2, 430), f'1 – {DONE}', font=ImageFont.truetype(FONT, 110), fill=(255, 255, 255), anchor='mm',
               stroke_width=2, stroke_fill=(60, 40, 10))
        fm = ImageFont.truetype(FONT_B, 40)
        for y, line in [(560, 'Prophet Stories · Prophetengeschichten · Histoires des prophètes'),
                        (620, 'Peygamber Kıssaları · Priče o vjerovjesnicima · Tregime për pejgamberët')]:
            d.text((W // 2, y), line, font=fm, fill=(220, 225, 255), anchor='mm')
        ar_text(d, (W // 2, 720), 'من القرآن الكريم والسنة الصحيحة', 44, (255, 230, 160))
    else:
        d.text((W // 2, 250), f'{DONE} / 25', font=ImageFont.truetype(FONT, 130), fill=GOLD, anchor='mm',
               stroke_width=3, stroke_fill=(60, 40, 10))
        ar_text(d, (W // 2, 420), 'تصبحون على خير', 96, (255, 255, 255))
        d.text((W // 2, 540), 'Good night · Gute Nacht · Bonne nuit · İyi geceler · Laku noć · Natën e mirë',
               font=ImageFont.truetype(FONT_B, 40), fill=(220, 225, 255), anchor='mm')
        nx = NAMES[DONE]
        d.text((W // 2 - 20, 660), f'… {nx}', font=ImageFont.truetype(FONT, 64), fill=(255, 230, 160), anchor='rm')
        ar_text(d, (W // 2 + 20, 660), '· ' + AR[DONE], 64, (255, 230, 160), anchor='lm')
    return img


def render(path, mode, cur, dur):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-stream_loop', '-1', '-i', AMB, '-t', str(dur),
                          '-filter_complex', f'[1:a]volume=0.25,afade=t=in:d=0.6,afade=t=out:st={dur-0.8}:d=0.8,aresample=48000,aformat=channel_layouts=stereo[a]',
                          '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-profile:v', 'high', '-video_track_timescale', '15360',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', path],
                         stdin=subprocess.PIPE)
    n = int(dur * FPS)
    for i in range(n):
        p.stdin.write(frame(cur, i / FPS, dur, mode).tobytes())
    p.stdin.close()
    p.wait()


def norm(src, dst):
    info = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                                    'stream=width,height,avg_frame_rate,codec_name', '-of', 'csv=p=0', src]).decode().strip()
    if info == 'h264,1920,1080,30/1':  # already 1080p30 H.264 -> keep the picture as is, only unify the audio
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'copy',
                        '-af', 'aresample=48000,aformat=channel_layouts=stereo', '-c:a', 'aac', '-b:a', '160k',
                        '-ar', '48000', '-video_track_timescale', '15360', dst], check=True)
        return
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src,
                    '-vf', f'scale={W}:{H}:flags=lanczos,fps={FPS},format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'superfast', '-crf', '21', '-profile:v', 'high', '-video_track_timescale', '15360',
                    '-af', 'aresample=48000,aformat=channel_layouts=stereo', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
                    dst], check=True)


def dur_of(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'csv=p=0', p]).decode())


def main(src, out):
    global SKY, SCENE_DIR
    SCENE_DIR = out
    SKY = sky()
    os.makedirs(out, exist_ok=True)
    parts, chapters, t = [], [], 0.0
    intro = os.path.join(out, 'c00_intro.mp4')
    if not os.path.exists(intro):
        render(intro, 'intro', 0, 7)
    parts.append(intro); t += dur_of(intro)
    for n in range(1, DONE + 1):
        card = os.path.join(out, f'c{n:02d}_card.mp4')
        if not os.path.exists(card):
            render(card, 'card', n, 5)
        ep = os.path.join(out, f'e{n:02d}.mp4')
        if not os.path.exists(ep):
            norm(os.path.join(src, f'{n:02d}.mp4'), ep)
        chapters.append((t, n))
        parts += [card, ep]
        t += dur_of(card) + dur_of(ep)
        print('ok', n, round(t), flush=True)
    outro = os.path.join(out, 'c99_outro.mp4')
    if not os.path.exists(outro):
        render(outro, 'outro', 0, 6)
    parts.append(outro)
    with open(os.path.join(out, 'list.txt'), 'w') as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    final = os.path.join(out, 'boa_tv_compilation_teil1_01-16_de.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i',
                    os.path.join(out, 'list.txt'), '-c', 'copy', '-movflags', '+faststart', final], check=True)
    json.dump([{'t': round(a, 2), 'n': n, 'name': NAMES[n - 1]} for a, n in chapters],
              open(os.path.join(out, 'chapters.json'), 'w'), indent=1)
    print('final', final, round(dur_of(final)))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'preview':
        SKY = sky(); SCENE_DIR = sys.argv[3]
        for mode, cur, tt in [('intro', 0, 6.5), ('card', 3, 3.0), ('card', 16, 3.0), ('card', 11, 3.0), ('outro', 0, 3)]:
            frame(cur, tt, 7 if mode == 'intro' else 5, mode).save(os.path.join(sys.argv[2], f'prev_{mode}_{cur}.jpg'), quality=88)
    else:
        main(sys.argv[1], sys.argv[2])
