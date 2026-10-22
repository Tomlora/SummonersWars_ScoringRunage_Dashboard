# Apparence

Le menu latéral **Apparence** propose trois palettes : Personnalisé (le bleu
sombre existant, par défaut), Blanc et Noir. Le choix est conservé dans le
navigateur, indépendamment de l’import et du compte. Un stockage bloqué ne doit
pas empêcher le changement immédiat ; la préférence ne sera alors pas conservée
après fermeture de la page. Aucune configuration globale du serveur n’est modifiée.

Le composant V2 utilise le message `SET_CUSTOM_THEME_CONFIG` de Streamlit 1.65.0
depuis la fenêtre de l’application vers sa propre origine. Le gestionnaire natif
applique ainsi la palette aux widgets et aux tableaux, y compris ceux dessinés
dans un canvas. Les variables CSS des éléments propres au dashboard sont mises
à jour en même temps. Les graphiques utilisent toujours `st.context.theme.type`.

Cette intégration est liée à la version de Streamlit fixée dans requirements.txt.
Lors d’une mise à jour de Streamlit, vérifier le protocole et refaire le contrôle
visuel ci-dessous. Ne pas remplacer ce mécanisme par une modification de
`st._config` : elle affecterait les autres utilisateurs.

## Déploiement

Redémarrer Streamlit après mise à jour de `.streamlit/config.toml`. La liste
`client.allowedOrigins` autorise uniquement le domaine de production
`https://scoringsw.eu` et les adresses de développement locales. Pour déployer
sous un autre domaine, ajouter son origine exacte à cette liste. Ne pas utiliser
un joker de domaine ni désactiver les protections CORS/XSRF. Si un proxy remplace
`/_stcore/host-config`, il doit également conserver cette origine autorisée.
Un message dans Apparence signale si le thème n’a pas été appliqué.

## Contrôle visuel

Sans utiliser Print, sélectionner Blanc, Noir, puis Personnalisé. Contrôler les
fonds de page et du menu, les champs, les tableaux, les graphiques et les cartes.
Changer de page, puis recharger : le choix doit rester actif. Refaire le parcours
en anglais et avec deux profils de navigateur distincts : leurs choix doivent
rester indépendants. Vérifier également les touches Tab et les flèches du groupe
de boutons radio.
