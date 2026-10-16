# BoA – Montage (kostenlos)

Beloved of Allah Kids – Islam für Kinder. Hier entstehen die Videos automatisch aus Bildern und Erzählung.

- `jobs/<name>.json`: eine Folge. Sie enthält die Bilder mit Zeiten und die Erzählung.
- Nach jedem Push rendert GitHub Actions das Video:
  - 1920×1080, 30 fps
  - Ton auf −14 LUFS normalisiert
  - weiche Übergänge und langsame Kamerabewegung
- Das Ergebnis steht unter **Releases**. Dort liegen das Video und `contact.jpg` (ein Bild pro Abschnitt).
- In `out/<name>/` liegen `status.json` (Länge, Lautheit, Links), `contact.jpg` und `log.txt`.
- Kein Upload zu YouTube ohne zwei Prüfungen und die Freigabe des Besitzers (H29).
