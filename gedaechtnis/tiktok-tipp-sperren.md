---
name: tiktok-tipp-sperren
description: Nie oben links auf dem eigenen TikTok-Profil tippen, nie Textsuche nach "Poste"; nach jedem Tipp auf Post/Story-Bildschirm prüfen
metadata:
  type: feedback
---
Am 20.11.2026 wurde beim Ablesen versehentlich eine Story auf artur.official gepostet (Artur hat sie gelöscht) und vorher der Aktivitätsstatus-Dialog geöffnet.
Ursachen: Teilstring-Suche „Poste“ traf „Posteingang“ und den Knopf „Posten“; blindes „Zurück“ (22,58) traf auf dem eigenen Profil den Story-Stift; Tipp auf Kontonamen traf „Was läuft?“.

**Why:** Posten ohne Arturs OK ist ein harter Regelbruch (CLAUDE.md: Posten nur nach OK pro Stapel).
**How to apply:** In allen iPhone-Skripten: nach jedem Tipp `gesperrt()` (export_holen.py) prüfen und bei Post-/Story-Bildschirm sofort STOPP; nie Teilstrings wie „Poste“ antippen; auf dem eigenen Profil nie oben links tippen; Profil-Erkennung „Gefolgt“ ohne „Nachricht“. Siehe [[upload-speed-regeln]].
