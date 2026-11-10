# Smart Internship Match

Projet de recherche de stage fondé sur les offres officielles de France Travail. Le dépôt contient le pipeline, un score explicable, un tableau de bord et un suivi des candidatures conservé dans le navigateur.

## Préparer le projet

1. Installer Python 3.10+ et `pip install -r requirements.txt`.
2. Copier `data/profile/my_skills.example.csv` vers `data/profile/my_skills.csv`, puis saisir **vos** compétences réelles : `skill,level,evidence`. Niveau de 1 à 5, preuve concrète obligatoire pour qu'une compétence soit comptée comme acquise. Ce fichier est ignoré par Git.
3. Créer une application France Travail, souscrire à « Offres d'emploi v2 » et définir `FRANCETRAVAIL_CLIENT_ID` et `FRANCETRAVAIL_CLIENT_SECRET` dans l'environnement local et dans les Secrets GitHub Actions. Ne jamais les mettre dans un fichier suivi.
4. Installer Ollama et télécharger `qwen3:8b` (ou définir `OLLAMA_MODEL`).

## Exécuter

Depuis la racine du projet :

```text
python scripts/fetch_offers.py
python scripts/merge_offer_sources.py
python scripts/extract_offers.py
python scripts/match_offers.py
python scripts/draft_cv.py
python -m http.server 8000 --directory docs
```

Ouvrir `http://localhost:8000`. Le fichier `docs/data/matches.json` initial ne contient aucune offre réelle. Les données apparaissent après la collecte et le traitement. Relire chaque extraction et chaque brouillon avant utilisation.

## Score de correspondance

Les noms des compétences sont comparés après normalisation Unicode, des espaces et de la casse. Les doublons dans une offre ne comptent qu'une fois. Une compétence est acquise uniquement si le profil contient une preuve non vide. `coverage` = nombre de compétences acquises / nombre de compétences requises distinctes. `score` = `coverage × (0,7 + 0,3 × niveau moyen / 5)`. Une offre sans compétence extraite reçoit un score nul ; ce score ne permet pas de juger sa pertinence et demande une lecture manuelle. Le score reste entre 0 et 1. Les différences de libellé sémantique (par exemple « PowerBI » et « Power BI ») nécessitent encore une revue humaine.

## Confidentialité et publication

Seules les offres France Travail marquées publiables vont dans `docs/data/matches.json`. Les données intermédiaires et les brouillons restent locaux. Le profil et les candidatures ne sont jamais publiés ; le suivi du tableau de bord utilise `localStorage`, avec un bouton d'export JSON. La page doit être servie par HTTP pour charger les données.

Le workflow hebdomadaire collecte uniquement les offres officielles et valide l'acquisition. L'extraction, le score, le tableau de bord public et la rédaction tournent localement. Après vérification du fichier public, vous pouvez le committer. Pour GitHub Pages, utiliser la branche `main` et le dossier `/docs`.

## Suivi

Le bouton « Lancer le contrôle » signale les candidatures au statut « Envoyée » depuis plus de 10 jours. Lancer le contrôle à deux dates différentes pendant le projet et consigner les résultats dans le rapport. Aucun résultat réel n'est présumé ici.
