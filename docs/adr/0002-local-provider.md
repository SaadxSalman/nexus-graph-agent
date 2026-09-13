# ADR 0002: Deterministic Local Provider

## Status

Accepted

## Context

A reference architecture must be runnable in development and CI without paid model credentials or network access.

## Decision

Keep a deterministic local generator and local retrieval corpus as the default. Hosted providers are opt-in through `MODEL_PROVIDER` and explicit credentials.

## Consequences

The demo is reproducible and inexpensive. The local provider is not a substitute for semantic model quality; evaluation must run separately against the selected production provider.
