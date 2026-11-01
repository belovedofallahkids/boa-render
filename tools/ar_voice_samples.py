"""Free Arabic voice samples (edge-tts) for the owner to listen to. Same text for every voice."""
import asyncio, edge_tts, os
TXT = ("بِسْمِ اللَّهِ. السَّلامُ عَلَيْكُمْ يا أحبّائي. اقتربا منّي، فقصّةُ الليلةِ جميلةٌ جدًّا. "
       "قالَ يعقوبُ عليه السلام: فَصَبْرٌ جَمِيلٌ وَاللَّهُ الْمُسْتَعَانُ عَلَى مَا تَصِفُونَ. "
       "تُصبحونَ على خيرٍ يا أحبّائي.")
async def main():
    os.makedirs("out/ar_voices", exist_ok=True)
    vs = [v for v in await edge_tts.list_voices() if v["ShortName"].startswith("ar-") and v["Gender"] == "Female"]
    for v in vs:
        n = v["ShortName"]
        for tag, rate, pitch in (("normal", "-8%", "+0Hz"), ("oma", "-15%", "-4Hz")):
            try:
                await edge_tts.Communicate(TXT, n, rate=rate, pitch=pitch).save(f"out/ar_voices/{n}_{tag}.mp3"); print("ok", n, tag)
            except Exception as e: print("FAIL", n, tag, e)
asyncio.run(main())
