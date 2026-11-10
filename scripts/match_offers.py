"""Deterministic match KPI. Coverage is the share of distinct required skills supported."""
import csv
import json
import time
import unicodedata
from pathlib import Path

PROFILE = Path("data/profile/my_skills.csv")
SOURCE = Path("data/offers/structured_offers.json")
LOCAL = Path("data/offers/matches_all_local.json")
PUBLIC = Path("docs/data/matches.json")


def normalize(skill):
    return " ".join(unicodedata.normalize("NFKC", skill).casefold().split())


def load_profile(path=PROFILE):
    with open(path, newline="", encoding="utf-8-sig") as source:
        rows = csv.DictReader(source)
        profile = {}
        for row in rows:
            name = (row.get("skill") or "").strip()
            if not name:
                continue
            level = int(row["level"])
            if not 1 <= level <= 5:
                raise ValueError(f"Niveau hors de 1–5 : {name}")
            key = normalize(name)
            if key in profile:
                raise ValueError(f"Compétence en double : {name}")
            profile[key] = {"skill": name, "level": level, "evidence": (row.get("evidence") or "").strip()}
        return profile


def score_offer(profile, required_skills):
    """Return score 0..1, coverage 0..1, profile names matched, and missing skills.

    Score combines 70% coverage and 30% average confidence (level / 5),
    weighted by coverage so an offer with no supported skill always scores zero.
    """
    unique = {}
    for raw in required_skills or []:
        if isinstance(raw, str) and normalize(raw):
            unique.setdefault(normalize(raw), raw.strip())
    if not unique:
        return {"score": 0.0, "coverage": 0.0, "matched": [], "gaps": []}
    matched, gaps, levels = [], [], []
    for key, raw in unique.items():
        item = profile.get(key)
        if item and item["evidence"]:
            matched.append(item["skill"])
            levels.append(item["level"])
        else:
            gaps.append(raw)
    coverage = len(matched) / len(unique)
    confidence = sum(levels) / (5 * len(levels)) if levels else 0.0
    return {"score": round(coverage * (0.7 + 0.3 * confidence), 4),
            "coverage": round(coverage, 4), "matched": matched, "gaps": gaps}


def build_output(results, profile):
    gaps, matched = {}, {}
    for offer in results:
        for name in offer["gaps"]:
            gaps[name] = gaps.get(name, 0) + 1
        for name in offer["matched"]:
            matched[name] = matched.get(name, 0) + 1
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_offers": len(results), "offers": results,
        "top_skill_gaps": [{"skill": s, "count": n} for s, n in sorted(gaps.items(), key=lambda x: -x[1])[:10]],
        "top_matched_skills": [{"skill": s, "count": n, "level": profile[normalize(s)]["level"]}
                               for s, n in sorted(matched.items(), key=lambda x: -x[1])[:10]],
        "n_offers_with_compensation": sum(bool(o.get("compensation_mentioned")) for o in results),
    }


def main():
    profile = load_profile()
    offers = json.loads(SOURCE.read_text(encoding="utf-8"))["offers"]
    results = [{**offer, **score_offer(profile, offer.get("required_skills", []))} for offer in offers]
    results.sort(key=lambda row: row["score"], reverse=True)
    LOCAL.write_text(json.dumps(build_output(results, profile), ensure_ascii=False, indent=2), encoding="utf-8")
    public = [offer for offer in results if offer.get("source") == "france_travail" and offer.get("publishable") is True]
    PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC.write_text(json.dumps(build_output(public, profile), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(results)} offres classées ; {len(public)} publiables")


if __name__ == "__main__":
    main()
