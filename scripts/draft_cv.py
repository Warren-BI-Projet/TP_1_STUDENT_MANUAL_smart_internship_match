"""Draft private paragraphs using only skills backed by profile evidence."""
import json
import os
import re
from pathlib import Path

import requests
from match_offers import load_profile, normalize

SOURCE = Path("data/offers/matches_all_local.json")
OUTPUT = Path("output/cv_drafts")
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


def main():
    profile = load_profile()
    offers = json.loads(SOURCE.read_text(encoding="utf-8"))["offers"]
    candidates = [o for o in offers if o["coverage"] >= 0.3 and o["matched"]][:3]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.trust_env = False
    for offer in candidates:
        evidence = {s: profile[normalize(s)]["evidence"] for s in offer["matched"]}
        prompt = ("Rédige en français un paragraphe d'accroche de 3 à 4 phrases pour cette candidature. "
                  "Utilise uniquement les preuves fournies ; n'invente aucune expérience. "
                  f"Offre : {offer['title']} chez {offer.get('company') or 'cette entreprise'}. "
                  f"Missions : {offer.get('responsibilities', [])}. Preuves : {json.dumps(evidence, ensure_ascii=False)}")
        response = session.post("http://127.0.0.1:11434/api/generate", json={"model": MODEL, "prompt": prompt,
                                                                            "stream": False}, timeout=(10, 180))
        response.raise_for_status()
        safe_id = re.sub(r"[^\w-]", "_", offer["id"])
        (OUTPUT / f"offer_{safe_id}.txt").write_text(response.json()["response"].strip() + "\n", encoding="utf-8")
    print(f"{len(candidates)} brouillons à relire dans {OUTPUT}")


if __name__ == "__main__":
    main()
