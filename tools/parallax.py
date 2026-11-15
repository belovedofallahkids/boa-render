"""2.5D parallax (free, CPU): turns a still into a moving camera shot, so no picture is ever static.
Depth-Anything-V2-Small estimates depth; near pixels move more than far ones while the camera
drifts and slowly pushes in. Drop-in replacement for render.render_clip (same signature).
"""
import os, subprocess
import numpy as np
import cv2

_PIPE = None
_DEPTH = {}
W, H = 1920, 1080


def _depth(img_path):
    global _PIPE
    if img_path in _DEPTH:
        return _DEPTH[img_path]
    if _PIPE is None:
        from transformers import pipeline
        _PIPE = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=-1)
    from PIL import Image
    im = Image.open(img_path).convert("RGB")
    d = np.array(_PIPE(im)["depth"], dtype=np.float32)
    d = cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC)
    d = (d - d.min()) / max(1e-6, d.max() - d.min())          # 1 = near
    d = cv2.GaussianBlur(d, (0, 0), 6)
    _DEPTH[img_path] = d
    return d


# camera paths: (dx, dy) parallax direction, push-in amount
PATHS = {
    "zoom_in": ((1.0, 0.25), 0.06), "zoom_out": ((-1.0, 0.2), -0.05), "pan_right": ((1.0, 0.0), 0.03),
    "pan_left": ((-1.0, 0.0), 0.03), "pan_up": ((0.3, -1.0), 0.04), "pan_down": ((-0.3, 1.0), 0.04),
    "none": ((0.6, 0.2), 0.03),
}


def render_clip(i, seg, img, length, fps, out):
    frames = int(round(length * fps)) + 2
    src = cv2.imread(img, cv2.IMREAD_COLOR)
    src = cv2.resize(src, (W, H), interpolation=cv2.INTER_AREA) if src.shape[1] != W else src
    depth = _depth(img)
    (dx, dy), push = PATHS.get(seg.get("motion", "zoom_in"), PATHS["zoom_in"])
    amp = float(seg.get("parallax", 28.0))                      # pixels of near-field travel
    base_zoom = 1.10                                            # margin so edges never show
    gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(frames):
        p = f / max(1, frames - 1)
        e = 0.5 - 0.5 * np.cos(np.pi * p)                       # ease in-out
        off = (e - 0.5) * 2                                     # -1 .. 1
        z = base_zoom * (1 + push * e) if push >= 0 else base_zoom * (1 - push * (1 - e))
        # breathing: tiny sway so even long shots stay alive
        sway = 0.15 * np.sin(2 * np.pi * f / (fps * 6.0))
        shx = (dx * off + sway) * amp * depth
        shy = (dy * off + 0.5 * sway) * amp * 0.6 * depth
        mx = cx + (gx - cx) / z - shx
        my = cy + (gy - cy) / z - shy
        frame = cv2.remap(src, mx.astype(np.float32), my.astype(np.float32), interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    if ff.wait():
        raise RuntimeError("ffmpeg parallax encode failed")
    return i
