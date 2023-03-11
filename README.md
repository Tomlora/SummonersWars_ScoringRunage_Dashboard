# SummonersWars_ScoringRunage_Api
Dashboard permettant d'attribuer un score aux runes d'un compte Summoners Wars

# Fonctionnement

L'utilisateur upload un fichier json, qui est généré par [SWEX](https://github.com/Xzandro/sw-exporter) et qui récapitule l'ensemble des informations de son compte.

Il a ensuite accès à un certain nombre de pages.

Les données sont stockées dans une base de données PostgreSQL. __Seuls les scores, la date, le pseudo et la guilde du joueur sont stockées.__

 <p align="center">
  <img width="300" height="500" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/Menu2.png?raw=true">
</p>

## Calcul du score

L'utilisateur a accès à 3 scorings différents, où deux sont basés sur l'efficience d'une rune/artefact et un autre est calculé en fonction de la sous-stat la plus importante du jeu, qui est la rapidité.


L'efficience correspond aux stats de la rune, comparé au maximum possible qu'il est possible d'avoir.
Il existe également des objets pour améliorer ses runes, ce qui permet de dépasser le maximum possible. Dans ce cas, l'efficience sera supérieur à 100%.

Pour notre calcul, nous ne prenons en compte que les runes ayant 100 ou plus d'efficience.

Certains sets de runes (c'est-à-dire des familles de runes donnant des bonus si elles sont associées ensemble), ont une importance supérieure à d'autres. 
C'est pourquoi chaque set a un coefficient différent dans le scoring final en fonction de leur importance.

| Set        | Coefficient      | 
| ------|-----|
| Violent  	| 3 	| 
| Destroy 	| 3 	|
| Will 	| 2 	| 
| Despair | 2      |
| Swift (score rapidité) | 3 |

****

Pour un set :

$\alpha$ = nombre de runes dont l'efficience est entre 100 et 110

$\beta$ = nombre de runes dont l'efficience est entre 110 et 120
 
$\gamma$ = nombre de runes dont l'efficience est supérieur à 120
 
$$score = ( \alpha * 1 + \beta * 2 + \gamma * 3) * coefficient$$
 
 Le score total correspond à l'addition de tous les sets :
 $$\sum_{i=1}^n set_i$$
  


# Pages
### Général

Cette page permet à un utilisateur de voir ses différents scores. Il peut également se comparer à la moyenne des joueurs enregistrés ou à la moyenne de sa guilde.

 <p align="center">
  <img width="400" height="600" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/general2.png?raw=true">
</p>

****

### Evolution

Permet de suivre l'évolution de ses scorings

 <p align="center">
  <img width="400" height="600" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/evolution.png?raw=true">
</p>

****

### Classement

Affiche un classement des différents scorings présents sur le site.

L'utilisateur a la possibilité de :
- Ne pas y apparaitre
- Apparaitre en anonyme
- Apparaitre uniquement pour sa guilde
- Apparaitre pour tout le monde

**Note** : Par soucis de confidentialité, les pseudos/guildes sont retirés sur cette image.

 <p align="center">
  <img width="500" height="600" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/classement.png?raw=true">
</p>

****

### Runes

Permet d'analyser les runes, et d'identifier celles dont l'efficience peut être amélioré avec des objets d'améliorations.

 <p align="center">
  <img width="500" height="600" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/runes.png?raw=true">
</p>

Il est également possible de télécharger ces données au format Excel, et mis en page :

 <p align="center">
  <img width="1000" height="600" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/runes_excel.png?raw=true">
  <img width="800" height="700" src="https://github.com/Tomlora/SummonersWars_ScoringRunage_Dashboard/blob/main/img/runes_excel2.png?raw=true">
</p>


D'autres outils sont disponibles :) 

# Lien

https://scoringsw.herokuapp.com/


