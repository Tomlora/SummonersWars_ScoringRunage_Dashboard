import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

@pytest.fixture
def export():
    return json.loads((Path(__file__).resolve().parents[1]/'examples/demo.json').read_text(encoding='utf-8'))

import os
from uuid import uuid4
from sqlalchemy import create_engine,text
from fonctions import gestion_bdd as db

@pytest.fixture(params=['sqlite'] + (['postgresql'] if os.environ.get('TEST_DATABASE_URL') else []))
def engine(tmp_path,monkeypatch,request):
    import streamlit as st
    from fonctions import access
    monkeypatch.setattr(access, "identity", lambda: ("https://test.invalid", "owner"))
    monkeypatch.setattr(access, "access_config", lambda: {"accounts":[{"wizard_id":1,"issuer":"https://test.invalid","subject":"owner"}]})
    st.cache_data.clear()
    admin = None
    if request.param == 'postgresql':
        admin = create_engine(os.environ['TEST_DATABASE_URL'])
        schema = 'test_' + uuid4().hex
        with admin.begin() as conn: conn.execute(text(f'CREATE SCHEMA {schema}'))
        engine = create_engine(os.environ['TEST_DATABASE_URL'],connect_args={'options':f'-csearch_path={schema}'})
    else:
        engine=create_engine('sqlite:///'+str(tmp_path/'test.sqlite'))
    monkeypatch.setattr(db,'init_connection',lambda:engine)
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE sw_user(id ' + ('BIGSERIAL' if request.param == 'postgresql' else 'INTEGER') + ' PRIMARY KEY, joueur TEXT, joueur_id BIGINT, guilde_id BIGINT, visibility INTEGER, rank INTEGER DEFAULT 0, lang TEXT)'))
        conn.execute(text('CREATE TABLE sw_guilde(guilde_id BIGINT PRIMARY KEY,guilde TEXT)'))
        conn.execute(text('CREATE TABLE writes(id INTEGER)'))
    yield engine
    engine.dispose()
    if admin is not None:
        with admin.begin() as conn: conn.execute(text(f'DROP SCHEMA {schema} CASCADE'))
        admin.dispose()
