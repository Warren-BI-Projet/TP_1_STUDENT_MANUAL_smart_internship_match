"""Use a local Ollama model to extract only facts stated in each offer."""
import json
import os
import time
from pathlib import Path

import requests

SOURCE = Path("data/offers/merged_offers.json")
OUTPUT = Path("data/offers/structured_offers.json")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
PROMPT = """Extrais uniquement les faits explicitement présents dans cette offre. Réponds par un objet JSON avec required_skills (outils et compétences techniques nommés), responsibilities (missions), experience_required (citation exacte ou null), compensation_mentioned (montant exact ou null). N'invente rien. Texte :\n"""


def extract(description):
    session = requests.Session()
    session.trust_env = False
    response = session.post(OLLAMA_URL, json={"model": MODEL, "prompt": PROMPT + description,
                                              "format": "json", "stream": False}, timeout=(10, 180))
    response.raise_for_status()
    data = json.loads(response.json()["response"])
    for key in ("required_skills", "responsibilities"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Réponse Ollama invalide : {key}")
    return data


def main():
    offers = json.loads(SOURCE.read_text(encoding="utf-8"))["offers"]
    structured = []
    for offer in offers:
        facts = extract(offer.get("description", ""))
        structured.append({key: value for key, value in offer.items() if key != "description"} | {
            "required_skills": facts["required_skills"],
            "responsibilities": facts["responsibilities"],
            "experience_required": facts.get("experience_required"),
            "compensation_mentioned": facts.get("compensation_mentioned"),
        })
        OUTPUT.write_text(json.dumps({"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                      "offers": structured}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{len(structured)}/{len(offers)} : {offer['title']}")
    if not offers:
        OUTPUT.write_text(json.dumps({"offers": []}), encoding="utf-8")


if __name__ == "__main__":
    main()
