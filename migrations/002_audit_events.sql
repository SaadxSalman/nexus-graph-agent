CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    request_id TEXT NOT NULL,
    session_id TEXT,
    tenant_id TEXT NOT NULL DEFAULT 'default',
    event_name TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS audit_events_session_idx ON audit_events (tenant_id, session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_events_request_idx ON audit_events (request_id);
