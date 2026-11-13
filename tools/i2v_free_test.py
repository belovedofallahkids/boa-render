#!/usr/bin/env python3
"""Free image-to-video test on a CPU runner (LTX-Video 2B via diffusers). Usage: i2v_free_test.py <image> <out.mp4> <w> <h> <frames> <steps>"""
import sys, time, gc, torch
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video, load_image
img, out, W, H, F, S = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
torch.set_num_threads(4)
t0 = time.time()
from transformers import T5Tokenizer
tok = T5Tokenizer.from_pretrained("Lightricks/LTX-Video", subfolder="tokenizer", legacy=True)
pipe = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", tokenizer=tok, torch_dtype=torch.bfloat16)
print("loaded", round(time.time()-t0), "s", flush=True)
prompt = ("The animals walk slowly in pairs up the wooden ramp into the big wooden ark, birds flap their wings and fly "
          "gently toward the door, soft clouds drift in the evening sky, the little stream sparkles. Pixar-like 3D "
          "animation, calm bedtime mood, slow camera push-in.")
neg = "people, humans, faces, hands, text, watermark, worst quality, blurry, jittery, distorted"
with torch.no_grad():
    pe, pm, ne, nm = pipe.encode_prompt(prompt, neg, do_classifier_free_guidance=True, max_sequence_length=128)
pipe.text_encoder = None; gc.collect()
print("prompt encoded", round(time.time()-t0), "s", flush=True)
image = load_image(img).resize((W, H))
t1 = time.time()
with torch.no_grad():
    frames = pipe(image=image, prompt_embeds=pe, prompt_attention_mask=pm, negative_prompt_embeds=ne,
                  negative_prompt_attention_mask=nm, width=W, height=H, num_frames=F,
                  num_inference_steps=S, generator=torch.Generator().manual_seed(7)).frames[0]
print("generated", round(time.time()-t1), "s", flush=True)
export_to_video(frames, out, fps=24)
print("total", round(time.time()-t0), "s", flush=True)
