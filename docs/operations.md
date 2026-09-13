# Operations Runbook

## Startup Order

1. Apply database migrations.
2. Start Chroma or the configured vector service.
3. Start the Python agent and wait for `/ready`.
4. Start the Rust edge.
5. Probe the edge `/health` endpoint.

## Health Semantics

`/health` means the process is responding. `/ready` includes provider configuration warnings and is the better deployment readiness probe. A local provider warning is expected in development. A missing API key for an explicitly selected hosted provider must fail at process startup.

## Incident Triage

Capture the `x-request-id` response header first. Search structured logs for the same request ID, then inspect the session checkpoint. The response trace shows decomposition, retrieval iterations, grading, rewrites, and synthesis. Do not log raw prompts or retrieved content in production unless redacted and explicitly approved.

## Common Failures

### 502 from the Rust edge

Check that the agent is listening on `AGENT_BASE_URL`. Probe the agent directly. Inspect Docker service logs and the edge request ID.

### Low confidence

Inspect the source list and query rewrite trace. Confirm the corpus was ingested and that tenant filters are correct. Do not raise the confidence threshold blindly; add or repair evidence.

### MCP permission denied

Check `MCP_ALLOWED_TOOLS`. Tool names are exact and permission is checked at invocation time. Keep read and write tools in separate servers.

### Stale checkpoints

Check the configured `CHECKPOINT_DB` volume or PostgreSQL checkpoint table. A relative SQLite path is development-only.

## Backups and Recovery

Back up PostgreSQL documents, chunks, entities, relationships, checkpoints, and audit events. Chroma can be rebuilt from the system-of-record documents and embeddings. Test restoring a checkpoint and resuming a session in a staging environment.

## Security Response

Rotate provider keys through the deployment secret manager, revoke compromised MCP credentials, preserve audit events, and invalidate affected sessions. Do not commit incident material or secrets into the repository while investigating.
