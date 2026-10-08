from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pandas as pd
import pytest
import os
from uuid import uuid4
from sqlalchemy import create_engine,text
from fonctions import gestion_bdd as db
from fonctions.import_service import analyse_export,persist_analysis,validate_export


def test_transaction_rolls_back_all_writes(engine):
    with pytest.raises(ValueError):
        with db.transaction():
            db.requete_perso_bdd('INSERT INTO writes VALUES (:id)',{'id':1})
            db.requete_perso_bdd('INSERT INTO writes VALUES (:id)',{'id':2})
            raise ValueError('forced failure')
    assert db.lire_bdd('writes').empty

def test_connections_are_not_shared_between_threads(engine):
    barrier=Barrier(2)
    def use_connection(_):
        with db.transaction() as conn:
            barrier.wait(timeout=5)
            with db.transaction() as nested:
                assert nested is conn
            return id(conn)
    with ThreadPoolExecutor(2) as pool:
        assert len(set(pool.map(use_connection,range(2))))==2

def test_import_idempotence_replace_day_and_delete(engine,export):
    result=analyse_export(validate_export(export),pd.DataFrame())
    metadata,created=persist_analysis(result,'04/10/2026')
    assert created
    assert not persist_analysis(result,'04/10/2026')[1]
    assert len(db.lire_bdd('sw_score').T)==1
    export['wizard_info']['wizard_mana']+=1
    result2=analyse_export(validate_export(export),pd.DataFrame())
    persist_analysis(result2,'04/10/2026')
    assert len(db.lire_bdd('sw_score').T)==1
    persist_analysis(result,'05/10/2026')
    assert len(db.lire_bdd('sw_score').T)==2
    db.supprimer_data(metadata['id_joueur'],'04/10/2026')
    assert len(db.lire_bdd('sw_score').T)==1
    db.supprimer_data_all(metadata['id_joueur'])
    for table in ['sw_score','sw_user','sw_scoring_com2us','sw_score_qual','sw_arte_top','sw_arte_substats','sw_imports']:
        assert db.lire_bdd(table).empty

def test_late_failure_leaves_previous_snapshot(engine,export,monkeypatch):
    result=analyse_export(validate_export(export),pd.DataFrame())
    persist_analysis(result,'04/10/2026')
    before=db.lire_bdd('sw_score')
    export['wizard_info']['wizard_mana']+=1
    updated=analyse_export(validate_export(export),pd.DataFrame())
    from fonctions import import_service
    def fail(*args): raise ValueError('late failure')
    monkeypatch.setattr(import_service,'update_info_compte',fail)
    with pytest.raises(ValueError): persist_analysis(updated,'04/10/2026')
    pd.testing.assert_frame_equal(before,db.lire_bdd('sw_score'))
