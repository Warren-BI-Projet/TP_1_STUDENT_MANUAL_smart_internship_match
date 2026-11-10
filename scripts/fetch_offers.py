"""Fetch public offers through France Travail's official API."""
import json
import os
import time
from pathlib import Path

import requests

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
SCOPE = "api_offresdemploiv2 o2dsoffre"
SEARCH_PARAMS = {"motsCles": os.getenv("SEARCH_TERMS", "stage informatique"), "sort": "1", "range": "0-49"}
OUTPUT = Path("data/offers/raw_offers.json")


def request_with_retry(method, url, **kwargs):
    for attempt in range(4):
        try:
            response = requests.request(method, url, timeout=(10, 30), **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def main():
    client_id = os.environ["FRANCETRAVAIL_CLIENT_ID"]
    client_secret = os.environ["FRANCETRAVAIL_CLIENT_SECRET"]
    token = request_with_retry("POST", TOKEN_URL, data={
        "grant_type": "client_credentials", "client_id": client_id,
        "client_secret": client_secret, "scope": SCOPE,
    }).json()["access_token"]
    response = request_with_retry("GET", SEARCH_URL, params=SEARCH_PARAMS,
                                  headers={"Authorization": f"Bearer {token}"})
    offers = [] if response.status_code == 204 else response.json().get("resultats", [])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                  "search_params": SEARCH_PARAMS, "offers": offers}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(offers)} offres enregistrées dans {OUTPUT}")


if __name__ == "__main__":
    main()
