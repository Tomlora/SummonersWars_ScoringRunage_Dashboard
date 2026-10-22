from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text
from streamlit.testing.v1 import AppTest

from fonctions.community import community_counts

ROOT = Path(__file__).resolve().parents[1]


def seed_counts(engine):
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE count_rows ("table" TEXT, total BIGINT)'))
        for table, total in [('sw_user', 3860), ('sw_guilde', 1900), ('sw_score', 41230)]:
            conn.execute(text('INSERT INTO count_rows VALUES (:table, :total)'),
                         {'table': table, 'total': total})


def test_counts_cache_totals_and_refresh_time(engine):
    seed_counts(engine)
    before = datetime.now(ZoneInfo('Europe/Paris')).strftime('%H:%M')
    first = community_counts()
    after = datetime.now(ZoneInfo('Europe/Paris')).strftime('%H:%M')
    assert first[:3] == (3860, 1900, 41230)
    assert first[3] in (before, after)
    with engine.begin() as conn:
        conn.execute(text('UPDATE count_rows SET total=total+1'))
    assert community_counts() == first
    community_counts.clear()
    assert community_counts()[:3] == (3861, 1901, 41231)


@pytest.mark.parametrize('language,labels', [
    ('Français', ('utilisateurs', 'guildes', 'scores')),
    ('English', ('users', 'guilds', 'scores')),
])
def test_home_displays_community_counts(engine, monkeypatch, language, labels):
    seed_counts(engine)
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv('API_SQL', 'configured')
    app = AppTest.from_file(str(ROOT/'pages_streamlit/upload.py'))
    app.session_state['translations_selected'] = language
    app.run()
    assert not app.exception
    assert any(f':green[3860] {labels[0]} | :violet[1900] {labels[1]} | :orange[41230] {labels[2]}'
               in item.value for item in app.markdown)


def test_missing_counts_do_not_block_demo(engine, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv('API_SQL', 'configured')
    app = AppTest.from_file(str(ROOT/'pages_streamlit/upload.py')).run()
    assert not app.exception
    assert any('temporairement indisponibles' in item.value for item in app.caption)
    app.checkbox(key='demo_mode').check().run()
    app.button(key='upload_submit').click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state['analysis_ready']
