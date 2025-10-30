CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Raw patent grants we extract from IPG XML
CREATE TABLE IF NOT EXISTS grants_raw (
  patent        text PRIMARY KEY,
  title         text NOT NULL,
  grant_date    date,
  created_at    timestamptz DEFAULT now()
);

-- Raw maintenance fee events from ptmnfee ZIP
CREATE TABLE IF NOT EXISTS maint_events_raw (
  patent        text NOT NULL,
  event_code    text NOT NULL,     -- USPTO code (e.g., EXP, PMNT, REMI, etc.)
  event_date    date NOT NULL,
  details       jsonb DEFAULT '{}'::jsonb
);

-- Derived table: patents that are currently inactive (expired for non-payment)
CREATE TABLE IF NOT EXISTS inactive_patents (
  patent        text PRIMARY KEY,
  title         text NOT NULL,
  grant_date    date
);

-- Indexes for search speed
CREATE INDEX IF NOT EXISTS idx_grants_raw_title_trgm
  ON grants_raw USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_inactive_title_trgm
  ON inactive_patents USING gin (title gin_trgm_ops);