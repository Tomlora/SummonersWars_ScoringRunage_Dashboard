-- Apply to the existing dashboard database before deploying the new application.
-- This migration does not rewrite historical scores.
BEGIN;
CREATE TABLE IF NOT EXISTS sw.sw_imports (
    id_joueur BIGINT NOT NULL,
    payload_sha TEXT NOT NULL,
    scoring_version TEXT NOT NULL,
    date TEXT NOT NULL,
    PRIMARY KEY (id_joueur, payload_sha, scoring_version)
);
CREATE INDEX IF NOT EXISTS sw_imports_account_date ON sw.sw_imports(id_joueur, date);
COMMIT;
