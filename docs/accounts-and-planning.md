# Comptes, préférences et planification

## Avant de déployer

Le fonctionnement historique est conservé par défaut : avec `API_SQL` configuré,
l'import d'un export valide propose la sauvegarde activée, sans connexion OIDC ni
rattachement administrateur. Le compte est reconnu par son identifiant dans l'export ;
sa propriété n'est donc pas certifiée. Une ancienne ligne dont `joueur_id=0` peut être
rattachée par pseudo comme auparavant, sans écraser l'identifiant d'un autre compte.

Installer `requirements.txt` et appliquer les migrations `20261005_import_manifest.sql`
puis `20261006_workspace_snapshots.sql` dans le schéma `sw`. Les tables historiques et
référentiels existants restent nécessaires. Les sauvegardes restent atomiques et
idempotentes. Après une sauvegarde, Évolution, Comparaison, les classements, les objectifs
et les autres pages de compte sont disponibles. Le menu est déplié, avec Calculateurs
en dernière section. Réimporter le JSON après cette mise à jour pour remplacer une
ancienne analyse locale qui n'avait pas pu être enregistrée.

Le référentiel des monstres est chargé dès qu'une base est configurée, même si la
sauvegarde est décochée. Le mode de démonstration ne consulte jamais la base. Sans
référentiel, les identifiants restent le recours pour les noms inconnus.

### OIDC strict : option désactivée par défaut

Aucun fichier de secrets OIDC n'est nécessaire pour le fonctionnement précédent.
La présence d'une configuration OIDC ou de rattachements existants n'active pas le
contrôle strict. Pour l'activer volontairement :

1. Définir explicitement `[access] require_oidc = true` dans les secrets du serveur.
2. Configurer un fournisseur OIDC et l'URL `https://votre-domaine/oauth2callback`, à
   partir de `.streamlit/secrets.example.toml`. Utiliser HTTPS et remplacer les
   valeurs d'exemple ; ne jamais versionner les vrais secrets.
3. Après vérification indépendante de la propriété du compte de jeu, ajouter un bloc
   `[[access.accounts]]` liant son `wizard_id` au couple exact `iss`/`sub` de l'identité.
4. En mode strict, les anciennes lignes `joueur_id=0` doivent être rattachées par
   l'administrateur : la correspondance de pseudo automatique est désactivée.
5. Valider connexion, déconnexion et révocation avec le fournisseur réel. Recharger
   les secrets/redémarrer les instances après modification. Le prochain rerun
   réévalue les droits ; les données déjà affichées ne peuvent pas être rappelées.

En mode strict uniquement, les écritures et pages privées exigent une identité
vérifiée et un rattachement serveur. L'expiration du jeton est vérifiée lorsqu'elle
est exposée. Les tests utilisent des identités contrôlées, sans appeler de fournisseur.
Les règles de visibilité des classements sont conservées dans les deux modes.
Référence : [authentification OIDC native de Streamlit](https://docs.streamlit.io/develop/concepts/connections/authentication).

## Utilisation

- **Changements entre imports** : sauvegarder deux exports distincts, même le même
  jour, puis choisir « Avant » et « Après ». La somme des contributions explique le
  changement du score runage. Les seuils 100/110/120 et les coefficients de set
  expliquent pourquoi un gain d'efficience ne change pas toujours le score. Les
  changements d'équipement sont distingués des améliorations. L'absence d'une rune
  ne prouve pas qu'elle a été vendue. Des versions de calcul différentes ne sont pas
  comparées. Aucun historique détaillé antérieur n'est inventé.
- **Planification → Protéger mes équipes** : sélectionner des identifiants de rune,
  des monstres ou des builds enregistrés, puis enregistrer les verrous. Les monstres
  sont identifiés par leur ID (deux exemplaires du même monstre restent distincts).
  Leurs runes actuelles sont protégées au prochain import. Un build protégé suit les
  six IDs de sa version enregistrée. Les IDs absents restent dans les préférences.
- **Stock de meules** : le plan réserve des quantités entières, sans réutiliser une
  meule sur plusieurs runes, et respecte les sets, qualités et runes antiques. Il
  privilégie le gain d'efficience maximal, puis les meules ordinaires en cas d'égalité
  avec une meule universelle. Cette allocation gloutonne ne garantit pas l'optimum
  global. Une seule tentative par statistique est planifiée ; le jet réel peut être
  inférieur au maximum, voire n'apporter aucun gain. Aucun objet n'est consommé dans
  le jeu. Les gemmes et réappraisals ne sont pas simulés dans ce plan.
- **Build sur critères** : choisir les sets, SPD minimale et ACC minimale apportées
  par les runes de niveau ≥12. Les valeurs sont celles du JSON, principales et
  innées comprises. Elles excluent la base du monstre, les bonus de set (y compris
  Focus), bâtiments et leader. La recherche maximise la SPD parmi les builds
  admissibles. Si sa limite de 100 000 états est atteinte, elle le signale sans
  conclure qu'aucun build n'existe. Restreindre le set secondaire réduit la recherche.
- **Préférences** : enregistrer pour conserver filtres, colonnes, critères et verrous
  sur le compte importé, après fermeture du navigateur. Les filtres nommés sont
  également persistants. Les actions/priorités utilisent des codes indépendants de
  la langue. Les objectifs se sauvegardent sur leurs propres pages. En mode local,
  exporter puis restaurer le JSON de préférences ; il ne contient pas l'export du
  joueur ni ses informations de connexion. Réimporter le même compte conserve les
  préférences de session ; changer de compte isole les préférences.

## Conservation et suppression

`sw_rune_snapshots` conserve uniquement les statistiques normalisées de runes et leurs
contributions, indexées par compte, empreinte de fichier et version de calcul. Le JSON
complet n'est pas conservé. Les instantanés sont atomiques avec l'import. Réimporter
le même fichier ne les duplique pas ; un ancien import sans détail reçoit son premier
instantané lors de sa prochaine analyse. Les courbes historiques gardent un point
par jour. Supprimer une date supprime tous ses instantanés détaillés ; supprimer un
compte supprime aussi ses préférences/verrous. Aucun effacement automatique par âge
n'est effectué : surveiller le volume et appliquer la politique de conservation du
déploiement.

Les préférences d'un compte sont partagées entre ses sessions : la dernière
sauvegarde remplace la précédente. Après toute modification dans le jeu, refaire un
export pour recalculer stock et verrous sur un inventaire à jour.
