"""Server-side OIDC identity and operator-managed game-account grants.

No identity or grant is accepted from the uploaded JSON or session_state.
"""
import time
import streamlit as st
from sqlalchemy import text


class AccessDenied(PermissionError):
    pass


def access_config():
    try:
        return dict(st.secrets.get('access', {}))
    except (FileNotFoundError, KeyError):
        return {}


def identity():
    user = st.user
    if not user.get('is_logged_in', False):
        return None
    issuer, subject = user.get('iss'), user.get('sub')
    expires = user.get('exp')
    if expires is not None and (not isinstance(expires, (int, float)) or expires <= time.time()):
        return None
    return (issuer, subject) if issuer and subject else None


def can_access(wizard_id):
    who = identity()
    if who is None:
        return False
    return any(str(g.get('wizard_id')) == str(wizard_id)
               and (g.get('issuer'), g.get('subject')) == who
               for g in access_config().get('accounts', []))


def require_account(wizard_id):
    if not can_access(wizard_id):
        raise AccessDenied('Compte non autorisé / Account not authorized')


def require_user(user_id):
    from fonctions.gestion_bdd import connection
    with connection() as conn:
        wizard = conn.execute(text('SELECT joueur_id FROM sw_user WHERE id=:id'), {'id': int(user_id)}).scalar()
    if wizard is None:
        raise AccessDenied('Compte inconnu / Unknown account')
    require_account(wizard)


def require_saved_page():
    user_id = st.session_state.get('id_joueur')
    try:
        if user_id is None:
            raise AccessDenied()
        require_user(user_id)
    except AccessDenied:
        st.error('Connectez-vous avec un compte autorisé / Sign in with an authorized account.')
        st.stop()


def login_panel():
    try:
        configured = bool(st.secrets.get('auth', {}).get('server_metadata_url'))
    except (FileNotFoundError, KeyError):
        configured = False
    if st.user.get('is_logged_in', False):
        st.sidebar.caption('Connexion / Signed in: ' + str(st.user.get('name', st.user.get('sub', ''))))
        if st.sidebar.button('Déconnexion / Sign out'):
            st.session_state.clear()
            st.logout()
    elif configured:
        if st.sidebar.button('Connexion / Sign in'):
            st.login()
