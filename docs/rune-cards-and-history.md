# Runes et historique

## Retrouver une rune

Planification et Liste de tâches affichent le set, le slot, le monstre équipé,
la statistique principale et les sous-statistiques. Une rune non équipée est
indiquée dans l’inventaire. Les identifiants restent utilisés en interne pour
les protections, les builds et les tâches. Pour une rune absente du dernier
import, l’identifiant sert uniquement de référence de secours.

Les fiches de Builds sont des images SVG générées à partir du JSON importé.
Elles montrent le niveau, les étoiles, la qualité d’origine, les statistiques
principale et innée, les quatre sous-statistiques, le monstre équipé et
l’efficience. Les totaux incluent les meules ; « dont +X » précise la part de
la meule sans l’ajouter une deuxième fois. Les fiches fonctionnent hors ligne.
La silhouette s’oriente selon le slot : 1 en haut, puis 2 à 6 dans le sens
horaire. Le numéro reste droit. Un petit diagramme des six emplacements
surligne la position de la rune. Cette fiche est aussi disponible dans
Optimisation, Planification, Liste de tâches, Meilleure vitesse et Améliorations.

La recherche de build vise la vitesse, selon les sets, la vitesse minimale,
la principale du slot 2 et les protections. L’ancien minimum d’ACC n’est plus
utilisé, même si une préférence ancienne le contient. Le total d’ACC reste
une information sur le résultat.

## Doublons dans Évolution

À l’ouverture de la page, un nettoyage transactionnel de `sw_score` conserve
une seule ligne pour chaque combinaison identique : joueur, date, score runes,
score vitesse, score artéfacts et score qualité. Une différence sur l’un de ces
champs conserve la ligne. Les autres joueurs et les instantanés détaillés des
imports ne sont pas modifiés. Aucun nettoyage n’est effectué lors du déploiement.

## Apparence

Le menu ⋮ en haut à droite propose Theme : **Dark** reprend les couleurs du
dashboard, **Light** utilise un fond blanc et **System** suit l’appareil.
La configuration de base reste sombre. Les blocs personnalisés s’adaptent au
mode choisi et les graphiques utilisent une palette adaptée lors de leur rendu.
Le choix de thème utilise le mécanisme natif de Streamlit, propre au navigateur.

Le lien Nouveautés se trouve dans Accueil, avant Mon compte. L’espace vertical
des objectifs utilise maintenant `st.space`, sans l’extension dépréciée.

## Classements et objectifs

Les classements proposent les six scores les plus proches du compte connecté,
avec son propre compte toujours présent, l’écart de score et le rang du
classement complet. Les filtres de guilde et les règles de visibilité restent
appliqués avant toute sélection ou comparaison.

Pour les scores et PvP/World Boss, le rang est reconstitué à la date du précédent
relevé distinct du joueur : chaque concurrent utilise son dernier relevé
disponible à cette date, ou son record à cette date en mode Record. Le rang
actuel inclut les nouveaux concurrents. La population de chaque classement est
indiquée ; les mouvements intrajournaliers et les relevés supprimés ne peuvent
pas être reconstitués. La visibilité et l’appartenance aux guildes sont celles
d’aujourd’hui. Pour les scores calculés, toutes les observations utilisées
doivent avoir une méthode de calcul connue et identique. Sinon, aucune variation
n’est annoncée. Les classements détaillés Runes et Artéfacts ne conservent que
la dernière mesure : leurs variations restent explicitement indisponibles.

Les objectifs affichent les réussites, les manques et la progression, avec les
filtres Tous, À atteindre et Nouveaux objectifs atteints. Pour les runes, chaque
set/palier/emplacement compte séparément ; un surplus ne compense plus un manque
sur un autre emplacement. Les paliers existants restent distincts : [100,110[
et 110+. Pour les artéfacts, la meilleure valeur doit dépasser le seuil entier
choisi : un seuil de 10 demande donc 11 %. La matrice effets × attributs utilise
les catégories observées dans l’un des deux imports pour chaque principale
activée ; les anciennes lignes S3/S4 sont réunies par leur maximum.

Les nouveaux objectifs atteints comparent l’import affiché à son prédécesseur
enregistré, y compris le même jour, selon les paramètres actuels appliqués aux
deux imports. Recharger le même export ne crée pas de nouvelle réussite.
Les méthodes différentes, l’absence d’un prédécesseur et les anciens instantanés
sans détail d’artéfacts donnent une comparaison indisponible, jamais zéro réussite
supposée. Les futurs instantanés ajoutent uniquement les meilleures valeurs
d’artéfacts par catégorie, sans sauvegarder l’export brut. Les paramètres sont
enregistrés atomiquement et restent propres au compte connecté.
