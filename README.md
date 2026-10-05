# Summoners War · Scoring & Runage

Tableau de bord Streamlit pour analyser un export SW Exporter, identifier les runes à améliorer et suivre l’historique du compte.

## Démarrage local

Python **3.12**, pandas **3.0.1**, Streamlit **1.65.0**.

```sh
python -m venv .venv
# Windows : .venv\Scripts\activate
# Linux/macOS : source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run scoring_runage.py
```

Sans `API_SQL`, les imports et les analyses fonctionnent en mémoire. La page d’import propose un compte fictif (`examples/demo.json`) qui n’est jamais sauvegardé, même lorsqu’une base est configurée. Un nouvel import réussi remplace les données de la session ; un échec conserve l’analyse précédente. Les favoris de filtres sont conservés pendant la session.

## Historique et déploiement

`API_SQL` contient l’URL SQLAlchemy PostgreSQL de l’installation existante. Le schéma utilisé est `sw`. Ne pas mettre les identifiants dans Git. Les tables historiques et les référentiels `sw_ref_monsters`, `sw_ref_monsters_stats` et `sw_where2use` doivent déjà exister : ce dépôt ne contient pas un installateur de base complet.

1. Sauvegarder la base existante et tester la migration sur sa copie.
2. Appliquer `migrations/20261005_import_manifest.sql` dans cette copie, puis dans l’environnement cible validé.
3. Installer les dépendances dans un environnement Python 3.12 neuf et exécuter les tests.
4. Redémarrer Streamlit ; importer un compte de test, vérifier les scores, les exports et les historiques.

Le rôle applicatif doit pouvoir lire/écrire les tables du schéma. La création automatique du manifeste est conservée pour les installations disposant du droit `CREATE`. La migration préalable évite de dépendre de ce droit. Un import est atomique, protégé par un verrou PostgreSQL par compte ; les calculs précèdent la transaction. Le même contenu/version ne crée pas de doublon. Un contenu modifié remplace le relevé du même jour (Europe/Paris), sans modifier les autres dates. Les maxima et la collection des monstres représentent le dernier import.

La version de calcul `2026.10-v2` corrige les paliers incomplets, les statistiques absentes et les combinaisons de vitesse. Les anciens relevés ne sont pas recalculés : les comparer peut révéler une rupture de méthode. Une combinaison impossible est enregistrée comme valeur manquante. Les exports indiquent l’identifiant exact des runes ; les moyennes des Top N utilisent les runes disponibles, sans compléter artificiellement par des zéros.

Le gain potentiel des recommandations est un maximum théorique. Les opportunités avec stock tiennent compte du set, de la qualité et des meules antiques ; elles ne garantissent pas le résultat aléatoire d’une meule. Le stock est partagé entre les recommandations, sans allocation simultanée. La recherche de vitesse inclut les valeurs actuelles principales/innées et une rune Intangible au maximum ; une Intangible ambiguë ne complète aucun set. Les bonus de bâtiment/leader sont hors du total des runes.

Les classements distinguent dernier relevé et record personnel pour les scores, et conservent la date du score retenu. Le score Com2us global est la somme des scores du relevé ; les moyennes par set restent disponibles. Les paramètres de visibilité sont appliqués à partir des identifiants de compte/guilde.

## Vérification des régressions

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Pour les tests PostgreSQL, fournir `TEST_DATABASE_URL` vers une **base de test dédiée**, avec les droits de création/suppression de schémas. La suite crée des schémas `test_<uuid>` temporaires ; elle n’utilise jamais `API_SQL` pour ses écritures. Sans cette variable, les tests de transaction utilisent SQLite. GitHub Actions exécute aussi PostgreSQL 16.

La suite couvre calculs, recherche exhaustive de vitesse, conservation des identifiants, classements/ex æquo, stocks, exports Excel, rollback/idempotence/suppression et navigation Streamlit en français/anglais avec comptes vides ou réduits. L’export de référence déjà présent dans le dépôt est utilisé comme contrôle d’intégration. Les essais locaux/CI ne remplacent pas la validation du schéma, des données et des services de l’installation réelle.

## Planification et comptes

La comparaison détaillée des imports, le stock limité de meules, les verrous et les préférences persistantes sont décrits dans [le guide de configuration et d’utilisation](docs/accounts-and-planning.md). Sur un déploiement partagé, configurer OIDC et les rattachements administrateur avant la mise à jour : les écritures anonymes sont désormais refusées. L’analyse locale reste disponible.
