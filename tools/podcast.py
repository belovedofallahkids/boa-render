#!/usr/bin/env python3
"""Podcast RSS (Spotify, Apple, ...) from podcast/episodes.json -> podcast/feed.xml
Each episode: {"guid","title","description","audio","bytes","duration","pubDate" (RFC 2822),"episode","type"}
Only episodes whose YouTube video is already public go into episodes.json."""
import json, os
from xml.sax.saxutils import escape as e
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/belovedofallahkids/boa-render/main/podcast/"
C = {"title": "Oma erzählt – Prophetengeschichten für Kinder (Beloved of Allah Kids)",
     "desc": ("Islamische Gute-Nacht-Geschichten für Kinder von 4 bis 12 Jahren. Jeden Abend erzählt Oma Karmoucha ihren Enkeln "
              "Noah und Ilyas eine Geschichte von den Propheten – von Adam bis zu unserem geliebten Propheten Muhammad ﷺ. "
              "Alles aus dem Koran und aus sicheren Hadithen, nichts dazuerfunden. Jeden Freitag eine neue Folge. "
              "Auch als Video auf YouTube: @BelovedOfAllahKids"),
     "email": "houtacampino@gmail.com", "author": "Beloved of Allah Kids", "link": "https://www.youtube.com/@BelovedOfAllahKids"}
eps = json.load(open(os.path.join(ROOT, "podcast", "episodes.json")))
items = []
for x in sorted(eps, key=lambda x: x.get("order", 0), reverse=True):
    items.append(f"""  <item>
   <title>{e(x['title'])}</title>
   <description>{e(x['description'])}</description>
   <itunes:summary>{e(x['description'])}</itunes:summary>
   <enclosure url="{e(x['audio'])}" length="{x['bytes']}" type="audio/mpeg"/>
   <guid isPermaLink="false">{e(x['guid'])}</guid>
   <pubDate>{x['pubDate']}</pubDate>
   <itunes:duration>{int(x['duration'])}</itunes:duration>
   <itunes:episodeType>{x.get('type','full')}</itunes:episodeType>
   {'<itunes:episode>%d</itunes:episode>' % x['episode'] if x.get('episode') else ''}
   <itunes:explicit>false</itunes:explicit>
  </item>""")
xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
 <channel>
  <title>{e(C['title'])}</title>
  <link>{C['link']}</link>
  <atom:link href="{RAW}feed.xml" rel="self" type="application/rss+xml"/>
  <language>de</language>
  <description>{e(C['desc'])}</description>
  <itunes:summary>{e(C['desc'])}</itunes:summary>
  <itunes:author>{e(C['author'])}</itunes:author>
  <itunes:owner><itunes:name>{e(C['author'])}</itunes:name><itunes:email>{C['email']}</itunes:email></itunes:owner>
  <itunes:image href="{RAW}cover.jpg"/>
  <image><url>{RAW}cover.jpg</url><title>{e(C['title'])}</title><link>{C['link']}</link></image>
  <itunes:category text="Kids &amp; Family"><itunes:category text="Stories for Kids"/></itunes:category>
  <itunes:category text="Religion &amp; Spirituality"><itunes:category text="Islam"/></itunes:category>
  <itunes:explicit>false</itunes:explicit>
  <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
 </channel>
</rss>
"""
open(os.path.join(ROOT, "podcast", "feed.xml"), "w").write(xml)
print("feed with", len(items), "episodes")
