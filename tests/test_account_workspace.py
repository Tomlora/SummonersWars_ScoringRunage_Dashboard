from copy import deepcopy
import pandas as pd
import pytest
from sqlalchemy import text
from fonctions import access, gestion_bdd as db
from fonctions.import_service import analyse_export, persist_analysis, validate_export
from fonctions.snapshots import list_snapshots, load_snapshot, compare_snapshots
from fonctions.workspace import settings, load_settings, save_settings


def imported(export): return analyse_export(validate_export(export),pd.DataFrame())


def test_same_day_snapshots_preferences_and_deletion(engine,export):
    result=imported(export);meta,_=persist_analysis(result,'06/10/2026');uid=meta['id_joueur']
    export['runes'][0]['sec_eff'][0][1]+=1
    persist_analysis(imported(export),'06/10/2026')
    snapshots=list_snapshots(uid)
    assert len(snapshots)==2
    assert len(db.lire_bdd('sw_score').T)==1
    before,after=[load_snapshot(uid,s['payload_sha'],s['scoring_version']) for s in snapshots]
    assert len(compare_snapshots(before,after))==1
    prefs=settings();prefs.update(locked_runes=[301],filters={'optimisation_filter_actions':['gem'],'optimisation_filter_priority':'high','plan_accuracy':50})
    save_settings(uid,prefs)
    assert load_settings(uid)==prefs
    db.supprimer_data(uid,'06/10/2026')
    assert list_snapshots(uid)==[]
    assert load_settings(uid)==prefs
    db.supprimer_data_all(uid)
    with engine.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_workspace')).scalar()==0


def test_duplicate_legacy_import_gets_detail_once(engine,export):
    result=imported(export);meta,_=persist_analysis(result,'06/10/2026');uid=meta['id_joueur']
    with engine.begin() as conn: conn.execute(text('DROP TABLE sw_rune_snapshots'))
    assert not persist_analysis(result,'07/10/2026')[1]
    assert not persist_analysis(result,'07/10/2026')[1]
    assert len(list_snapshots(uid))==1


def test_unauthorized_services_cannot_read_write_or_delete(engine,export,monkeypatch):
    result=imported(export);meta,_=persist_analysis(result);uid=meta['id_joueur']
    monkeypatch.setattr(access,'identity',lambda:('https://test.invalid','other'))
    for operation in [lambda:persist_analysis(result),lambda:load_settings(uid),lambda:save_settings(uid,settings()),
                      lambda:list_snapshots(uid),lambda:db.supprimer_data_all(uid),
                      lambda:db.requete_perso_bdd('UPDATE sw_user SET visibility=3 WHERE id=:joueur',{'joueur':uid})]:
        with pytest.raises(access.AccessDenied):operation()
    with engine.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_score')).scalar()==1
        assert conn.execute(text('SELECT visibility FROM sw_user')).scalar()==0


def test_spoofing_account_id_does_not_grant_access(engine,export):
    export['wizard_info']['wizard_id']=987654
    with pytest.raises(access.AccessDenied):persist_analysis(imported(export))
    with engine.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_user')).scalar()==0


def test_missing_identity_wrong_issuer_expiry_and_revocation(monkeypatch):
    class User(dict): pass
    monkeypatch.setattr(access.st,'user',User(is_logged_in=True,iss='issuer',sub='subject',exp=10**12))
    monkeypatch.setattr(access,'access_config',lambda:{'accounts':[dict(wizard_id=1,issuer='issuer',subject='subject')]})
    assert access.can_access(1)
    access.st.user['iss']='other';assert not access.can_access(1)
    access.st.user['iss']='issuer';access.st.user['exp']=0;assert not access.can_access(1)
    access.st.user['exp']=10**12;access.st.user['is_logged_in']=False;assert not access.can_access(1)
    access.st.user['is_logged_in']=True
    monkeypatch.setattr(access,'access_config',lambda:{})
    assert not access.can_access(1)


def test_late_snapshot_failure_rolls_back_everything(engine,export,monkeypatch):
    result=imported(export);meta,_=persist_analysis(result)
    from fonctions import snapshots
    before=db.lire_bdd('sw_score').copy();known=list_snapshots(meta['id_joueur'])
    export['runes'][0]['sec_eff'][0][1]+=1
    def fail(*args): raise ValueError('snapshot failure')
    monkeypatch.setattr(snapshots,'save_snapshot',fail)
    with pytest.raises(ValueError):persist_analysis(imported(export))
    pd.testing.assert_frame_equal(before,db.lire_bdd('sw_score'))
    assert list_snapshots(meta['id_joueur'])==known
