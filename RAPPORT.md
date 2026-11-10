# Rapport de projet — Smart Internship Match

## Objectif et périmètre

Le système aide à prioriser des offres de stage, à repérer des compétences à développer et à suivre les candidatures. Il ne décide pas à la place du candidat. Le projet exploite l'API officielle France Travail ; les données de candidature et le profil restent locaux.

## Pipeline et sources

Le workflow hebdomadaire télécharge les offres officielles. Les scripts locaux normalisent les champs, extraient les compétences et missions à l'aide d'Ollama, puis calculent le score. Une revue humaine doit contrôler les extractions. Les fichiers intermédiaires sont ignorés par Git ; seuls les résultats officiels explicitement publiables sont exportés vers le tableau de bord.

**À compléter après la première exécution réelle :** date de collecte, paramètres de recherche, nombre d'offres, exemples d'offres vérifiées, taux d'erreur d'extraction observé et au moins une erreur concrète de l'IA corrigée.

## Définition du KPI de correspondance

La couverture mesure la part des compétences requises distinctes qui sont appuyées par une preuve dans le profil. Le score multiplie cette couverture par `0,7 + 0,3 × niveau moyen / 5`. Le niveau influe donc sur le classement sans masquer les compétences absentes. La comparaison ignore la casse et les espaces superflus ; elle ne résout pas les synonymes. Les offres sans compétence extraite obtiennent zéro, ce qui indique une donnée insuffisante à examiner manuellement.

## Indicateurs et choix visuels

| Catégorie | Indicateur | Visualisation | Décision soutenue |
|---|---|---|---|
| Santé du pipeline | Nombre d'offres officielles, offres sans compétence extraite, présence d'une rémunération | Cartes et valeurs explicites | Vérifier que l'acquisition et l'extraction ont produit des données utilisables ; éviter un graphique salarial presque vide. |
| Efficacité de recherche | Score médian, nombre d'offres au-dessus de 70 %, fréquence des écarts | Cartes et barres horizontales classées | Prioriser la lecture des offres et choisir une compétence à travailler. Les barres rendent les libellés longs lisibles. |
| Résultats | Candidatures envoyées, taux de réponse | Cartes et tableau de suivi | Réévaluer la stratégie de candidature et relancer les dossiers en attente. |

Le score est une mesure construite à partir du profil saisi, pas une probabilité d'embauche. Le tableau de bord n'affiche aucun résultat inventé avant la collecte réelle.

## Contrôle de suivi

Règle : signaler une candidature marquée « Envoyée » depuis plus de dix jours. Le contrôle est déclenché manuellement dans le tableau de bord. Il ne conclut pas qu'une candidature est rejetée ; il invite à vérifier si une relance est appropriée.

| Date d'exécution | Candidatures contrôlées | Alertes | Action prise |
|---|---:|---:|---|
| À renseigner après exécution réelle | — | — | — |
| À renseigner après une seconde exécution | — | — | — |

## Limites et suite

Les intitulés de compétences générés par l'IA peuvent varier. Les synonymes et équivalences doivent être revus. La rémunération est souvent absente des annonces. Le suivi est lié au navigateur utilisé ; l'export JSON permet une sauvegarde manuelle. Les identifiants France Travail, le profil personnel, une collecte réelle, les brouillons relus et les deux contrôles datés doivent être ajoutés par l'étudiant pour finaliser le rendu.
