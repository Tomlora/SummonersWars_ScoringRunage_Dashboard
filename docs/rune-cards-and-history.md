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
