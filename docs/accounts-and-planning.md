# Comptes, préférences et planification

## Avant de déployer

Cette version ferme les accès persistants anonymes. Sans configuration OIDC et sans
rattachement administrateur, l'analyse locale reste disponible, mais aucun import
ne peut lire ou modifier l'historique d'un compte. Préparer la configuration avant
de remplacer l'application partagée.

1. Installer `requirements.txt` (inclut `streamlit[auth]`) et sauvegarder la base.
2. Appliquer les migrations `20261005_import_manifest.sql` puis
   `20261006_workspace_snapshots.sql` dans le schéma `sw`. Les tables historiques et
   référentiels existants restent nécessaires ; ces migrations ne les recréent pas.
3. Enregistrer une application chez le fournisseur OIDC, avec l'URL exacte
   `https://votre-domaine/oauth2callback`. Copier `.streamlit/secrets.example.toml`
   vers le fichier secret du serveur et remplacer toutes les valeurs d'exemple.
   Utiliser HTTPS, un secret de cookie aléatoire, et ne pas versionner ce fichier.
4. Après vérification indépendante de la propriété du compte de jeu, ajouter un
   bloc `[[access.accounts]]` associant son `wizard_id` au couple exact `iss`/`sub`
   de l'identité vérifiée par le fournisseur. Ne pas prendre ces valeurs depuis un
   export, un nom de joueur ou une adresse email fournie librement. Plusieurs
   comptes peuvent être rattachés à la même identité par plusieurs blocs.
5. Vérifier les anciennes lignes `sw_user` dont `joueur_id=0`, ainsi que les doublons
   de `joueur_id`. Après contrôle administratif, renseigner l'identifiant externe
   sur la ligne historique correcte. L'application ne récupère plus automatiquement
   une ancienne ligne en faisant correspondre uniquement le pseudo.
6. Tester une connexion autorisée, une autre identité non autorisée, la déconnexion,
   puis le retrait d'un rattachement. Recharger les secrets/redémarrer les instances
   après leur modification ; le prochain rerun réévalue les droits et efface l'état
   privé si l'accès a été retiré. Les données déjà affichées dans un navigateur ne
   peuvent pas être rappelées à distance.

L'identité provient uniquement de `st.user`, jamais de `session_state` ou du JSON.
L'expiration du jeton est vérifiée lorsqu'elle est exposée par le fournisseur.
Les services d'import, suppression, préférences et instantanés vérifient aussi les
droits côté serveur. Les pages privées vérifient l'accès avant lecture, y compris
avant les lectures mises en cache. Les classements conservent leurs règles de
visibilité existantes.

Le flux réel avec votre fournisseur et vos secrets doit être validé au déploiement.
Les tests automatisés utilisent des identités contrôlées, sans appeler un fournisseur.
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
  sur le compte autorisé, après fermeture du navigateur. Les filtres nommés sont
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

Les préférences d'un compte sont partagées entre ses sessions autorisées : la dernière
sauvegarde remplace la précédente. Après toute modification dans le jeu, refaire un
export pour recalculer stock et verrous sur un inventaire à jour.
