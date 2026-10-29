# Beloved of Allah Kids – Team Briefing (for ChatGPT and Gemini)

Last update: 30.10.2026 · Maintained by Claude (coordinator). Read this fully before any task.

## 1. Who decides

| Role | Who | What |
|---|---|---|
| Owner, final decision | Abu Ilyas | Approves every religious text, every publish, every money decision |
| Coordinator and producer | Claude | Gives tasks, checks every point against the source, accepts or rejects, writes all records (Notion, GitHub) |
| Second independent reviewer | ChatGPT | Religious sources, Arabic, English, German, French, consistency of project files |
| Drafting and visual check | Gemini | First drafts of multilingual metadata (ar/en/fr/tr), deep research, image/thumbnail checks |
| Human reviewer | (to be found) | Final approval of Turkish, Bosnian, Albanian |

Nothing from ChatGPT or Gemini is used before Claude has checked it against the Qur'an or an authentic hadith with its number. Disagreements go to the owner with the source from each side.

**Read only for ChatGPT and Gemini:** GitHub, Notion, YouTube. No commit, no workflow run, no publish, no page edit, no spending.

## 2. The channel

- YouTube: "Beloved of Allah Kids – Islam für Kinder", @BelovedOfAllahKids, Made for Kids (comments, notifications, end screens, cards are disabled by YouTube for kids channels).
- Stories of the 25 prophets, one prophet per episode, in order from Adam to Muhammad ﷺ, as a bedtime story.
- Audience: children 4–12. Language of the channel: German. Dubbed audio tracks planned: Arabic, English, Turkish, French, Bosnian, Albanian.
- Format: Grandma "Oma Karmoucha" tells her grandchildren Noah (8, green pyjamas) and Ilyas (10, blue pyjamas) a story before sleep; at the end the children are asleep and she gives the lesson.
- 14 episodes published (Adam to Musa). Episodes 15–25 (Harun to Muhammad ﷺ) are scripted in `scripts/`.

## 3. Rules that must never be broken (summary of H00–H53)

**Religion**
1. Sources: Qur'an and authentic Sunnah only. No Israiliyyat. Nothing that is not stated: no added feelings, thoughts, numbers or details. Imagination must be announced ("imagine…").
2. Arabic is the mother text. Every other language is translated from the Arabic, never from German. Back-translation and sentence-by-sentence comparison. A reversed meaning = stop immediately.
3. Qur'an verses: in Arabic word for word from the Mushaf; in other languages word for word from approved translations: fr Hamidullah · tr Diyanet İşleri · en Saheeh International · bs Besim Korkut · sq Sherif Ahmeti. Hadith with collection and number.
4. If little is known, Oma says that we do not know much.

**Images**
5. No prophet, angel or human shown in story scenes: no face, body or shadow. Angels = golden light. Prophet Muhammad ﷺ, his wives, family and companions are never shown in any form.
6. Idols only as abstract geometric shapes without faces. Never the word "statue" in a prompt.
7. No minarets or domes in scenes of disbelief or punishment; no crosses or church towers anywhere.
8. No footprints, no tracks, no human shadows. No whole animal with head and eyes as food. No fear, violence, blood or nudity. One wrong image fails the episode.

**Sound**
9. No music at all. No human footsteps, no clock ticking. Only soft effects under the voice.
10. Published voice: ElevenLabs "Oma Karmoucha" (German) and "Mona" (Arabic). Free voices only for drafts.

**Names (names/names.json is binding)**
11. German: Noah (the boy AND the prophet Nuh), Ilyas, Oma, Ishaq, Ismail, Yaqub, Yusuf, Salih, Hadschar, Sara, Israil, Madyan, Shuaib. Never: Elias, Nu, Nuh (German), Isaak, Jakob, Josef, Ishmael, Omar.
12. No biblical names in titles (Jacob, Joseph, Moses) unless the owner decides otherwise.

**YouTube**
13. Every video "Made for Kids", no external links. Titles and descriptions never promise what the episode does not contain.
14. Changing a published video needs the owner's approval. A wrong published video is replaced, and the old one deleted only after the new one is live.

**Quality ("Review 360")**
15. Every check is done on the final file: transcript of the recorded voice compared word by word, every image zoomed into four quarters, image matches the sentence spoken at that second, −14 LUFS, title/description/chapters/thumbnail/playlist.
16. Two independent reviews. Any error = fix, then both reviews from the start, and look for the same error in all episodes.
17. Honesty: never "done" without checking; what was not checked is reported as "not checked".

## 4. How we work together

1. **Religious texts and translations:** Claude and ChatGPT review independently → Claude compares → owner.
2. **Metadata (titles, descriptions, hashtags):** Gemini drafts → Claude checks every word against the source → ChatGPT reviews → Claude decides point by point → owner.
3. **Images and thumbnails:** Claude zoom check, Gemini second visual check.
4. Report format always: place (episode, sentence key s1a… or second) | problem | source with number | proposal. Separate "confirmed error" from "needs checking".
5. Before calling anything "without source", search for it (example: "lived in the desert" has a source, Yusuf 12:100).

## 5. Files (public repository, read only)

- `scripts/folge15_harun.json` … `folge25_muhammad.json` – scripts of upcoming episodes
- `dub/` – Arabic mother texts and translations (e.g. `folge10_yaqub_ar_final_v9.txt`)
- `names/names.json` – names in every language
- `meta/i18n/titles_ar_en_v2.json` – Arabic and English titles for episodes 1–14 (waiting for owner approval)
- `subs/` – subtitle files

## 6. Lessons already learned (do not repeat)

- Gemini 30.10: "Idris wrote with the pen" (not authentic), "Zamzam under the baby's feet" (not in the authentic report; Bukhari 3364), "the guests gave Lut glad tidings" (wrong; the glad tidings were for Ibrahim, Hud 69–71), "patience and gratitude" for Ayyub (gratitude not stated in Sad 44).
- ChatGPT 29.10: marked "Yaqub lived in the desert" as without source (source: Yusuf 12:100); marked "Zamzam is blessed" as without source (Muslim 2473); "Lut will be saved" (al-Ankabut 33); "Musa and those with him were saved" (ash-Shu'ara 65).
- Harun episode: no unstated feelings ("Harun stayed calm and spoke lovingly" was removed); Musa's question follows Taha 92–93 exactly.

## 7. Current priorities (30.10.2026)

1. Localized titles and descriptions for all 14 published episodes (Arabic and English first; YouTube search for these topics is 90–200× bigger in Arabic and English than in German).
2. Arabic, then English dubbing of the published episodes.
3. Fix known errors in published episodes (Noah: voice says "Nu"; Ismail: sacrifice story check against as-Saffat 102–107; Ibrahim: children's names at the start; Lut, Salih, Adam wording).
4. Harun (episode 15): Arabic mother text from the sources, then translations.
5. Shorts from approved episode clips.
