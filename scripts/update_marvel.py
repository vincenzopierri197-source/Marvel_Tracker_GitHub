#!/usr/bin/env python3
"""
Aggiornatore prudente del Marvel Tracker.

Fonte:
https://www.sorrisi.com/cinema/migliori-film/la-lista-dei-film-marvel-ordine-cronologico/

La pagina può bloccare richieste automatiche. In quel caso lo script NON
modifica i dati esistenti e termina senza errore, così il sito resta online.
Quando trova titoli nuovi riconoscibili, li inserisce in una sezione separata
"Nuovi titoli dalla fonte", lasciando intatto l'elenco curato manualmente.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "marvel.json"
URL = "https://www.sorrisi.com/cinema/migliori-film/la-lista-dei-film-marvel-ordine-cronologico/"

KEYWORDS = [
    "avengers", "captain america", "capitan america", "iron man", "thor",
    "hulk", "guardiani della galassia", "guardians of the galaxy", "ant-man",
    "black panther", "spider-man", "doctor strange", "loki", "wandavision",
    "falcon", "winter soldier", "shang-chi", "eternals", "hawkeye",
    "moon knight", "she-hulk", "ms marvel", "werewolf", "licantropus",
    "secret invasion", "the marvels", "echo", "daredevil", "agatha",
    "thunderbolts", "ironheart", "fantastici quattro", "fantastic four",
    "visionquest", "vision quest", "wonder man", "x-men", "zombies",
    "blade", "deadpool", "venom", "morbius", "armor wars", "brand new day",
]

def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip(" \t\r\n•·-")
    # Elimina date/anno alla fine, senza alterare il titolo.
    text = re.sub(r"\s*\((?:19|20)\d{2}(?:\s*[-–]\s*(?:19|20)\d{2})?\)\s*$", "", text)
    return text.strip()

def is_candidate(text: str) -> bool:
    t = text.lower()
    if not (2 <= len(text) <= 110):
        return False
    if any(x in t for x in ("cookie", "newsletter", "abbonati", "pubblicità", "leggi anche")):
        return False
    return any(k in t for k in KEYWORDS)

def infer_type(title: str) -> str:
    t = title.lower()
    serie_markers = (
        "stagione", "season", "serie", "what if", "loki", "wandavision",
        "falcon and the winter soldier", "echo", "daredevil", "agatha",
        "ironheart", "hawkeye", "moon knight", "she-hulk", "ms marvel",
        "x-men '97", "marvel zombies", "wonder man", "i am groot"
    )
    return "serie" if any(x in t for x in serie_markers) else "film"

def slug(title: str) -> str:
    t = title.lower()
    t = re.sub(r"[^a-z0-9àèéìòù]+", "-", t)
    return t.strip("-")

def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    existing = {
        slug(item["title"])
        for section in data.get("sections", [])
        for item in section.get("items", [])
    }
    existing.update(slug(item["title"]) for item in data.get("sourceUpdates", []))

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; MarvelTracker/1.0; "
            "+https://github.com/)"
        ),
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    }

    try:
        response = requests.get(URL, headers=headers, timeout=25)
        response.raise_for_status()
    except Exception as exc:
        print(f"Fonte non raggiungibile ({exc}). Mantengo i dati esistenti.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    candidates = []

    for node in soup.select("h2, h3, h4, li"):
        text = clean(node.get_text(" ", strip=True))
        if is_candidate(text):
            candidates.append(text)

    # Mantieni l'ordine della pagina e rimuovi duplicati.
    seen = set()
    candidates = [x for x in candidates if not (slug(x) in seen or seen.add(slug(x)))]

    new_items = [
        {"title": title, "type": infer_type(title), "source": URL}
        for title in candidates
        if slug(title) not in existing
    ]

    if new_items:
        data["sourceUpdates"] = data.get("sourceUpdates", []) + new_items
        print("Nuovi titoli trovati:")
        for item in new_items:
            print(" -", item["title"])
    else:
        print("Nessun nuovo titolo riconosciuto.")

    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
