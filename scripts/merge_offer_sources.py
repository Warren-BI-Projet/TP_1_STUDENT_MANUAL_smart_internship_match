"""Normalize official France Travail offers to a stable local schema."""
import json
from pathlib import Path

SOURCE = Path("data/offers/raw_offers.json")
OUTPUT = Path("data/offers/merged_offers.json")


def normalize_offer(offer):
    return {
        "id": f"ft_{offer['id']}", "source": "france_travail",
        "title": offer.get("intitule") or "Intitulé non précisé",
        "company": (offer.get("entreprise") or {}).get("nom"),
        "location": (offer.get("lieuTravail") or {}).get("libelle"),
        "description": offer.get("description") or "",
        "url": offer.get("origineOffre", {}).get("urlOrigine") if isinstance(offer.get("origineOffre"), dict) else None,
        "date_posted": offer.get("dateCreation"),
        "is_apprenticeship": bool(offer.get("alternance", False)),
        "accessible_disability": bool(offer.get("accessibleTH", False)),
        "publishable": True,
    }


def main():
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    offers = [normalize_offer(offer) for offer in raw["offers"]]
    OUTPUT.write_text(json.dumps({"offers": offers}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(offers)} offres normalisées")


if __name__ == "__main__":
    main()
