-- Run against the application's schema, after the existing import-manifest migration.
-- Application services also create these tables on their first authorized write.
BEGIN;
SET LOCAL search_path TO sw;
CREATE TABLE IF NOT EXISTS sw_workspace (
    id_joueur BIGINT PRIMARY KEY,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sw_rune_snapshots (
    id_joueur BIGINT NOT NULL,
    payload_sha TEXT NOT NULL,
    scoring_version TEXT NOT NULL,
    date TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY(id_joueur,payload_sha,scoring_version)
);
COMMIT;
